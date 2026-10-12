CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -I..

BUILD := build
SMOKE ?= ../../../notebooks/data/esp32_simulation/rule_based/smoke/ecg_reference.csv
FULL ?= ../../../notebooks/data/esp32_simulation/rule_based/full/ecg_reference.csv

.PHONY: all run run-full clean

all: $(BUILD)/fall_agent_test $(BUILD)/ecg_agent_test $(BUILD)/serial_protocol_test \
	$(BUILD)/agent_runner_test $(BUILD)/triage_test

$(BUILD)/fall_agent_test: fall_agent_test.cpp ../fall_agent.cpp ../fall_agent.h
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ fall_agent_test.cpp ../fall_agent.cpp

$(BUILD)/ecg_agent_test: ecg_agent_test.cpp ../ecg_agent.cpp ../ecg_agent.h ../ecg_filter_coeffs.h
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ ecg_agent_test.cpp ../ecg_agent.cpp

$(BUILD)/serial_protocol_test: serial_protocol_test.cpp ../serial_protocol.cpp ../serial_protocol.h
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ serial_protocol_test.cpp ../serial_protocol.cpp

$(BUILD)/agent_runner_test: agent_runner_test.cpp ../agent_runner.cpp ../agent_runner.h \
		../serial_protocol.cpp ../serial_protocol.h ../fall_agent.cpp ../fall_agent.h \
		../ecg_agent.cpp ../ecg_agent.h ../ecg_filter_coeffs.h ../triage.h
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ agent_runner_test.cpp ../agent_runner.cpp ../serial_protocol.cpp \
		../fall_agent.cpp ../ecg_agent.cpp

$(BUILD)/triage_test: triage_test.cpp ../triage.h
	@mkdir -p $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ triage_test.cpp

run: all
	$(BUILD)/serial_protocol_test
	$(BUILD)/fall_agent_test
	$(BUILD)/agent_runner_test
	$(BUILD)/triage_test
	$(BUILD)/ecg_agent_test $(SMOKE)

run-full: all
	$(BUILD)/serial_protocol_test
	$(BUILD)/fall_agent_test
	$(BUILD)/agent_runner_test
	$(BUILD)/triage_test
	$(BUILD)/ecg_agent_test $(SMOKE)
	$(BUILD)/ecg_agent_test $(FULL)

clean:
	rm -rf $(BUILD)
