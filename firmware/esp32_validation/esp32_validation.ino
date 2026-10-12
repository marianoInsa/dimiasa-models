#include <Arduino.h>

#include <cstdio>
#include <cstring>

#include "agent_runner.h"
#include "ecg_inference.h"
#include "serial_protocol.h"

namespace {

void writeLine(const char* line, void* context) {
  (void)context;
  if (std::strcmp(line, "READY,1") == 0) {
    char info[96];
    std::snprintf(info, sizeof info, "INFO,heap=%u,arena=%u,model=%s",
                  static_cast<unsigned>(ESP.getFreeHeap()),
                  static_cast<unsigned>(ecg_inference::arenaSize()),
                  ecg_inference::ready() ? "OK" : "FAIL");
    Serial.println(info);
  }
  Serial.println(line);
}

uint32_t nowUs() { return static_cast<uint32_t>(micros()); }

uint32_t freeHeap() { return static_cast<uint32_t>(ESP.getFreeHeap()); }

bool inferAdapter(void* context, const int8_t* tensor, int8_t* q, float* out_scale,
                  int* out_zero_point) {
  (void)context;
  return ecg_inference::invoke(tensor, q, out_scale, out_zero_point);
}

agent_runner::AgentRunner g_runner(writeLine, nullptr, inferAdapter, nullptr, nowUs, freeHeap);
serial_protocol::Protocol g_protocol(writeLine, nullptr, 5000, g_runner.hooks());

}  // namespace

void setup() {
  Serial.begin(115200);
  ecg_inference::begin();
}

void loop() {
  while (Serial.available() > 0) {
    g_protocol.feedChar(static_cast<char>(Serial.read()));
  }
  g_protocol.tick(millis());
}
