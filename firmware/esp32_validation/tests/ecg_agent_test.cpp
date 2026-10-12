#include "ecg_agent.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace {

struct RecordAccumulator {
  long ecg_id = -1;
  std::vector<uint16_t> adc;
  std::vector<double> expected_float;
  std::vector<int> expected_int8;
};

double g_max_error = 0.0;
long g_mismatches = 0;
long g_saturated = 0;
long g_records = 0;
long g_samples = 0;

void evaluateRecord(const RecordAccumulator& rec) {
  if (rec.ecg_id < 0) return;
  if (rec.adc.size() != static_cast<size_t>(ECG_WINDOW_SAMPLES)) {
    std::printf("registro %ld: %zu muestras != %d\n", rec.ecg_id, rec.adc.size(),
                ECG_WINDOW_SAMPLES);
    ++g_mismatches;
    return;
  }
  std::vector<double> filtrada(ECG_WINDOW_SAMPLES);
  std::vector<int8_t> tensor(ECG_WINDOW_SAMPLES);
  ecg_agent::preprocess(rec.adc.data(), filtrada.data());
  ecg_agent::quantize(filtrada.data(), tensor.data());

  double max_error = 0.0;
  long mismatches = 0;
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    const double error = std::fabs(filtrada[i] - rec.expected_float[i]);
    if (error > max_error) max_error = error;
    if (tensor[i] != rec.expected_int8[i]) ++mismatches;
  }
  const int saturated = ecg_agent::countSaturated(filtrada.data());
  ++g_records;
  g_samples += ECG_WINDOW_SAMPLES;
  g_max_error = std::max(g_max_error, max_error);
  g_mismatches += mismatches;
  g_saturated += saturated;
  std::printf("registro %-6ld error_max=%.3e int8_dif=%ld saturados=%d %s\n", rec.ecg_id,
              max_error, mismatches, saturated,
              (max_error < 1e-6 && mismatches == 0) ? "OK" : "FALLA");
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) {
    std::fprintf(stderr, "uso: %s <ecg_reference.csv>\n", argv[0]);
    return 2;
  }
  FILE* file = std::fopen(argv[1], "r");
  if (file == nullptr) {
    std::fprintf(stderr, "no se pudo abrir %s\n", argv[1]);
    return 2;
  }

  char line[512];
  if (std::fgets(line, sizeof line, file) == nullptr) return 2;
  RecordAccumulator current;
  while (std::fgets(line, sizeof line, file) != nullptr) {
    char* fields[5];
    int count = 0;
    char* token = std::strtok(line, ",");
    while (token != nullptr && count < 5) {
      fields[count++] = token;
      token = std::strtok(nullptr, ",");
    }
    if (count != 5) continue;
    const long id = std::strtol(fields[0], nullptr, 10);
    if (id != current.ecg_id) {
      evaluateRecord(current);
      current = RecordAccumulator();
      current.ecg_id = id;
    }
    current.adc.push_back(static_cast<uint16_t>(std::strtol(fields[2], nullptr, 10)));
    current.expected_float.push_back(std::strtod(fields[3], nullptr));
    current.expected_int8.push_back(static_cast<int>(std::strtol(fields[4], nullptr, 10)));
  }
  evaluateRecord(current);
  std::fclose(file);

  const bool pass = g_mismatches == 0 && g_max_error < 1e-6;
  std::printf("\n%s: registros=%ld muestras=%ld error_max=%.3e int8_dif=%ld saturados=%ld\n",
              pass ? "PARIDAD OK" : "PARIDAD FALLIDA", g_records, g_samples, g_max_error,
              g_mismatches, g_saturated);
  return pass ? 0 : 1;
}
