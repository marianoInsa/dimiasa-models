# Fundamentación Científica del Pipeline de Preprocesamiento

Justificación bibliográfica de las decisiones, métricas y umbrales del pipeline de detección de caídas en adultos mayores (`notebooks/pipeline/00_Preprocesamiento.ipynb`).

**Estado de verificación:** cada cita fue validada contra registros Crossref/DOI (agosto 2026). Los detalles atribuidos que no pudieron confirmarse en el texto original se marcan explícitamente.

---

## 1. Bibliografía verificada

| #    | Cita                                                                                                                                                                                                                                  | DOI                          |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| [1]  | Tsinganos, P., & Skodras, A. (2018). On the Comparison of Wearable Sensor Data Fusion to a Single Sensor Machine Learning Technique in Fall Detection. _Sensors_, 18(2), 592.                                                         | 10.3390/s18020592            |
| [2]  | Sucerquia, A., López, J. D., & Vargas-Bonilla, J. F. (2017). SisFall: A Fall and Movement Dataset. _Sensors_, 17(1), 198.                                                                                                             | 10.3390/s17010198            |
| [3]  | Yu, X., Jang, J., & Xiong, S. (2021). A Large-Scale Open Motion Dataset (KFall) and Benchmark Algorithms for Detecting Pre-impact Fall of the Elderly Using Wearable Inertial Sensors. _Frontiers in Aging Neuroscience_, 13, 692865. | 10.3389/fnagi.2021.692865    |
| [4]  | Chen, H., Schall, M. C., & Fethke, N. B. (2023). Gyroscope vector magnitude: A proposed method for measuring angular velocities. _Applied Ergonomics_, 109, 103981. _(Preprint: medRxiv 2022.10.05.22280752)_                         | 10.1016/j.apergo.2023.103981 |
| [5]  | Guo, P., & Nakayama, M. (2025). A Feature Engineering Method for Smartphone-Based Fall Detection. _Sensors_, 25(20), 6500.                                                                                                            | 10.3390/s25206500            |
| [6]  | Casilari, E., et al. (2022). A Cross-dataset Evaluation of Wearable Fall Detection Systems. _Proc. 15th Int. Conf. PETRA (PETRA '22)_.                                                                                                | 10.1145/3529190.3529191      |
| [7]  | Tseng, et al. (2025). Wearable Fall Detection System with Real-Time Localization and Notification Capabilities. _Sensors_, 25(12), 3632.                                                                                              | 10.3390/s25123632            |
| [8]  | Lai, et al. (2016). A Knowledge-Based Step Length Estimation Method Based on Fuzzy Logic and Multi-Sensor Fusion Algorithms for a Pedestrian Dead Reckoning System. _ISPRS Int. J. Geo-Inf._, 5(5), 70.                               | 10.3390/ijgi5050070          |
| [9]  | (2026). Efficient Fall Detection from Wrist-Worn IMU Signals via Knowledge Distillation. _Sensors_, 26(11), 3328.                                                                                                                     | 10.3390/s26113328            |
| [10] | (2022). Wearable Sensor Systems for Fall Risk Assessment: A Review. _Frontiers in Digital Health_, 4, 921506.                                                                                                                         | 10.3389/fdgth.2022.921506    |
| [11] | (2015). Adaptive Data Filtering of Inertial Sensors with Variable Bandwidth. _Sensors_, 15(2), 3282.                                                                                                                                  | 10.3390/s150203282           |
| [12] | (2015). Selecting the optimal anti-aliasing filter for multichannel biosignal acquisition intended for inter-signal phase shift analysis. _Physiological Measurement_, 36(1), N23.                                                    | 10.1088/0967-3334/36/1/N23   |

---

## 2. Fundamentación por elemento del pipeline

### 2.1 Proceso general

| Elemento                                                          | Respaldo      | Tipo        | Nota                                                                                                                                                                                                                                           |
| ----------------------------------------------------------------- | ------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frecuencia única de 50 Hz                                         | [1]           | **Directo** | Espectro útil del movimiento humano 0–20 Hz → Nyquist ≥ 40 Hz; 50 Hz como compromiso entre fidelidad y consumo. Texto exacto en [1].                                                                                                           |
| Resampleo con `resample_poly` (polifase FIR) + ventana Kaiser β=5 | [11]          | Análogo     | [11] usa filtro pasa-bajos con ventana Kaiser en IMU para controlar transición y lóbulos laterales. La ventana Kaiser como diseño FIR anti-aliasing es práctica estándar (ver `kaiserord` en SciPy). Implementación concreta: decisión propia. |
| Derivar AVM (magnitud del vector de aceleración)                  | [2], [1]      | **Directo** | AVM/SMV es la señal estándar de detección de caídas; invariante a la orientación del sensor.                                                                                                                                                   |
| Derivar GVM (magnitud del vector de giroscopio)                   | [4]           | Análogo     | [4] propone GVM como medida de velocidad angular 3D completa. ⚠️ Contexto: ergonomía ocupacional (brazo), no detección de caídas. Extensión a caídas: decisión propia.                                                                         |
| Población objetivo: adultos mayores                               | [2], [3], [5] | **Directo** | SisFall incluye 14 adultos mayores (>62 años); FARSEEING registra caídas reales de sujetos de 56–86 años [5].                                                                                                                                  |

### 2.2 Métricas de fidelidad del resampleo (por trial, AVM y GVM)

| Elemento                                                           | Respaldo  | Tipo        | Nota                                                                                                                                                                                                                          |
| ------------------------------------------------------------------ | --------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SNR en banda [0, 25] Hz                                            | —         | **Propio**  | Sin respaldo directo como control de resampleo en literatura de caídas. Métrica DSP estándar aplicada como QC propio.                                                                                                         |
| Correlación de Pearson `r` entre original y resampleada            | [1]       | Análogo     | La correlación se usa como característica y en comparación de patrones de señales. Como validación de resampleo: decisión propia.                                                                                             |
| Desfase de pico (ms)                                               | [12]      | Análogo     | [12] cuantifica que los filtros anti-aliasing introducen retardos de 2–46 ms comparables al desfase entre señales; recomienda filtrado idéntico para no sesgar el análisis de fase. Respalda la pertinencia de medir desfase. |
| Atenuación de pico (%)                                             | [6]       | Análogo     | [6] advierte que normalizaciones/filtrados suavizan los picos de impacto de caídas y degradan la detección. Como umbral de QC: decisión propia.                                                                               |
| Estadísticos descriptivos pre/post (media, std, mediana, P05, P95) | [3], [10] | Análogo     | Media, desviación y percentiles son características estándar sobre ventanas. Como verificación de conservación de distribución: decisión propia.                                                                              |
| Ventana de evaluación ±1 s alrededor del pico                      | [1]       | **Directo** | El algoritmo descrito en [1] (basado en Figuereido et al.) extrae características en `(tSV − 1, tSV + 1)` s centrado en el pico de la magnitud de aceleración.                                                                |

### 2.3 Umbrales de filtrado de calidad (política OR ≥ 2)

| Elemento                                                              | Respaldo | Tipo       | Nota                                                                                                                                        |
| --------------------------------------------------------------------- | -------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Pearson `r ≥ 0.85`                                                    | —        | **Propio** | Sin análogo directo. Heurística de control de calidad.                                                                                      |
| Desfase de pico `≤ 100 ms`                                            | [12]     | Análogo    | Orden de magnitud coherente con retardos de filtrado anti-aliasing (2–46 ms) [12]; el umbral lo absorbe con margen. Valor concreto: propio. |
| Atenuación de pico `≤ 25 %`                                           | —        | **Propio** | Sin análogo directo.                                                                                                                        |
| Política OR ≥ 2 (falla en AVM _o_ GVM; descarte con ≥2 de 3 métricas) | —        | **Propio** | Regla de decisión multivariable propia.                                                                                                     |

### 2.4 Auditoría de calidad de datos crudos

| Elemento                                                | Respaldo      | Tipo        | Nota                                                                                                                                                                                       |
| ------------------------------------------------------- | ------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Mediana de AVM ≈ 1 g (aceptable 0.75–1.35 g)            | [2], [7], [8] | Análogo     | La gravedad (1 g) es el valor de referencia estático del acelerómetro, invariante a rotación [8]; SisFall y sistemas reales reportan AVM ≈ 1 g en reposo [2], [7]. Rango concreto: propio. |
| Detección de canales muertos (std = 0)                  | —             | **Propio**  | Sin respaldo textual; la limpieza de canales inservibles en datasets de caídas es protocolo estándar. Regla `std = 0`: propia.                                                             |
| Detección de saturación (≥ 0.99 del full-scale)         | [3]           | Análogo     | [3] confirma full-scales altos (±16 G, ±2000 °/s) para evitar recorte de picos en impactos de alta dinámica. El umbral de 0.99: propio.                                                    |
| Full-scales por dataset (acc 8/16 g, giro 256/2000 °/s) | [3], [2]      | **Directo** | KFall: LPMS-B2 con acelerómetro ±16 G y giroscopio ±2000 °/s, configurado a 100 Hz [3]. SisFall emplea múltiples acelerómetros de alto rango [2].                                          |

---

## 3. Decisiones propias sin respaldo directo

Estos elementos son contribuciones metodológicas del pipeline y deben defenderse como tales en la investigación (control de calidad del resampleo, no prescrito por la literatura):

- **Métricas de fidelidad** como control de resampleo: SNR in-band, Pearson pre/post, desfase de pico, atenuación de pico, estadísticos pre/post.
- **Umbrales** r ≥ 0.85, desfase ≤ 100 ms, atenuación ≤ 25 %.
- **Política de descarte** OR ≥ 2 sobre AVM/GVM.
- **Reglas de auditoría** de unidades (rango 0.75–1.35 g), canales muertos (std = 0) y saturación (fracción ≥ 0.99).
- **GVM en detección de caídas** (la referencia [4] es de ergonomía ocupacional).

---
