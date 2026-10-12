#ifndef ECG_INFERENCE_H
#define ECG_INFERENCE_H

#include <cstddef>
#include <cstdint>

namespace ecg_inference {

// TinyECGNet INT8 en TFLM. Solo se compila para la placa: depende de
// TensorFlowLite_ESP32 y de los headers del modelo en notebooks/data/modelos/.
// El harness nativo no incluye este modulo (usa la inferencia inyectada del runner).

bool begin();
bool ready();
size_t arenaSize();
// tensor: 2500 valores INT8 ya preprocesados/cuantizados. q y la cuantizacion de
// salida se leen del tensor de salida del modelo.
bool invoke(const int8_t* tensor, int8_t* q, float* out_scale, int* out_zero_point);

}  // namespace ecg_inference

#endif
