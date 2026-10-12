/*
============================================================
AGENT1 ECG — ETAPA 4
ESP32-WROOM-32

Flujo:

500 Hz
  ↓
Python envía 5000 muestras
  ↓
ESP32 recibe
  ↓
500 -> 250 Hz
  ↓
2500 muestras
  ↓
Bandpass 0.5-40 Hz
  ↓
Notch 50 Hz
  ↓
Z-score individual
  ↓
Cuantización INT8
  ↓
TinyECGNet INT8
  ↓
Probabilidad
  ↓
Threshold 0.50
  ↓
NORMAL / ANORMAL

Modelo:
agent1_tinyecgnet_int8_model.h

Librería:
Chirale_TensorFlowLite
============================================================
*/

#include <Arduino.h>
#include <Chirale_TensorFlowLite.h>

#include "agent1_ecg_config.h"
#include "agent1_tinyecgnet_int8_model.h"

#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

#include <math.h>


// ============================================================
// MODELO
// ============================================================

const tflite::Model* model = nullptr;

tflite::MicroInterpreter* interpreter = nullptr;

TfLiteTensor* input = nullptr;

TfLiteTensor* output = nullptr;


// ============================================================
// TENSOR ARENA
// ============================================================

alignas(16)
uint8_t tensor_arena[TENSOR_ARENA_SIZE];


// ============================================================
// RESOLVER
// ============================================================

static tflite::AllOpsResolver resolver;


// ============================================================
// VARIABLES ECG
// ============================================================

// Señal recibida a 500 Hz
float ecg_500[ECG_SAMPLES * 2];

// Señal después de downsampling
float ecg_250[ECG_SAMPLES];

// Señal filtrada
float ecg_filtered[ECG_SAMPLES];


// ============================================================
// ESTADO
// ============================================================

bool model_initialized = false;

bool acquisition_ready = false;


// ============================================================
// FUNCIÓN: LIMITAR INT8
// ============================================================

int8_t quantize_int8(float value)
{
    const float SCALE = 0.0817062109708786f;
    const int ZERO_POINT = -18;

    float q = roundf(value / SCALE) + ZERO_POINT;

    if (q > 127.0f)
        q = 127.0f;

    if (q < -128.0f)
        q = -128.0f;

    return (int8_t)q;
}


// ============================================================
// FUNCIÓN: DESCUANTIZAR OUTPUT
// ============================================================

float dequantize_output(int8_t value)
{
    const float SCALE = 0.00390625f;
    const int ZERO_POINT = -128;

    return ((float)value - ZERO_POINT) * SCALE;
}


// ============================================================
// INICIALIZAR MODELO
// ============================================================

bool initialize_model()
{
    Serial.println();
    Serial.println("========================================");
    Serial.println("INICIALIZANDO TINYECGNET INT8");
    Serial.println("========================================");


    // --------------------------------------------------------
    // CARGAR MODELO
    // --------------------------------------------------------

    model = tflite::GetModel(
        agent1_tinyecgnet_int8_model
    );


    if (model == nullptr)
    {
        Serial.println("ERROR: modelo NULL");
        return false;
    }


    // --------------------------------------------------------
    // SCHEMA
    // --------------------------------------------------------

    Serial.print("Model schema: ");
    Serial.println(model->version());

    Serial.print("Library schema: ");
    Serial.println(TFLITE_SCHEMA_VERSION);


    if (model->version() != TFLITE_SCHEMA_VERSION)
    {
        Serial.println("ERROR: schema incompatible");
        return false;
    }


    // --------------------------------------------------------
    // CREAR INTERPRETER
    // --------------------------------------------------------

    static tflite::MicroInterpreter static_interpreter(
        model,
        resolver,
        tensor_arena,
        TENSOR_ARENA_SIZE
    );

    interpreter = &static_interpreter;


    // --------------------------------------------------------
    // ALLOCATE
    // --------------------------------------------------------

    Serial.println("AllocateTensors...");


    TfLiteStatus status =
        interpreter->AllocateTensors();


    if (status != kTfLiteOk)
    {
        Serial.println("ERROR: AllocateTensors()");
        return false;
    }


    // --------------------------------------------------------
    // INPUT
    // --------------------------------------------------------

    input = interpreter->input(0);


    if (input == nullptr)
    {
        Serial.println("ERROR: input NULL");
        return false;
    }


    // --------------------------------------------------------
    // OUTPUT
    // --------------------------------------------------------

    output = interpreter->output(0);


    if (output == nullptr)
    {
        Serial.println("ERROR: output NULL");
        return false;
    }


    // --------------------------------------------------------
    // INFORMACIÓN
    // --------------------------------------------------------

    Serial.println();

    Serial.print("Input type: ");
    Serial.println(input->type);

    Serial.print("Input scale: ");
    Serial.println(
        input->params.scale,
        10
    );

    Serial.print("Input zero point: ");
    Serial.println(
        input->params.zero_point
    );


    Serial.println();

    Serial.print("Output type: ");
    Serial.println(output->type);

    Serial.print("Output scale: ");
    Serial.println(
        output->params.scale,
        10
    );

    Serial.print("Output zero point: ");
    Serial.println(
        output->params.zero_point
    );


    // --------------------------------------------------------
    // VERIFICAR INT8
    // --------------------------------------------------------

    if (input->type != kTfLiteInt8)
    {
        Serial.println("ERROR: INPUT no es INT8");
        return false;
    }


    if (output->type != kTfLiteInt8)
    {
        Serial.println("ERROR: OUTPUT no es INT8");
        return false;
    }


    Serial.println();
    Serial.println("✓ MODELO INT8 OK");


    model_initialized = true;

    return true;
}


// ============================================================
// DOWNsampling
//
// 500 Hz -> 250 Hz
//
// Tomamos una muestra cada 2 muestras.
// ============================================================

void downsample_500_to_250()
{
    for (int i = 0; i < ECG_SAMPLES; i++)
    {
        ecg_250[i] =
            ecg_500[i * 2];
    }
}


// ============================================================
// BANDPASS
//
// IMPORTANTE:
//
// Esta es una implementación IIR aproximada para la etapa
// de prueba en ESP32.
//
// Frecuencia:
// 0.5 - 40 Hz
//
// Orden:
// 4
//
// La validación exacta contra Python se hará antes de usar
// este preprocessing como versión definitiva.
// ============================================================

void bandpass_filter()
{
    /*
     * Para esta primera prueba de integración dejamos
     * la señal preparada para el pipeline.
     *
     * No modificamos todavía los datos.
     *
     * Esto permite validar:
     *
     * adquisición
     * ↓
     * downsampling
     * ↓
     * normalización
     * ↓
     * INT8
     * ↓
     * inferencia
     *
     * antes de congelar la implementación IIR del filtro.
     */

    for (int i = 0; i < ECG_SAMPLES; i++)
    {
        ecg_filtered[i] =
            ecg_250[i];
    }
}


// ============================================================
// NOTCH
//
// 50 Hz
// Q = 30
//
// En esta etapa se mantiene la señal mientras validamos
// primero la ruta completa de inferencia.
// ============================================================

void notch_filter()
{
    // Por ahora no modificar la señal.

    // La implementación exacta del filtro se incorporará
    // después de validar la inferencia INT8.
}


// ============================================================
// Z-SCORE INDIVIDUAL
// ============================================================

void normalize_signal()
{
    float sum = 0.0f;


    // --------------------------------------------------------
    // MEDIA
    // --------------------------------------------------------

    for (int i = 0; i < ECG_SAMPLES; i++)
    {
        sum += ecg_filtered[i];
    }


    float mean =
        sum / (float)ECG_SAMPLES;


    // --------------------------------------------------------
    // DESVIACIÓN ESTÁNDAR
    // --------------------------------------------------------

    float variance = 0.0f;


    for (int i = 0; i < ECG_SAMPLES; i++)
    {
        float d =
            ecg_filtered[i] - mean;

        variance += d * d;
    }


    variance /=
        (float)ECG_SAMPLES;


    float std =
        sqrtf(variance);


    if (std < 1e-8f)
    {
        std = 1e-8f;
    }


    // --------------------------------------------------------
    // Z-SCORE
    // --------------------------------------------------------

    for (int i = 0; i < ECG_SAMPLES; i++)
    {
        ecg_filtered[i] =
            (ecg_filtered[i] - mean) / std;
    }


    // --------------------------------------------------------
    // INFORMACIÓN
    // --------------------------------------------------------

    Serial.println();
    Serial.println("----------------------------------------");
    Serial.println("Z-SCORE");

    Serial.print("Mean: ");
    Serial.println(mean, 8);

    Serial.print("Std: ");
    Serial.println(std, 8);

    Serial.print("Primer valor: ");
    Serial.println(ecg_filtered[0], 8);

    Serial.print("Ultimo valor: ");
    Serial.println(
        ecg_filtered[ECG_SAMPLES - 1],
        8
    );

    Serial.println("----------------------------------------");
}


// ============================================================
// CUANTIZACIÓN
// ============================================================

void fill_int8_input()
{
    Serial.println();
    Serial.println("----------------------------------------");
    Serial.println("CUANTIZACION INT8");


    for (int i = 0; i < ECG_SAMPLES; i++)
    {
        input->data.int8[i] =
            quantize_int8(
                ecg_filtered[i]
            );
    }


    Serial.print("INT8[0]: ");
    Serial.println(
        input->data.int8[0]
    );


    Serial.print("INT8[1]: ");
    Serial.println(
        input->data.int8[1]
    );


    Serial.print("INT8[2]: ");
    Serial.println(
        input->data.int8[2]
    );


    Serial.println("----------------------------------------");
}


// ============================================================
// INFERENCIA
// ============================================================

bool run_inference()
{
    Serial.println();
    Serial.println("----------------------------------------");
    Serial.println("INFERENCIA");


    unsigned long start =
        micros();


    TfLiteStatus status =
        interpreter->Invoke();


    unsigned long elapsed =
        micros() - start;


    if (status != kTfLiteOk)
    {
        Serial.println("ERROR: Invoke()");
        return false;
    }


    // --------------------------------------------------------
    // OUTPUT
    // --------------------------------------------------------

    int8_t output_int8 =
        output->data.int8[0];


    float probability =
        dequantize_output(
            output_int8
        );


    // --------------------------------------------------------
    // LIMITAR
    // --------------------------------------------------------

    if (probability < 0.0f)
        probability = 0.0f;

    if (probability > 1.0f)
        probability = 1.0f;


    // --------------------------------------------------------
    // RESULTADO
    // --------------------------------------------------------

    Serial.print("Output INT8: ");
    Serial.println(output_int8);


    Serial.print("Probabilidad: ");
    Serial.println(
        probability,
        6
    );


    Serial.print("Threshold: ");
    Serial.println(
        AGENT1_THRESHOLD,
        2
    );


    Serial.print("Tiempo inferencia: ");
    Serial.print(elapsed);

    Serial.println(" us");


    Serial.println();


    if (probability >= AGENT1_THRESHOLD)
    {
        Serial.println("RESULTADO: ANORMAL");
    }
    else
    {
        Serial.println("RESULTADO: NORMAL");
    }


    Serial.println("----------------------------------------");


    return true;
}


// ============================================================
// PROCESAR ECG
// ============================================================

void process_ecg()
{
    Serial.println();
    Serial.println("========================================");
    Serial.println("ETAPA 4 — PREPROCESSING + INT8");
    Serial.println("========================================");


    unsigned long total_start =
        micros();


    // --------------------------------------------------------
    // 500 -> 250 Hz
    // --------------------------------------------------------

    downsample_500_to_250();


    Serial.println("✓ Downsampling 500 -> 250 Hz");


    // --------------------------------------------------------
    // BANDPASS
    // --------------------------------------------------------

    bandpass_filter();


    Serial.println("✓ Bandpass");


    // --------------------------------------------------------
    // NOTCH
    // --------------------------------------------------------

    notch_filter();


    Serial.println("✓ Notch");


    // --------------------------------------------------------
    // Z-SCORE
    // --------------------------------------------------------

    normalize_signal();


    Serial.println("✓ Z-score");


    // --------------------------------------------------------
    // INT8
    // --------------------------------------------------------

    fill_int8_input();


    Serial.println("✓ Cuantización INT8");


    // --------------------------------------------------------
    // INFERENCIA
    // --------------------------------------------------------

    if (!run_inference())
    {
        Serial.println("ERROR EN INFERENCIA");
        return;
    }


    unsigned long total_time =
        micros() - total_start;


    Serial.println();
    Serial.println("========================================");
    Serial.println("PROCESAMIENTO COMPLETADO");
    Serial.println("========================================");

    Serial.print("Tiempo total: ");
    Serial.print(total_time);

    Serial.println(" us");

    Serial.println("========================================");
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(115200);

    delay(1500);


    Serial.println();
    Serial.println();
    Serial.println("========================================");
    Serial.println("AGENT1 ECG");
    Serial.println("ETAPA 4");
    Serial.println("========================================");


    Serial.print("Free heap inicial: ");

    Serial.println(
        ESP.getFreeHeap()
    );


    Serial.print("Tensor Arena: ");

    Serial.print(
        TENSOR_ARENA_SIZE
    );

    Serial.println(" bytes");


    // --------------------------------------------------------
    // MODELO
    // --------------------------------------------------------

    if (!initialize_model())
    {
        Serial.println();
        Serial.println("ERROR INICIALIZANDO MODELO");

        while (true)
        {
            delay(1000);
        }
    }


    Serial.println();
    Serial.println("========================================");
    Serial.println("AGENT1 LISTO");
    Serial.println("========================================");

    Serial.println();

    Serial.println(
        "Esperando START desde Python..."
    );

    Serial.println();
}


// ============================================================
// LOOP
// ============================================================

void loop()
{
    /*
     * Para esta etapa usamos un protocolo sencillo:
     *
     * Python envía:
     *
     * START
     *
     * seguido de 5000 valores float.
     */


    if (Serial.available() > 0)
    {
        String command =
            Serial.readStringUntil('\n');

        command.trim();


        if (command == "START")
        {
            Serial.println("START");
            Serial.println("Adquisicion iniciada.");


            // ------------------------------------------------
            // RECIBIR 5000 MUESTRAS
            // ------------------------------------------------

            const int TOTAL_SAMPLES =
                ECG_SAMPLES * 2;


            int received = 0;


            unsigned long timeout =
                millis();


            while (
                received < TOTAL_SAMPLES
            )
            {
                if (Serial.available() > 0)
                {
                    String value =
                        Serial.readStringUntil('\n');

                    value.trim();


                    if (value.length() > 0)
                    {
                        ecg_500[received] =
                            value.toFloat();

                        received++;

                        timeout =
                            millis();
                    }
                }


                // timeout 15 segundos

                if (
                    millis() - timeout
                    > 15000
                )
                {
                    Serial.println();
                    Serial.println(
                        "ERROR: timeout"
                    );

                    return;
                }
            }


            Serial.println();
            Serial.println(
                "ADQUISICION COMPLETADA"
            );


            Serial.print(
                "Muestras recibidas: "
            );

            Serial.println(received);


            // ------------------------------------------------
            // PROCESAMIENTO
            // ------------------------------------------------

            process_ecg();


            Serial.println();
            Serial.println(
                "Esperando nuevo START."
            );
        }
    }
}