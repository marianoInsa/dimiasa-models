# Módulo C — Plan de Implementación C1 (Preprocesamiento PPG, FC y calidad)

> **Estado:** ejecutado 18-sep-2026 (commit `5ee0d6b`). Alcance **C1 = pipeline PPG + validación de FC/calidad sobre BIDMC**, sin modelo SpO2 (C2 bloqueado: BIDMC no tiene Rojo/IR ni ground truth independiente). Réplica la arquitectura Módulo A (`bronce/plata/oro`). Fs **125 Hz** nativa (sin resampleo). Resultados: 6 307 ventanas (5 895 `ok` / 412 `low-quality`), FC global MAE 2.2344 bpm / RMSE 5.4574 / Pearson 0.9186 / sesgo −1.0639 bpm; pipeline y resultados completos en [preprocesamiento-ppg](../04_PIPELINE/preprocesamiento-ppg.md). Todo umbral citado; lo no probado va como nota o decisión propia explícita.

## 1. Estructura de datos y notebooks

```text
notebooks/fase_1/modulo_c_ppg/
  00_Preprocesamiento-PPG.ipynb   ← único notebook de C1

notebooks/data/
  bronce/ppg/   ← BIDMC-Reduced.csv (53 rec / 46 sujetos / 3 180 053 filas) + crudos futuros (ptt-ppg, openox-repo, vitaldb, uq, capnobase, senssmarttech)
  plata/ppg/    ← bidmc_audit.json + ppg_quality_config.json + ppg_quality_per_window_125hz.csv (SQI+FC) + hr_validation_summary.json + fig_*.png
  oro/ppg/      ← set_a.parquet (BIDMC) a 125 Hz
```

`modelos/ppg/` no se usa en C1 (no hay modelo). El bronce BIDMC se lee del CSV reducido; el crudo WFDB/MAT no se usa (reducción y decisiones D1–D10 en [Elegidos/BIDMC](../03_DATASETS/Elegidos/BIDMC.md)).

Esquema oro (una fila = una muestra a 125 Hz):

```text
Dataset, Subject, Record, Sample_Index, PPG, PPG_Raw, SpO2_Ref, HR_Ref, RR_Ref
# PPG = PLETH filtrada 0.5-8 Hz (entrada de modelo futura); PPG_Raw = PLETH cruda (auditoría/morfología);
# SpO2_Ref/HR_Ref/RR_Ref = numéricos 1 Hz en step-hold (D5/D10); HR_Ref usa HR (FC del monitor), no PULSE.
# Sin PPG_R/PPG_IR/Dual_Flag: BIDMC es PLETH monocanal procesado por monitor (Pimentel et al., 2017).
```

## 2. Notebook C1 (`00_Preprocesamiento-PPG.ipynb`)

| # | Celda | Contenido |
|---|-------|-----------|
| 1 | MD cabecera | Alcance C1, límites de BIDMC, citas (Pimentel 2017; Makowski 2021; Elgendi 2013), enlaces a `BIDMC.md` y a este plan |
| 2 | Config | Paths `../../data/{bronce,plata,oro}/ppg`; `FS=125`, `WINDOW_S=8`, `STEP_S=4`, `BANDPASS=(0.5, 8)` Hz (banda de `nk.ppg_clean` y de la SNR), rangos de auditoría SpO2 70-100 / HR 30-220 / RR 4-60, `SEED=42` |
| 3 | Ingesta | CSV reducido; asserts de esquema y conteos (53 records / 46 sujetos / 3 180 053 filas); PLETH a float32 por registro |
| 4 | Auditoría física | NaN (D10 ⇒ 0), flatline, valores fuera de rango, AC/DC de perfusión por registro, cobertura de numéricos → `plata/ppg/bidmc_audit.json` |
| 5 | Filtrado | `nk.ppg_clean(method="elgendi")` por registro (Butterworth 2.º, pasa-banda 0.5-8 Hz, fase cero `sosfiltfilt`; Elgendi 2013); se conservan crudo (`PPG_Raw`) y filtrado (`PPG`) |
| 6 | Ventaneo | 8 s (1 000 muestras), paso 4 s (500), por registro |
| 7 | SQI por ventana | NeuroKit2 `ppg_peaks(method="elgendi")` + `ppg_quality(method="templatematch")` por pulso (vector por muestra en NK2 0.2.13 ⇒ `q[peaks]`); propias: SNR Welch 0.5-8 Hz, skewness/kurtosis, AC/DC; `Quality_Flag`: flags duros (`N_Peaks<2`, dropout, flatline) fuerzan `low-quality`; si no, OR≥2 entre los 3 criterios por percentil P10 |
| 8 | Validación FC | `HR_Ref` = media de HR en ventana vs FC estimada por picos; MAE/RMSE, Pearson, Bland-Altman por registro y global → `plata/ppg/hr_validation_summary.json` + figuras (las métricas por ventana van al CSV único de la celda 10) |
| 9 | EDA | Histograma SpO2 (colapso normoxia 83-100), HR/RR, morfología media (muesca dicrota), tasas SQI/flags, AC/DC |
| 10 | Export | `oro/ppg/set_a.parquet` + `plata/ppg/ppg_quality_per_window_125hz.csv`; asserts de conteos y no-NaN |
| 11 | MD cierre | Resultados, limitaciones y estado C2 |

**Decisiones de la celda 5.** Se reemplaza el filtro propio del borrador (Butterworth orden 4) por `nk.ppg_clean(method="elgendi")`, refinamiento aprobado antes de implementar: banda 0.5-8 Hz y Butterworth de 2.º orden con fase cero (`sosfiltfilt`) tal como lo entrega NeuroKit2 0.2.13, que es la banda que Elgendi et al. (2013) reporta como óptima para detección de picos sistólicos. El doble pasaje equivale en magnitud a un orden 4 sin distorsión de fase.

**Decisiones de la celda 6.** Ventana 8 s / paso 4 s es decisión propia: a FC 60-90 bpm cubre ~8-12 pulsos, 1 000 muestras float32 = 4 KB/canal (apto SRAM objetivo), y el solape 50 % replica el criterio del Módulo A. BIDMC (480 s/registro) ⇒ 119 ventanas/registro, 6 307 en total. La cobertura SpO2 ≥90 % por ventana no aplica a BIDMC: los numéricos vienen en step-hold con faltantes imputados en la reducción (D5/D10), por lo que la cobertura es 100 % por construcción; el gate queda documentado para los datasets de `set_b` (C2).

**Decisiones de la celda 7.** Detección de picos: método Elgendi (Elgendi et al., 2013) vía NeuroKit2 (Makowski et al., 2021). SQI: `templatematch` de NeuroKit2 (Makowski et al., 2021) más SNR en banda de pulso, skewness/kurtosis y perfusión AC/DC, consistentes con las revisiones de calidad PPG (Desquins et al., 2022; Argüello-Prada & Castillo García, 2024; Charlton et al., 2023). En NK2 0.2.13 `ppg_quality` devuelve un vector por muestra (interpola la correlación por pulso con step-hold): el SQI por pulso se recupera con `q[peaks]` y el de la ventana es la media de los pulsos cuyo pico cae en ella. `Quality_Flag`: umbrales P10 de SQI, SNR y AC/DC persistidos en `ppg_quality_config.json`; flags duros (`N_Peaks<2`, dropout, flatline) fuerzan `low-quality`; si no, OR≥2 entre los tres criterios por percentil (análogo al Módulo A, sin valores fijos inventados). `motion` no se calcula: BIDMC no trae ACC (limitación registrada en `BIDMC.md`).

**Decisiones de la celda 8.** Concordancia con Bland-Altman (Bland & Altman, 1986). No se fija umbral binario de aprobación: se persisten MAE/RMSE, Pearson, sesgo y límites de concordancia, y la distribución del error. `HR` (no `PULSE`) es la referencia del monitor.

> [!IMPORTANT] pyPPG bloqueado en C1 (evidencia reproducida 18-sep-2026)
> `pyPPG 1.0.14` — única versión resoluble con el stack actual — falla en NumPy 2 (`np.NaN` eliminado) y además no declara `dotmap`; las versiones ≥1.0.15 fijan `numpy==1.23.2`, `scipy==1.9.1` y `pandas==1.4.4`, incompatibles con el proyecto. Falla `FpCollection.get_fiducials` (`fiducials.py:152`) y `get_ppgSQI`. Decisión: C1 usa NeuroKit2 para picos/FC/SQI y se documenta el bloqueo; no se degrada el stack numérico validado de FASE 2 (TF 2.18 / LiteRT 2.2). Reintento en C2 con entorno `numpy<2` o versión futura de pyPPG (Goda et al., 2024).

## 3. Criterios de aceptación

1. El notebook corre con solo `bronce/ppg/BIDMC-Reduced.csv` (sin WFDB ni crudos).
2. Conteos verificados: 53 records / 46 sujetos / 3 180 053 filas; 6 307 ventanas (5 895 `ok` / 412 `low-quality`); 0 NaN en oro.
3. FC validada con MAE/RMSE/Pearson/Bland-Altman persistidos y figuras; SQI por ventana persistido.
4. Sin fuga: `Subject` y `Record` preservados (no hay modelo; el split sujeto-wise queda para C2).
5. Reproducible: semilla fija y sin pasos manuales.

Verificación 18-sep-2026 (commit `5ee0d6b`): los cinco criterios se cumplen; evidencia en [preprocesamiento-ppg](../04_PIPELINE/preprocesamiento-ppg.md).

## 4. C2 — bloqueado

El target `PPG cruda → SpO2%` exige canales Rojo/IR y ground truth independiente (SaO2 de co-oximetría); BIDMC solo aporta PLETH monocanal y SpO2 del monitor, con sesgo de normoxia (Sjoding et al., 2020; Cabanas et al., 2024). Opciones de desbloqueo: OpenOximetry (requiere DUA; Fong et al., 2025) o cohorte propia con MAX30102. Cuando se desbloquee: ventana 8 s, split sujeto-wise, TCN/1D-CNN <1 MB y QAT calibrado en desaturaciones. Mejoras no probadas (dual-only, multitarea HR/RR/SpO2/BP, rama FR) quedan en [Plan_Investigacion_Módulo_C](Plan_Investigacion_Módulo_C.md).

## 5. Referencias

- Argüello-Prada, E. J., & Castillo García, J. F. (2024). Machine learning applied to reference signal-less detection of motion artifacts in photoplethysmographic signals: A review. *Sensors, 24*(22), Article 7193. https://doi.org/10.3390/s24227193
- Bland, J. M., & Altman, D. G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement. *The Lancet, 327*(8476), 307–310. https://doi.org/10.1016/S0140-6736(86)90837-8
- Cabanas, A. M., Valderrama Sáez, N. M., Collao-Caiconte, P. O., Martín-Escudero, P., Pagán, J., Jiménez-Herranz, E., & Ayala, J. L. (2024). Evaluating AI methods for pulse oximetry: Performance, clinical accuracy, and comprehensive bias analysis. *Bioengineering, 11*(11), Article 1061. https://doi.org/10.3390/bioengineering11111061
- Charlton, P. H., et al. (2023). The 2023 wearable photoplethysmography roadmap. *Physiological Measurement, 44*(11), Article 111001. https://doi.org/10.1088/1361-6579/acead2
- Desquins, T., Bousefsaf, F., Pruski, A., & Maaoui, C. (2022). A survey of photoplethysmography and imaging photoplethysmography quality assessment methods. *Applied Sciences, 12*(19), Article 9582. https://doi.org/10.3390/app12199582
- Elgendi, M., Norton, I., Brearley, M., Abbott, D., & Schuurmans, D. (2013). Systolic peak detection in acceleration photoplethysmograms measured from emergency responders in tropical conditions. *PLoS ONE, 8*(10), Article e76585. https://doi.org/10.1371/journal.pone.0076585
- Fong, N., et al. (2025). Open access dataset and common data model for pulse oximeter performance data. *Scientific Data, 12*, Article 570. https://doi.org/10.1038/s41597-025-04870-8
- Goda, M. Á., Charlton, P. H., & Behar, J. A. (2024). pyPPG: A Python toolbox for comprehensive photoplethysmography signal analysis. *Physiological Measurement, 45*(4), Article 045001. https://doi.org/10.1088/1361-6579/ad33a2
- Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lespinasse, F., Pham, H., Schölzel, C., & Chen, S. A. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. *Behavior Research Methods, 53*(4), 1689–1696. https://doi.org/10.3758/s13428-020-01516-y
- Pimentel, M. A. F., Johnson, A. E. W., Charlton, P. H., Birrenkott, D., Watkinson, P. J., Tarassenko, L., & Clifton, D. A. (2017). Toward a robust estimation of respiratory rate from pulse oximeters. *IEEE Transactions on Biomedical Engineering, 64*(8), 1914–1923. https://doi.org/10.1109/TBME.2016.2613124
- Sjoding, M. W., Dickson, R. P., Iwashyna, T. J., Gay, S. E., & Valley, T. S. (2020). Racial bias in pulse oximetry measurement. *New England Journal of Medicine, 383*(25), 2477–2478. https://doi.org/10.1056/NEJMc2029240
