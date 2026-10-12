#ifndef SERIAL_PROTOCOL_H
#define SERIAL_PROTOCOL_H

#include <cstdint>

namespace serial_protocol {

// Contrato M3/M4/M5:
//   HELLO,1                        -> READY,1
//   CASE,<id>,<fall_id>,<ecg_id>   -> (sin respuesta; abre un escenario)
//   BEGIN,<A|B>,<id>,<count>       -> (sin respuesta; con CASE abierto el id debe coincidir)
//   S,<indice>,<valores...>        -> (sin respuesta; A: 6 valores, B: 1 entero ADC 0..65535)
//   END,<id>                       -> AGENT,... (via hooks) y despues ACK,<id>,<received>
//   Al completar los dos miembros  -> RESULT,<id>,... (via hook onCaseReady, tras el ACK)
//   Cualquier error                -> ERROR,<codigo>[,<id>] y descarta el bloque y el caso
// Codigos: HELLO, SYNTAX, STATE, AGENT, COUNT, SAMPLE, END, TIMEOUT.
// A exige count>0 multiplo de 100; B exige count == 2500. Indices desde 0.
// AGENT/RESULT no los emite el parser: onEnd escribe AGENT y devuelve true; si devuelve
// false el bloque se descarta con ERROR,AGENT,<id> (sin ACK). onCaseReady lo invoca el
// parser tras el ACK del segundo miembro. Los errores y el timeout no invocan hooks.
// Un CASE nuevo solo se acepta en reposo; un error descarta el escenario abierto y su
// timeout (5 s) responde ERROR,TIMEOUT,<id_del_escenario>.

using WriteFn = void (*)(const char* line, void* context);

struct AgentHooks {
  void* context;
  void (*onBegin)(void* context, char agent, const char* id, uint32_t count);
  void (*onSampleA)(void* context, const float values[6]);
  void (*onSampleB)(void* context, uint16_t value);
  bool (*onEnd)(void* context, const char* id, uint32_t received);
  void (*onCaseReady)(void* context, const char* case_id);
};

class Protocol {
 public:
  Protocol(WriteFn write, void* context, uint32_t timeout_ms = 5000,
           const AgentHooks* hooks = nullptr);

  void feedChar(char c);
  void tick(uint32_t now_ms);

  bool handshaken() const { return handshake_; }
  bool inCase() const { return state_ == State::IN_CASE; }
  uint32_t blocksAccepted() const { return blocks_accepted_; }
  uint32_t casesCompleted() const { return cases_completed_; }
  uint32_t errorsEmitted() const { return errors_emitted_; }
  uint32_t lastReceived() const { return last_received_; }
  const char* lastErrorCode() const { return last_error_; }

 private:
  enum class State : uint8_t { IDLE, IN_CASE, CASE_OPEN };

  static const int kMaxLine = 256;
  static const int kMaxId = 32;
  static const int kMaxFields = 10;

  void processLine();
  void emit(const char* text);
  void emitError(const char* code);
  void resetCase();
  bool parseUint(const char* token, uint32_t* value) const;
  bool parseValue(const char* token, double* value) const;
  bool parseAdc(const char* token, uint16_t* value) const;

  WriteFn write_;
  void* context_;
  uint32_t timeout_ms_;
  const AgentHooks* hooks_;

  char buffer_[kMaxLine];
  int length_;
  bool overflow_;
  bool activity_pending_;
  uint32_t last_activity_ms_;

  bool handshake_;
  State state_;
  char case_id_[kMaxId];
  char case_agent_;
  uint32_t case_count_;
  uint32_t expected_index_;
  uint32_t received_;
  bool block_in_case_;

  char scenario_id_[kMaxId];
  char scenario_fall_id_[kMaxId];
  char scenario_ecg_id_[kMaxId];
  bool scenario_a_done_;
  bool scenario_b_done_;

  uint32_t blocks_accepted_;
  uint32_t cases_completed_;
  uint32_t errors_emitted_;
  uint32_t last_received_;
  const char* last_error_;
};

}  // namespace serial_protocol

#endif
