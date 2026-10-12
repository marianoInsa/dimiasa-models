# M8 — Reproducción temporizada, resiliencia y cierre

Fecha: 2026-10-11
Estado: **validación cerrada — gate HITL aprobado** (2026-10-11); evidencia y decisiones documentadas abajo.

## Modo temporizado (paced)

Comando (subconjunto fijo repetido 3 veces, una sesión):

```bash
.venv/bin/python scripts/esp32_simulation/replay.py run --port /dev/ttyUSB0 \
    --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --mode paced \
    --trials KTR0002,KTR0004 --ecgs 14501 --scenarios S0007 --repeat 3 \
    --output reports/esp32_validation/m8_paced
```

- **12/12 filas `ok`** (6 trials A + 3 registros B + 3 escenarios). Planificación por reloj monotónico: A a 100 Hz, B a 250 Hz; `--trials/--ecgs/--scenarios` seleccionan subconjuntos y `--repeat` repite el conjunto; `repeat_index` distingue pasadas.
- Retraso real frente al calendario (ms), por tipo de caso: mediana de medianas 0,102–0,106 ms; máximo P95 1,785 ms; máximo puntual 5,803 ms (una muestra en la repetición 3). Sin deriva creciente.
- Extremo a extremo por pasada (incluye adquisición simulada + transferencia; no es cómputo):

| caso | rep 1 | rep 2 | rep 3 | duración programada |
|---|---|---|---|---|
| trial_A (KTR0002/KTR0004) | 6.507 ms mediana | 6.509 | 6.508 | 6.000/7.000 ms + protocolo |
| record_B (14501) | 11.246 ms | 11.252 | 11.247 | 10.000 ms + inferencia |
| scenario (S0007) | 18.261 ms | 18.260 | 18.258 | 17.000 ms + inferencia |

La repetición 1 se conserva como calentamiento; las repeticiones 1–3 se registran por separado y sus medianas difieren < 0,1 %.

**Tiempo de cómputo separado de la reproducción** (por repetición, mediana): reglas A 1.321–1.335 ms; preproceso B 108,1 ms; inferencia B 1.112,9–1.113,1 ms; triaje 5 µs. Memoria estable: heap 194.532 → 194.268 B. El `e2e_ms` paced no se usa como cómputo.

`summary.json` de la corrida incluye `scheduling` (retraso vs calendario) y `repeats`. Nota: el triaje contra salidas reales figura `no_evaluable=3` porque el escenario usa KTR0003/5837 y solo se seleccionaron KTR0002/KTR0004/14501; el RESULT del dispositivo fue correcto en las 3 pasadas (AMARILLO).

## Resiliencia (inyecciones)

```bash
.venv/bin/python scripts/esp32_simulation/replay.py resilience --port /dev/ttyUSB0 \
    --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke \
    --output reports/esp32_validation/m8_resilience
```

| Paso | Inyección | Observado | Recuperación |
|---|---|---|---|
| `linea_truncada` | prefijo `S,5,` sin salto + continuación (línea de 5 campos) | `ERROR,SAMPLE,KTR0003` | caso válido → `ACK` + `RESULT,S0007,AMARILLO,…` |
| `muestra_omitida` | salto de índice (falta la muestra 5) | `ERROR,SAMPLE,KTR0003` | caso válido → `ACK` + `RESULT` |
| `timeout` | bloque A incompleto (sin `END`) | `ERROR,TIMEOUT,KTR0003` | caso válido → `ACK` + `RESULT` |
| `host_desconectado` | cierre del puerto con el bloque a medias; reconexión tras 7 s | `HELLO`→`READY,1` tras reconectar | caso válido → `ACK` + `RESULT` |

- Resultado global **PASS** (`resilience.json`, `all_ok=true`). Ninguna interrupción produjo clase ni color; tras cada error el siguiente caso válido se aceptó sin estado residual (sin reiniciar el dispositivo).
- En `host_desconectado` el `ERROR,TIMEOUT` del dispositivo ocurre con el puerto cerrado (no observable); la evidencia es la reconexión limpia y el caso válido inmediato. Un primer intento del arnés se conserva en `m8_resilience_intento1_estado_sucio/`: su fallo fue de las muestras extra tras la inyección (contaminaban el buffer), no del firmware.

## Cierre — criterios finales de aceptación

| Criterio | Evidencia |
|---|---|
| Versiones registradas; LiteFallNet fuera de la corrida | M0 (`M0_entorno.md`); nunca se compiló/ejecutó |
| Datos KFall 100 Hz íntegros, sin concatenar ni remuestrear | M1 + integridad; `trim_remainder` declarado |
| FSM pasa vectores e inválidos; paridad ECG | M2 (10/10 casos; error máx 8,9e-15; 0 dif. INT8) |
| Reglas y TinyECGNet responden al ID correcto | M4 (AGENT por ID; checksum del tensor) |
| Triaje 4 reglas y falla seguro | M5 (4/4; sin color en ausente/inválido/indeterminado) |
| `results.csv` sin escenarios omitidos | M6 smoke 36/36; M7 full 80/80 |
| Tiempos por etapa, e2e, muestras y memoria separados | M7 (medianas/P95) y M8 (paced + estadísticas) |
| Informe con limitaciones declaradas | este documento (abajo) |

**Limitaciones declaradas:** KFall y PTB-XL no están sincronizados ni comparten sujetos (los escenarios son emparejamientos sintéticos); el montaje validado es cintura/lumbar, consistente con KFall (un montaje de pecho requeriría protocolo aparte); `ANORMAL` es la clase del modelo ECG y no equivale a taquicardia; no se infiere eficacia clínica, tasa de falsas alarmas por hora ni rendimiento en pacientes; la arena de 80 KiB se asigna del heap al arrancar (motivo en M4); la inferencia en placa difiere de TFLite x86 en ≤2 LSB con tensor idéntico.

## Decisiones para el gate M8

1. Aceptar la caracterización paced (retraso mediano ~0,1 ms; máx puntual 5,8 ms) y la separación cómputo/reproducción.
2. Aceptar las pruebas de resiliencia (error/timeout registrados, recuperación sin reinicio, nunca una clase).
3. Cerrar la validación A/B con los criterios finales de la tabla.
