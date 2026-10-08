# Validación experimental de los módulos A y B en ESP32

**Alcance:** módulos A (caídas, MPU6050) y B (ECG, AD8232). Módulo C y sensores ambientales quedan fuera.

El plan comprueba captura, inferencia, coordinación y rendimiento técnico. No valida diagnóstico clínico. Los pasos con LiteRT Micro y ESP-IDF se deben ajustar a la placa y al firmware exactos.

Las frecuencias y ventanas indicadas vienen de los pipelines del proyecto. Los criterios numéricos de éxito deben acordarse antes de medir; no se fijan pines ni límites no publicados. Una ventana es un tramo fijo de señal que recibe el modelo.

## Pasos e hitos

### 1. Identificar placa y firmware

**Acción:** registrar modelo exacto de ESP32, placa, framework y versión del firmware. Registrar también los modelos de las placas MPU6050 y AD8232. Si se conserva MQTT, indicar dónde estará el broker.

**Advertencia:** “ESP32” no identifica una placa ni sus pines. No elegir pines o conexiones solo con la ficha del chip: revisar la guía de la placa y el esquema de cada módulo.

**Hito:** ficha del equipo con placa, framework, versiones y ubicación del broker definidos.

### 2. Comprobar que ambos modelos corren en la ESP32

**Acción:** comprobar que el programa LiteRT para la placa admite las operaciones de ambos modelos y el formato de sus entradas. Cargar primero A y luego B; después probar ambos en una misma sesión. Si el firmware lo requiere, convertir los archivos `.tflite` a datos C incluidos en el programa. Comparar resultados de la placa y de referencia con el mismo archivo de prueba.

**Advertencia:** LiteRT para microcontroladores solo admite parte de las operaciones y requiere gestionar memoria manualmente. Un `.tflite` convertido no demuestra por sí mismo que pueda ejecutarse en la placa. El componente de Espressif publica una lista de versiones de ESP-IDF compatibles; respetarla si se elige ese componente.

**Hito:** ambos modelos cargan e infieren; se registran memoria, tiempo y diferencia frente a la referencia. El límite aceptable de diferencia se fija antes de medir.

### 3. Verificar captura y preparación de las señales

**Acción:** mantener el formato usado por los modelos:

- **A:** AVM y GVM (magnitudes de aceleración y giro), a 50 Hz; ventana de 3 s (150 muestras) y el escalador documentado, guardado por separado del modelo.
- **B:** ECG Lead II, a 250 Hz; ventana de 10 s (2.500 muestras) y preparación usada durante el entrenamiento.

Usar la conexión I²C para el MPU6050. Leer la salida analógica del AD8232 con la entrada ADC de la ESP32, que convierte esa señal en datos digitales. Registrar muestras recibidas, tiempos y errores de lectura.

**Advertencia:** Espressif documenta muestreo continuo, calibración y errores posibles por ruido o por llenar el búfer, lo que puede dejar muestras sin procesar. La guía del ESP32 clásico indica una relación entre ADC2 y Wi-Fi; verificarla para el chip exacto antes de elegir el pin. No cambiar filtros, escalado ni frecuencia sin medir el efecto sobre el modelo.

**Hito:** se forman ventanas completas con las dimensiones esperadas y el registro no presenta muestras perdidas ni desbordes durante la prueba definida.

### 4. Definir y probar la regla entre A y B

**Acción:** escribir una tabla corta con todas las combinaciones de salida de A y B y la respuesta esperada del coordinador. Incluir también el caso de salida ausente o señal inválida. Ejecutar pruebas de tabla con resultados preparados antes de conectar inferencia continua.

**Advertencia:** B clasifica ECG como NORMAL/ANORMAL; no informa por sí solo “taquicardia”. La tabla de Fase 4 usa taquicardia y ritmo estable. No equiparar esos términos sin una regla validada y aprobada. Una salida ausente tampoco debe contarse como normal.

**Hito:** reglas aprobadas y una prueba automática confirma el resultado esperado para cada combinación.

### 5. Reproducir datos de prueba en la ESP32

**Acción:** ejecutar los conjuntos de prueba reservados de A y B, conservando sus etiquetas. Comparar dos modos con las mismas entradas: agentes aislados y agentes con coordinador. Guardar señales o identificadores de prueba, salidas de cada modelo, decisión final y tiempos.

**Advertencia:** los datos de caídas y ECG provienen de colecciones distintas y no son registros sincronizados de una misma persona. Al combinarlos se prueban escenarios preparados, no una relación clínica real entre ambas señales. Mantener los conjuntos de prueba reservados; no usarlos para ajustar reglas o umbrales.

**Hito:** existe un registro reproducible de cada prueba y ambas modalidades recibieron las mismas entradas en los dos modos.

### 6. Medir resultados y desconexión

**Acción:** informar por separado:

- Para A y B: aciertos y errores por clase (caída/no caída; ECG normal/anormal).
- Para el sistema: eventos detectados, falsas alarmas por hora y tiempo desde la señal hasta la decisión final.
- Para ESP32: tiempo de inferencia de cada modelo, tiempo total y errores de captura.
- Si MQTT forma parte de la prueba: repetir con broker disponible y desconectado; registrar qué decisiones siguen funcionando y qué mensajes se pierden.

**Advertencia:** el pipeline de caídas reporta resultados por ventana y usa ventanas solapadas; no contarlas como eventos independientes. ESP-MQTT documenta un **cliente** MQTT, no un broker Mosquitto. Si se usa MQTT, definir el broker fuera de la ESP32. No afirmar funcionamiento offline hasta probar la ruta completa sin ese enlace. La meta de reducción de latencia frente a nube debe compararse con la misma entrada y medirse; no se debe presentar como resultado anticipado.

**Hito:** tabla de métricas con duración de prueba, criterios de éxito acordados antes de medir y resultado de la prueba de desconexión.

### 7. Cerrar evidencia

**Acción:** guardar versión del firmware, modelo exacto y su huella (hash), placa, configuración, conjunto de prueba, reglas y resultados. Incluir fallos y límites observados.

**Advertencia:** los resultados validan el funcionamiento técnico en los escenarios probados; no prueban uso clínico ni desempeño con señales reales, alineadas en el tiempo y tomadas de los mismos pacientes.

**Hito:** informe reproducible con datos suficientes para repetir la evaluación y actualizar los resultados del proyecto.

## Referencias consultadas

Consultadas el 8 de octubre de 2026.

### Documentación oficial de dispositivos y tecnologías

- Google, [LiteRT para microcontroladores: plataformas, flujo y límites](https://developers.google.com/edge/litert/microcontrollers/overview).
- Espressif, [componente esp-tflite-micro](https://components.espressif.com/components/espressif/esp-tflite-micro): ejemplos para ESP32 y versiones de ESP-IDF indicadas por el componente.
- Espressif, [I²C para ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/i2c.html).
- Espressif, [ADC continuo para ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc/adc_continuous.html) y [calibración del ADC](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/adc/adc_calibration.html).
- Espressif, [ESP-MQTT para ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/protocols/mqtt.html).
- Eclipse Mosquitto, [documentación del broker MQTT](https://mosquitto.org/documentation/).
- TDK InvenSense, [ficha técnica MPU-6000/MPU-6050](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf) y [mapa de registros](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf).
- Analog Devices, [ficha técnica AD8232](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8232.pdf).

### Documentación del proyecto

- [README del proyecto](../README.md): entradas, frecuencia y ventanas del módulo A.
- [Entrenamiento del módulo A](04_PIPELINE/entrenamiento.md): escalado, métricas y límites de evaluación por ventana.
- [Pipeline ECG del módulo B](04_PIPELINE/ecg-ptb-xl-agent1.md): datos, frecuencia y clasificación del modelo.
- [Plan de Fase 4](00_PLAN/FASE%204%20-%20SISTEMA%20MULTIAGENTE.md): coordinación y tabla de decisiones original.
- [Plan de Fase 5](00_PLAN/FASE%205%20-%20VALIDACI%C3%93N%20EXPERIMENTAL.md): métricas previstas de latencia, desconexión y falsas alarmas.
