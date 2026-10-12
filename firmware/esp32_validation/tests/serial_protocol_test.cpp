#include "serial_protocol.h"

#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

namespace {

std::vector<std::string> g_output;
int g_failures = 0;

void capture(const char* line, void* context) {
  (void)context;
  g_output.push_back(line);
}

void feed(serial_protocol::Protocol& protocol, const std::string& text) {
  for (const char c : text) {
    protocol.feedChar(c);
  }
}

std::string makeASamples(int count, int start = 0, int step = 1) {
  std::string text;
  char line[128];
  for (int i = 0; i < count; ++i) {
    const int index = start + i * step;
    std::snprintf(line, sizeof line, "S,%d,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n", index,
                  0.05 + index * 0.001, -1.0, 0.0, 0.05, 0.4, 0.34);
    text += line;
  }
  return text;
}

std::string makeBSamples(int count) {
  std::string text;
  char line[64];
  for (int i = 0; i < count; ++i) {
    std::snprintf(line, sizeof line, "S,%d,%d\n", i, 2000 + (i % 100));
    text += line;
  }
  return text;
}

struct HookLog {
  int begins = 0;
  int samples_a = 0;
  int samples_b = 0;
  int ends = 0;
  int cases = 0;
  char last_agent = 0;
  std::string last_id;
  std::string last_case;
  uint32_t last_count = 0;
  uint32_t last_received = 0;
  uint16_t last_b = 0;
  float last_a0 = 0.0f;
  bool fail_end = false;
};

void hookBegin(void* context, char agent, const char* id, uint32_t count) {
  auto* log = static_cast<HookLog*>(context);
  ++log->begins;
  log->last_agent = agent;
  log->last_id = id;
  log->last_count = count;
}

void hookSampleA(void* context, const float values[6]) {
  auto* log = static_cast<HookLog*>(context);
  ++log->samples_a;
  log->last_a0 = values[0];
}

void hookSampleB(void* context, uint16_t value) {
  auto* log = static_cast<HookLog*>(context);
  ++log->samples_b;
  log->last_b = value;
}

bool hookEnd(void* context, const char* id, uint32_t received) {
  auto* log = static_cast<HookLog*>(context);
  ++log->ends;
  log->last_id = id;
  log->last_received = received;
  if (log->fail_end) {
    return false;
  }
  g_output.push_back(std::string("AGENT_FAKE,") + id);
  return true;
}

void hookCaseReady(void* context, const char* case_id) {
  auto* log = static_cast<HookLog*>(context);
  ++log->cases;
  log->last_case = case_id;
  g_output.push_back(std::string("CASE_READY,") + case_id);
}

void check(const char* name, const std::vector<std::string>& expected) {
  bool ok = g_output.size() == expected.size();
  for (size_t i = 0; ok && i < expected.size(); ++i) {
    ok = g_output[i] == expected[i];
  }
  std::printf("%-32s %s", name, ok ? "PASS" : "FAIL");
  if (!ok) {
    std::printf("  esperado:");
    for (const auto& line : expected) std::printf(" [%s]", line.c_str());
    std::printf("  recibido:");
    for (const auto& line : g_output) std::printf(" [%s]", line.c_str());
    ++g_failures;
  }
  std::printf("\n");
}

void checkOk(const char* name, bool ok) {
  std::printf("%-32s %s\n", name, ok ? "PASS" : "FAIL");
  if (!ok) ++g_failures;
}

}  // namespace

int main() {
  serial_protocol::Protocol protocol(capture, nullptr, 5000);

  g_output.clear();
  feed(protocol, "S,0,0,0,1,0,0,0\n");
  check("muestra_sin_hello", {"ERROR,STATE"});

  g_output.clear();
  feed(protocol, "HELLO,2\n");
  check("hello_version_mala", {"ERROR,HELLO"});

  g_output.clear();
  feed(protocol, "HELLO,1\n");
  check("hello_ok", {"READY,1"});
  g_output.clear();
  feed(protocol, "HELLO,1\n");
  check("hello_repetido", {"READY,1"});

  g_output.clear();
  feed(protocol, "BEGIN,C,id1,100\n");
  check("begin_agente_malo", {"ERROR,AGENT"});
  g_output.clear();
  feed(protocol, "BEGIN,A,id1,150\n");
  check("begin_count_A_malo", {"ERROR,COUNT"});
  g_output.clear();
  feed(protocol, "BEGIN,B,id1,2400\n");
  check("begin_count_B_malo", {"ERROR,COUNT"});

  g_output.clear();
  feed(protocol, "BEGIN,A," + std::string(40, 'x') + ",100\n");
  check("begin_id_largo", {"ERROR,SYNTAX"});

  g_output.clear();
  feed(protocol, "BEGIN,A,KTR0001,200\n" + makeASamples(200) + "END,KTR0001\n");
  check("bloque_valido_A", {"ACK,KTR0001,200"});

  g_output.clear();
  feed(protocol, "BEGIN,B,ecg1,2500\n" + makeBSamples(2500) + "END,ecg1\n");
  check("bloque_valido_B", {"ACK,ecg1,2500"});

  g_output.clear();
  feed(protocol, std::string(300, 'x') + "\n");
  check("linea_larga", {"ERROR,SYNTAX"});

  g_output.clear();
  feed(protocol, "BEGIN,A,t2,200\n" + makeASamples(10) + "S,11,0,0,1,0,0,0\n");
  check("muestra_perdida", {"ERROR,SAMPLE,t2"});
  g_output.clear();
  feed(protocol, "BEGIN,A,t2b,100\n" + makeASamples(100) + "END,t2b\n");
  check("recuperacion_tras_error", {"ACK,t2b,100"});

  g_output.clear();
  feed(protocol, "BEGIN,A,t3,200\n" + makeASamples(1) + "S,0,0,0,1,0,0,0\n");
  check("indice_repetido", {"ERROR,SAMPLE,t3"});

  g_output.clear();
  feed(protocol, "BEGIN,A,t4,100\n" + makeASamples(1) + "END,OTRO\n");
  check("end_id_incorrecto", {"ERROR,END,t4"});

  g_output.clear();
  feed(protocol, "BEGIN,A,t5,200\n" + makeASamples(1) + "END,t5\n");
  check("end_antes_de_tiempo", {"ERROR,END,t5"});

  g_output.clear();
  feed(protocol, "BEGIN,A,t6,300\n" + makeASamples(5));
  protocol.tick(2000);
  g_output.clear();
  protocol.tick(2000 + 6001);
  check("timeout", {"ERROR,TIMEOUT,t6"});

  g_output.clear();
  feed(protocol, "BEGIN,A,t7,100\nS,0,nan,0,1,0,0,0\n");
  check("valor_no_finito", {"ERROR,SAMPLE,t7"});

  g_output.clear();
  feed(protocol, "BEGIN,A,t8,100\nBEGIN,A,t9,100\n");
  check("anidado_invalido", {"ERROR,STATE,t8"});
  g_output.clear();
  feed(protocol, "END,t9\n");
  check("end_sin_caso", {"ERROR,STATE"});

  g_output.clear();
  feed(protocol, "FIN\n");
  check("comando_desconocido", {"ERROR,SYNTAX"});

  g_output.clear();
  feed(protocol, "BEGIN,B,adc_neg,2500\nS,0,-5\n");
  check("B_adc_negativo", {"ERROR,SAMPLE,adc_neg"});
  g_output.clear();
  feed(protocol, "BEGIN,B,adc_alto,2500\nS,0,65536\n");
  check("B_adc_fuera_de_rango", {"ERROR,SAMPLE,adc_alto"});
  g_output.clear();
  feed(protocol, "BEGIN,B,adc_float,2500\nS,0,2048.0\n");
  check("B_adc_no_entero", {"ERROR,SAMPLE,adc_float"});
  g_output.clear();
  feed(protocol, "BEGIN,B,adc_ok,2500\nS,0,65535\nEND,adc_ok\n");
  check("B_adc_limite_aceptado", {"ERROR,END,adc_ok"});

  HookLog log;
  serial_protocol::AgentHooks hooks{&log, hookBegin, hookSampleA, hookSampleB, hookEnd,
                                    hookCaseReady};
  serial_protocol::Protocol hooked(capture, nullptr, 5000, &hooks);

  feed(hooked, "HELLO,1\n");
  g_output.clear();
  feed(hooked, "BEGIN,A,h1,200\n" + makeASamples(200) + "END,h1\n");
  check("hooks_orden_agente_ack", {"AGENT_FAKE,h1", "ACK,h1,200"});
  checkOk("hooks_A_contadores",
          log.begins == 1 && log.samples_a == 200 && log.ends == 1 && log.last_agent == 'A' &&
              log.last_id == "h1" && log.last_count == 200 && log.last_received == 200 &&
              std::fabs(log.last_a0 - 0.249) < 1e-6);

  g_output.clear();
  feed(hooked, "BEGIN,B,b1,2500\n" + makeBSamples(2500) + "END,b1\n");
  check("hooks_orden_B", {"AGENT_FAKE,b1", "ACK,b1,2500"});
  checkOk("hooks_B_contadores", log.begins == 2 && log.samples_b == 2500 &&
                                    log.last_agent == 'B' && log.last_b == 2099 &&
                                    log.last_id == "b1" && log.last_received == 2500);

  g_output.clear();
  feed(hooked, "BEGIN,A,e1,200\n" + makeASamples(10) + "S,11,0,0,1,0,0,0\n");
  check("hooks_error_sin_end", {"ERROR,SAMPLE,e1"});
  checkOk("hooks_error_no_invoca_end", log.begins == 3 && log.samples_a == 210 && log.ends == 2);

  g_output.clear();
  feed(hooked, "BEGIN,A,h2,100\n" + makeASamples(100) + "END,h2\n");
  check("hooks_recuperacion", {"AGENT_FAKE,h2", "ACK,h2,100"});

  g_output.clear();
  log.fail_end = true;
  feed(hooked, "BEGIN,A,h3,100\n" + makeASamples(100) + "END,h3\n");
  check("hooks_end_fallido", {"ERROR,AGENT,h3"});
  log.fail_end = false;
  g_output.clear();
  feed(hooked, "BEGIN,A,h4,100\n" + makeASamples(100) + "END,h4\n");
  check("hooks_recuperacion_final", {"AGENT_FAKE,h4", "ACK,h4,100"});
  checkOk("hooks_contadores_finales", log.begins == 6 && log.ends == 5);

  const int cases_before = log.cases;

  g_output.clear();
  feed(hooked, "CASE,c1,t1,e1\n");
  check("case_abierto_sin_respuesta", {});

  g_output.clear();
  feed(hooked, "BEGIN,A,t1,100\n" + makeASamples(100) + "END,t1\n");
  check("case_miembro_A", {"AGENT_FAKE,t1", "ACK,t1,100"});
  checkOk("case_parcial_sin_resultado", log.cases == cases_before);

  g_output.clear();
  feed(hooked, "BEGIN,B,e1,2500\n" + makeBSamples(2500) + "END,e1\n");
  check("case_completo", {"AGENT_FAKE,e1", "ACK,e1,2500", "CASE_READY,c1"});
  checkOk("case_contadores", log.cases == cases_before + 1 && log.last_case == "c1");

  g_output.clear();
  feed(hooked, "CASE,c2,t2,e2\nBEGIN,A,otro,100\n");
  check("case_id_no_coincide", {"ERROR,STATE,c2"});

  g_output.clear();
  feed(hooked, "CASE,c3,t3,e3\nCASE,c4,t4,e4\n");
  check("case_anidado", {"ERROR,STATE,c3"});

  g_output.clear();
  feed(hooked, "CASE,c5,t5,e5\n");
  hooked.tick(1000);
  g_output.clear();
  hooked.tick(1000 + 6001);
  check("case_timeout", {"ERROR,TIMEOUT,c5"});

  g_output.clear();
  feed(hooked, "CASE,c7,t7,e7\n");
  feed(hooked, "BEGIN,B,e7,2500\n" + makeBSamples(2500) + "END,e7\n");
  check("case_b_primero", {"AGENT_FAKE,e7", "ACK,e7,2500"});
  g_output.clear();
  feed(hooked, "BEGIN,A,t7,100\n" + makeASamples(100) + "END,t7\n");
  check("case_b_primero_cierra", {"AGENT_FAKE,t7", "ACK,t7,100", "CASE_READY,c7"});

  g_output.clear();
  feed(hooked, "CASE,c8,t8,e8\n");
  feed(hooked, "BEGIN,A,t8,200\n" + makeASamples(10) + "S,11,0,0,1,0,0,0\n");
  check("case_error_descarta", {"ERROR,SAMPLE,t8"});
  g_output.clear();
  feed(hooked, "CASE,c9,t9,e9\n");
  feed(hooked, "BEGIN,A,t9,100\n" + makeASamples(100) + "END,t9\n");
  feed(hooked, "BEGIN,B,e9,2500\n" + makeBSamples(2500) + "END,e9\n");
  check("case_tras_error", {"AGENT_FAKE,t9", "ACK,t9,100", "AGENT_FAKE,e9", "ACK,e9,2500",
                            "CASE_READY,c9"});

  g_output.clear();
  feed(hooked, "CASE,c10,t10\n");
  check("case_mal_formado", {"ERROR,SYNTAX"});

  serial_protocol::Protocol fresh(capture, nullptr, 5000, &hooks);
  g_output.clear();
  feed(fresh, "CASE,c11,t11,e11\n");
  check("case_sin_hello", {"ERROR,STATE"});

  std::printf("\nbloques_aceptados=%lu errores=%lu ultimo_recibido=%lu ultimo_error=%s\n",
              static_cast<unsigned long>(protocol.blocksAccepted()),
              static_cast<unsigned long>(protocol.errorsEmitted()),
              static_cast<unsigned long>(protocol.lastReceived()),
              protocol.lastErrorCode() ? protocol.lastErrorCode() : "-");
  std::printf("%s (%d fallos)\n", g_failures == 0 ? "TODOS LOS CASOS OK" : "HAY FALLOS",
              g_failures);
  return g_failures == 0 ? 0 : 1;
}
