# M3 — Handshake y receptor serial sin modelos

Fecha: 2026-10-11
Estado: firmware y pruebas de host listos; **gate HITL abierto** (se requiere evidencia del usuario en la placa).

## Archivos creados

- `firmware/esp32_validation/esp32_validation.ino` — arranque, lectura de `Serial` carácter a carácter y `tick(millis())`.
- `firmware/esp32_validation/serial_protocol.{h,cpp}` — parser con buffer fijo de 256 bytes (sin `String`), estado explícito y validación completa.
- `scripts/esp32_simulation/replay.py` — transporte mínimo: abrir puerto, `hello`, enviar un bloque A del dataset `smoke` y esperar acuse (incluye `--truncate` y `--bad-end`).
- `firmware/esp32_validation/tests/serial_protocol_test.cpp` — pruebas nativas con transporte falso (sin placa).

## Protocolo (M3)

| Mensaje | Respuesta | Validaciones |
|---|---|---|
| `HELLO,1` | `READY,1` (repetible) | versión exacta |
| `BEGIN,<A\|B>,<id>,<count>` | (sin respuesta) | agente válido; A: `count>0` múltiplo de 100; B: `count==2500` |
| `S,<indice>,<valores...>` | (sin respuesta) | índice consecutivo desde 0; A: 6 valores, B: 1; valores finitos |
| `END,<id>` | `ACK,<id>,<received>` | id igual al de `BEGIN` y `received == count` |
| error | `ERROR,<codigo>[,<id>]` | el caso incompleto se descarta |

Códigos: `HELLO`, `SYNTAX`, `STATE`, `AGENT`, `COUNT`, `SAMPLE`, `END`, `TIMEOUT`. Timeout entre líneas de un caso: 5000 ms. Sin `HELLO` previo, cualquier comando responde `ERROR,STATE`. La inferencia no se ejecuta en M3: el protocolo solo valida y contabiliza.

## Resultados de las pruebas nativas (21/21 PASS, exit 0)

Cubren: muestra sin handshake, versión de HELLO inválida, HELLO repetido, agente desconocido, `count` inválido para A y B, id demasiado largo, bloque A completo (200 muestras), bloque B completo (2500), línea de 300 bytes, muestra perdida (salto de índice), recuperación tras error, índice repetido, `END` con id incorrecto, `END` antes de completar, timeout, valor `nan`, `BEGIN` anidado, `END` sin caso y comando desconocido.

## Procedimiento final (arduino-cli, aprobado en M3)

Arduino IDE 2.3.10 quedó inusable en este equipo: su language server preprocesaba los `.cpp` del sketch con las ~200 rutas del core esp32 2.0.17, saturando la CPU (varias sesiones reiniciadas, interfaz congelada). El flujo pasó a terminal con `arduino-cli` 1.5.1 instalado en `~/.local/bin`, que ve el core **esp32 2.0.17** y la librería **TensorFlowLite_ESP32 1.0.0** ya instalados:

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 firmware/esp32_validation
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 firmware/esp32_validation
.venv/bin/python scripts/esp32_simulation/replay.py hello --port /dev/ttyUSB0
.venv/bin/python scripts/esp32_simulation/replay.py block --port /dev/ttyUSB0 \
    --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --trial KTR0001
.venv/bin/python scripts/esp32_simulation/replay.py block --port /dev/ttyUSB0 \
    --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --trial KTR0001 --truncate 30
```

## Evidencia obtenida en la placa (2026-10-11)

- Compilación: 269.593 bytes de programa (20 %), 21.744 bytes de globales (6 %).
- Subida: 269.952 bytes, hash verificado, reset por RTS correcto.
- `HELLO,1` → `READY,1` dos veces (repetible).
- Bloque válido `KTR0001` (700 muestras) → `ACK,KTR0001,700` exacto.
- Bloque truncado en 30 muestras → `ERROR,TIMEOUT,KTR0001` (tras 5 s).
- `END` incorrecto (trial `KTR0002`) → `ERROR,END,KTR0002`.

**M3 pasa:** `READY` repetible, conteo exacto en el acuse y `ERROR` en todos los casos inválidos; ninguna entrada inválida produjo clase (en M3 no hay inferencia). El bundle ya no se copia a una carpeta personal: se compila desde el repo.
