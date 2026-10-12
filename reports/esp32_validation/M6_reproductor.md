# M6 — Reproductor Ubuntu y suite smoke

Fecha: 2026-10-11
Estado: **gate HITL aprobado** (2026-10-11); corrida smoke y decisiones documentadas abajo.

## Archivos

- `scripts/esp32_simulation/replay.py` — nuevo subcomando `run`: recorre manifiestos (trials A, registros B, escenarios), abre una sola sesión serial, decodifica `AGENT`/`RESULT` por ID y escribe resultados.
  - Argumentos: `--port`, `--baud` (115200), `--dataset-dir`, `--mode fast|paced` (paced deshabilitado hasta M8 con mensaje explícito), `--suite` (etiqueta; por defecto el nombre del dataset-dir), `--output` (por defecto `reports/esp32_validation/<suite>_<UTC>`).
  - Fallos contabilizados por caso con `status` (`ok`, `partial`, `error`, `timeout`, `missing_agent`) y columna `error`; un timeout o una línea corrupta nunca se convierten en predicción. Sin reintentos automáticos (M8 caracterizará las inyecciones).
- `tests/test_esp32_simulation.py` (nuevo) — 6 pruebas offline: reglas por trial (Fall/ADL/INDETERMINADO), tabla de triaje, triaje esperado desde salidas reales, asociaciones de manifiestos con dataset sintético, parser host de `AGENT`/`RESULT`, y esquema/escritura de `results.csv`.
- `pyproject.toml` — extra opcional `serial = ["pyserial>=3.5"]`.

## Esquema de `results.csv`

Una fila por trial A (`kind=trial_A`), registro B (`kind=record_B`) y escenario (`kind=scenario`):

`case_id, kind, fall_trial_id, ecg_id, scenario_id, reference_class, predicted_class, match, state, confirmed, q, p, tensor_fnv, expected_samples, received_samples, fall_us, preproc_us, infer_us, triage_us, e2e_ms, status, error, mode`

`reference_class` usa etiquetas de origen; el triaje desde salidas reales se reconstruye uniendo `trial_A`/`record_B` por `fall_trial_id`/`ecg_id` (M7). A no lleva `q`/score.

`run_metadata.json`: suite, modo, puerto/baud, dataset-dir, marcas UTC, versiones (Python/NumPy/Pandas/pyserial), líneas `INFO` del dispositivo, hashes del dataset (KFall/PTB-XL) y sha256 del `.tflite`.

## Verificación en Ubuntu

`.venv/bin/python -m pytest -m "not slow" -v` → **16 passed** (10 previos + 6 nuevos).

## Corrida smoke en placa

Comando:

```bash
.venv/bin/python scripts/esp32_simulation/replay.py run --port /dev/ttyUSB0 \
    --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --mode fast \
    --output reports/esp32_validation/m6_smoke
```

Resultado: **PASS 36/36 filas** (6 trials A + 10 registros B + 20 escenarios), `status=ok` en todas, todos los IDs del manifiesto resueltos, 312,6 s de corrida. Dispositivo: `INFO,heap=194532,arena=81920,model=OK`; tflite `e4fd65e3…`.

Coincidencias con etiquetas de origen: 21/36 (A 5/6, B 6/10, triaje 10/20). Es el comportamiento esperado: las etiquetas de KFall/PTB-XL no coinciden con las salidas reales en algunos casos (p. ej. KTR0001 recortado no confirma; registros donde el modelo difiere de la etiqueta). M7 calculará matriz de confusión y métricas por separado para ambas vistas; M6 solo garantiza registro íntegro y auditable.

### Incidencia de transporte (documentada)

La primera corrida registró 35/36 `ok` y un caso (S0018) con una línea `AGENT,A` corrupta en el camino USB (bytes no UTF-8); el `RESULT` del dispositivo llegó correcto. El caso quedó registrado (no hubo pérdida silenciosa) y se mejoró la clasificación (`partial`/`missing_agent`/`timeout`), repitiendo la corrida completa con resultado limpio. Evidencia del intento 1 en `reports/esp32_validation/m6_smoke_intento1_glitch_usb/`. La frecuencia de estos eventos y la recuperación se caracterizan en M8.

## Límites

- Una corrida; modo `paced`, jitter e inyecciones quedan para M8.
- Sin reintentos: un caso no-ok se registra y la corrida termina con exit code 1.
- Los pares KFall/ECG son sintéticos y no sincronizados; `match` contra etiquetas no es una métrica clínica.

## Decisiones para el gate M6

1. Esquema de `results.csv` y `run_metadata.json`.
2. Clasificación de estados (`ok/partial/error/timeout/missing_agent`); un timeout nunca es predicción.
3. Sin reintentos automáticos en M6 (las inyecciones/recuperación se prueban en M8).
