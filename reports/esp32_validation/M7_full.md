# M7 — Corrida full rápida y métricas

Fecha: 2026-10-11
Estado: **gate HITL aprobado** (2026-10-11); corrida, resumen y decisiones documentadas abajo.

## Corrida

```bash
.venv/bin/python scripts/esp32_simulation/replay.py run --port /dev/ttyUSB0 \
    --dataset-dir notebooks/data/esp32_simulation/rule_based/full --mode fast \
    --output reports/esp32_validation/m7_full
```

- Dataset `full` íntegro: 20 trials KFall (10 Fall/10 ADL), 40 ECG PTB-XL fold 10 (20/20), 20 escenarios; `int8_sha256_all_records` `dd3319ba…` coincide con el congelado.
- Una sola sesión: **80/80 filas `ok`**, cero errores de transporte, 631,1 s.
- Salidas: `results.csv`, `run_metadata.json`, `summary.json` (nuevo `scripts/esp32_simulation/summarize.py`) en `reports/esp32_validation/m7_full/`.

## A por trial (reglas, etiqueta `Fall` = positiva)

| predice \ etiqueta | Fall | ADL |
|---|---|---|
| Fall | 7 | 1 |
| ADL | 0 | 7 |
| INDETERMINADO | 3 | 2 |

- 5 indeterminados (3 en trials Fall, 2 en ADL): salida conservadora de M1, nunca `ADL` dudoso; **no entran** en la matriz binaria y se informan aparte.
- Sensibilidad 0,875 (7/8); especificidad 1,000 (7/7); precisión 1,000; F1 0,933 sobre predicciones válidas (14 de 20 trials).
- **A vs referencia de reglas del host: 20/20.** El dispositivo reproduce exactamente el contrato congelado en cada trial; las diferencias con las etiquetas KFall son de la capa de reglas (el trial recortado no llega a confirmar en algunos casos), no del firmware.
- Latencia desde evento: no se informa (M1: KFall sin ancla temporal fiable).

## B por registro (etiqueta `ANORMAL` = positiva)

| predice \ etiqueta | ANORMAL | NORMAL |
|---|---|---|
| ANORMAL | 16 | 4 |
| NORMAL | 3 | 17 |

- Sensibilidad 0,842; especificidad 0,810; precisión 0,800; F1 0,821.
- Paridad con el host: **checksum del tensor 40/40** (preproceso bit-exacto), `q` exacto 37/40, `|Δq| ≤ 2` 40/40, máximo 2 LSB (redondeo de kernels TFLM vs TFLite, misma clase en todos).

## Triaje

- **vs etiquetas del manifiesto: 14/20.** Matriz (predice \ etiqueta): ROJO 4/4; AMARILLO 6/7 y 1 verde→amarillo; VERDE 4/6; INDETERMINADO 3 (con etiquetas ROJO/AMARILLO).
- **vs salidas reales de los agentes: 20/20.** La tabla de decisión en placa es correcta en los 20 escenarios; todas las discrepancias con etiquetas provienen de la clasificación de A/B, no del triaje.
- **Taxonomía de errores**: transporte 0; A vs reglas 0; checksum B 0; lógica de triaje 0. Los desvíos contra etiquetas quedan cuantificados arriba (reglas vs labels KFall; modelo vs labels PTB-XL).

## Tiempos y memoria

| etapa | mediana | P95 | máximo |
|---|---|---|---|
| reglas A (`fall_us`) | 1,324 ms | 2,088 ms | 5,735 ms |
| preproceso B (`preproc_us`) | 107,87 ms | 108,22 ms | 108,24 ms |
| inferencia B (`infer_us`) | 1,1129 s | 1,1129 s | 1,1131 s |
| triaje (`triage_us`) | 5 µs | 5,2 µs | 8 µs |

- Extremo a extremo (incluye transmisión en `fast`, no es cómputo): trial_A mediana 4,44 s (P95 7,02); record_B 6,60 s (6,84); escenario 11,39 s (25,7).
- Memoria: heap inicial 194.532 B; mínimo y último 194.268 B; máximo 194.532 B. Estable durante los 80 casos (una sesión).

## Límites

- Una corrida en modo `fast`; el reparto temporal (paced/jitter) y las inyecciones de fallo son M8.
- Los 5 indeterminados son política de seguridad M1, no errores del dispositivo; su exclusión de la matriz binaria está declarada.
- KFall/PTB-XL no sincronizados; `ANORMAL` es la clase del modelo, no taquicardia; sin métricas clínicas.

## Decisiones para el gate M7

1. Aceptar la presentación de métricas (matriz + indeterminados aparte; dos vistas de triaje).
2. Aceptar la taxonomía de errores (transporte/reglas/ECG/lógica).
3. Pasar a M8 (modo temporizado, inyecciones y cierre del informe final).
