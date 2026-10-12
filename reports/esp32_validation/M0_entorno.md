# M0 — Ficha de entorno (validación A/B ESP32 ↔ Ubuntu)

Fecha: 2026-10-11
Estado: **M0 aprobado — el usuario confirmó las versiones y respondió `CONTINUAR`.**

## Placa y puerto (evidencia del usuario)

- Placa: **ESP-WROOM-32** (ESP32 clásica), conectada por USB.
- Puente serial: CP2102 USB to UART Bridge (VID:PID `10C4:EA60`, SER `0001`, LOCATION `3-3`).
- Puerto: `/dev/ttyUSB0`; velocidad de trabajo prevista: **115200 baud**.
- Salida de `python3 -m serial.tools.list_ports -v` registrada por el usuario (33 puertos; solo `ttyUSB0` corresponde al puente USB).

## Host Ubuntu (verificado por el agente)

- `.venv` del proyecto: Python 3.12.3.
- numpy 2.4.4, pandas 2.3.3, scipy 1.17.1, h5py 3.14.0, tensorflow 2.21.0 (uso de referencia/offline).
- pyserial 3.5 instalado en `.venv` por el usuario.
- g++ 13.3.0 (harness nativo C++ de M2).
- No hay `arduino-cli`; el usuario opera Arduino IDE. El proyecto Arduino vive en una carpeta personal a la que el agente **no accede**: en cada hito de hardware el agente enumera en el chat los archivos y pasos, y el usuario los aplica.

## Versiones confirmadas por el usuario (gate M0)

- Arduino IDE: **2.3.10**.
- ESP32 Core: **2.0.17**.
- `TensorFlowLite_ESP32`: **1.0.0**.
- El usuario responde `CONTINUAR`; el baseline `firmware/esp32_int8_baseline/esp32_int8_baseline.ino` no se compila ni ejecuta en esta corrida y queda como evidencia histórica.

## Artefactos ECG (hashes registrados)

| Artefacto | sha256 |
|---|---|
| `…/tflite/agent1_tinyecgnet_sequential_int8.tflite` | `e4fd65e3bb19ceb3312d6d23e6b8a795a882ed032edddb420844f605ea389de0` |
| `…/firmware/agent1_tinyecgnet_sequential_int8_config.h` | `4fa79ed196baef5daf3f568609ef593af7c0e9ea7b518012493e4366475a7c50` |
| `…/firmware/agent1_tinyecgnet_sequential_int8_model.h` | `2a794de5a8ab687bb2b9a1e077de76a20915dfb912de88ed57b0ce0ffc39aeef` |

## Baseline histórico (reportado, no evidencia cruda)

Valores informados en la documentación previa; se conservan como **antecedente sintético** y no se vuelven a ejecutar:

- Arena: 80 KiB (baseline sintético).
- LiteFallNet: `q=-106` → 0,0859 (~638 ms); TinyECGNet: `q=57` → 0,7227 (~1113 ms).
- Heap libre: 267.276 → 267.012 bytes.

No se conserva un log serial original en el repositorio: se marca como *baseline reportado*, separado de los resultados nuevos. El sketch baseline invoca LiteFallNet y queda fuera de esta corrida; en la corrida nueva solo B usa TensorFlow Lite Micro.

## Salida esperada del hito

Ficha M0 (este documento) con placa, puerto y versiones registradas. **M0 pasa** cuando el usuario confirma placa, Core, biblioteca y puerto, y acepta que el baseline no se reejecuta.
