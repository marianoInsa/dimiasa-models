# Resultados de la prueba con ESP32

La prueba envió registros guardados desde una computadora a una ESP32 por USB. Comprobó el intercambio de datos, el procesamiento de las señales y la respuesta del firmware. **No utilizó sensores conectados a una persona y no es una evaluación clínica.**

## Qué se probó

- 20 ensayos de caída de KFall: 10 caídas y 10 actividades cotidianas.
- 40 registros de ECG de PTB-XL: 20 normales y 20 anormales.
- 20 combinaciones de caída y ECG para probar la tabla de triaje.

Las 80 filas de datos llegaron y fueron procesadas sin errores de comunicación.

## Resultados de los modelos

**Caídas:** de los 20 ensayos, el firmware clasificó 15 y dejó 5 como “indeterminado” para evitar una respuesta insegura. De los 15 clasificados, identificó las 7 caídas y clasificó correctamente 7 de 8 actividades cotidianas. Los casos indeterminados se informan por separado; no se cuentan como aciertos.

**ECG:** de los 20 registros anormales, reconoció 16; de los 20 normales, reconoció 17. Esto equivale a 80 % de sensibilidad y 85 % de especificidad en este conjunto de prueba.

En palabras simples, la sensibilidad indica cuántos registros anormales encontró el modelo y la especificidad cuántos registros normales reconoció correctamente.

**Prioridad de atención (triaje):** la tabla de decisión del dispositivo coincidió con las salidas de los dos agentes en las 20 combinaciones. Al comparar el sistema completo con las etiquetas originales, coincidió en 14 de 20; el resto refleja los errores o casos indeterminados de los modelos, no de la tabla de prioridad.

## Tiempo y comunicación

El reproductor también comprobó el envío de señales a su frecuencia prevista y la recuperación tras interrupciones de comunicación. En la placa probada, el cálculo de caídas tomó alrededor de 1,3 milisegundos; el preprocesamiento de ECG, 108 milisegundos; y la inferencia de ECG, alrededor de 1,1 segundos. Son mediciones de esa configuración y pueden variar según la placa, la computadora y las versiones utilizadas.

## Límites de estos resultados

- La computadora envió señales guardadas; no hubo adquisición directa desde sensores físicos.
- Las señales de caída y ECG se emparejaron para probar el triaje; no proceden de la misma persona ni del mismo momento.
- “Anormal” es la categoría del modelo ECG; no indica por sí sola una enfermedad ni una frecuencia cardíaca alta.
- Los datos no demuestran seguridad, eficacia clínica ni funcionamiento en pacientes.

Los archivos de resultados detallados en formato CSV y JSON se conservan bajo `reports/esp32_validation/`.
