#include "fall_agent.h"

#include <cmath>

namespace fall_agent {

namespace {

float magnitude(float x, float y, float z) {
  return std::sqrt(x * x + y * y + z * z);
}

}  // namespace

const char* trialResultName(TrialResult result) {
  switch (result) {
    case TrialResult::ADL:
      return "ADL";
    case TrialResult::FALL:
      return "Fall";
    default:
      return "INDETERMINADO";
  }
}

const char* stateName(State state) {
  switch (state) {
    case State::NORMAL:
      return "NORMAL";
    case State::IMPACT:
      return "IMPACTO";
    default:
      return "POSIBLE_CAIDA";
  }
}

FallAgent::FallAgent() { beginTrial(); }

void FallAgent::beginTrial() {
  sample_count_ = 0;
  state_ = State::NORMAL;
  still_windows_ = 0;
  post_impact_windows_ = 0;
  confirmed_ = false;
  invalid_ = false;
  windows_processed_ = 0;
}

void FallAgent::resetDetection() {
  state_ = State::NORMAL;
  still_windows_ = 0;
  post_impact_windows_ = 0;
}

bool FallAgent::addSample(float ax, float ay, float az, float gx, float gy, float gz) {
  if (!std::isfinite(ax) || !std::isfinite(ay) || !std::isfinite(az) || !std::isfinite(gx) ||
      !std::isfinite(gy) || !std::isfinite(gz)) {
    invalid_ = true;
    return false;
  }
  ax_[sample_count_] = ax;
  ay_[sample_count_] = ay;
  az_[sample_count_] = az;
  gx_[sample_count_] = gx;
  gy_[sample_count_] = gy;
  gz_[sample_count_] = gz;
  ++sample_count_;
  if (sample_count_ >= kWindowSamples) {
    processWindow();
    ++windows_processed_;
    sample_count_ = 0;
  }
  return true;
}

void FallAgent::processWindow() {
  float acc_min = 999999.0f;
  float acc_max = -999999.0f;
  float gyro_min = 999999.0f;
  float gyro_max = -999999.0f;
  for (int i = 0; i < kWindowSamples; ++i) {
    const float acc = magnitude(ax_[i], ay_[i], az_[i]);
    const float gyro = magnitude(gx_[i], gy_[i], gz_[i]);
    if (acc < acc_min) acc_min = acc;
    if (acc > acc_max) acc_max = acc;
    if (gyro < gyro_min) gyro_min = gyro;
    if (gyro > gyro_max) gyro_max = gyro;
  }
  const float acc_range = acc_max - acc_min;
  const float gyro_range = gyro_max - gyro_min;
  const bool impact = acc_range >= kAccImpactThreshold && gyro_range >= kGyroImpactThreshold;
  const bool still = acc_range < kAccStillThreshold && gyro_range < kGyroStillThreshold;

  switch (state_) {
    case State::NORMAL:
      still_windows_ = 0;
      post_impact_windows_ = 0;
      if (impact) {
        state_ = State::IMPACT;
        post_impact_windows_ = 0;
        still_windows_ = 0;
      }
      break;

    case State::IMPACT:
      ++post_impact_windows_;
      if (still) {
        still_windows_ = 1;
        state_ = State::POSSIBLE_FALL;
      } else if (post_impact_windows_ >= kPostImpactMaxWindows) {
        resetDetection();
      }
      break;

    case State::POSSIBLE_FALL:
      if (still) {
        ++still_windows_;
        if (still_windows_ >= kStillWindowsRequired) {
          confirmed_ = true;
          resetDetection();
        }
      } else {
        resetDetection();
      }
      break;
  }
}

TrialResult FallAgent::endTrial() const {
  if (invalid_) return TrialResult::INDETERMINATE;
  if (sample_count_ > 0) return TrialResult::INDETERMINATE;
  if (confirmed_) return TrialResult::FALL;
  if (state_ != State::NORMAL) return TrialResult::INDETERMINATE;
  return TrialResult::ADL;
}

}  // namespace fall_agent
