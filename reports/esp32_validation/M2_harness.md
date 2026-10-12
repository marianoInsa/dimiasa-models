# M2 — Reglas A extraídas y paridad ECG en Ubuntu

Fecha: 2026-10-11
Estado: trabajo del agente completo; **pendiente el gate M2** (revisión del usuario). Todo se ejecutó en Ubuntu; no se usó la placa.

## A — Máquina de estados `fall_agent.{h,cpp}`

Extraída del sketch donante `monitor-signos-vitales/agente2-caida/Agent2_Fall_ESP32/Agent2_Fall_ESP32.ino` sin el parser Arduino ni las señales del sketch. Umbrales y transiciones idénticos:

- Ventanas no solapadas de 100 muestras; impacto `acc_range >= 2.0` y `gyro_range >= 150`; quietud `acc_range < 0.40` y `gyro_range < 30`; 2 ventanas quietas confirman; 3 ventanas post-impacto móviles cancelan.
- La confirmación se guarda en un pestillo (`fallConfirmed()`) y el estado se reinicia, para que el resultado por trial sobreviva al reset del `CASE`.
- Resultado por trial: `Fall`, `ADL` o `INDETERMINADO` — entrada no finita, ventana final parcial o sospecha sin resolver nunca producen `ADL`; una muestra inválida invalida el trial completo (incluso si ya había confirmación), según la restricción global.

### Vectores del harness (10/10 PASS, exit 0)

| Caso | Origen | Esperado | Resultado |
|---|---|---|---|
| `reposo_estatico` | `test_agent2.py` (señal estática) | ADL | ADL, 3 ventanas |
| `movimiento_normal` | `normal.py` | ADL | ADL, 5 ventanas |
| `caida_confirmada` | `test_agent2_caida.py` | Fall | Fall, 5 ventanas, confirmado |
| `movimiento_fuerte_sin_impacto` | construido (rango ACC 1,2 g < 2,0; giro 200 °/s) | ADL | ADL, 3 ventanas |
| `cancelacion_por_movimiento` | construido (impacto → quietud → movimiento) | ADL | ADL, 5 ventanas |
| `timeout_tres_ventanas_moviles` | `test_agent2_falso_positivo.py` **extendido a 6 s** | ADL | ADL, 6 ventanas |
| `falso_positivo_truncado` | `test_agent2_falso_positivo.py` original (5 s) | INDETERMINADO | INDETERMINADO |
| `reset_entre_trials` | Fall → estático → Fall en el mismo agente | Fall/ADL/Fall | Fall/ADL/Fall |
| `datos_no_finitos` | Fall + muestra NaN | INDETERMINADO | INDETERMINADO (rechaza el NaN) |
| `ventana_final_parcial` | estático de 250 muestras | INDETERMINADO | INDETERMINADO, 2 ventanas |

El script donante de falso positivo terminaba antes de probar el tercer timeout; el vector extendido cubre ese límite (el original queda como caso truncado, que bajo el contrato es `INDETERMINADO`, no `ADL`).

## B — Paridad ECG (SciPy ↔ C++)

`scripts/esp32_simulation/reference.py` replica paso a paso `sosfiltfilt`/`filtfilt` de SciPy (extensión impar, condiciones iniciales `sosfilt_zi`/`lfilter_zi`, dos pasadas) y se autoverifica contra SciPy con error < 1e-9. Exporta a `firmware/esp32_validation/ecg_filter_coeffs.h`:

- Butterworth orden 4, 0,5–40 Hz en 4 secciones SOS, `padlen = 27`.
- Notch 50 Hz / Q=30 (b, a), `padlen = 9`.
- Cuantización `0.081706210970878601`, zero point `-18` (leídos del `.tflite` INT8).

Vectores de referencia por registro (ruta `adc_count_sim`, igual que enviará el host): `notebooks/data/esp32_simulation/rule_based/{smoke,full}/ecg_reference.csv` + `ecg_reference_summary.json` (hash por registro, saturación y, opcionalmente, `q/p/clase` de la inferencia TFLite).

### Resultados del harness C++ (`ecg_agent_test`)

| Suite | Registros | Muestras | Error máx. flotante | Diferencias INT8 | Saturados |
|---|---|---|---|---|---|
| smoke | 10 | 25.000 | 8,882e-15 | 0 | 0 |
| full | 40 | 100.000 | 7,105e-15 | 0 | 0 |

- Tolerancia del plan: error < 1e-6 y tensor INT8 idéntico. Se cumple con margen amplio; `exit 0` en ambos.
- Hash SHA-256 de los vectores INT8 de referencia: smoke `4351591c36425eba…`, full `dd3319baf2d45cd8…` (completos en `ecg_reference_summary.json`).
- `ecg_agent` usa ~40 KB estáticos (dos buffers dobles) para no consumir la pila de la tarea de Arduino; se registrará en el informe de memoria de M4. La arena de 80 KiB sigue reservada solo para TinyECGNet.

### Cómo reproducir

```bash
make -C firmware/esp32_validation/tests run        # reglas + paridad smoke
make -C firmware/esp32_validation/tests run-full   # reglas + paridad smoke + full
.venv/bin/python scripts/esp32_simulation/reference.py --self-check --export-header
```

## Gate M2

No se flashea código que no haya pasado su verificación: ambos harnesses terminan con `exit 0`, el error flotante es < 1e-6 y el tensor INT8 coincide exactamente. Pendiente: revisión y aprobación del usuario.
