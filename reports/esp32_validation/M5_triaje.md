# M5 — Triaje funcional, CASE/RESULT y reset de estado

Fecha: 2026-10-11
Estado: **gate HITL aprobado** (2026-10-11); implementación, evidencia y decisiones documentadas abajo.

## Archivos

- `firmware/esp32_validation/triage.h` (nuevo) — tabla de decisión pura, independiente del transporte: `Fall+ANORMAL→ROJO`, `Fall+NORMAL→AMARILLO`, `ADL+ANORMAL→AMARILLO`, `ADL+NORMAL→VERDE`; entrada ausente, vacía, desconocida o `INDETERMINADO` → `NINGUNO` (nunca color válido). `TAQUICARDIA` no es una clase aceptada.
- `firmware/esp32_validation/serial_protocol.{h,cpp}` — nuevo `CASE,<id>,<fall_id>,<ecg_id>` (abre escenario; comando nuevo en reposo) y `RESULT` emitido por hook `onCaseReady` tras el ACK del segundo miembro. Con escenario abierto, `BEGIN,A/B` debe usar exactamente los ids declarados. Cualquier error descarta el bloque y el escenario (sin `RESULT`); un escenario abierto sin actividad 5 s responde `ERROR,TIMEOUT,<id_escenario>`. `CASE` solo se acepta en reposo.
- `firmware/esp32_validation/agent_runner.{h,cpp}` — guarda la salida terminal de A y B por caso, calcula el triaje midiendo `triage_us` por separado y emite `RESULT,<id>,<color_o_INDETERMINADO>,<clase_caida>,<clase_ecg>,<triage_us>`.
- `scripts/esp32_simulation/replay.py` — subcomando `scenario` (`--ids`, `--drop-b`, `--truncate`, `--bad-end-b`); la expectativa se calcula desde las **salidas reales** de los agentes (reglas + clase del modelo), y muestra aparte la expectativa por etiquetas del manifiesto.
- Tests: `tests/triage_test.cpp` (nuevo), casos `CASE` en `serial_protocol_test.cpp` y dos escenarios completos (ROJO e INDETERMINADO) en `agent_runner_test.cpp`; `tests/Makefile` actualizado.

## Contrato M5

| Mensaje | Respuesta | Validaciones |
|---|---|---|
| `CASE,<id>,<fall\|ecg id>` | (sin respuesta) | solo en reposo; ids no vacíos `<32`; un CASE nuevo reemplaza al anterior (que se descarta sin RESULT) |
| `BEGIN,A\|B,<id>,<count>` | (sin respuesta) | con escenario abierto el id debe coincidir; resto igual que M3/M4 |
| cierre del segundo miembro | `RESULT,...` tras el ACK | solo si ambos bloques terminaron sin error |

Un `RESULT` con `INDETERMINADO` no es un color; los casos inválidos no generan `RESULT`.

## Verificación en Ubuntu

- `make -C firmware/esp32_validation/tests run` → **exit 0, 107 PASS** (15 triaje, 14 protocolo+CASE, 4 runner+CASE, resto de harness previos; paridad ECG intacta).
- Compilación: 445.149 B flash (33 %), 94.088 B estáticas (28 %).

## Evidencia en placa (una sesión, firmware M5)

Cuatro reglas y un caso no-confirmado, en orden `S0003,S0007,S0011,S0017,S0001,S0017,S0007`:

| Escenario | A (reglas) | B (modelo) | RESULT esperado | RESULT placa | triage_us |
|---|---|---|---|---|---|
| S0003 KTR0002+5606 | Fall | ANORMAL (q=125) | ROJO | `RESULT,S0003,ROJO,Fall,ANORMAL,7` | 7 |
| S0007 KTR0003+5837 | Fall | NORMAL (q=-98) | AMARILLO | `RESULT,S0007,AMARILLO,Fall,NORMAL,5` | 5 |
| S0011 KTR0005+16132 | ADL | ANORMAL (q=126) | AMARILLO | `RESULT,S0011,AMARILLO,ADL,ANORMAL,5` | 5 |
| S0017 KTR0006+5837 | ADL | NORMAL (q=-98) | VERDE | `RESULT,S0017,VERDE,ADL,NORMAL,5` | 5 |
| S0001 KTR0001+3632 | INDETERMINADO | NORMAL (q=-26) | INDETERMINADO | `RESULT,S0001,INDETERMINADO,INDETERMINADO,NORMAL,3` | 3 |
| S0017 (repetido) | ADL | NORMAL (q=-98) | VERDE | idéntico | 5 |
| S0007 (repetido) | Fall | NORMAL (q=-98) | AMARILLO | idéntico | 5 |

- 4/4 reglas correctas; `INDETERMINADO` no produjo color. AGENT de A y B coincidió con la referencia en los 7 casos (checksum de tensor exacto en los B ejecutados; 5837 repetido 3× con `q=-98` y `TS=2521799226` idénticos).
- **Reset/repetición**: 5 trials A distintos consecutivos y 3 corridas del mismo registro B en una sola sesión, sin fuga: los resultados repetidos son idénticos.
- **Memoria**: heap 194.532 B al abrir sesión; baja una única vez 264 B tras el primer caso completo y se mantiene en 194.268 B durante los 7 casos (una sesión; estabilidad multi-sesión se verá en M7).
- **Errores** (sin RESULT ni color): B ausente → `ERROR,TIMEOUT,S0003`; A parcial (corte en 30) → `ERROR,TIMEOUT,KTR0002`; END de B inválido → `ERROR,END,5606`.
- Regresión M4: `block` A y B sin CASE siguen PASS.

### Nota de interpretación (etiquetas vs salidas reales)

`scenario_manifest.csv` trae `expected_triage_from_reference_labels`; el triaje funcional debe validarse contra las **salidas reales** (p. ej. S0001 tiene etiqueta ROJO pero la regla no confirma la caída: INDETERMINADO; S0002/S0006 incluyen registros donde la etiqueta y el modelo difieren). M7 medirá ambas vistas por separado; M5 valida la tabla de decisión y la lógica de seguridad.

## Límites

- Una sesión por tabla; la estabilidad de arena/memoria en corridas largas corresponde a M7/M8.
- Los emparejamientos son sintéticos y no sincronizados; el color no es diagnóstico.

## Decisiones para el gate M5

1. Formato y semántica `CASE`/`RESULT` (RESULT tras el ACK del segundo miembro; error = descarte sin color; timeout de escenario 5 s).
2. El triaje se valida contra salidas reales de los agentes; las etiquetas del manifiesto quedan como contexto (M7 comparará ambas).
3. Aceptar el comportamiento de heap observado (bajada única de 264 B y meseta en 194.268 B en la sesión).
