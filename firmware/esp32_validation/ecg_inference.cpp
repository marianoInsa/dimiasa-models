#define TFLITE_USE_CTIME

#include "ecg_inference.h"

#include <Arduino.h>
#include <esp_heap_caps.h>
#include <new>

#include <TensorFlowLite_ESP32.h>

#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

#include "agent1_tinyecgnet_sequential_int8_config.h"
#include "agent1_tinyecgnet_sequential_int8_model.h"

namespace ecg_inference {

namespace {

constexpr size_t kArenaSize = 80 * 1024;

tflite::MicroErrorReporter g_error_reporter;
tflite::MicroMutableOpResolver<40> g_resolver;
tflite::MicroInterpreter* g_interpreter = nullptr;
// Un unico bloque de 80 KiB dedicado a TinyECGNet. Se asigna del heap al arrancar
// porque el segmento estatico de DRAM del ESP32 (~124,6 KiB) no admite el proyecto
// completo; el tamano y el uso exclusivo para B no cambian.
uint8_t* g_arena = nullptr;

// Misma lista de operadores que el baseline sintetico historico que ejecuto este
// modelo en esta placa (firmware/esp32_int8_baseline/esp32_int8_baseline.ino).
bool registerOperators() {
#define AGREGAR_OP(OP)                  \
  do {                                  \
    if (g_resolver.OP() != kTfLiteOk) { \
      return false;                     \
    }                                   \
  } while (0)
  AGREGAR_OP(AddConv2D);
  AGREGAR_OP(AddDepthwiseConv2D);
  AGREGAR_OP(AddMaxPool2D);
  AGREGAR_OP(AddAveragePool2D);
  AGREGAR_OP(AddFullyConnected);
  AGREGAR_OP(AddReshape);
  AGREGAR_OP(AddExpandDims);
  AGREGAR_OP(AddSqueeze);
  AGREGAR_OP(AddMean);
  AGREGAR_OP(AddAdd);
  AGREGAR_OP(AddMul);
  AGREGAR_OP(AddSub);
  AGREGAR_OP(AddLogistic);
  AGREGAR_OP(AddTanh);
  AGREGAR_OP(AddRelu);
  AGREGAR_OP(AddRelu6);
  AGREGAR_OP(AddLeakyRelu);
  AGREGAR_OP(AddConcatenation);
  AGREGAR_OP(AddTranspose);
  AGREGAR_OP(AddSplit);
  AGREGAR_OP(AddSplitV);
  AGREGAR_OP(AddStridedSlice);
  AGREGAR_OP(AddShape);
  AGREGAR_OP(AddPack);
  AGREGAR_OP(AddUnpack);
  AGREGAR_OP(AddPad);
  AGREGAR_OP(AddQuantize);
  AGREGAR_OP(AddDequantize);
  AGREGAR_OP(AddSoftmax);
  AGREGAR_OP(AddSquare);
  AGREGAR_OP(AddMaximum);
  AGREGAR_OP(AddMinimum);
  AGREGAR_OP(AddReduceMax);
#undef AGREGAR_OP
  return true;
}

}  // namespace

bool begin() {
  if (g_interpreter != nullptr) {
    return true;
  }
  const tflite::Model* model = tflite::GetModel(agent1_tinyecgnet_sequential_int8_model);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    return false;
  }
  if (!registerOperators()) {
    return false;
  }
  g_arena = static_cast<uint8_t*>(heap_caps_aligned_alloc(16, kArenaSize, MALLOC_CAP_8BIT));
  if (g_arena == nullptr) {
    return false;
  }
  g_interpreter = new tflite::MicroInterpreter(model, g_resolver, g_arena, kArenaSize,
                                               &g_error_reporter);
  if (g_interpreter->AllocateTensors() != kTfLiteOk) {
    return false;
  }
  const TfLiteTensor* input = g_interpreter->input(0);
  const TfLiteTensor* output = g_interpreter->output(0);
  if (input->type != kTfLiteInt8 || input->bytes != TAMANO_VENTANA) {
    return false;
  }
  if (output->type != kTfLiteInt8 || output->bytes != 1 || output->params.scale <= 0.0f) {
    return false;
  }
  return true;
}

bool ready() { return g_interpreter != nullptr; }

size_t arenaSize() { return kArenaSize; }

bool invoke(const int8_t* tensor, int8_t* q, float* out_scale, int* out_zero_point) {
  if (g_interpreter == nullptr) {
    return false;
  }
  TfLiteTensor* input = g_interpreter->input(0);
  for (int i = 0; i < TAMANO_VENTANA; ++i) {
    input->data.int8[i] = tensor[i];
  }
  if (g_interpreter->Invoke() != kTfLiteOk) {
    return false;
  }
  const TfLiteTensor* output = g_interpreter->output(0);
  *q = output->data.int8[0];
  *out_scale = output->params.scale;
  *out_zero_point = output->params.zero_point;
  return true;
}

}  // namespace ecg_inference
