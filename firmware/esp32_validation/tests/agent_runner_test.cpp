#include "agent_runner.h"

#include "serial_protocol.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

namespace {

std::vector<std::string> g_output;
int g_failures = 0;

void capture(const char* line, void* context) {
  (void)context;
  g_output.push_back(line);
}

uint32_t g_now = 0;
uint32_t fakeNow() {
  g_now += 3;
  return g_now;
}

uint32_t fakeHeap() { return 123456; }

bool g_infer_fail = false;

bool fakeInfer(void* context, const int8_t* tensor, int8_t* q, float* out_scale,
               int* out_zero_point) {
  (void)context;
  (void)tensor;
  if (g_infer_fail) {
    return false;
  }
  *q = 57;
  *out_scale = 0.00390625f;
  *out_zero_point = -128;
  return true;
}

void feed(serial_protocol::Protocol& protocol, const std::string& text) {
  for (const char c : text) {
    protocol.feedChar(c);
  }
}

std::string quietSamples(int start, int count) {
  std::string text;
  char line[64];
  for (int i = 0; i < count; ++i) {
    std::snprintf(line, sizeof line, "S,%d,0,0,1,0,0,0\n", start + i);
    text += line;
  }
  return text;
}

std::string impactSamples(int start, int count) {
  std::string text;
  char line[64];
  for (int i = 0; i < count; ++i) {
    const bool strong = (i % 2) == 1;
    std::snprintf(line, sizeof line, "S,%d,%s\n", start + i,
                  strong ? "0,0,3.5,0,200,0" : "0,0,1,0,0,0");
    text += line;
  }
  return text;
}

std::string ecgSamples(int count) {
  std::string text;
  char line[48];
  for (int i = 0; i < count; ++i) {
    std::snprintf(line, sizeof line, "S,%d,2048\n", i);
    text += line;
  }
  return text;
}

std::vector<std::string> split(const std::string& line) {
  std::vector<std::string> fields;
  size_t start = 0;
  while (start <= line.size()) {
    const size_t comma = line.find(',', start);
    if (comma == std::string::npos) {
      fields.push_back(line.substr(start));
      break;
    }
    fields.push_back(line.substr(start, comma - start));
    start = comma + 1;
  }
  return fields;
}

void check(const char* name, bool ok) {
  std::printf("%-32s %s\n", name, ok ? "PASS" : "FAIL");
  if (!ok) ++g_failures;
}

const std::string* findLine(const char* prefix) {
  for (const auto& line : g_output) {
    if (line.rfind(prefix, 0) == 0) return &line;
  }
  return nullptr;
}

bool hasLine(const std::string& expected) {
  for (const auto& line : g_output) {
    if (line == expected) return true;
  }
  return false;
}

}  // namespace

int main() {
  agent_runner::AgentRunner runner(capture, nullptr, fakeInfer, nullptr, fakeNow, fakeHeap);
  serial_protocol::Protocol protocol(capture, nullptr, 5000, runner.hooks());

  feed(protocol, "HELLO,1\n");
  g_output.clear();
  g_now = 0;

  feed(protocol, "BEGIN,A,tF,300\n" + impactSamples(0, 100) + quietSamples(100, 200) +
                    "END,tF\n");
  const std::string* line_a = findLine("AGENT,A,");
  check("A_agente_presente", line_a != nullptr);
  check("A_ack_presente", hasLine("ACK,tF,300"));
  if (line_a != nullptr) {
    const std::vector<std::string> f = split(*line_a);
    check("A_campos", f.size() == 10);
    check("A_clase", f[3] == "Fall");
    check("A_estado", f[4] == "NORMAL");
    check("A_confirmado", f[5] == "1");
    check("A_muestras", f[6] == "300");
    check("A_ventanas", f[7] == "3");
    check("A_tiempo", f[8] == "900");
    check("A_heap", f[9] == "123456");
  }
  check("A_sin_linea_previa", g_output.size() == 2 && g_output[0].rfind("AGENT,A,", 0) == 0);

  g_output.clear();
  feed(protocol, "BEGIN,A,tADL,100\n" + quietSamples(0, 100) + "END,tADL\n");
  const std::string* line_adl = findLine("AGENT,A,");
  check("A_reset_entre_trials", line_adl != nullptr &&
                                    split(*line_adl)[3] == "ADL" && split(*line_adl)[5] == "0" &&
                                    split(*line_adl)[6] == "100" && split(*line_adl)[7] == "1" &&
                                    split(*line_adl)[8] == "300");

  g_output.clear();
  feed(protocol, "BEGIN,B,ecg1,2500\n" + ecgSamples(2500) + "END,ecg1\n");
  const std::string* line_b = findLine("AGENT,B,");
  check("B_agente_presente", line_b != nullptr);
  check("B_ack_presente", hasLine("ACK,ecg1,2500"));
  if (line_b != nullptr) {
    const std::vector<std::string> f = split(*line_b);
    check("B_campos", f.size() == 14);
    check("B_clase", f[3] == "ANORMAL");
    check("B_q", f[4] == "57");
    check("B_p", std::fabs(std::strtod(f[5].c_str(), nullptr) - 0.72265625) < 1e-9);
    check("B_recibidas", f[6] == "2500");
    check("B_saturados", f[7] == "0");
    check("B_tensor_fnv", std::strtoul(f[8].c_str(), nullptr, 10) > 0);
    const double zmin = std::strtod(f[9].c_str(), nullptr);
    const double zmax = std::strtod(f[10].c_str(), nullptr);
    check("B_zmin_zmax", std::isfinite(zmin) && std::isfinite(zmax) && zmin <= zmax);
    check("B_preproc_us", f[11] == "3");
    check("B_infer_us", f[12] == "3");
    check("B_heap", f[13] == "123456");
  }

  g_output.clear();
  g_infer_fail = true;
  feed(protocol, "BEGIN,B,ecg2,2500\n" + ecgSamples(2500) + "END,ecg2\n");
  check("B_inferencia_fallida", g_output.size() == 1 && g_output[0] == "ERROR,AGENT,ecg2");
  g_infer_fail = false;

  g_output.clear();
  feed(protocol, "BEGIN,B,ecg3,2500\n" + ecgSamples(2500) + "END,ecg3\n");
  check("B_recuperacion", hasLine("ACK,ecg3,2500") && findLine("AGENT,B,ecg3,") != nullptr);

  g_output.clear();
  feed(protocol, "CASE,sc1,tF,ecg1\n");
  feed(protocol, "BEGIN,A,tF,300\n" + impactSamples(0, 100) + quietSamples(100, 200) +
                    "END,tF\n");
  const bool partial_sin_resultado = findLine("RESULT,") == nullptr;
  feed(protocol, "BEGIN,B,ecg1,2500\n" + ecgSamples(2500) + "END,ecg1\n");
  check("caso_resultado_presente", findLine("RESULT,sc1,") != nullptr);
  check("caso_orden_y_color",
        g_output.size() == 5 && g_output[0].rfind("AGENT,A,", 0) == 0 &&
            g_output[1] == "ACK,tF,300" && g_output[2].rfind("AGENT,B,", 0) == 0 &&
            g_output[3] == "ACK,ecg1,2500" &&
            g_output[4] == "RESULT,sc1,ROJO,Fall,ANORMAL,3");
  check("caso_sin_resultado_parcial", partial_sin_resultado);

  g_output.clear();
  feed(protocol, "CASE,sc2,tQ,ecg2\n");
  feed(protocol, "BEGIN,A,tQ,200\n" + impactSamples(0, 100) + quietSamples(100, 100) +
                    "END,tQ\n");
  feed(protocol, "BEGIN,B,ecg2,2500\n" + ecgSamples(2500) + "END,ecg2\n");
  check("caso_indeterminado_sin_color",
        g_output.size() == 5 &&
            g_output[4] == "RESULT,sc2,INDETERMINADO,INDETERMINADO,ANORMAL,3");

  g_output.clear();
  feed(protocol, "CASE,sc3,tF,ecg3\n");
  feed(protocol, "BEGIN,A,otro,100\n");
  check("caso_id_incorrecto", g_output.size() == 1 && g_output[0] == "ERROR,STATE,sc3");

  g_output.clear();
  feed(protocol, "CASE,sc4,tF,ecg3\n");
  feed(protocol, "BEGIN,A,tF,100\n" + quietSamples(0, 100) + "END,tF\n");
  feed(protocol, "BEGIN,B,ecg3,2500\n" + ecgSamples(2500) + "END,ecg3\n");
  check("caso_tras_error",
        g_output.size() == 5 && g_output[4] == "RESULT,sc4,AMARILLO,ADL,ANORMAL,3");

  std::printf("\n%s (%d fallos)\n", g_failures == 0 ? "TODOS LOS CASOS OK" : "HAY FALLOS",
              g_failures);
  return g_failures == 0 ? 0 : 1;
}
