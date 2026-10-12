#ifndef TRIAGE_H
#define TRIAGE_H

#include <cstdint>
#include <cstring>

namespace triage {

// Tabla de decision congelada M1, independiente del transporte:
//   Fall + ANORMAL -> ROJO
//   Fall + NORMAL  -> AMARILLO
//   ADL  + ANORMAL -> AMARILLO
//   ADL  + NORMAL  -> VERDE
// Entrada ausente, clase desconocida o resultado no terminal (INDETERMINADO)
// devuelve NINGUNO: nunca un color valido.

enum class Color : uint8_t { NINGUNO, ROJO, AMARILLO, VERDE };

inline bool esClaseCaida(const char* fall_class) {
  return fall_class != nullptr &&
         (std::strcmp(fall_class, "Fall") == 0 || std::strcmp(fall_class, "ADL") == 0);
}

inline bool esClaseEcg(const char* ecg_class) {
  return ecg_class != nullptr &&
         (std::strcmp(ecg_class, "NORMAL") == 0 || std::strcmp(ecg_class, "ANORMAL") == 0);
}

inline Color decide(const char* fall_class, const char* ecg_class) {
  if (!esClaseCaida(fall_class) || !esClaseEcg(ecg_class)) {
    return Color::NINGUNO;
  }
  const bool fall = std::strcmp(fall_class, "Fall") == 0;
  const bool anormal = std::strcmp(ecg_class, "ANORMAL") == 0;
  if (fall && anormal) return Color::ROJO;
  if (anormal) return Color::AMARILLO;
  return fall ? Color::AMARILLO : Color::VERDE;
}

inline const char* colorName(Color color) {
  switch (color) {
    case Color::ROJO:
      return "ROJO";
    case Color::AMARILLO:
      return "AMARILLO";
    case Color::VERDE:
      return "VERDE";
    default:
      return "INDETERMINADO";
  }
}

}  // namespace triage

#endif
