// ============================================================
// TEST CONJUNTO: MODELO A (CAIDAS) + MODELO B (ECG)
// Placa: ESP32
// Biblioteca: TensorFlowLite_ESP32
// ============================================================

#define TFLITE_USE_CTIME

#include <Arduino.h>
#include <math.h>
#include <esp_system.h>

#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/schema/schema_generated.h"

// ------------------------------------------------------------
// HEADERS DE LOS MODELOS Y SUS CONFIGURACIONES
// ------------------------------------------------------------

#include "litefallnet_sisfall_int8_model.h"
#include "litefallnet_sisfall_int8_config.h"

#include "agent1_tinyecgnet_sequential_int8_model.h"
#include "agent1_tinyecgnet_sequential_int8_config.h"

// Fallback por si la constante no está expuesta en el header
#ifndef LITEFALLNET_UMBRAL_CAIDA
  #define LITEFALLNET_UMBRAL_CAIDA 0.5f
#endif

#define FALL_MODEL_DATA litefallnet_sisfall_int8_model
#define ECG_MODEL_DATA  agent1_tinyecgnet_sequential_int8_model

// ------------------------------------------------------------
// DIMENSIONES ESPERADAS
// ------------------------------------------------------------

// Modelo A: [1, 150, 2] = AVM + GVM
constexpr int FALL_SAMPLES = 150;
constexpr int FALL_CHANNELS = 2;
constexpr int FALL_INPUT_BYTES = FALL_SAMPLES * FALL_CHANNELS;

// Modelo B: [1, 2500, 1] = ECG
constexpr int ECG_SAMPLES = 2500;

// ------------------------------------------------------------
// MEMORIA COMPARTIDA (ARENA ÚNICA)
// ------------------------------------------------------------
// Una sola arena compartida por ambos modelos.
// Los modelos se ejecutarán secuencialmente para no desbordar DRAM.
constexpr size_t TENSOR_ARENA_SIZE = 80 * 1024;

alignas(16) static uint8_t tensor_arena[TENSOR_ARENA_SIZE];

// ------------------------------------------------------------
// TENSORFLOW LITE MICRO
// ------------------------------------------------------------

tflite::MicroErrorReporter micro_error_reporter;

// Resolver compartido: contiene operadores para ambos modelos.
tflite::MicroMutableOpResolver<40> resolver;

// Punteros a los modelos
const tflite::Model* fall_model = nullptr;
const tflite::Model* ecg_model = nullptr;


// ============================================================
// REGISTRAR OPERADORES
// ============================================================

bool registerOperators() {
  Serial.println("\n[PASO 1] Registrando operadores...");

  #define ADD_OP(OP)                                              \
    do {                                                          \
      if (resolver.OP() != kTfLiteOk) {                           \
        Serial.printf("ERROR registrando %s\n", #OP);             \
        return false;                                             \
      }                                                           \
    } while (0)

  ADD_OP(AddConv2D);
  ADD_OP(AddDepthwiseConv2D);
  ADD_OP(AddMaxPool2D);
  ADD_OP(AddAveragePool2D);

  ADD_OP(AddFullyConnected);
  ADD_OP(AddReshape);
  ADD_OP(AddExpandDims);
  ADD_OP(AddSqueeze);

  ADD_OP(AddMean);
  ADD_OP(AddAdd);
  ADD_OP(AddMul);
  ADD_OP(AddSub);

  ADD_OP(AddLogistic);
  ADD_OP(AddTanh);
  ADD_OP(AddRelu);
  ADD_OP(AddRelu6);
  ADD_OP(AddLeakyRelu);

  ADD_OP(AddConcatenation);
  ADD_OP(AddTranspose);
  ADD_OP(AddSplit);
  ADD_OP(AddSplitV);
  ADD_OP(AddStridedSlice);

  ADD_OP(AddShape);
  ADD_OP(AddPack);
  ADD_OP(AddUnpack);
  ADD_OP(AddPad);

  ADD_OP(AddQuantize);
  ADD_OP(AddDequantize);
  ADD_OP(AddSoftmax);
  ADD_OP(AddSquare);
  ADD_OP(AddMaximum);
  ADD_OP(AddMinimum);

  // Operador faltante para capas de GlobalMaxPooling / tf.reduce_max:
  ADD_OP(AddReduceMax);

  #undef ADD_OP

  Serial.println("[PASO 1] Operadores registrados.");
  return true;
}


// ============================================================
// VERIFICAR MODELO
// ============================================================

bool checkModelVersion(const tflite::Model* model, const char* model_name) {
  if (model == nullptr) {
    Serial.printf("ERROR: %s no se pudo cargar.\n", model_name);
    return false;
  }

  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.printf("ERROR: version de schema incompatible en %s.\n", model_name);
    return false;
  }

  Serial.printf("%s: modelo y schema correctos.\n", model_name);
  return true;
}


// ============================================================
// GENERAR ENTRADA SINTETICA PARA EL MODELO A
// ============================================================

void fillSyntheticFallInput(TfLiteTensor* input) {
  const int zero_point = input->params.zero_point;

  for (int i = 0; i < FALL_SAMPLES; i++) {
    // Canal 0: AVM | Canal 1: GVM
    int q_avm = zero_point + (int)roundf(8.0f * sinf(2.0f * PI * 2.0f * i / 50.0f));
    int q_gvm = zero_point + (int)roundf(10.0f * sinf(2.0f * PI * 0.8f * i / 50.0f + 0.5f));

    q_avm = constrain(q_avm, -128, 127);
    q_gvm = constrain(q_gvm, -128, 127);

    input->data.int8[i * FALL_CHANNELS]     = (int8_t)q_avm;
    input->data.int8[i * FALL_CHANNELS + 1] = (int8_t)q_gvm;
  }
}


// ============================================================
// GENERAR ENTRADA SINTETICA PARA EL MODELO B
// ============================================================

void fillSyntheticEcgInput(TfLiteTensor* input) {
  const int zero_point = input->params.zero_point;

  for (int i = 0; i < ECG_SAMPLES; i++) {
    float t = (float)i / 250.0f;
    float wave = 8.0f * sinf(2.0f * PI * 1.2f * t) + 2.0f * sinf(2.0f * PI * 12.0f * t);

    int q = zero_point + (int)roundf(wave);
    q = constrain(q, -128, 127);

    input->data.int8[i] = (int8_t)q;
  }
}


// ============================================================
// MOSTRAR INFORMACION Y VALIDAR TENSOR
// ============================================================

bool validateTensors(TfLiteTensor* input,
                     TfLiteTensor* output,
                     int expected_input_bytes,
                     const char* model_name) {
  if (input == nullptr || output == nullptr) {
    Serial.printf("ERROR: tensores nulos en %s.\n", model_name);
    return false;
  }

  Serial.printf("%s - Entrada: tipo=%d, bytes=%d\n", model_name, input->type, (int)input->bytes);
  Serial.printf("%s - Salida:  tipo=%d, bytes=%d\n", model_name, output->type, (int)output->bytes);

  if (input->type != kTfLiteInt8 || input->bytes != expected_input_bytes) {
    Serial.printf("ERROR: tipo o dimension de entrada inesperados en %s.\n", model_name);
    return false;
  }

  if (output->type != kTfLiteInt8 || output->bytes != 1) {
    Serial.printf("ERROR: tipo o dimension de salida inesperados en %s.\n", model_name);
    return false;
  }

  if (input->params.scale <= 0.0f || output->params.scale <= 0.0f) {
    Serial.printf("ERROR: escala de cuantizacion invalida en %s.\n", model_name);
    return false;
  }

  return true;
}


// ============================================================
// EJECUTAR MODELO A: DETECCION DE CAIDAS
// ============================================================

void runFallModel(tflite::MicroInterpreter* interpreter) {
  Serial.println("\n----------------------------------------");
  Serial.println("MODELO A - DETECCION DE CAIDAS");
  Serial.println("----------------------------------------");

  TfLiteTensor* input = interpreter->input(0);
  TfLiteTensor* output = interpreter->output(0);

  if (!validateTensors(input, output, FALL_INPUT_BYTES, "Modelo A")) {
    return;
  }

  Serial.println("[A] Generando entrada sintetica...");
  fillSyntheticFallInput(input);

  Serial.println("[A] Ejecutando Invoke...");
  uint32_t start_us = micros();

  if (interpreter->Invoke() != kTfLiteOk) {
    Serial.println("ERROR: Invoke fallo en el modelo A.");
    return;
  }

  uint32_t elapsed_us = micros() - start_us;

  int q_output = output->data.int8[0];

  // Descuantificación y delimitación en [0.0, 1.0]
  float probability = (q_output - output->params.zero_point) * output->params.scale;
  probability = constrain(probability, 0.0f, 1.0f);

  Serial.printf("Salida int8: %d\n", q_output);
  Serial.printf("Probabilidad de caida: %.4f\n", probability);
  Serial.printf("Tiempo Invoke: %lu us\n", (unsigned long)elapsed_us);

  // Clasificación por umbral configurado
  Serial.printf(
    "Clasificacion: %s\n",
    probability >= LITEFALLNET_UMBRAL_CAIDA ? "CAIDA" : "ACTIVIDAD NORMAL"
  );

  Serial.println("[A] Inferencia finalizada.");
}


// ============================================================
// EJECUTAR MODELO B: CLASIFICACION DE ECG
// ============================================================

void runEcgModel(tflite::MicroInterpreter* interpreter) {
  Serial.println("\n----------------------------------------");
  Serial.println("MODELO B - CLASIFICACION DE ECG");
  Serial.println("----------------------------------------");

  TfLiteTensor* input = interpreter->input(0);
  TfLiteTensor* output = interpreter->output(0);

  if (!validateTensors(input, output, ECG_SAMPLES, "Modelo B")) {
    return;
  }

  Serial.println("[B] Generando entrada sintetica...");
  fillSyntheticEcgInput(input);

  Serial.println("[B] Ejecutando Invoke...");
  uint32_t start_us = micros();

  if (interpreter->Invoke() != kTfLiteOk) {
    Serial.println("ERROR: Invoke fallo en el modelo B.");
    return;
  }

  uint32_t elapsed_us = micros() - start_us;

  int q_output = output->data.int8[0];

  float probability = (q_output - output->params.zero_point) * output->params.scale;
  probability = constrain(probability, 0.0f, 1.0f);

  Serial.printf("Salida int8: %d\n", q_output);
  Serial.printf("Probabilidad: %.4f\n", probability);
  Serial.printf("Tiempo Invoke: %lu us\n", (unsigned long)elapsed_us);

  Serial.printf(
    "Clasificacion: %s\n",
    probability >= 0.5f ? "ECG ANORMAL" : "ECG NORMAL"
  );

  Serial.println("[B] Inferencia finalizada.");
}


// ============================================================
// SETUP
// ============================================================

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println("\n========================================");
  Serial.println(" TEST CONJUNTO DE MODELOS EN ESP32");
  Serial.println(" Modelo A: Caidas");
  Serial.println(" Modelo B: ECG");
  Serial.println("========================================");

  Serial.printf("Heap libre inicial: %u bytes\n", (unsigned int)ESP.getFreeHeap());
  Serial.printf("Arena compartida:   %u bytes\n", (unsigned int)TENSOR_ARENA_SIZE);

  // 1. Cargar ambos modelos
  Serial.println("\n[PASO 0] Cargando modelos...");

  fall_model = tflite::GetModel(FALL_MODEL_DATA);
  ecg_model  = tflite::GetModel(ECG_MODEL_DATA);

  if (!checkModelVersion(fall_model, "Modelo A") ||
      !checkModelVersion(ecg_model, "Modelo B")) {
    return;
  }

  // 2. Registrar operadores compartidos
  if (!registerOperators()) {
    return;
  }

  // ============================================================
  // MODELO A: CAIDAS
  // ============================================================
  Serial.println("\n[PASO 2] Inicializando modelo A...");

  {
    // El interprete existe localmente solo en este bloque
    tflite::MicroInterpreter fall_interpreter(
      fall_model,
      static_cast<const tflite::MicroOpResolver&>(resolver),
      tensor_arena,
      TENSOR_ARENA_SIZE,
      &micro_error_reporter
    );

    if (fall_interpreter.AllocateTensors() != kTfLiteOk) {
      Serial.println("ERROR: AllocateTensors fallo en modelo A.");
      return;
    }

    Serial.println("Modelo A: tensores reservados correctamente.");
    runFallModel(&fall_interpreter);

  } // El interprete A se destruye aquí liberando el uso de la arena

  // ============================================================
  // MODELO B: ECG
  // ============================================================
  Serial.println("\n[PASO 3] Inicializando modelo B...");

  {
    // Reutiliza la misma arena limpia en memoria
    tflite::MicroInterpreter ecg_interpreter(
      ecg_model,
      static_cast<const tflite::MicroOpResolver&>(resolver),
      tensor_arena,
      TENSOR_ARENA_SIZE,
      &micro_error_reporter
    );

    if (ecg_interpreter.AllocateTensors() != kTfLiteOk) {
      Serial.println("ERROR: AllocateTensors fallo en modelo B.");
      return;
    }

    Serial.println("Modelo B: tensores reservados correctamente.");
    runEcgModel(&ecg_interpreter);

  } // El interprete B se destruye aquí

  Serial.printf("\nHeap libre al finalizar: %u bytes\n", (unsigned int)ESP.getFreeHeap());

  Serial.println("\n========================================");
  Serial.println(" FIN DEL TEST CONJUNTO");
  Serial.println("========================================");
}


// ============================================================
// LOOP
// ============================================================

void loop() {
  // Test unitario ejecutado una sola vez en setup()
}
