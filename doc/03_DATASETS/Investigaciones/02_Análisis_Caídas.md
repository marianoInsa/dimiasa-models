# Cuadro Comparativo Integral de Datasets de Detección de Caídas con IMU

Se unificaron:
- características técnicas,
- cantidad y perfil de sujetos,
- sensores utilizados,
- frecuencia de muestreo,
- actividades incluidas,
- fortalezas diferenciales,
- limitaciones,
- aplicabilidad para TinyML / Edge AI,
- y disponibilidad pública.

---

# Tabla Comparativa Integral

| Dataset                    | Año  | Sensores / Hardware                                   | Ubicación del Sensor                       | Frecuencia                              | Sujetos                                      | Actividades Incluidas                          | Características Diferenciales                                                                                                                                                       | Limitaciones                                                           | Relevancia para Edge AI / TinyML                                                                  |
| -------------------------- | ---- | ----------------------------------------------------- | ------------------------------------------ | --------------------------------------- | -------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **SisFall**                | 2017 | Acelerómetro + Giroscopio (IMU)                       | Cintura                                    | 200 Hz                                  | 38 sujetos (jóvenes y adultos mayores)       | 15 tipos de caídas + 19 ADL                    | Dataset de referencia en la literatura. Excelente calidad cinemática y señales muy limpias. Incluye adultos mayores reales para ADL.                                                | Variabilidad limitada. Menor diversidad de falsos positivos complejos. | Muy alta. Excelente baseline para entrenamiento y comparación.                                    |
| **FallAllD**               | 2021 | Acelerómetro ±8g, Giroscopio, Magnetómetro, Barómetro | Muñeca, cuello y cintura                   | 200–238 Hz                              | 15–26 sujetos                                | 35 tipos de caídas + 44 ADL                    | Uno de los datasets más completos y exigentes. Incluye caídas con recuperación, actividades de mano y múltiples posiciones corporales. Diseñado específicamente para Deep Learning. | Población relativamente pequeña y principalmente joven.                | Extremadamente alta. Ideal para robustecer modelos TFLite y estudiar ubicación óptima del sensor. |
| **UMAFall**                | 2017 | Smartphone + SensorTag (MPU-9250)                     | Tobillo, cintura, muñeca, pecho y bolsillo | 20 Hz (wearables) / 200 Hz (smartphone) | 17–19 sujetos                                | 3 caídas + 7–12 ADL                            | Dataset multisensorial único. Excelente para estudiar impacto de la ubicación del sensor y validación en bajas frecuencias.                                                         | Frecuencia de 20 Hz puede perder detalles finos del impacto.           | Muy alta para TinyML y BLE. Ideal para ESP32 de bajo consumo.                                     |
| **MobiFall**               | 2013 | Smartphone (Galaxy S3)                                | Bolsillo del pantalón                      | ~87 Hz accel / ~200 Hz gyro             | 24 sujetos                                   | 4 caídas + 9 ADL                               | Dataset clásico ampliamente utilizado. Incluye orientación aleatoria del smartphone.                                                                                                | Acelerómetro ±2g produce saturación en impactos fuertes.               | Alta como baseline y pruebas de robustez.                                                         |
| **MobiAct**                | 2016 | Smartphone IMU                                        | Bolsillo / cintura                         | 87 Hz accel / 100 Hz gyro               | 57 sujetos                                   | 4 caídas + 9 ADL similares a caídas            | Gran diversidad demográfica y alta cantidad de actividades confusas (sentarse bruscamente, entrar/salir de auto, trotar, saltar).                                                   | Sensores de smartphone introducen ruido y variabilidad de orientación. | Muy alta. Excelente para reducir falsos positivos en Edge AI.                                     |
| **KFall**                  | 2021 | LPMS-B2 IMU (Accel + Gyro + Euler)                    | Zona lumbar / espalda baja                 | 100 Hz                                  | 32 sujetos                                   | 15 caídas + 21 ADL                             | Posee etiquetado preciso de fases de pre-impacto e impacto mediante sincronización por video. Ideal para predicción temprana de caídas.                                             | Solo hombres jóvenes en muchas capturas.                               | Extremadamente alta para modelos predictivos y sistemas multiagente.                              |
| **UP-Fall**                | 2019 | IMU + sensores multimodales                           | Cintura / pecho                            | 100 Hz                                  | 17 sujetos                                   | 5 caídas + 6 ADL                               | Dataset multimodal muy utilizado en HAR y fall detection.                                                                                                                           | Menor volumen comparado con otros datasets modernos.                   | Alta como dataset complementario y validación cruzada.                                            |
| **AybuFall**               | 2026 | IMU (Accel + Gyro)                                    | Frente y antebrazo                         | 200 Hz                                  | 17 sujetos                                   | 11 caídas + 13 ADL + 5 movimientos de rezo     | Introduce actividades culturales complejas (rezos) como falsos positivos difíciles. Excelente para robustez contextual.                                                             | Dataset reciente con menor adopción aún en la literatura.              | Muy alta para sistemas resilientes y reducción de falsas alarmas.                                 |
| **SmartFallMM**            | 2018 | Smartwatch + Smartphone IMU                           | Muñeca y cadera                            | 32 Hz                                   | 42 sujetos (16 jóvenes + 26 adultos mayores) | 5 caídas + 9 ADL                               | Uno de los pocos datasets con fuerte presencia de adultos mayores. Excelente para estudiar sesgo geriátrico.                                                                        | Caídas realizadas principalmente por sujetos jóvenes.                  | Muy alta para TinyML y despliegues reales geriátricos.                                            |
| **UniMiB-SHAR**            | 2016 | Smartphone acelerómetro                               | Bolsillo                                   | 50 Hz                                   | 30 sujetos                                   | 8 caídas + 9 ADL                               | Más de 11.700 muestras. Dataset masivo ideal para Deep Learning y entrenamiento batch.                                                                                              | Solo acelerómetro; no incluye giroscopio.                              | Alta para CNN 1D y modelos ligeros cuantizados.                                                   |
| **FARSEEING**              | 2016 | Acelerómetro + parcialmente giroscopio y magnetómetro | Lumbar (L5) y muslo                        | 20–100 Hz                               | Adultos mayores reales (edad media ~76 años) | Caídas reales verificadas + ADL de vida diaria | Único gran repositorio público con caídas reales de adultos mayores en entorno real.                                                                                                | Acceso restringido y dataset difícil de obtener.                       | Crítico para validación clínica final.                                                            |
| **Coventry / Cogent Labs** | 2015 | Shimmer IMU                                           | Pecho y muslo                              | 100 Hz                                  | 42 sujetos                                   | 4 caídas inducidas + ADL + near-falls          | Incluye near-falls y caídas inducidas más realistas mediante perturbaciones físicas. Excelente para clases negativas difíciles.                                                     | Menor popularidad y menor disponibilidad pública actual.               | Muy alta para entrenamiento robusto contra falsos positivos.                                      |
| **ShimFall&ADL**           | 2020 | Shimmer v2 acelerómetro triaxial                      | Pecho                                      | 50 Hz                                   | 35 sujetos                                   | 9 caídas + 6 ADL                               | Evaluación extensa de features espacio-frecuenciales y muy alto F1-score reportado.                                                                                                 | Solo acelerómetro y sujetos jóvenes.                                   | Alta para modelos clásicos ML y sensores torácicos.                                               |
| **Wertner et al. Dataset** | 2015 | Smartphone (Accel + Gyro)                             | Smartphone móvil                           | 5 Hz                                    | 5 sujetos                                    | 4 caídas simuladas + 10 ADL                    | Dataset extremadamente liviano y simple. Útil para estudiar detección en ultra bajo consumo.                                                                                        | Muy baja frecuencia y muestra reducida.                                | Moderada. Interesante para escenarios ultra low-power.                                            |

---

# Comparación Estratégica por Objetivo

## 1. Mejores datasets para TinyML / ESP32

| Dataset     | Motivo                                          |
| ----------- | ----------------------------------------------- |
| UMAFall     | Validación realista en 20 Hz y BLE              |
| SmartFallMM | Frecuencia baja (32 Hz) y adultos mayores       |
| MobiAct     | Alta variabilidad para reducir falsos positivos |
| AybuFall    | Casos difíciles y movimientos complejos         |

---

## 2. Mejores datasets para Deep Learning

|Dataset|Motivo|
|---|---|
|FallAllD|Gran volumen y múltiples sensores|
|UniMiB-SHAR|Más de 11k muestras|
|KFall|Etiquetado temporal extremadamente preciso|
|MobiAct|Gran diversidad poblacional|

---

## 3. Mejores datasets para validación clínica real

|Dataset|Motivo|
|---|---|
|FARSEEING|Caídas reales de adultos mayores|
|SmartFallMM|ADL geriátricas reales|
|SisFall|Incluye población adulta mayor|

---

## 4. Mejores datasets para reducir falsos positivos

| Dataset         | Motivo                             |
| --------------- | ---------------------------------- |
| MobiAct         | Actividades similares a caídas     |
| AybuFall        | Movimientos de rezo                |
| Coventry/Cogent | Near-falls y perturbaciones reales |
| FallAllD        | Caídas con recuperación            |

---

# Hallazgos Clave del Cruce de Investigaciones

## 1. FallAllD aparece consistentemente como el dataset más robusto

Las tres investigaciones coinciden en que FallAllD representa uno de los mejores benchmarks modernos debido a:

- múltiples ubicaciones del sensor,
- alta frecuencia,
- gran variedad de ADL,
- caídas complejas,
- y dificultad real para clasificación.

Es el dataset más recomendado para entrenar modelos modernos de Deep Learning y TFLite.

---

## 2. UMAFall es extremadamente importante para Edge AI

Aunque menos complejo que FallAllD, UMAFall aparece como uno de los datasets más relevantes para dispositivos embebidos porque demuestra que:

- 20 Hz pueden ser suficientes,
- BLE introduce restricciones reales,
- y múltiples ubicaciones del sensor afectan significativamente el rendimiento.

---

## 3. Existe un fuerte sesgo hacia sujetos jóvenes

La mayoría de los datasets:

- usan estudiantes universitarios,
- poseen caídas simuladas,
- y no representan completamente la biomecánica geriátrica.

Los únicos datasets que mitigan parcialmente este problema son:

- FARSEEING,
- SmartFallMM,
- y parcialmente SisFall.

---

## 4. Los falsos positivos son el verdadero desafío

Las investigaciones coinciden en que el problema más complejo no es detectar impactos, sino diferenciar:

- sentarse bruscamente,
- tropezones,
- rezos,
- saltos,
- acostarse,
- near-falls,
- y actividades transicionales.

Por ello, datasets como:

- MobiAct,
- AybuFall,
- Coventry,
- y FallAllD

son especialmente valiosos.

---

## 5. Frecuencias extremadamente altas no siempre son necesarias

Los análisis convergen en que:

- 20–32 Hz pueden ser suficientes para TinyML,
- mientras que 100–200 Hz benefician principalmente el entrenamiento y análisis fino.

Esto es crítico para ESP32 y TFLite Micro.

---

# Recomendación Final para DiMIASA

## Combinación Óptima de Datasets

| Objetivo                         | Dataset recomendado           |
| -------------------------------- | ----------------------------- |
| Base principal                   | FallAllD                      |
| Robustez contra falsos positivos | MobiAct + AybuFall + Coventry |
| TinyML / ESP32                   | UMAFall + SmartFallMM         |
| Predicción pre-impacto           | KFall                         |
| Validación clínica final         | FARSEEING                     |
| Baseline académico               | SisFall                       |

---

# Conclusión Global

La integración conjunta de estos datasets permite construir un corpus extremadamente robusto para sistemas de detección de caídas basados en IMU y Edge AI.

Cada dataset aporta una dimensión distinta:

- FallAllD aporta complejidad,
- UMAFall aporta realismo embebido,
- MobiAct aporta falsos positivos,
- KFall aporta precisión temporal,
- SmartFallMM aporta biomecánica geriátrica,
- FARSEEING aporta validación real,
- AybuFall aporta contexto cultural,
- Coventry aporta near-falls,
- y UniMiB-SHAR aporta volumen estadístico.

La combinación de todos ellos representa una estrategia significativamente más sólida que depender exclusivamente de SisFall para entrenar modelos de detección de caídas resilientes, cuantizados y desplegables en ESP32/TFLite.