# M1 — Contratos congelados (agente A por reglas, agente B ECG, datos y triaje)

Fecha: 2026-10-11
Estado: preparado por el agente; **pendiente la aprobación del usuario (gate M1)** antes de implementar el firmware.

## Fuentes y hashes

| Fuente | Ruta | sha256 |
|---|---|---|
| Caídas | `notebooks/data/bronce/falls/KFall-Reduced.csv` | `dfbbde497446c301351866a27b710a4650b8aa2a306eefec8ff4f483d978e08c` |
| ECG | `notebooks/data/oro/ecg/ptb_xl_250hz_lead_ii/PTB_XL_senal_250Hz_derivacion_II.h5` | `bf6ae877b45b3bb63d03ad2f40f42dbeb9304c97003d873491bafcc890547377` |

El H5 usa la señal Lead-II a 250 Hz (fold 10, 2.113 registros elegibles).

## Fuente de caídas KFall (verificado sobre el CSV)

- Frecuencia nativa **100 Hz**; seis ejes `Ax…Gz` en **g** y **°/s** (rangos observados: |acc| ≤ 4 g por eje, |gyro| ≤ 1.794 °/s; sin NaN ni Inf).
- 5.075 trials, 32 sujetos, etiquetas `Fall`/`ADL`; `Sample_Index` contiguo `1..N` por trial, sin huecos.
- **No hay ancla temporal de impacto/onset** en el CSV reducido → A se evalúa **por trial**, sin latencia desde evento.
- Montaje (decisión del gate M1): el prototipo validado monta el sensor en la **cintura** (zona lumbar/pélvica), consistente con KFall en espalda baja. El comentario «Pecho» del sketch donante corresponde a otro prototipo y no aplica a esta corrida; validar un montaje de pecho requeriría un protocolo aparte.

## Contrato A (congelado)

- Entrada: 6 ejes crudos por muestra a 100 Hz. Sin filtro, sin remuestreo, sin interpolación.
- Ventanas **no solapadas** de **100 muestras**.
- **Impacto**: `acc_range >= 2.0` **y** `gyro_range >= 150`.
- **Quietud**: `acc_range < 0.40` **y** `gyro_range < 30`.
- **Confirmación**: 2 ventanas quietas (la primera en POST-IMPACTO, la segunda en POSIBLE CAÍDA).
- **Timeout**: 3 ventanas post-impacto móviles agotan la sospecha y vuelven a NORMAL.
- `ACC_STRONG_THRESHOLD=0.40` y `GYRO_STRONG_THRESHOLD=60` son informativos (solo mensajes), no condiciones de confirmación.
- Umbrales congelados: **no se ajustan con `full`**.

### Resultado por trial (contrato de salida)

- Caída confirmada → `Fall`.
- Trial completo sin confirmación y sin sospecha pendiente → `ADL`.
- Entrada incompleta (transporte), ventana final parcial o sospecha sin resolver al terminar → `INDETERMINADO`/`ERROR`. **Nunca** `ADL`.

Decisión de datos adoptada: los streams generados recortan cada trial a `floor(N/100)*100` muestras (ventanas completas) y registran el resto en `trim_remainder`. Así "ventana final parcial" solo puede aparecer por truncamiento de transporte, y se castiga como `INDETERMINADO`/`ERROR`.

## Contrato B (congelado)

- Entrada `[1, 2500, 1]` **INT8**; 2.500 muestras a 250 Hz (10 s), Lead II.
- Preprocesamiento (fuente: `notebooks/fase_1/modulo_b_ecg/01_M2_Entrenamiento_TinyECGNet_Sequential_PTB-XL.ipynb`):
  1. Pasa-banda Butterworth orden 4, 0,5–40 Hz en SOS con `sosfiltfilt` (fase cero).
  2. Notch 50 Hz / Q=30 (`iirnotch`) con `filtfilt`.
  3. Z-score por ventana (media/desviación de la señal filtrada; piso 1e-8).
  4. Cuantización: `q = clip(round(x / 0.081706210970878601) + (-18), -128, 127)`.
- Salida: `p = (q + 128) * 0.00390625`; umbral 0,5 (`UMBRAL_SALIDA_INT8 = 0`).
- Etiquetas: `NORMAL` / `ANORMAL` (ANORMAL es la clase positiva del modelo; **no** es "taquicardia").
- Ruta primaria de comparación: `adc_count_sim` (conversión afín sintética, no calibración física del AD8232); la señal original queda como referencia secundaria.
- Valores tomados de `agent1_tinyecgnet_sequential_int8_config.h` (hash en la ficha M0).

## Tabla de triaje (congelada)

| Fall | ECG | Resultado |
|---|---|---|
| Fall | ANORMAL | ROJO |
| Fall | NORMAL | AMARILLO |
| ADL | ANORMAL | AMARILLO |
| ADL | NORMAL | VERDE |

`INDETERMINADO`/`ERROR`/salida ausente/entrada inválida **no** producen color válido.

## Datasets generados (M1)

Generador: `scripts/esp32_dataset_preparation/prepare_test_datasets.py` (adaptado a trials KFall; la ruta ECG reutiliza el mismo preprocesamiento de selección que ya usaba el proyecto).

| Suite | Trials | ECG | Escenarios |
|---|---|---|---|
| `notebooks/data/esp32_simulation/rule_based/smoke/` | 3 Fall + 3 ADL | 5 NORMAL + 5 ANORMAL | 20 (5 por celda) |
| `notebooks/data/esp32_simulation/rule_based/full/` | 10 Fall + 10 ADL | 20 NORMAL + 20 ANORMAL | 20 (5 por celda) |

Archivos por suite: `fall_stream.csv`, `fall_trial_manifest.csv`, `ecg_records.csv`, `ecg_stream.csv`, `scenario_manifest.csv`, `summary.json`. `scenario_manifest.csv` referencia `fall_trial_id` y `ecg_id` (ya no `fall_window_id`).

Integridad verificada por el generador y por una comprobación independiente: IDs únicos; índices consecutivos; valores finitos; recuento por trial/registro/escenario; referencias sin huérfanos con `merge(validate="many_to_one")`; 5 escenarios por celda. No se modificaron KFall, PTB-XL ni los `smoke/full` previos de UMAFall.

## Hashes de los datos generados

| Archivo | sha256 |
|---|---|
| `smoke/fall_stream.csv` | `9500e1c09de43dd4614d2aef2dac09d86cdf21232e7c78fad9cd4f8bf105a7f5` |
| `smoke/fall_trial_manifest.csv` | `ef02210b78e1dbe27674b452ce3b03669697fb64aa9ad7f9de8e517c56215402` |
| `smoke/ecg_records.csv` | `38be8f28619aa9be6c5664ec6d3e381377d8355d9ccba6aad51ea748f453a030` |
| `smoke/ecg_stream.csv` | `d94f93446fe7395df6681d09851cdf8be15ef8e216f4b919fe1f645cb3b96a43` |
| `smoke/scenario_manifest.csv` | `adcc511dfcca195eeaf06a28b43256d1c8a43d89cf5806e7e19fbe35e900ecf3` |
| `full/fall_stream.csv` | `58e0595171fc9c79a42e6283b13203d930549dffb78311879ca8c46221da1dfb` |
| `full/fall_trial_manifest.csv` | `5d722bff06ee808d621614973bd3df66a6eecf307b46da70f15ced2c899eff95` |
| `full/ecg_records.csv` | `a1b70049fffa106ec1a317838a4d6ea055a648018ae3dd3cdad1278135ea6055` |
| `full/ecg_stream.csv` | `7a1c6352b02a14ca39b2b2801b1a93da2cc1d9bdaa105a4a862e9312b85b54c5` |
| `full/scenario_manifest.csv` | `e89802c59c789ed182c4bd73c757b8cee1cddada7f7c266391659e7f6002f902` |

## Limitaciones declaradas

- KFall y PTB-XL no comparten sujetos ni sincronía; los escenarios solo prueban transporte y triaje, no fusión clínica.
- Sin ancla temporal de impacto: sin latencia desde evento.
- Montaje: cintura/lumbar, consistente con KFall. El montaje de pecho no se valida en esta corrida; exigiría un protocolo aparte.
- Sin estimación de falsas alarmas clínicas por hora: los pares son sintéticos.
- `ANORMAL` de PTB-XL no equivale a taquicardia; el color del triaje no es diagnóstico.
