#include "serial_protocol.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace serial_protocol {

Protocol::Protocol(WriteFn write, void* context, uint32_t timeout_ms, const AgentHooks* hooks)
    : write_(write),
      context_(context),
      timeout_ms_(timeout_ms),
      hooks_(hooks),
      length_(0),
      overflow_(false),
      activity_pending_(false),
      last_activity_ms_(0),
      handshake_(false),
      state_(State::IDLE),
      case_count_(0),
      expected_index_(0),
      received_(0),
      block_in_case_(false),
      scenario_a_done_(false),
      scenario_b_done_(false),
      blocks_accepted_(0),
      cases_completed_(0),
      errors_emitted_(0),
      last_received_(0),
      last_error_(nullptr) {
  buffer_[0] = '\0';
  case_id_[0] = '\0';
  case_agent_ = 'A';
  scenario_id_[0] = '\0';
  scenario_fall_id_[0] = '\0';
  scenario_ecg_id_[0] = '\0';
}

void Protocol::feedChar(char c) {
  activity_pending_ = true;
  if (c == '\r') {
    return;
  }
  if (c == '\n') {
    if (overflow_) {
      overflow_ = false;
      emitError("SYNTAX");
      resetCase();
    } else if (length_ > 0) {
      buffer_[length_] = '\0';
      processLine();
    }
    length_ = 0;
    return;
  }
  if (length_ >= kMaxLine - 1) {
    overflow_ = true;
    return;
  }
  buffer_[length_++] = c;
}

void Protocol::tick(uint32_t now_ms) {
  if (activity_pending_) {
    activity_pending_ = false;
    last_activity_ms_ = now_ms;
  }
  if ((state_ == State::IN_CASE || state_ == State::CASE_OPEN) &&
      now_ms - last_activity_ms_ > timeout_ms_) {
    emitError("TIMEOUT");
    resetCase();
  }
}

void Protocol::emit(const char* text) { write_(text, context_); }

void Protocol::emitError(const char* code) {
  char message[80];
  const char* id = nullptr;
  if (state_ == State::IN_CASE) {
    id = case_id_;
  } else if (state_ == State::CASE_OPEN) {
    id = scenario_id_;
  }
  if (id != nullptr) {
    std::snprintf(message, sizeof message, "ERROR,%s,%s", code, id);
  } else {
    std::snprintf(message, sizeof message, "ERROR,%s", code);
  }
  ++errors_emitted_;
  last_error_ = code;
  emit(message);
}

void Protocol::resetCase() {
  state_ = State::IDLE;
  case_id_[0] = '\0';
  case_agent_ = 'A';
  case_count_ = 0;
  expected_index_ = 0;
  received_ = 0;
  block_in_case_ = false;
  scenario_id_[0] = '\0';
  scenario_fall_id_[0] = '\0';
  scenario_ecg_id_[0] = '\0';
  scenario_a_done_ = false;
  scenario_b_done_ = false;
}

bool Protocol::parseUint(const char* token, uint32_t* value) const {
  if (token == nullptr || *token == '\0') {
    return false;
  }
  char* end = nullptr;
  const unsigned long parsed = std::strtoul(token, &end, 10);
  if (end == token || *end != '\0') {
    return false;
  }
  *value = static_cast<uint32_t>(parsed);
  return true;
}

bool Protocol::parseValue(const char* token, double* value) const {
  if (token == nullptr || *token == '\0') {
    return false;
  }
  char* end = nullptr;
  const double parsed = std::strtod(token, &end);
  if (end == token || *end != '\0' || !std::isfinite(parsed)) {
    return false;
  }
  *value = parsed;
  return true;
}

bool Protocol::parseAdc(const char* token, uint16_t* value) const {
  if (token == nullptr || *token == '\0') {
    return false;
  }
  for (const char* p = token; *p != '\0'; ++p) {
    if (*p < '0' || *p > '9') {
      return false;
    }
  }
  char* end = nullptr;
  const unsigned long parsed = std::strtoul(token, &end, 10);
  if (end == token || *end != '\0' || parsed > 65535UL) {
    return false;
  }
  *value = static_cast<uint16_t>(parsed);
  return true;
}

void Protocol::processLine() {
  char* fields[kMaxFields];
  int nfields = 1;
  fields[0] = buffer_;
  for (char* p = buffer_; *p != '\0'; ++p) {
    if (*p == ',') {
      *p = '\0';
      if (nfields >= kMaxFields) {
        emitError("SYNTAX");
        resetCase();
        return;
      }
      fields[nfields++] = p + 1;
    }
  }
  const char* command = fields[0];

  if (std::strcmp(command, "HELLO") == 0) {
    if (nfields != 2 || std::strcmp(fields[1], "1") != 0) {
      emitError("HELLO");
      resetCase();
      return;
    }
    handshake_ = true;
    resetCase();
    emit("READY,1");
    return;
  }

  if (!handshake_) {
    emitError("STATE");
    return;
  }

  if (std::strcmp(command, "CASE") == 0) {
    if (state_ != State::IDLE) {
      emitError("STATE");
      resetCase();
      return;
    }
    if (nfields != 4) {
      emitError("SYNTAX");
      return;
    }
    for (int i = 1; i <= 3; ++i) {
      const size_t len = std::strlen(fields[i]);
      if (len == 0 || len >= kMaxId) {
        emitError("SYNTAX");
        return;
      }
    }
    std::strcpy(scenario_id_, fields[1]);
    std::strcpy(scenario_fall_id_, fields[2]);
    std::strcpy(scenario_ecg_id_, fields[3]);
    scenario_a_done_ = false;
    scenario_b_done_ = false;
    state_ = State::CASE_OPEN;
    activity_pending_ = true;
    return;
  }

  if (std::strcmp(command, "BEGIN") == 0) {
    if (state_ == State::IN_CASE) {
      emitError("STATE");
      resetCase();
      return;
    }
    if (nfields != 4) {
      emitError("SYNTAX");
      return;
    }
    if (std::strlen(fields[2]) == 0 || std::strlen(fields[2]) >= kMaxId) {
      emitError("SYNTAX");
      return;
    }
    const char* agent = fields[1];
    if (std::strcmp(agent, "A") != 0 && std::strcmp(agent, "B") != 0) {
      emitError("AGENT");
      return;
    }
    uint32_t count = 0;
    if (!parseUint(fields[3], &count)) {
      emitError("SYNTAX");
      return;
    }
    const bool count_ok =
        (agent[0] == 'A') ? (count > 0 && count % 100 == 0) : (count == 2500);
    if (!count_ok) {
      emitError("COUNT");
      return;
    }
    if (state_ == State::CASE_OPEN) {
      const char* expected = (agent[0] == 'A') ? scenario_fall_id_ : scenario_ecg_id_;
      if (std::strcmp(fields[2], expected) != 0) {
        emitError("STATE");
        resetCase();
        return;
      }
    }
    block_in_case_ = (state_ == State::CASE_OPEN);
    std::strcpy(case_id_, fields[2]);
    case_agent_ = agent[0];
    case_count_ = count;
    expected_index_ = 0;
    received_ = 0;
    state_ = State::IN_CASE;
    activity_pending_ = true;
    if (hooks_ != nullptr) {
      hooks_->onBegin(hooks_->context, case_agent_, case_id_, case_count_);
    }
    return;
  }

  if (std::strcmp(command, "S") == 0) {
    if (state_ != State::IN_CASE) {
      emitError("STATE");
      return;
    }
    const int expected_fields = (case_agent_ == 'A') ? 8 : 3;
    if (nfields != expected_fields) {
      emitError("SAMPLE");
      resetCase();
      return;
    }
    uint32_t index = 0;
    if (!parseUint(fields[1], &index) || index != expected_index_) {
      emitError("SAMPLE");
      resetCase();
      return;
    }
    if (case_agent_ == 'A') {
      float values[6];
      for (int i = 0; i < 6; ++i) {
        double value = 0.0;
        if (!parseValue(fields[2 + i], &value)) {
          emitError("SAMPLE");
          resetCase();
          return;
        }
        values[i] = static_cast<float>(value);
      }
      ++expected_index_;
      ++received_;
      if (hooks_ != nullptr) {
        hooks_->onSampleA(hooks_->context, values);
      }
    } else {
      uint16_t value = 0;
      if (!parseAdc(fields[2], &value)) {
        emitError("SAMPLE");
        resetCase();
        return;
      }
      ++expected_index_;
      ++received_;
      if (hooks_ != nullptr) {
        hooks_->onSampleB(hooks_->context, value);
      }
    }
    return;
  }

  if (std::strcmp(command, "END") == 0) {
    if (state_ != State::IN_CASE) {
      emitError("STATE");
      return;
    }
    if (nfields != 2 || std::strcmp(fields[1], case_id_) != 0) {
      emitError("END");
      resetCase();
      return;
    }
    if (received_ != case_count_) {
      emitError("END");
      resetCase();
      return;
    }
    if (hooks_ != nullptr && !hooks_->onEnd(hooks_->context, case_id_, received_)) {
      emitError("AGENT");
      resetCase();
      return;
    }
    char reply[64];
    std::snprintf(reply, sizeof reply, "ACK,%s,%lu", case_id_,
                  static_cast<unsigned long>(received_));
    ++blocks_accepted_;
    last_received_ = received_;
    const bool block_in_scenario = block_in_case_;
    const char closed_agent = case_agent_;
    block_in_case_ = false;
    case_id_[0] = '\0';
    case_count_ = 0;
    expected_index_ = 0;
    received_ = 0;
    case_agent_ = 'A';
    emit(reply);
    if (!block_in_scenario) {
      resetCase();
      return;
    }
    if (closed_agent == 'A') {
      scenario_a_done_ = true;
    } else {
      scenario_b_done_ = true;
    }
    if (scenario_a_done_ && scenario_b_done_) {
      ++cases_completed_;
      state_ = State::IDLE;
      if (hooks_ != nullptr && hooks_->onCaseReady != nullptr) {
        hooks_->onCaseReady(hooks_->context, scenario_id_);
      }
      resetCase();
    } else {
      state_ = State::CASE_OPEN;
      activity_pending_ = true;
    }
    return;
  }

  emitError("SYNTAX");
  resetCase();
}

}  // namespace serial_protocol
