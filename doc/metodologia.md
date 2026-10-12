# Datos y metodología

El proyecto procesa señales guardadas, prepara conjuntos comparables y evalúa modelos. Los notebooks contienen los pasos exactos y son la referencia principal cuando se necesita reproducir un cálculo.

## Datos utilizados

| Área | Conjunto de datos | Uso en el proyecto |
|---|---|---|
| Caídas | SisFall, FallAllD, KFall, UP-Fall y UMAFall | Aceleración y giroscopio. Sus tasas originales van de aproximadamente 18 a 238 muestras por segundo; el flujo común de caídas las lleva a 50. |
| Electrocardiograma (ECG) | PTB-XL | Señales clínicas de 10 segundos. Se usa la derivación II a 250 muestras por segundo y una etiqueta normal/anormal. |
| Fotopletismografía (PPG) | BIDMC | Señal óptica a 125 muestras por segundo para revisar calidad y estimar frecuencia cardíaca. |

Los archivos originales o reducidos no están versionados en Git. Las fuentes de descarga son [SisFall](https://doi.org/10.3390/s17010198), [FallAllD](https://doi.org/10.1109/JSEN.2020.3018335), [KFall](https://doi.org/10.3389/fnagi.2021.692865), [UP-Fall](https://doi.org/10.3390/s19091988), [UMAFall](https://doi.org/10.1016/j.procs.2017.06.110), [PTB-XL](https://physionet.org/content/ptb-xl/1.0.3/) y [BIDMC](https://physionet.org/content/bidmc/1.0.0/).

## Detección de caídas

Se combinan cinco conjuntos de datos. Antes del entrenamiento, la aceleración y el giroscopio se resumen en dos señales: AVM, magnitud de aceleración, y GVM, magnitud del giroscopio. Esto reduce el efecto de la orientación del sensor.

El modelo principal es una CNN-BiLSTM: una red que reconoce patrones cortos y cómo cambian a lo largo del tiempo. Analiza ventanas de tres segundos y distingue caídas de actividades diarias. Se comparan dos grupos: `set_a` usa los cinco conjuntos y `set_b` excluye UMAFall.

La **sensibilidad** indica cuántas caídas encuentra; la **especificidad**, cuántas actividades normales descarta correctamente; y la **precisión**, cuántas alertas de caída corresponden a caídas dentro de la prueba.

| Conjunto | Sensibilidad | Especificidad | Precisión |
|---|---:|---:|---:|
| `set_a` | 0,9772 ± 0,0096 | 0,9922 ± 0,0032 | 0,9799 ± 0,0082 |
| `set_b` | 0,9742 ± 0,0132 | 0,9934 ± 0,0025 | 0,9823 ± 0,0063 |

Son promedios de cinco particiones separadas por sujeto. La precisión depende de cuántas caídas y actividades no peligrosas haya en la evaluación, por lo que estos valores no predicen por sí solos el resultado en el uso cotidiano.

## ECG

Se seleccionaron 20.970 registros de PTB-XL. El modelo TinyECGNet clasifica cada señal como normal o anormal; esa etiqueta no es un diagnóstico médico. Su versión INT8 —un formato compacto para ejecutar modelos en dispositivos pequeños— ocupa 18.584 bytes.

En el conjunto de prueba de 2.113 registros, la versión INT8 obtuvo 79,6 % de aciertos, 73,9 % de sensibilidad y 87,1 % de especificidad. Los aciertos son las señales clasificadas correctamente; sensibilidad y especificidad se explican en la sección de caídas. La evaluación se hizo con datos de PTB-XL, no con pacientes conectados a un sensor.

## PPG y frecuencia cardíaca

El flujo PPG usa 53 registros de BIDMC de 46 personas. Se revisa la calidad de la señal y se compara la frecuencia cardíaca calculada con la informada por el conjunto de datos. En 6.307 ventanas, el error absoluto medio fue de 2,23 latidos por minuto.

No se entrenó un modelo de saturación de oxígeno en sangre (SpO₂). BIDMC no contiene las señales ópticas roja e infrarroja ni una medición independiente adecuada para comprobar ese cálculo.

## Qué está en el dispositivo

La prueba de ESP32 usa reglas para detectar caídas y TinyECGNet para el ECG. LiteFallNet es un modelo candidato aparte y no se usó en esa prueba. La integración de un sistema multiagente completo, los sensores físicos y las comunicaciones MQTT no forman parte de los resultados validados aquí.
