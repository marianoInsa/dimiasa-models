# Plan de implementación: validación experimental A/B en ESP32 y Ubuntu

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validar en una ESP32 clásica la integridad de entrada serial, el preprocesamiento, las inferencias INT8 de LiteFallNet y TinyECGNet, la regla de triaje y el rendimiento técnico con los datasets seleccionados.

**Architecture:** Ubuntu valida los manifiestos, calcula la referencia Python y reproduce las señales por USB/Serial. La ESP32 procesa cada bloque secuencialmente con los modelos actuales y devuelve predicciones y tiempos; el host conserva los resultados auditables.

**Tech Stack:** Arduino IDE, ESP32 Core 2.0.17, `TensorFlowLite_ESP32` 1.0.0, TensorFlow Lite Micro, Python, NumPy, Pandas y pySerial.

**Spec:** Este documento contiene el plan aprobado para la Fase 5; el alcance general de la fase está resumido en [`doc/00_PLAN/FASE 5 - VALIDACIÓN EXPERIMENTAL.md`](00_PLAN/FASE%205%20-%20VALIDACI%C3%93N%20EXPERIMENTAL.md).

## Global Constraints

- Usar el firmware secuencial y la arena compartida de 80 KiB; no añadir MQTT, concurrencia ni ejecución en varios núcleos.
- Mantener los modelos, umbrales y conjuntos de prueba sin ajuste durante la evaluación.
- Las señales ECG y caídas se emparejan artificialmente: los resultados integrados validan el prototipo, no una asociación clínica.
- Las entradas inválidas, incompletas o ausentes producen `ERROR`/`INDETERMINADO`; nunca `NORMAL`, `ADL` ni una alerta válida.
- LiteFallNet se ejecuta como candidato de validación experimental. Su gate de producción pendiente no bloquea esta prueba.
- Usar los datos existentes en `notebooks/data/esp32_simulation/{smoke,full}/`; no modificar los CSV fuente.

---

## Estado inicial y baseline

El sketch de prueba sintética está guardado en [`firmware/esp32_int8_baseline/esp32_int8_baseline.ino`](../firmware/esp32_int8_baseline/esp32_int8_baseline.ino). Se conserva como baseline; el reproductor de datasets y el protocolo serial se implementarán aparte.

La prueba informada usa `TensorFlowLite_ESP32` 1.0.0, ESP32 Core 2.0.17 y una arena compartida de 80 KiB. Con entradas sintéticas, los modelos pasaron comprobación del esquema, registro de operadores, `AllocateTensors()` e `Invoke()`. Valores informados: LiteFallNet `q=-106` (0,0859; actividad normal; ~638 ms), TinyECGNet `q=57` (0,7227; ECG anormal; ~1113 ms) y heap libre de 267.276 a 267.012 bytes. Estos valores son una referencia de integración, no una medición con señales de los datasets.

Los modelos INT8 y headers están en el almacenamiento local ignorado bajo `notebooks/data/modelos/`. Para compilar el sketch baseline, sus cuatro headers generados deben estar disponibles en el include path de Arduino. El sketch no contiene todavía parser serial ni preprocesamiento de señales reales.

## Archivos del trabajo de validación

- `firmware/esp32_int8_baseline/esp32_int8_baseline.ino` — prueba sintética conservada, no modificar durante la nueva integración.
- `firmware/esp32_validation/esp32_validation.ino` — arranque y coordinación serial de la prueba con datasets.
- `firmware/esp32_validation/serial_protocol.{h,cpp}` — parser acotado, validación de mensajes y estado del caso.
- `firmware/esp32_validation/fall_agent.{h,cpp}` — AVM/GVM, filtro, remuestreo, ventana, cuantización e inferencia.
- `firmware/esp32_validation/ecg_agent.{h,cpp}` — filtros, z-score, cuantización e inferencia ECG.
- `firmware/esp32_validation/triage.h` — tabla de decisión independiente del transporte.
- `scripts/esp32_simulation/reference.py` — referencia Python de preprocesamiento, cuantización e inferencia TFLite.
- `scripts/esp32_simulation/replay.py` — reproducción rápida/temporizada, comunicación y registro.
- `tests/test_esp32_simulation.py` — pruebas offline de datos, protocolo y tabla de triaje.
- `pyproject.toml` — extra opcional de pySerial; NumPy y Pandas ya son dependencias del proyecto.
- `reports/esp32_validation/<run-id>/` — `results.csv`, `run_metadata.json` y `summary.json` por corrida.

`scripts/export_tflite_header.py` ya permite generar headers en un directorio de salida; reutilizarlo, sin duplicar el exportador. Incluir la configuración de cada modelo desde su propia unidad de compilación para aislar sus macros.

## Plan por tareas

### Task 1: Congelar contratos y validar los datos

**Archivos:** `doc/ESTADO_MODELOS_INT8_ESP32.md`, notebooks de entrenamiento/cuantización, `notebooks/data/esp32_simulation/full/summary.json` y manifiestos.

- [ ] Registrar placa exacta, versiones de Arduino IDE/Core/biblioteca, hashes de modelos, configuración de build y puerto serial.
- [ ] Confirmar forma, escalas, puntos cero, umbrales, unidades y semántica de las dos salidas a partir de los artefactos y notebooks.
- [ ] Verificar en el código de entrenamiento si LiteFallNet filtra cada trial completo antes de ventanear. La documentación actual recomienda AVM/GVM → `sosfiltfilt` a frecuencia nativa → `resample_poly` a 50 Hz → ventana de 150 muestras con paso 75.
- [ ] Comparar la regla de `model_target_reference` del manifiesto —pico AVM del trial UMAFall original a 20 Hz— con la regla exacta del entrenamiento. Detener las métricas de clasificación si no coincide; no corregir etiquetas silenciosamente.
- [ ] Comprobar integridad de claves, filas, índices consecutivos, NaN/Inf, IDs únicos y cardinalidad de las relaciones entre manifiestos y streams.
- [ ] Acordar antes de medir la tolerancia de paridad y los criterios de latencia; mantener los resultados como mediciones experimentales, no como aprobación de producción.

**Contrato conocido:** entrada A `[1,150,2]` INT8; entrada B `[1,2500,1]` INT8. La clase ECG positiva es `ANORMAL`, no “caída” ni “taquicardia”.

### Task 2: Crear la referencia Python y las pruebas de manifiestos

**Archivos:** crear `scripts/esp32_simulation/reference.py` y `tests/test_esp32_simulation.py`.

- [ ] Escribir primero pruebas que comprueben que `full` contiene 20 trials, 161 ventanas de caída, 40 ECG y 20 escenarios; comprobar también los conteos de `smoke`.
- [ ] Añadir selección por `trial_id`, `window_id`, `ecg_id` y `scenario_id`, validando las relaciones con `pandas.merge(..., validate=...)` y fallando ante referencias huérfanas.
- [ ] Generar desde Python los tensores INT8 y las salidas de referencia de ambos modelos con el mismo preprocesamiento y umbrales que el firmware.
- [ ] Para ECG, usar `adc_count_sim` en la comparación principal; conservar la señal original como referencia secundaria, no mezclar ambas rutas en una misma métrica.
- [ ] Guardar las salidas de referencia con los IDs de origen para poder distinguir errores de preprocesamiento, inferencia y triaje.

**Verificación:** ejecutar las pruebas offline sin abrir el puerto serial; todos los IDs de `scenario_manifest.csv` deben resolver a una entrada de cada agente.

### Task 3: Implementar el preprocesamiento y comprobar paridad nativa

**Archivos:** `firmware/esp32_validation/fall_agent.{h,cpp}`, `ecg_agent.{h,cpp}` y un harness nativo de prueba.

- [ ] Exportar desde SciPy los coeficientes y condiciones iniciales de `sosfiltfilt`/`filtfilt`; no aproximar los estados con ceros.
- [ ] Implementar la ruta de caídas según el orden exacto verificado en Task 1. Si el filtro opera sobre el trial completo, recibir y procesar el trial completo antes de seleccionar las ventanas solicitadas; no filtrar 60 muestras aisladas por defecto.
- [ ] Implementar ECG en 2.500 muestras: pasa-banda Butterworth de orden 4 (0,5–40 Hz), notch 50 Hz/Q30, z-score por ventana y cuantización con escala `0.081706210970878601` y zero point `-18`.
- [ ] Comparar el código C/C++ nativo que luego compilará para ESP32 contra SciPy y la referencia Python, incluyendo el tensor INT8.

**Criterio propuesto:** error máximo de señal flotante `< 1e-6` y coincidencia exacta de los bytes INT8 de entrada. Registrar cualquier diferencia antes de flashear.

### Task 4: Añadir comunicación serial y ejecución secuencial

**Archivos:** crear `firmware/esp32_validation/esp32_validation.ino` y `serial_protocol.{h,cpp}`.

- [ ] Empezar con `Serial.begin(115200)` y handshake `HELLO,1` → `READY,1`.
- [ ] Recibir mensajes delimitados por `\n` mediante `Serial.available()`/`read()` y un buffer fijo; validar límite de línea, IDs, valores finitos, orden de índices, cantidad declarada y `END` correspondiente.
- [ ] Usar `CASE` para asociar una entrada de cada agente. Emitir una respuesta `AGENT` al completar cada inferencia y un solo `RESULT` al terminar el caso; no responder por muestra.
- [ ] Devolver `ERROR` con causa y conteos ante timeout, truncamiento o datos inválidos. Limpiar el estado incompleto antes de aceptar otro caso.
- [ ] Medir `preprocess_us`, `inference_us`, `triage_us` y `device_processing_us` con `micros()`, sin incluir impresión serial en los intervalos de cómputo.
- [ ] Mantener la arena de 80 KiB y probar secuencias repetidas A→B→A y B→A→B. Registrar arena usada y heap libre/mínimo; no dejar dos intérpretes asignados simultáneamente sobre la misma arena.

**Protocolo lógico:** `HELLO`; `CASE`; `BEGIN` con agente, ID y cantidad; muestras `S` con índice; `END` con ID; respuestas `AGENT`, `RESULT` o `ERROR`. Para A, el tamaño del bloque se fija luego de confirmar el límite del filtro; para B son 2.500 muestras.

### Task 5: Probar la tabla de triaje sin modelos

**Archivo:** crear `firmware/esp32_validation/triage.h` y cubrirlo desde `tests/test_esp32_simulation.py` o un harness nativo pequeño.

- [ ] Probar `Fall + ANORMAL → ROJO`.
- [ ] Probar `Fall + NORMAL → AMARILLO`.
- [ ] Probar `ADL + ANORMAL → AMARILLO`.
- [ ] Probar `ADL + NORMAL → VERDE`.
- [ ] Probar salida ausente, etiqueta desconocida y señal inválida; ninguno debe producir una alerta normal/clínica.

### Task 6: Implementar el reproductor de Ubuntu

**Archivos:** crear `scripts/esp32_simulation/replay.py`, extender `tests/test_esp32_simulation.py` y declarar pySerial como extra opcional en `pyproject.toml`.

- [ ] Añadir argumentos `--port`, `--baud` (115200 por defecto), `--dataset-dir`, `--mode` (`fast`/`paced`), `--suite` y `--output`.
- [ ] Leer los CSV existentes, validar las asociaciones con los manifiestos y enviar las entradas sin concatenar trials.
- [ ] Configurar timeout de lectura y escritura; tratar una línea incompleta o una respuesta que no llega como fallo de la prueba, no como predicción.
- [ ] En modo rápido, transmitir en orden a máxima velocidad y esperar una respuesta por bloque.
- [ ] En modo temporizado, programar envíos a 20 Hz para A y 250 Hz para B usando reloj monotónico; registrar retraso real frente al instante programado.
- [ ] Medir `end_to_end_ms` desde antes del primer envío del bloque hasta recibir la respuesta completa. No sumar etapas que ya están incluidas en ese tiempo.
- [ ] Escribir una fila por entrada/caso en `results.csv`, incluyendo IDs, referencias, predicciones, q/scores, tiempos, muestras esperadas/recibidas, modo y estado/error. Guardar versiones, hashes, baud rate y semilla en `run_metadata.json`.

### Task 7: Ejecutar aceptación y producir el informe

- [ ] Compilar el sketch de validación con ESP32 Core 2.0.17 y `TensorFlowLite_ESP32` 1.0.0.
- [ ] Probar el handshake y los contadores con `smoke` en modo rápido.
- [ ] Ejecutar `full` en modo rápido: agentes individuales y los 20 escenarios del manifiesto.
- [ ] Repetir un subconjunto fijo para la distribución de latencia; después probar modo temporizado y registrar el jitter.
- [ ] Inyectar línea truncada, muestra omitida, bloque incompleto y desconexión del host; comprobar recuperación y que no aparezcan etiquetas válidas falsas.
- [ ] Resumir por separado métricas por ventana de A, métricas por registro de B, paridad Python↔ESP32, tabla de triaje, mediana/P95 de tiempos, uso de memoria y errores de comunicación.
- [ ] Guardar `results.csv`, `run_metadata.json` y `summary.json` en `reports/esp32_validation/<run-id>/`.

**Verificaciones de software:** `python -m pytest -m "not slow" -v` y el harness nativo de preprocesamiento. **Criterios mínimos:** cero pérdidas silenciosas; todos los IDs esperados registrados; paridad de entrada dentro de la tolerancia acordada; 4/4 reglas correctas; entradas inválidas nunca se clasifican como normales.

## Interpretación y límites

- `fall_window_manifest.csv` produce ventanas solapadas. Las métricas de A son por ventana; no contar ventanas solapadas como eventos independientes.
- `full` usa UMAFall para caídas y PTB-XL fold 10 para ECG; los 40 ECG seleccionados corresponden a 39 pacientes únicos.
- Las filas de `scenario_manifest.csv` son emparejamientos artificiales y no sincronizados. La coincidencia de triaje mide la lógica del prototipo, no una mejora clínica ni reducción de falsos positivos en pacientes.
- `ANORMAL` de PTB-XL no equivale a taquicardia. No presentar el color del triaje como diagnóstico.
- No calcular falsas alarmas clínicas por hora a partir de los pares sintéticos; requeriría exposición negativa continua y una regla temporal de agrupación de ventanas.
- No afirmar funcionamiento offline durante pérdida del host USB/Serial: Ubuntu es la fuente de datos de esta prueba.

## Referencias

- [Arduino-ESP32 Serial](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/serial.html): configuración y recepción/transmisión serial.
- [pySerial API](https://pyserial.readthedocs.io/en/latest/pyserial_api.html) y [lectura de líneas](https://pyserial.readthedocs.io/en/latest/shortintro.html): timeouts, `readline()` y escritura.
- [Preparación de datasets ESP32](../scripts/esp32_dataset_preparation/README.md): columnas, ventanas y advertencias de los datos generados.
- [Estado de los modelos INT8](ESTADO_MODELOS_INT8_ESP32.md): contrato de cuantización, estado experimental y gate de producción.
