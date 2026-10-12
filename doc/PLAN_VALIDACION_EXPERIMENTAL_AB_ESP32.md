# Plan de implementación: agente de caídas por reglas y ECG en ESP32/Ubuntu

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validar en una ESP32 clásica la integridad serial, un agente de caídas basado en reglas (módulo A), la inferencia INT8 de TinyECGNet (módulo B), el triaje y el rendimiento técnico. LiteFallNet queda fuera de esta corrida. A/B identifica los agentes de caída y ECG; no compara dos detectores de caídas.

**Architecture:** Ubuntu valida manifiestos y reproduce trials KFall a 100 Hz y registros PTB-XL a 250 Hz por USB/Serial. La ESP32 aplica la máquina de estados A sobre los seis ejes crudos, ejecuta TinyECGNet para B y devuelve resultados/tiempos; solo B usa TensorFlow Lite Micro. El host conserva los resultados auditables.

**Tech Stack:** Arduino IDE, ESP32 Core 2.0.17, `TensorFlowLite_ESP32` 1.0.0 para ECG, TensorFlow Lite Micro, Python, NumPy, Pandas, SciPy como referencia ECG y pySerial.

**Spec:** Este documento contiene el plan aprobado para la Fase 5; el alcance general de la fase está resumido en [`doc/00_PLAN/FASE 5 - VALIDACIÓN EXPERIMENTAL.md`](00_PLAN/FASE%205%20-%20VALIDACI%C3%93N%20EXPERIMENTAL.md).

## Global Constraints

- Mantener una arena estática de 80 KiB para TinyECGNet; el agente A no usa TFLM. No añadir MQTT, concurrencia ni ejecución en varios núcleos.
- Mantener congelados los umbrales del agente A, el modelo/umbral ECG y los conjuntos de prueba durante la evaluación.
- Las señales ECG y caídas se emparejan artificialmente: los resultados integrados validan el prototipo, no una asociación clínica.
- Las entradas inválidas, incompletas o ausentes producen `ERROR`/`INDETERMINADO`; nunca `NORMAL`, `ADL` ni una alerta válida.
- LiteFallNet no se ejecuta en esta validación. Su baseline e informe de cuantización quedan como evidencia histórica/candidato independiente.
- A usa KFall a su frecuencia nativa de 100 Hz, seis ejes en `g` y °/s, con ventanas no solapadas de 100 muestras. No remuestrear ni interpolar UMAFall de 20 Hz para simular 100 Hz.
- Generar conjuntos separados en `notebooks/data/esp32_simulation/rule_based/{smoke,full}/`; no modificar KFall, PTB-XL ni los CSV previos de UMAFall.
- El prototipo validado monta el sensor en cintura (zona lumbar/pélvica), consistente con KFall (espalda baja). El comentario «Pecho» del sketch donante corresponde a otro prototipo y no aplica; validar un montaje de pecho requeriría un protocolo aparte.

---

## Estado inicial y baseline

El sketch de prueba sintética está guardado en [`firmware/esp32_int8_baseline/esp32_int8_baseline.ino`](../firmware/esp32_int8_baseline/esp32_int8_baseline.ino). Se conserva como baseline; el reproductor de datasets y el protocolo serial se implementarán aparte.

La prueba informada usa `TensorFlowLite_ESP32` 1.0.0, ESP32 Core 2.0.17 y una arena compartida de 80 KiB. Con entradas sintéticas, los modelos pasaron comprobación del esquema, registro de operadores, `AllocateTensors()` e `Invoke()`. Valores informados: LiteFallNet `q=-106` (0,0859; actividad normal; ~638 ms), TinyECGNet `q=57` (0,7227; ECG anormal; ~1113 ms) y heap libre de 267.276 a 267.012 bytes. Estos valores son una referencia de integración, no una medición con señales de los datasets.

Los headers INT8 oficiales están en el almacenamiento local ignorado bajo `notebooks/data/modelos/`. El baseline sintético que contiene LiteFallNet se conserva sin cambios como evidencia histórica y no se vuelve a ejecutar en la corrida nueva. El agente A usa reglas; el bundle nuevo solo requiere los dos headers ECG. El sketch baseline no contiene parser serial ni preprocesamiento de señales reales.

## Archivos del trabajo de validación

- `firmware/esp32_int8_baseline/esp32_int8_baseline.ino` — prueba sintética histórica; conservar y no incluir en la corrida nueva.
- `firmware/esp32_validation/esp32_validation.ino` — arranque y coordinación serial de la prueba con datasets.
- `firmware/esp32_validation/serial_protocol.{h,cpp}` — parser acotado, validación de mensajes y estado del caso.
- `firmware/esp32_validation/fall_agent.{h,cpp}` — máquina de estados por reglas sobre seis ejes, ventanas de 100 muestras a 100 Hz y resultado por trial; sin TFLM.
- `firmware/esp32_validation/ecg_agent.{h,cpp}` — filtros, z-score, cuantización e inferencia ECG.
- `firmware/esp32_validation/triage.h` — tabla de decisión independiente del transporte.
- `scripts/esp32_simulation/reference.py` — referencia Python de preprocesamiento, cuantización e inferencia TFLite para ECG; no calcula score LiteFallNet.
- `scripts/esp32_simulation/replay.py` — reproducción rápida/temporizada, comunicación y registro.
- `tests/test_esp32_simulation.py` — pruebas offline de datos, protocolo y tabla de triaje.
- `pyproject.toml` — extra opcional de pySerial; NumPy y Pandas ya son dependencias del proyecto.
- `notebooks/data/esp32_simulation/rule_based/{smoke,full}/` — trials KFall nativos, manifiestos y escenarios para esta validación.
- `reports/esp32_validation/<run-id>/` — `results.csv`, `run_metadata.json` y `summary.json` por corrida.

`scripts/export_tflite_header.py` ya permite generar headers en un directorio de salida; reutilizarlo solo para ECG, sin duplicar el exportador. No generar/copiar header de LiteFallNet para la corrida por reglas.

## Plan por tareas

### Task 1: Congelar contratos y validar los datos

**Archivos:** `monitor-signos-vitales/agente2-caida/Agent2_Fall_ESP32/Agent2_Fall_ESP32.ino`, `doc/04_PIPELINE/preprocesamiento.md`, `notebooks/data/bronce/falls/KFall-Reduced.csv`, `scripts/esp32_dataset_preparation/prepare_test_datasets.py` y artefactos/manifiestos ECG.

- [ ] Registrar placa exacta, versiones de Arduino IDE/Core/biblioteca, hash del modelo ECG, configuración de build y puerto serial. El baseline LiteFallNet queda como referencia histórica, no se reejecuta.
- [ ] Confirmar KFall nativo a 100 Hz, canales `Ax…Gz`, unidades `g`/°s, índices, etiquetas y límites por trial. Mantener los datos crudos; no filtrar, remuestrear ni interpolar para A.
- [ ] Congelar las reglas de A: `acc_range >= 2.0` y `gyro_range >= 150` para impacto; `acc_range < 0.40` y `gyro_range < 30` para quietud; dos ventanas quietas para confirmar y tres ventanas móviles post-impacto para timeout. No ajustar umbrales con `full`.
- [ ] Declarar el montaje validado: cintura/lumbar, consistente con KFall (espalda baja). El «Pecho» del código donante no aplica a esta corrida (decisión del gate M1).
- [ ] Verificar si KFall conserva anclas temporales de inicio/impacto. Si no hay índice temporal fiable, reportar clasificación por trial y omitir latencia desde el evento.
- [ ] Congelar el mapeo de A: caída confirmada → `Fall`; trial completo sin confirmación → `ADL`; muestras inválidas/incompletas, ventana final parcial o sospecha sin resolver → `INDETERMINADO`/`ERROR`.
- [ ] Comprobar integridad de claves, filas, índices consecutivos, NaN/Inf, IDs únicos, conteos y relaciones entre manifiestos y streams.
- [ ] Acordar antes de medir tolerancias de paridad ECG y criterios de latencia; mantener los resultados como mediciones experimentales, no como aprobación de producción.

**Contratos:** A recibe muestras `Ax,Ay,Az,Gx,Gy,Gz` en secuencia a 100 Hz y produce una salida por trial; B recibe `[1,2500,1]` INT8. La clase ECG positiva es `ANORMAL`, no “caída” ni “taquicardia”.

### Task 2: Crear la referencia Python y las pruebas de manifiestos

**Archivos:** crear/adaptar `scripts/esp32_simulation/reference.py`, `scripts/esp32_dataset_preparation/prepare_test_datasets.py` y `tests/test_esp32_simulation.py`.

- [ ] Generar `notebooks/data/esp32_simulation/rule_based/{smoke,full}/` con KFall nativo a 100 Hz, manteniendo trials completos y separados; crear un manifiesto por trial, no ventanas solapadas de LiteFallNet.
- [ ] Crear `fall_trial_manifest.csv` con una fila por trial y actualizar `scenario_manifest.csv` para referenciar `fall_trial_id`, no `fall_window_id`.
- [ ] Confirmar conteos desde los manifiestos generados: smoke con 3 trials Fall + 3 ADL, full con 10 Fall + 10 ADL, 10/40 registros ECG y 20 escenarios, siempre que la validación de fuente mantenga esos tamaños.
- [ ] Añadir selección por `trial_id`, `ecg_id` y `scenario_id`, validando relaciones con `pandas.merge(..., validate=...)` y fallando ante referencias huérfanas.
- [ ] Generar desde Python la entrada cuantizada y salida TFLite de ECG con el mismo preprocesamiento/umbral del firmware. A no tiene tensor, score ni referencia de LiteFallNet.
- [ ] Para ECG, usar `adc_count_sim` en la comparación principal; conservar la señal original como referencia secundaria, no mezclar ambas rutas en una misma métrica.
- [ ] Guardar las salidas de referencia con los IDs de origen para poder distinguir errores de preprocesamiento, inferencia y triaje.

**Verificación:** ejecutar pruebas offline sin abrir el puerto serial; todos los IDs de `scenario_manifest.csv` deben resolver a un trial KFall y un registro ECG.

### Task 3: Probar el motor de reglas y comprobar paridad ECG nativa

**Archivos:** `firmware/esp32_validation/fall_agent.{h,cpp}`, `ecg_agent.{h,cpp}` y un harness nativo de prueba.

- [ ] Extraer la máquina de estados donante a `fall_agent.{h,cpp}` sin su parser Arduino ni señales sintéticas; preservar umbrales/transiciones y exponer evento confirmado por trial antes de resetear el estado.
- [ ] Crear un harness C++ nativo para A: reposo/normal, caída confirmada, movimiento fuerte sin confirmación, cancelación, timeout de tres ventanas, reset entre trials, valores no finitos y ventana final parcial.
- [ ] Exportar desde SciPy los coeficientes y condiciones iniciales ECG de `sosfiltfilt`/`filtfilt`; no aproximar estados con ceros.
- [ ] Implementar ECG en 2.500 muestras: pasa-banda Butterworth orden 4 (0,5–40 Hz), notch 50 Hz/Q30, z-score por ventana y cuantización con escala `0.081706210970878601`, zero point `-18`.
- [ ] Comparar el código C/C++ ECG nativo contra SciPy/referencia Python, incluyendo tensor INT8. A no tiene preprocesamiento ni paridad de señal SciPy.

**Criterio propuesto:** todos los vectores de reglas producen el estado esperado; ECG con error máximo de señal flotante `< 1e-6` y coincidencia exacta de bytes INT8. Registrar diferencias antes de flashear.

### Task 4: Añadir comunicación serial y ejecución secuencial

**Archivos:** crear `firmware/esp32_validation/esp32_validation.ino` y `serial_protocol.{h,cpp}`.

- [ ] Empezar con `Serial.begin(115200)` y handshake `HELLO,1` → `READY,1`.
- [ ] Recibir mensajes delimitados por `\n` mediante `Serial.available()`/`read()` y un buffer fijo; validar límite de línea, IDs, valores finitos, orden de índices, cantidad declarada y `END` correspondiente.
- [ ] Usar `CASE` para asociar un trial KFall con un registro ECG en los escenarios sintéticos. Emitir `AGENT` al terminar A/B y un solo `RESULT` al terminar el caso; no responder por muestra.
- [ ] Devolver `ERROR` con causa y conteos ante timeout, truncamiento o datos inválidos. Limpiar el estado incompleto antes de aceptar otro caso.
- [ ] Medir `fall_rules_us`, `ecg_preprocess_us`, `ecg_inference_us`, `triage_us` y `device_processing_us` con `micros()`, sin incluir impresión serial en los intervalos de cómputo.
- [ ] Mantener la arena de 80 KiB solo para TinyECGNet. Probar trials A consecutivos para verificar reset de la FSM y registros B repetidos para verificar memoria; A no inicializa intérprete.

**Protocolo lógico:** `HELLO`; `CASE`; `BEGIN` con agente, ID y cantidad; muestras `S` con índice; `END` con ID; respuestas `AGENT`, `RESULT` o `ERROR`. A envía los seis ejes de un trial KFall a 100 Hz, con cantidad variable; B envía 2.500 muestras. No concatenar trials. Un trial con muestras faltantes, ventana final parcial o estado de impacto/sospecha sin resolver no se etiqueta `ADL`.

### Task 5: Probar la tabla de triaje sin modelos

**Archivo:** crear `firmware/esp32_validation/triage.h` y cubrirlo desde `tests/test_esp32_simulation.py` o un harness nativo pequeño.

- [ ] Probar `Fall + ANORMAL → ROJO`.
- [ ] Probar `Fall + NORMAL → AMARILLO`.
- [ ] Probar `ADL + ANORMAL → AMARILLO`.
- [ ] Probar `ADL + NORMAL → VERDE`.
- [ ] Probar `INDETERMINADO`, salida ausente, etiqueta desconocida y señal inválida; ninguno debe producir `ADL` ni una alerta/color válido.

### Task 6: Implementar el reproductor de Ubuntu

**Archivos:** crear `scripts/esp32_simulation/replay.py`, extender `tests/test_esp32_simulation.py` y declarar pySerial como extra opcional en `pyproject.toml`.

- [ ] Añadir argumentos `--port`, `--baud` (115200 por defecto), `--dataset-dir`, `--mode` (`fast`/`paced`), `--suite` y `--output`.
- [ ] Leer los CSV de `rule_based/{smoke,full}`, validar asociaciones con manifiestos y enviar los trials KFall sin concatenarlos.
- [ ] Configurar timeout de lectura y escritura; tratar una línea incompleta o una respuesta que no llega como fallo de la prueba, no como predicción.
- [ ] En modo rápido, transmitir en orden a máxima velocidad y esperar una respuesta por bloque.
- [ ] En modo temporizado, programar envíos a 100 Hz para A y 250 Hz para B usando reloj monotónico; registrar retraso real frente al instante programado.
- [ ] Medir `end_to_end_ms` desde antes del primer envío del bloque hasta recibir la respuesta completa. No sumar etapas que ya están incluidas en ese tiempo.
- [ ] Escribir una fila por trial A, registro B y escenario en `results.csv`, con IDs, referencia, predicción/estado, tiempos, muestras esperadas/recibidas, modo y error. `q`/score solo aplica a B. Guardar versiones, hashes, baud rate y semilla en `run_metadata.json`.

### Task 7: Ejecutar aceptación y producir el informe

- [ ] Compilar el sketch de validación con ESP32 Core 2.0.17 y `TensorFlowLite_ESP32` 1.0.0.
- [ ] Probar el handshake y los contadores con `smoke` en modo rápido.
- [ ] Ejecutar `full` en modo rápido: 20 trials KFall (10 Fall/10 ADL), 40 registros ECG y los 20 escenarios del manifiesto.
- [ ] Repetir un subconjunto fijo para la distribución de latencia; después probar modo temporizado y registrar el jitter.
- [ ] Inyectar línea truncada, muestra omitida, bloque incompleto y desconexión del host; comprobar recuperación y que no aparezcan etiquetas válidas falsas.
- [ ] Resumir A por trial y B por registro, además de paridad ECG Python↔ESP32, tabla de triaje, mediana/P95 de tiempos, uso de memoria y errores de comunicación. Informar latencia desde evento solo si el manifiesto conserva una marca temporal fiable.
- [ ] Guardar `results.csv`, `run_metadata.json` y `summary.json` en `reports/esp32_validation/<run-id>/`.

**Verificaciones de software:** `python -m pytest -m "not slow" -v`, harness de reglas y harness nativo de ECG. **Criterios mínimos:** cero pérdidas silenciosas; todos los IDs esperados registrados; paridad ECG dentro de tolerancia; vectores de regla correctos; 4/4 reglas de triaje correctas; entradas inválidas nunca se clasifican como `ADL`/`NORMAL`.

## Interpretación y límites

- A se evalúa por trial KFall, no con las ventanas solapadas del manifiesto UMAFall usado por LiteFallNet. No se cuentan ventanas como eventos independientes.
- `full` usa KFall para caídas y PTB-XL fold 10 para ECG; las cantidades se obtienen de los manifiestos nuevos y no se mezclan con los `smoke/full` previos de UMAFall.
- El montaje validado es cintura/lumbar, consistente con KFall. Un montaje de pecho queda fuera de esta corrida y requeriría un protocolo aparte.
- Las filas de `scenario_manifest.csv` son emparejamientos artificiales y no sincronizados. La coincidencia de triaje mide la lógica del prototipo, no una mejora clínica ni reducción de falsos positivos en pacientes.
- `ANORMAL` de PTB-XL no equivale a taquicardia. No presentar el color del triaje como diagnóstico.
- No calcular falsas alarmas clínicas por hora a partir de trials/pares sintéticos; requeriría exposición negativa continua y una regla temporal de agrupación de alertas.
- No afirmar funcionamiento offline durante pérdida del host USB/Serial: Ubuntu es la fuente de datos de esta prueba.

## Referencias

- [Arduino-ESP32 Serial](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/serial.html): configuración y recepción/transmisión serial.
- [pySerial API](https://pyserial.readthedocs.io/en/latest/pyserial_api.html) y [lectura de líneas](https://pyserial.readthedocs.io/en/latest/shortintro.html): timeouts, `readline()` y escritura.
- [Preparación de datasets ESP32](../scripts/esp32_dataset_preparation/README.md): referencia de columnas; el preparador deberá ajustarse para KFall nativo a 100 Hz y un manifiesto por trial.
- [Estado de los modelos INT8](ESTADO_MODELOS_INT8_ESP32.md): contrato de cuantización, estado experimental y gate de producción.
