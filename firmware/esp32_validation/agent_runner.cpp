#include "agent_runner.h"

#include <cstdio>

namespace agent_runner {

AgentRunner::AgentRunner(serial_protocol::WriteFn write, void* write_context, InferFn infer,
                         void* infer_context, NowUsFn now_us, HeapFn free_heap)
    : write_(write),
      write_context_(write_context),
      infer_(infer),
      infer_context_(infer_context),
      now_us_(now_us),
      free_heap_(free_heap),
      agent_('A'),
      a_received_(0),
      fall_us_(0),
      fall_outcome_(nullptr),
      ecg_outcome_(nullptr),
      b_received_(0),
      ecg_preprocess_us_(0),
      ecg_inference_us_(0) {
  hooks_.context = this;
  hooks_.onBegin = &AgentRunner::trampolineBegin;
  hooks_.onSampleA = &AgentRunner::trampolineSampleA;
  hooks_.onSampleB = &AgentRunner::trampolineSampleB;
  hooks_.onEnd = &AgentRunner::trampolineEnd;
  hooks_.onCaseReady = &AgentRunner::trampolineCaseReady;
}

void AgentRunner::trampolineBegin(void* context, char agent, const char* id, uint32_t count) {
  static_cast<AgentRunner*>(context)->beginCase(agent, id, count);
}

void AgentRunner::trampolineSampleA(void* context, const float values[6]) {
  static_cast<AgentRunner*>(context)->addSampleA(values);
}

void AgentRunner::trampolineSampleB(void* context, uint16_t value) {
  static_cast<AgentRunner*>(context)->addSampleB(value);
}

bool AgentRunner::trampolineEnd(void* context, const char* id, uint32_t received) {
  return static_cast<AgentRunner*>(context)->finishCase(id, received);
}

void AgentRunner::trampolineCaseReady(void* context, const char* case_id) {
  static_cast<AgentRunner*>(context)->onCaseReady(case_id);
}

void AgentRunner::emit(const char* text) { write_(text, write_context_); }

void AgentRunner::beginCase(char agent, const char* id, uint32_t count) {
  (void)id;
  (void)count;
  agent_ = agent;
  if (agent_ == 'A') {
    fall_.beginTrial();
    a_received_ = 0;
    fall_us_ = 0;
  } else {
    b_received_ = 0;
    ecg_preprocess_us_ = 0;
    ecg_inference_us_ = 0;
  }
}

void AgentRunner::addSampleA(const float values[6]) {
  const uint32_t start = now_us_();
  fall_.addSample(values[0], values[1], values[2], values[3], values[4], values[5]);
  fall_us_ += now_us_() - start;
  ++a_received_;
}

void AgentRunner::addSampleB(uint16_t value) {
  ecg_[b_received_] = value;
  ++b_received_;
}

bool AgentRunner::finishCase(const char* id, uint32_t received) {
  (void)received;
  char line[224];
  if (agent_ == 'A') {
    const fall_agent::TrialResult outcome = fall_.endTrial();
    std::snprintf(line, sizeof line, "AGENT,A,%s,%s,%s,%d,%lu,%d,%lu,%u", id,
                  fall_agent::trialResultName(outcome), fall_agent::stateName(fall_.state()),
                  fall_.fallConfirmed() ? 1 : 0, static_cast<unsigned long>(a_received_),
                  fall_.windowsProcessed(), static_cast<unsigned long>(fall_us_),
                  static_cast<unsigned>(free_heap_()));
    emit(line);
    fall_outcome_ = fall_agent::trialResultName(outcome);
    return true;
  }

  const uint32_t start = now_us_();
  ecg_agent::preprocess(ecg_, filtered_);
  ecg_agent::quantize(filtered_, tensor_);
  ecg_preprocess_us_ += now_us_() - start;

  uint32_t tensor_fnv = 2166136261u;
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    tensor_fnv ^= static_cast<uint8_t>(tensor_[i]);
    tensor_fnv *= 16777619u;
  }

  int8_t q = 0;
  float scale = 0.0f;
  int zero_point = 0;
  const uint32_t infer_start = now_us_();
  const bool ok = infer_(infer_context_, tensor_, &q, &scale, &zero_point);
  ecg_inference_us_ += now_us_() - infer_start;
  if (!ok || !(scale > 0.0f)) {
    return false;
  }

  double zmin = filtered_[0];
  double zmax = filtered_[0];
  for (int i = 1; i < ECG_WINDOW_SAMPLES; ++i) {
    if (filtered_[i] < zmin) zmin = filtered_[i];
    if (filtered_[i] > zmax) zmax = filtered_[i];
  }
  const float p = (q - zero_point) * scale;
  std::snprintf(line, sizeof line, "AGENT,B,%s,%s,%d,%.8g,%lu,%d,%lu,%.6f,%.6f,%lu,%lu,%u", id,
                p >= 0.5f ? "ANORMAL" : "NORMAL", static_cast<int>(q), static_cast<double>(p),
                static_cast<unsigned long>(b_received_), ecg_agent::countSaturated(filtered_),
                static_cast<unsigned long>(tensor_fnv), zmin, zmax,
                static_cast<unsigned long>(ecg_preprocess_us_),
                static_cast<unsigned long>(ecg_inference_us_), static_cast<unsigned>(free_heap_()));
  emit(line);
  ecg_outcome_ = p >= 0.5f ? "ANORMAL" : "NORMAL";
  return true;
}

void AgentRunner::onCaseReady(const char* case_id) {
  if (fall_outcome_ == nullptr || ecg_outcome_ == nullptr) {
    return;
  }
  const uint32_t start = now_us_();
  const triage::Color color = triage::decide(fall_outcome_, ecg_outcome_);
  const uint32_t triage_us = now_us_() - start;
  char line[160];
  std::snprintf(line, sizeof line, "RESULT,%s,%s,%s,%s,%lu", case_id, triage::colorName(color),
                fall_outcome_, ecg_outcome_, static_cast<unsigned long>(triage_us));
  emit(line);
  fall_outcome_ = nullptr;
  ecg_outcome_ = nullptr;
}

}  // namespace agent_runner
