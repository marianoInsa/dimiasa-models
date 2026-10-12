#include "ecg_agent.h"

#include <cmath>

namespace ecg_agent {

namespace {

constexpr int kExtSamples = ECG_WINDOW_SAMPLES + 2 * ECG_SOS_PADLEN;

double g_signal[ECG_WINDOW_SAMPLES];
double g_ext[kExtSamples];

void oddExt(const double* x, int n, int pad, double* ext) {
  for (int i = 0; i < pad; ++i) {
    ext[i] = 2.0 * x[0] - x[pad - i];
  }
  for (int i = 0; i < n; ++i) {
    ext[pad + i] = x[i];
  }
  for (int j = 0; j < pad; ++j) {
    ext[pad + n + j] = 2.0 * x[n - 1] - x[n - 2 - j];
  }
}

void reverse(double* x, int n) {
  for (int i = 0; i < n / 2; ++i) {
    const double tmp = x[i];
    x[i] = x[n - 1 - i];
    x[n - 1 - i] = tmp;
  }
}

void sosfiltInPlace(double* x, int n, double zi_scale) {
  for (int s = 0; s < ECG_SOS_SECTIONS; ++s) {
    const double b0 = ECG_SOS[s][0];
    const double b1 = ECG_SOS[s][1];
    const double b2 = ECG_SOS[s][2];
    const double a1 = ECG_SOS[s][4];
    const double a2 = ECG_SOS[s][5];
    double z0 = ECG_SOS_ZI[s][0] * zi_scale;
    double z1 = ECG_SOS_ZI[s][1] * zi_scale;
    for (int i = 0; i < n; ++i) {
      const double xi = x[i];
      const double yi = b0 * xi + z0;
      z0 = b1 * xi - a1 * yi + z1;
      z1 = b2 * xi - a2 * yi;
      x[i] = yi;
    }
  }
}

void notchfiltInPlace(double* x, int n, double zi_scale) {
  double z0 = ECG_NOTCH_ZI[0] * zi_scale;
  double z1 = ECG_NOTCH_ZI[1] * zi_scale;
  for (int i = 0; i < n; ++i) {
    const double xi = x[i];
    const double yi = ECG_NOTCH_B[0] * xi + z0;
    z0 = ECG_NOTCH_B[1] * xi - ECG_NOTCH_A[1] * yi + z1;
    z1 = ECG_NOTCH_B[2] * xi - ECG_NOTCH_A[2] * yi;
    x[i] = yi;
  }
}

}  // namespace

void preprocess(const uint16_t* adc_counts, double* out) {
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    g_signal[i] = static_cast<double>(adc_counts[i]);
  }

  int n_ext = ECG_WINDOW_SAMPLES + 2 * ECG_SOS_PADLEN;
  oddExt(g_signal, ECG_WINDOW_SAMPLES, ECG_SOS_PADLEN, g_ext);
  sosfiltInPlace(g_ext, n_ext, g_ext[0]);
  reverse(g_ext, n_ext);
  sosfiltInPlace(g_ext, n_ext, g_ext[0]);
  reverse(g_ext, n_ext);
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    g_signal[i] = g_ext[ECG_SOS_PADLEN + i];
  }

  n_ext = ECG_WINDOW_SAMPLES + 2 * ECG_NOTCH_PADLEN;
  oddExt(g_signal, ECG_WINDOW_SAMPLES, ECG_NOTCH_PADLEN, g_ext);
  notchfiltInPlace(g_ext, n_ext, g_ext[0]);
  reverse(g_ext, n_ext);
  notchfiltInPlace(g_ext, n_ext, g_ext[0]);
  reverse(g_ext, n_ext);
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    g_signal[i] = g_ext[ECG_NOTCH_PADLEN + i];
  }

  double suma = 0.0;
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    suma += g_signal[i];
  }
  const double media = suma / ECG_WINDOW_SAMPLES;
  double suma_cuadrados = 0.0;
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    const double d = g_signal[i] - media;
    suma_cuadrados += d * d;
  }
  double desviacion = std::sqrt(suma_cuadrados / ECG_WINDOW_SAMPLES);
  if (desviacion < 1e-8) {
    desviacion = 1e-8;
  }
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    out[i] = (g_signal[i] - media) / desviacion;
  }
}

void quantize(const double* signal, int8_t* out) {
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    double q = std::nearbyint(signal[i] / ECG_QUANT_SCALE) + ECG_QUANT_ZERO_POINT;
    if (q < -128.0) q = -128.0;
    if (q > 127.0) q = 127.0;
    out[i] = static_cast<int8_t>(q);
  }
}

int countSaturated(const double* signal) {
  int count = 0;
  for (int i = 0; i < ECG_WINDOW_SAMPLES; ++i) {
    const double q = std::nearbyint(signal[i] / ECG_QUANT_SCALE) + ECG_QUANT_ZERO_POINT;
    if (q < -128.0 || q > 127.0) {
      ++count;
    }
  }
  return count;
}

}  // namespace ecg_agent
