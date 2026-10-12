#ifndef FALL_AGENT_H
#define FALL_AGENT_H

#include <cstdint>

namespace fall_agent {

constexpr int kWindowSamples = 100;
constexpr float kAccImpactThreshold = 2.0f;
constexpr float kGyroImpactThreshold = 150.0f;
constexpr float kAccStillThreshold = 0.40f;
constexpr float kGyroStillThreshold = 30.0f;
constexpr int kStillWindowsRequired = 2;
constexpr int kPostImpactMaxWindows = 3;

enum class State : uint8_t {
  NORMAL,
  IMPACT,
  POSSIBLE_FALL,
};

enum class TrialResult : uint8_t {
  ADL,
  FALL,
  INDETERMINATE,
};

const char* trialResultName(TrialResult result);
const char* stateName(State state);

class FallAgent {
 public:
  FallAgent();

  void beginTrial();
  bool addSample(float ax, float ay, float az, float gx, float gy, float gz);
  TrialResult endTrial() const;

  bool fallConfirmed() const { return confirmed_; }
  bool invalid() const { return invalid_; }
  State state() const { return state_; }
  int windowsProcessed() const { return windows_processed_; }

 private:
  void processWindow();
  void resetDetection();

  float ax_[kWindowSamples];
  float ay_[kWindowSamples];
  float az_[kWindowSamples];
  float gx_[kWindowSamples];
  float gy_[kWindowSamples];
  float gz_[kWindowSamples];
  int sample_count_;
  State state_;
  int still_windows_;
  int post_impact_windows_;
  bool confirmed_;
  bool invalid_;
  int windows_processed_;
};

}  // namespace fall_agent

#endif
