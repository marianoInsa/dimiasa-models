#ifndef ECG_AGENT_H
#define ECG_AGENT_H

#include <cstdint>

#include "ecg_filter_coeffs.h"

namespace ecg_agent {

// Cadena congelada de B: Butterworth 0,5-40 Hz + notch 50 Hz/Q30 (fase cero,
// mismo algoritmo que filtfilt/sosfiltfilt de SciPy) + z-score por ventana.
void preprocess(const uint16_t* adc_counts, double* out);

// Cuantizacion INT8 del contrato del modelo (redondeo half-to-even, como np.rint).
void quantize(const double* signal, int8_t* out);

// Cantidad de muestras que exceden [-128, 127] antes del recorte.
int countSaturated(const double* signal);

}  // namespace ecg_agent

#endif
