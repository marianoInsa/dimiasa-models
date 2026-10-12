#include "fall_agent.h"

#include <array>
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

using fall_agent::FallAgent;
using fall_agent::TrialResult;

namespace {

constexpr double kPi = 3.14159265358979323846;

using Sample = std::array<float, 6>;
using Signal = std::vector<Sample>;

double round6(double v) { return std::round(v * 1e6) / 1e6; }

Sample makeSample(double ax, double ay, double az, double gx, double gy, double gz) {
  return {static_cast<float>(round6(ax)), static_cast<float>(round6(ay)),
          static_cast<float>(round6(az)), static_cast<float>(round6(gx)),
          static_cast<float>(round6(gy)), static_cast<float>(round6(gz))};
}

void append(Signal& s, const Sample& v, int count) {
  for (int i = 0; i < count; ++i) s.push_back(v);
}

Signal staticSignal(int n) {
  Signal s;
  append(s, makeSample(0.0, 0.0, 1.0, 0.0, 0.0, 0.0), n);
  return s;
}

Signal normalSignal(int n) {
  Signal s;
  for (int i = 0; i < n; ++i) {
    const double t = i / 100.0;
    s.push_back(makeSample(0.08 * std::sin(2 * kPi * 1.0 * t),
                           0.05 * std::sin(2 * kPi * 0.7 * t),
                           1.0 + 0.10 * std::sin(2 * kPi * 1.2 * t),
                           15.0 * std::sin(2 * kPi * 0.8 * t),
                           20.0 * std::sin(2 * kPi * 0.6 * t),
                           10.0 * std::sin(2 * kPi * 1.0 * t)));
  }
  return s;
}

Signal fallSignal(int n) {
  Signal s;
  for (int i = 0; i < n; ++i) {
    const double t = i / 100.0;
    double ax, ay, az, gx, gy, gz;
    if (t < 2.0) {
      ax = 0.05 * std::sin(2 * kPi * 1.0 * t);
      ay = 0.04 * std::sin(2 * kPi * 0.7 * t);
      az = 1.0 + 0.08 * std::sin(2 * kPi * 1.2 * t);
      gx = 10.0 * std::sin(2 * kPi * 0.8 * t);
      gy = 15.0 * std::sin(2 * kPi * 0.6 * t);
      gz = 8.0 * std::sin(2 * kPi * 1.0 * t);
    } else if (t < 2.2) {
      const double pt = t - 2.0;
      const double factor = pt / 0.2;
      ax = 0.2 * factor * std::sin(2 * kPi * 8.0 * pt);
      ay = 0.4 * factor * std::sin(2 * kPi * 6.0 * pt);
      az = 1.0 - 0.5 * factor;
      gx = 80.0 * factor * std::sin(2 * kPi * 4.0 * pt);
      gy = 120.0 * factor;
      gz = 60.0 * factor * std::sin(2 * kPi * 3.0 * pt);
    } else if (t < 2.4) {
      const double pt = t - 2.2;
      const double impact = std::exp(-((pt - 0.10) * (pt - 0.10)) / (2.0 * 0.025 * 0.025));
      ax = 1.5 * impact;
      ay = 2.0 * impact;
      az = 1.0 + 2.5 * impact;
      gx = 150.0 * impact;
      gy = 250.0 * impact;
      gz = 100.0 * impact;
    } else {
      ax = 0.85;
      ay = 0.05;
      az = 0.52;
      gx = 0.5;
      gy = 0.5;
      gz = 0.2;
    }
    s.push_back(makeSample(ax, ay, az, gx, gy, gz));
  }
  return s;
}

Signal falsePositiveSignal(int n) {
  Signal s;
  for (int i = 0; i < n; ++i) {
    const double t = i / 100.0;
    double ax, ay, az, gx, gy, gz;
    if (t < 2.0) {
      ax = 0.05 * std::sin(2 * kPi * 1.0 * t);
      ay = 0.04 * std::sin(2 * kPi * 0.7 * t);
      az = 1.0 + 0.08 * std::sin(2 * kPi * 1.2 * t);
      gx = 10.0 * std::sin(2 * kPi * 0.8 * t);
      gy = 15.0 * std::sin(2 * kPi * 0.6 * t);
      gz = 8.0 * std::sin(2 * kPi * 1.0 * t);
    } else if (t < 2.5) {
      const double pt = t - 2.0;
      ax = 2.0 * std::sin(2 * kPi * 8.0 * pt);
      ay = 1.5 * std::sin(2 * kPi * 6.0 * pt);
      az = 1.0 + 2.0 * std::sin(2 * kPi * 10.0 * pt);
      gx = 180.0 * std::sin(2 * kPi * 5.0 * pt);
      gy = 220.0 * std::sin(2 * kPi * 4.0 * pt);
      gz = 140.0 * std::sin(2 * kPi * 6.0 * pt);
    } else {
      const double pt = t - 2.5;
      ax = 0.20 * std::sin(2 * kPi * 1.5 * pt);
      ay = 0.15 * std::sin(2 * kPi * 1.1 * pt);
      az = 1.0 + 0.25 * std::sin(2 * kPi * 1.8 * pt);
      gx = 40.0 * std::sin(2 * kPi * 1.2 * pt);
      gy = 55.0 * std::sin(2 * kPi * 0.9 * pt);
      gz = 30.0 * std::sin(2 * kPi * 1.5 * pt);
    }
    s.push_back(makeSample(ax, ay, az, gx, gy, gz));
  }
  return s;
}

Signal strongWithoutImpactSignal(int n) {
  Signal s;
  const Sample quiet = makeSample(0.0, 0.0, 1.0, 0.0, 0.0, 0.0);
  const Sample strong = makeSample(0.0, 0.0, 2.2, 0.0, 200.0, 0.0);
  for (int i = 0; i < n; ++i) {
    s.push_back((i / 50) % 2 == 0 ? quiet : strong);
  }
  return s;
}

Signal impactCancelSignal() {
  Signal s;
  append(s, makeSample(0.0, 0.0, 1.0, 0.0, 0.0, 0.0), 50);
  append(s, makeSample(0.0, 0.0, 3.5, 0.0, 200.0, 0.0), 50);
  const Sample quiet = makeSample(0.0, 0.0, 1.0, 0.0, 0.5, 0.0);
  append(s, quiet, 100);
  append(s, quiet, 50);
  append(s, makeSample(0.0, 0.0, 1.6, 0.0, 0.5, 0.0), 50);
  append(s, quiet, 200);
  return s;
}

bool pushSignal(FallAgent& agent, const Signal& signal) {
  bool ok = true;
  for (const Sample& v : signal) {
    ok = agent.addSample(v[0], v[1], v[2], v[3], v[4], v[5]) && ok;
  }
  return ok;
}

int failures = 0;

void check(const char* name, bool pass, const std::string& detail) {
  std::printf("%-34s %s  %s\n", name, pass ? "PASS" : "FAIL", detail.c_str());
  if (!pass) ++failures;
}

std::string resultOf(const FallAgent& agent) {
  char buffer[128];
  std::snprintf(buffer, sizeof buffer, "resultado=%s windows=%d confirmed=%d",
                fall_agent::trialResultName(agent.endTrial()), agent.windowsProcessed(),
                agent.fallConfirmed() ? 1 : 0);
  return buffer;
}

}  // namespace

int main() {
  {
    FallAgent agent;
    pushSignal(agent, staticSignal(300));
    const bool ok = agent.endTrial() == TrialResult::ADL && agent.windowsProcessed() == 3;
    check("reposo_estatico", ok, resultOf(agent));
  }
  {
    FallAgent agent;
    pushSignal(agent, normalSignal(500));
    const bool ok = agent.endTrial() == TrialResult::ADL && agent.windowsProcessed() == 5;
    check("movimiento_normal", ok, resultOf(agent));
  }
  {
    FallAgent agent;
    pushSignal(agent, fallSignal(500));
    const bool ok = agent.endTrial() == TrialResult::FALL && agent.fallConfirmed() &&
                    agent.windowsProcessed() == 5;
    check("caida_confirmada", ok, resultOf(agent));
  }
  {
    FallAgent agent;
    pushSignal(agent, strongWithoutImpactSignal(300));
    const bool ok = agent.endTrial() == TrialResult::ADL && !agent.fallConfirmed();
    check("movimiento_fuerte_sin_impacto", ok, resultOf(agent));
  }
  {
    FallAgent agent;
    pushSignal(agent, impactCancelSignal());
    const bool ok = agent.endTrial() == TrialResult::ADL && !agent.fallConfirmed() &&
                    agent.windowsProcessed() == 5;
    check("cancelacion_por_movimiento", ok, resultOf(agent));
  }
  {
    FallAgent agent;
    pushSignal(agent, falsePositiveSignal(600));
    const bool ok = agent.endTrial() == TrialResult::ADL && !agent.fallConfirmed() &&
                    agent.windowsProcessed() == 6;
    check("timeout_tres_ventanas_moviles", ok, resultOf(agent));
  }
  {
    FallAgent agent;
    pushSignal(agent, falsePositiveSignal(500));
    const bool ok = agent.endTrial() == TrialResult::INDETERMINATE;
    check("falso_positivo_truncado", ok, resultOf(agent));
  }
  {
    FallAgent agent;
    pushSignal(agent, fallSignal(500));
    const bool first = agent.endTrial() == TrialResult::FALL;
    agent.beginTrial();
    pushSignal(agent, staticSignal(300));
    const bool second = agent.endTrial() == TrialResult::ADL;
    agent.beginTrial();
    pushSignal(agent, fallSignal(500));
    const bool third = agent.endTrial() == TrialResult::FALL;
    check("reset_entre_trials", first && second && third,
          std::string("fall=") + (first ? "1" : "0") + " adl=" + (second ? "1" : "0") +
              " fall2=" + (third ? "1" : "0"));
  }
  {
    FallAgent agent;
    pushSignal(agent, fallSignal(500));
    const bool rejected = !agent.addSample(NAN, 0.0f, 1.0f, 0.0f, 0.0f, 0.0f);
    const bool ok = rejected && agent.invalid() && agent.endTrial() == TrialResult::INDETERMINATE;
    check("datos_no_finitos", ok,
          std::string("rechazado=") + (rejected ? "1" : "0") + " " + resultOf(agent));
  }
  {
    FallAgent agent;
    pushSignal(agent, staticSignal(250));
    const bool ok = agent.endTrial() == TrialResult::INDETERMINATE &&
                    agent.windowsProcessed() == 2;
    check("ventana_final_parcial", ok, resultOf(agent));
  }

  std::printf("\n%s (%d fallos)\n", failures == 0 ? "TODOS LOS CASOS OK" : "HAY FALLOS", failures);
  return failures == 0 ? 0 : 1;
}
