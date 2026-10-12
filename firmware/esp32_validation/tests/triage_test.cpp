#include "triage.h"

#include <cstdio>
#include <cstring>

namespace {

int failures = 0;

void check(const char* name, triage::Color got, triage::Color want) {
  const bool ok = got == want;
  std::printf("%-34s %s (obtenido %s, esperado %s)\n", name, ok ? "PASS" : "FAIL",
              triage::colorName(got), triage::colorName(want));
  if (!ok) ++failures;
}

}  // namespace

int main() {
  check("fall_anormal_rojo", triage::decide("Fall", "ANORMAL"), triage::Color::ROJO);
  check("fall_normal_amarillo", triage::decide("Fall", "NORMAL"), triage::Color::AMARILLO);
  check("adl_anormal_amarillo", triage::decide("ADL", "ANORMAL"), triage::Color::AMARILLO);
  check("adl_normal_verde", triage::decide("ADL", "NORMAL"), triage::Color::VERDE);

  check("caida_ausente", triage::decide(nullptr, "NORMAL"), triage::Color::NINGUNO);
  check("ecg_ausente", triage::decide("Fall", nullptr), triage::Color::NINGUNO);
  check("ambos_ausentes", triage::decide(nullptr, nullptr), triage::Color::NINGUNO);
  check("caida_vacia", triage::decide("", "NORMAL"), triage::Color::NINGUNO);
  check("ecg_vacio", triage::decide("Fall", ""), triage::Color::NINGUNO);
  check("caida_indeterminada", triage::decide("INDETERMINADO", "NORMAL"),
        triage::Color::NINGUNO);
  check("caida_indeterminada_anormal", triage::decide("INDETERMINADO", "ANORMAL"),
        triage::Color::NINGUNO);
  check("caida_desconocida", triage::decide("ERROR", "NORMAL"), triage::Color::NINGUNO);
  check("ecg_desconocido", triage::decide("Fall", "TAQUICARDIA"), triage::Color::NINGUNO);
  check("minusculas_no_validas", triage::decide("fall", "normal"), triage::Color::NINGUNO);

  const bool name_ok = std::strcmp(triage::colorName(triage::Color::NINGUNO), "INDETERMINADO") == 0;
  std::printf("%-34s %s\n", "nombre_sin_color", name_ok ? "PASS" : "FAIL");
  if (!name_ok) ++failures;

  std::printf("\n%s (%d fallos)\n", failures == 0 ? "TODOS LOS CASOS OK" : "HAY FALLOS",
              failures);
  return failures == 0 ? 0 : 1;
}
