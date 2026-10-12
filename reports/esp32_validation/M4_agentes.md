# M4 — Agentes A (reglas) y B (TinyECGNet INT8) en placa

Fecha: 2026-10-11
Estado: **gate HITL aprobado** (2026-10-11); implementación, evidencia y decisiones documentadas abajo.

## Archivos

- `firmware/esp32_validation/serial_protocol.{h,cpp}` — hooks opcionales de agente (`onBegin/onSampleA/onSampleB/onEnd`); el parser sigue sin depender de agentes ni TFLM. `onEnd` corre los agentes y escribe `AGENT`; después el parser emite `ACK`. `onEnd` devuelve false → `ERROR,AGENT,<id>` sin ACK. Los errores/timeout no invocan hooks.
- `firmware/esp32_validation/agent_runner.{h,cpp}` — orquestación portable (sin TFLM): alimenta A/B, acumula tiempos con reloj inyectado y emite las líneas `AGENT`. Probado nativamente con inferencia y reloj falsos.
- `firmware/esp32_validation/ecg_inference.{h,cpp}` — TFLM exclusivo de placa: `GetModel`, operadores (lista del baseline histórico), `AllocateTensors`, `Invoke`, cuantización de salida leída del tensor.
- `firmware/esp32_validation/esp32_validation.ino` — cablea runner + inferencia; ante cada `HELLO` emite `INFO,heap=…,arena=…,model=…` antes de `READY,1`.
- `firmware/esp32_validation/agent1_tinyecgnet_sequential_int8_{model,config}.h` — generados dentro del sketch con `scripts/export_tflite_header.py` desde el .tflite (sha256 `e4fd65e3…`, igual al congelado). No se editan a mano.
- `tests/agent_runner_test.cpp` (nuevo), `tests/serial_protocol_test.cpp` y `tests/Makefile` ampliados.
- `scripts/esp32_simulation/replay.py` — `block --agent B --ecg-id`, referencia de reglas para A, comparación con `ecg_reference_summary.json` y checksum del tensor.

## Formato AGENT (M4)

- A: `AGENT,A,<id>,<clase>,<estado>,<confirmado>,<muestras>,<ventanas>,<fall_us>,<heap>`
- B: `AGENT,B,<id>,<clase>,<q>,<p>,<recibidas>,<saturados>,<tensor_fnv>,<zmin>,<zmax>,<preproc_us>,<infer_us>,<heap>`
- `tensor_fnv` (FNV-1a 32 bits del tensor INT8 de 2500 bytes) se añadió durante M4 como diagnóstico para separar preproceso de inferencia; se compara contra `ecg_reference.csv`.
- Validación nueva de B en el parser: `S` de B exige entero ADC 0–65535; si no, `ERROR,SAMPLE`.

## Desviación declarada: arena de 80 KiB

Con todo estático el enlazado desbordaba `dram0_0_seg` en **51.320 bytes** (arena 81.920 + buffers ECG 40.432 + runner 29.992 + core). La arena sigue siendo **un único bloque de 80 KiB usado solo por B**, pero se asigna con `heap_caps_aligned_alloc(16, 80 KiB)` al arrancar. Resultado: estáticas 93.968 B (28 %); heap tras arranque 194.652 B. A no crea intérprete ni usa la arena. Si el usuario prefiere otra solución (p. ej. reducir buffers), se revisa en este gate.

## Verificación en Ubuntu

- `make -C firmware/esp32_validation/tests run` → **exit 0**: 3 harness previos + hooks (orden AGENT→ACK, contadores, error sin `onEnd`, recuperación) + runner con casos A (Fall/ADL/reset) y B (formato, `ERROR,AGENT` si falla la inferencia, recuperación). Paridad ECG M2 intacta: error máx 8,882e-15, 0 diferencias INT8, 0 saturados en 25.000 muestras.
- Compilación `arduino-cli compile --fqbn esp32:esp32:esp32 firmware/esp32_validation` → 444.393 B flash (33 %), 93.968 B RAM estática.
- Incidente: el primer flash quedó con contenido corrupto de la placa (bucle `try 0x400805f0`). Se resolvió con `esptool erase_flash` + reflasheo; no afecta a datos ni código.

## Evidencia en placa (mismo binario final)

`HELLO,1` → `INFO,heap=194652,arena=81920,model=OK` + `READY,1`.

### Agente A (smoke)

| Caso | Salida en placa | Referencia (reglas M1 en Python) | Resultado |
|---|---|---|---|
| KTR0001 (700, etiqueta Fall) | `AGENT,A,KTR0001,INDETERMINADO,POSIBLE_CAIDA,0,700,7,1369,194652` + `ACK,KTR0001,700` | INDETERMINADO / POSIBLE_CAIDA, 7 ventanas (sospecha sin resolver por el recorte) | PASS |
| KTR0002 (600, Fall) | `AGENT,A,KTR0002,Fall,NORMAL,1,600,6,1176,194652` + `ACK,KTR0002,600` | Fall confirmado, 6 ventanas | PASS |
| KTR0001 truncado en 30 | `ERROR,TIMEOUT,KTR0001` (sin `AGENT`) | — | PASS |
| KTR0001 `END` incorrecto | `ERROR,END,KTR0001` (sin `AGENT`) | — | PASS |

`fall_us` varió 1.162–1.369 µs = 1,2–1,4 ms según corrida (una medición por caso; estabilidad en M5).

### Agente B (10 registros smoke, PTB-XL fold 10, ruta `adc_count_sim`)

`TS` = checksum del tensor INT8 en placa; en **10/10 coincide** con `ecg_reference.csv`. `zmin/zmax` coinciden a los 6 decimales impresos con la referencia. `recibidas=2500`, `saturados=0`, `heap=194652` en todos.

| ecg_id | clase | q placa (ref) | Δq | p placa (ref) | preproc_us | infer_us |
|---|---|---|---|---|---|---|
| 11723 | NORMAL | -5 (-5) | 0 | 0.48046875 | 107.800 | 1.113.035 |
| 14501 | ANORMAL | 59 (57) | +2 | 0.73046875 (0.72265625) | 108.140 | 1.113.033 |
| 15901 | ANORMAL | 78 (79) | -1 | 0.8046875 (0.80859375) | 107.784 | 1.113.023 |
| 20117 | NORMAL | -96 (-96) | 0 | 0.125 | 107.423 | 1.113.026 |
| 5837 | NORMAL | -98 (-98) | 0 | 0.1171875 | 107.763 | 1.113.005 |
| 11336 | ANORMAL | 127 (127) | 0 | 0.99609375 | 107.930 | 1.113.027 |
| 16132 | ANORMAL | 126 (126) | 0 | 0.9921875 | 107.689 | 1.113.040 |
| 3632 | NORMAL | -26 (-26) | 0 | 0.3984375 | 107.590 | 1.113.024 |
| 5606 | ANORMAL | 125 (125) | 0 | 0.98828125 | 107.581 | 1.113.042 |
| 65 | NORMAL | -102 (-101) | -1 | 0.1015625 (0.10546875) | 108.130 | 1.113.004 |

Clase correcta 10/10. En 3/10 el logit difiere ±1–2 LSB (misma clase, tensor de entrada idéntico): redondeo de los kernels TFLM en placa frente a TFLite x86; se descartó el delegado XNNPACK del host (sin delegado da el mismo 57). Tolerancia de M4 ratificable: **TS exacto + clase exacta + |Δq| ≤ 2 como aviso**. Tiempo de inferencia ~1,113 s (consistente con el antecedente sintético ~1.113 ms) y preproceso ~108 ms; medidos por separado.

## Límites

- Una ejecución por caso; repetibilidad y estabilidad de heap/arena se prueban en M5/M7, no se infieren de aquí.
- La cota ±2 LSB se observó en el smoke; no se garantiza en `full` (M7 la verifica con la misma comprobación TS+clase).
- KFall/PTB-XL no están sincronizados; `ANORMAL` es la clase del modelo, no taquicardia.

## Decisiones para el gate M4

1. Formato `AGENT` definitivo, incluido `tensor_fnv`.
2. Comparación B en adelante: checksum exacto + clase exacta + `|Δq|≤2` como aviso (M6/M7).
3. Arena de 80 KiB asignada del heap en arranque (motivo: desborde estático de DRAM).
