#ifndef AGENT_RUNNER_H
#define AGENT_RUNNER_H

#include <cstdint>

#include "ecg_agent.h"
#include "fall_agent.h"
#include "serial_protocol.h"
#include "triage.h"

namespace agent_runner {

// Orquestacion portable de A y B: alimenta los agentes, acumula tiempos y emite las
// lineas AGENT al cerrar cada bloque y RESULT al cerrar un CASE. Las dependencias
// (escritura, inferencia, reloj y heap) se inyectan para poder probar el runner en el
// harness nativo sin TFLM.
//
//   AGENT,A,<id>,<clase>,<estado>,<confirmado>,<muestras>,<ventanas>,<fall_us>,<heap>
//   AGENT,B,<id>,<clase>,<q>,<p>,<recibidas>,<saturados>,<tensor_fnv>,<zmin>,<zmax>,<preproc_us>,<infer_us>,<heap>
//   RESULT,<case_id>,<color_o_INDETERMINADO>,<clase_caida>,<clase_ecg>,<triage_us>
// RESULT solo cubre las cuatro reglas validas o A INDETERMINADO; las entradas
// ausentes/invalidas no llegan aqui (el protocolo descarta el caso).

using NowUsFn = uint32_t (*)();
using HeapFn = uint32_t (*)();
// Devuelve false si la inferencia falla; en exito entrega q y la cuantizacion de salida.
using InferFn = bool (*)(void* context, const int8_t* tensor, int8_t* q, float* out_scale,
                         int* out_zero_point);

class AgentRunner {
 public:
  AgentRunner(serial_protocol::WriteFn write, void* write_context, InferFn infer,
              void* infer_context, NowUsFn now_us, HeapFn free_heap);

  const serial_protocol::AgentHooks* hooks() const { return &hooks_; }

  void beginCase(char agent, const char* id, uint32_t count);
  void addSampleA(const float values[6]);
  void addSampleB(uint16_t value);
  bool finishCase(const char* id, uint32_t received);
  void onCaseReady(const char* case_id);

 private:
  static void trampolineBegin(void* context, char agent, const char* id, uint32_t count);
  static void trampolineSampleA(void* context, const float values[6]);
  static void trampolineSampleB(void* context, uint16_t value);
  static bool trampolineEnd(void* context, const char* id, uint32_t received);
  static void trampolineCaseReady(void* context, const char* case_id);

  void emit(const char* text);

  serial_protocol::WriteFn write_;
  void* write_context_;
  InferFn infer_;
  void* infer_context_;
  NowUsFn now_us_;
  HeapFn free_heap_;
  serial_protocol::AgentHooks hooks_;

  char agent_;
  fall_agent::FallAgent fall_;
  uint32_t a_received_;
  uint32_t fall_us_;
  const char* fall_outcome_;
  const char* ecg_outcome_;

  uint16_t ecg_[ECG_WINDOW_SAMPLES];
  double filtered_[ECG_WINDOW_SAMPLES];
  int8_t tensor_[ECG_WINDOW_SAMPLES];
  uint32_t b_received_;
  uint32_t ecg_preprocess_us_;
  uint32_t ecg_inference_us_;
};

}  // namespace agent_runner

#endif
