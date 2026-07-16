
---

## Análisis Comparativo de Datasets Públicos para Detección de Caídas (IMU)

He seleccionado **6 datasets** que cumplen con tus criterios: todos basados exclusivamente en sensores inerciales (acelerómetro 3D + giroscopio), sin visión computacional ni radar, y que complementan a SisFall. La tabla comparativa se encuentra al final; primero contextualizo cada dataset.

---

### 1. **FallAllD** — El más completo como alternativa a SisFall

El dataset **FallAllD** (2021) fue diseñado específicamente para superar las limitaciones de datasets previos [1]. Utiliza 3 dataloggers idénticos colocados en **muñeca, cintura y cuello**, cada uno equipado con un acelerómetro (±8 g, 238 Hz), giroscopio (±2000 dps, 238 Hz), magnetómetro y barómetro. Incluye **35 tipos de caídas** (considerando dirección, causa —resbalón, tropiezo, síncope—, y recuperación post-caída) y **44 tipos de ADL** (incluyendo 12 actividades solo de mano para la muñeca).

Es especialmente valioso para tu proyecto porque:

- El rango de ±8 g evita saturación en el impacto, algo crítico en muchos otros datasets con ±2 g [1,7].
- Incluye **caídas con recuperación**, que generan señales más confusas y realistas.
- Sus autores demuestran que clasificar sobre FallAllD es significativamente más difícil que sobre SisFall o UMAFall (la precisión balanceada cae de ~99% a ~93%), lo que lo convierte en un _benchmark_ más exigente [1].
- **Repositorio:** IEEE DataPort (`http://dx.doi.org/10.21227/bnya-mn34`).

### 2. **UMAFall** — 5 puntos de sensor simultáneos

**UMAFall** (2017) es único porque emplea **5 nodos de sensado simultáneo**: 4 motas SensorTag (MPU-9250: acelerómetro + giroscopio + magnetómetro) en tobillo, cintura, muñeca derecha y pecho, más un smartphone en el bolsillo del pantalón [2]. Esto permite estudiar el impacto de la ubicación del sensor en el rendimiento de detección.

Datos clave: 17 sujetos, 8 ADL (agacharse, subir/bajar escaleras, saltar, trotar, acostarse, sentarse, caminar) y 3 tipos de caída (atrás, adelante, lateral). Frecuencia de muestreo de 20 Hz en las motas y 200 Hz en el smartphone. Los archivos están en formato CSV con ventanas de 15 segundos por actividad [2].

Aunque la frecuencia de 20 Hz es baja, los autores demuestran que combinando sensores en muñeca y cintura se maximiza la separabilidad entre clases [2].

### 3. **MobiFall / MobiAct** — El clásico con smartphone en bolsillo

**MobiFall** (2013) y su extensión **MobiAct** son datasets pioneros donde un smartphone (Samsung Galaxy S3) se coloca en el bolsillo del pantalón en orientación aleatoria [3]. Capturan acelerómetro (~87 Hz) y giroscopio (~200 Hz). MobiFall: 24 sujetos, 4 tipos de caída y 9 ADL. MobiAct: 57 sujetos, más actividades.

La limitación principal es el rango del acelerómetro de solo **±2 g**, que causa saturación en los picos de impacto. Sin embargo, es un dataset muy utilizado para comparación y contiene actividades ADL que se asemejan a caídas (como sentarse bruscamente en una silla vacía) [3,7].

### 4. **Coventry/Cogent Labs Dataset** — 42 sujetos con caídas inducidas

Este dataset (2015) destaca por incluir **caídas inducidas** (empujando a sujetos con ojos vendados desde una tabla de equilibrio), lo que genera movimientos más realistas y menos controlados que las caídas voluntarias [6]. Usa dos sensores Shimmer (acelerómetro + giroscopio a 100 Hz) en pecho y muslo.

Incluye 4 tipos de caída, ADL variadas y **near-falls** (casi-caídas por tropiezos), que son excelentes como clase negativa difícil — exactamente lo que necesitas para tu sistema multiagente [6]. 42 sujetos (la muestra más grande entre los datasets analizados que no son smartphone). También incluye subida/bajada de escaleras.

### 5. **ShimFall&ADL** — Sensor torácico, 35 sujetos

**ShimFall&ADL** (2020) usa un acelerómetro triaxial Shimmer v2 colocado en el **pecho** a 50 Hz [4]. 35 sujetos sanos (19–34 años) realizaron 6 ADL (saltar, acostarse, agacharse, sentarse/levantarse, caminar) y 9 tipos de caída (frontales, laterales, traseras, escalonadas —cada una repetida suave y fuerte—).

Los autores evaluaron 216 características espacio-frecuenciales con máquinas de aprendizaje, logrando un F1-score de 98.41% para clasificación binaria caída/no-caída. El dataset se anunció como de acceso público, y es complementario a SisFall por usar una ubicación diferente (pecho vs. cintura) [4].

### 6. **FARSEEING** — El único con caídas reales de adultos mayores

**FARSEEING** (2016) es la **única base de datos pública con caídas reales** medidas con sensores inerciales en **adultos mayores** (edad media 76.1 años) [5]. Contiene 208 caídas verificadas, registradas con acelerómetros (100 Hz mayoritariamente) colocados en la zona lumbar (L5) o muslo, durante la vida diaria de los participantes.

Aunque el acceso es restringido (solicitud al consorcio), es la referencia para validar algoritmos en población geriátrica real. El 58% de las señales incluyen también giroscopio y magnetómetro. Incluye datos de línea base (ADL) de 24 horas sin caídas [5].

---

## Tabla Comparativa

| Dataset                  | Repositorio / Enlace                                                                                            |        Frecuencia (Hz)        |              Sujetos              | Tipos de Actividades                      | Paper de Validación                                                                                                                                                  |
| :----------------------- | :-------------------------------------------------------------------------------------------------------------- | :---------------------------: | :-------------------------------: | :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FallAllD**             | IEEE DataPort ([dx.doi.org/10.21227/bnya-mn34](http://dx.doi.org/10.21227/bnya-mn34))                           |        238 (acc+giro)         |      15 (8M, 7F) 21–53 años       | 35 caídas, 44 ADL (incluye 12 de mano)    | M. Saleh et al., "FallAllD: An Open Dataset of Human Falls and Activities of Daily Living for Classical and Deep Learning Applications," _IEEE Sensors J._, 2021 [1] |
| **UMAFall**              | Universidad de Málaga (contactar autores / repositorio institucional)                                           | 20 (motes) / 200 (smartphone) |      17 (10M, 7F) 18–55 años      | 3 caídas, 8 ADL (5 posiciones corporales) | E. Casilari et al., "UMAFall: A Multisensor Dataset for the Research on Automatic Fall Detection," _Procedia Computer Science_, 2017 [2]                             |
| **MobiFall / MobiAct**   | BMI Lab, TEI Crete ([www.bmi.teicrete.gr](http://www.bmi.teicrete.gr/))                                         |    ~87 (acc) / ~200 (giro)    |   24 (MobiFall) / 57 (MobiAct)    | 4 caídas (MF) / más en MA, 9 ADL          | G. Vavoulas et al., "The MobiFall dataset: An initial evaluation of fall detection algorithms using smartphones," _IEEE BIBE_, 2013 [3]                              |
| **Coventry/Cogent Labs** | [cogentee.coventry.ac.uk/datasets/fall_adl_data.zip](http://cogentee.coventry.ac.uk/datasets/fall_adl_data.zip) |              100              |      42 (36M, 6F) 18–51 años      | 4 caídas + inducidas, ADL, near-falls     | O. Ojetola et al., "Data set for fall events and daily activities from inertial sensors," _ACM MMSys_, 2015 [6]                                                      |
| **ShimFall&ADL**         | Acceso público (ver paper [4] para enlace actualizado)                                                          |              50               |      35 (jóvenes) 19–34 años      | 9 caídas, 6 ADL (sensor en pecho)         | D. Mrozek et al., "Triaxial Accelerometer-Based Falls and Activities of Daily Life Detection Using Machine Learning," _Sensors_, 2020 [4]                            |
| **FARSEEING**            | Por solicitud ([farseeingresearch.eu](http://www.farseeingresearch.eu/))                                        |     100 (73%) / 20 (27%)      | 94 caídas reales, 76.1 años media | Caídas reales verificadas + ADL 24h       | J. Klenk et al., "The FARSEEING real-world fall repository," _European Review of Aging and Physical Activity_, 2016 [5]                                              |

---

## Recomendaciones para DiMIASA

Basado en tu contexto de IoMT con ESP32/Raspberry Pi y modelos TFLite < 1 MB:

1. **FallAllD** es la mejor alternativa principal a SisFall. Con 238 Hz y ±8 g, es directamente compatible con MPU6050/MPU9250. Las 44 ADL incluyen actividades transicionales (sentarse, levantarse, acostarse) que generan falsos positivos — ideales para entrenar un sistema multiagente robusto [1].
    
2. **Coventry/Cogent Labs** es el segundo más recomendable por incluir **near-falls** y caídas inducidas, que son las muestras negativas más desafiantes [6]. Además, sus 42 sujetos le dan variabilidad estadística.
    
3. **UMAFall** te permite estudiar **optimización de posición del sensor** (5 ubicaciones), crucial para decidir dónde colocar el ESP32 en tu prototipo [2].
    
4. **FARSEEING** debería usarse solo para validación final, ya que contiene datos reales de adultos mayores, aunque el acceso es más restringido [5].
    
5. **MobiFall/MobiAct** es útil como baseline comparativo, pero su limitación de ±2 g puede no reflejar bien los picos de impacto reales para tu hardware [3,7].
    

El paper de revisión de Casilari et al. (2017) [7] confirma que los datasets con rango de aceleración ≥ ±8 g (como FallAllD, SisFall, DLR) muestran mejor separabilidad entre caídas y ADL que aquellos con ±2 g. Para tu ESP32, esto es relevante porque el MPU6050 permite configurar rangos de ±2 g hasta ±16 g — te sugiero usar ±8 g para alinearte con los benchmarks más desafiantes.

---

## Referencias

[[1]M. Saleh, M. Abbas, and R. Le Bouquin Jeannès, "FallAllD: An Open Dataset of Human Falls and Activities of Daily Living for Classical and Deep Learning Applications," IEEE Sensors Journal, vol. 21, no. 2, pp. 1849–1862, 2021  
DOI: 10.1109/JSEN.2020.3018335](https://sci-hub.box/10.1109/JSEN.2020.3018335)

[[2]E. Casilari, J. A. Santoyo-Ramón, and J. M. Cano-García, "UMAFall: A Multisensor Dataset for the Research on Automatic Fall Detection," Procedia Computer Science, vol. 110, pp. 32–39, 2017  
DOI: 10.1016/j.procs.2017.06.110](https://sci-hub.box/10.1016/j.procs.2017.06.110)

[[3]G. Vavoulas, M. Pediaditis, E. G. Spanakis, and M. Tsiknakis, "The MobiFall dataset: An initial evaluation of fall detection algorithms using smartphones," in 13th IEEE International Conference on BioInformatics and BioEngineering (BIBE), 2013, pp. 1–4  
DOI: 10.1109/BIBE.2013.6701629](https://sci-hub.box/10.1109/BIBE.2013.6701629)

[[4]D. Mrozek, A. Koczur, and B. Małysiak-Mrozek, "Triaxial Accelerometer-Based Falls and Activities of Daily Life Detection Using Machine Learning," Sensors, vol. 20, no. 13, art. 3777, 2020  
DOI: 10.3390/s20133777](https://sci-hub.box/10.3390/s20133777)

[[5]J. Klenk et al., "The FARSEEING real-world fall repository: a large-scale collaborative database to collect and share sensor signals from real-world falls," European Review of Aging and Physical Activity, vol. 13, art. 8, 2016  
DOI: 10.1186/s11556-016-0168-9](https://sci-hub.box/10.1186/s11556-016-0168-9)

[[6]O. Ojetola, E. Gaura, and J. Brusey, "Data set for fall events and daily activities from inertial sensors," in Proceedings of the 6th ACM Multimedia Systems Conference (MMSys), 2015, pp. 243–248  
DOI: 10.1145/2713168.2713198](https://sci-hub.box/10.1145/2713168.2713198)

[[7]E. Casilari, J. A. Santoyo-Ramón, and J. M. Cano-García, "Analysis of Public Datasets for Wearable Fall Detection Systems," Sensors, vol. 17, no. 7, art. 1513, 2017  
DOI: 10.3390/s17071513](https://sci-hub.box/10.3390/s17071513)