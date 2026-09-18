# Módulo C — Plan de Implementación (Preprocesamiento, EDA y Modelado PPG→SpO2)

> Réplica arquitectura Módulo A (`bronce/plata/oro` + `00/01` CPU+GPU). Target: **ventana PPG 8 s → SpO2% medio**. Fs común **125 Hz** (nativo BIDMC). Todo umbral citado; lo no probado como nota.

## 1. Estructura de datos y notebooks

```text
notebooks/data/
  bronce/ppg/   ← crudos inmutables (bidmc WFDB/CSV/MAT, ptt-ppg, openox-repo, vitaldb-.vital, uq-csv, capnobase, senssmarttech)
  plata/ppg/    ← SQI por ventana + cobertura SpO2 + mapeo canales (JSON/CSV)
  oro/ppg/      ← set_a.parquet (BIDMC) + set_b.parquet (combinado) a 125 Hz
  modelos/ppg/  ← set_{a,b}_final(.keras, _scaler.joblib, comparison_results.json) + variantes _gpu
notebooks/fase_1/
  00_Preprocesamiento-PPG.ipynb
  01_Entrenamiento-SpO2.ipynb        (CPU, subsampleo)
  01-Entrenamiento-SpO2-GPU.ipynb    (GPU, completo)
```

Esquema oro (una fila = una muestra a 125 Hz):

```text
Dataset, Subject, Sample_Index, PPG, PPG_R, PPG_IR, Dual_Flag, SpO2_Ref, HR_Ref, RR_Ref, SQI
# PPG monocanal (BIDMC/VitalDB/UQ/Capno) o PPG_R/PPG_IR duales (PTT/SensSmartTech/OpenOx); Dual_Flag 0/1; SpO2_Ref interpolado 1 Hz→125 Hz; SQI ∈ {ok, low-perfusion, motion, dropout}
```

## 2. Preprocesamiento (`00_Preprocesamiento-PPG.ipynb`)

1. **Ingesta** — `wfdb` (BIDMC/PTT/SensSmartTech) + CSV (BIDMC/UQ/OpenOx) + MAT (`bidmc_data.mat`) + Vital Recorder export `.vital`→CSV/EDF (VitalDB). Respaldos: Xie 2023 (WFDB), Lee-Jung 2018 (Vital Recorder).
2. **Auditoría fisiológica** — NaN, flatline, perfusión baja (AC/DC), rangos SpO2 70-100 / HR 30-220 / RR 4-60; reporta cobertura SpO2 por dataset (evidencia sesgo normoxia BIDMC 95-100%).
3. **Sincronía** — alinea PPG 125 Hz con numéricos 1 Hz (SpO2/HR/RR); exige cobertura SpO2 ≥90% por ventana o se excluye; OpenOximetry SaO2 arterial solo como calibración/evaluación (sujeto a DUA; PPG crudo 86 Hz no sincronizado; ChatGPT-C).
4. **Métricas fidelidad/SQI por ventana 8 s** — Pearson pre/post resample, SNR banda 0.5-8 Hz (pulso), skewness/kurtosis, tasa dropout, flag motion (ACC donde exista: PTT/SensSmartTech). Persiste `ppg_quality_per_window_125hz.csv` (análogo a `resampling_metrics` de A).
5. **Filtrado calidad** — descarta ventana si SQI motion/dropout o cobertura SpO2 insuficiente; política OR≥2 análoga a A. No inventa umbrales nuevos: usa percentiles EDA + reglas pyPPG/NeuroKit2 (Goda 2024; Makowski 2021).
6. **Resampleo** — `resample_poly` Kaiser β=5 a 125 Hz (PTT 500 Hz, VitalDB 500 Hz, CapnoBase 300 Hz, SensSmartTech 100→125 Hz); pasa-banda PPG 0.5-8 Hz preservando muesca dicrota (GEMINI-C: 100 Hz suficiente, 125 Hz unifica).
7. **Exportación** — `set_a.parquet` (BIDMC) + `set_b.parquet` (combinado con columna Dataset/Dual_Flag).

## 3. EDA obligatoria

Histograma SpO2 por dataset (demuestra colapso normoxia vs mesetas OpenOx 70-100%); HR/RR; morfología (muesca dicrota vs fs); tasa SQI por contexto (UCI inmóvil vs ejercicio vs quirófano); dispersión AC/DC y ratio R=`(ACr/DCr)/(ACir/DCir)` donde hay dual (física MAX30102, GEMINI-C) solo descriptiva.

## 4. Ventaneo y modelado (`01_Entrenamiento*.ipynb`)

- **Ventana 8 s (1.000 muestras @125 Hz), paso 4 s (solape 50%).** Target = media SpO2 ventana. Justificación: estándar MIMIC/VitalDB (Sci-Bot-C), ~8-12 pulsos, 4 KB/canal float32 (8 KB dual) apto SRAM.
- **Split sujeto-wise** — `GroupKFold(K=5)` sobre Subject (estratifica por bin hipoxia <90/90-95/>95); scaler solo train; CapnoBase reservado a validación de FR (no entrenar: la fuente lo prohíbe), OpenOx-hypoxia como hold-out de calibración solo si se aprueba el DUA.
- **Modelo TCN/1D-CNN** (<1 MB): convoluciones dilatadas causales `RF=1+Σ(k-1)·2^l` o depthwise-separable (ahorro >60% con 2 canales, k=5, GEMINI-C); entrada 1-2 canales ×1000; salida lineal SpO2; loss MSE, monitor MAE; `class`-balance por sobremuestreo ventanas <90%.
- **Variantes:** CPU = subsampleo acotado por bin, ~12 épocas; GPU = completo, 40 épocas, batch 512, patience 10, `mixed_float16` (igual que A).
- **Métricas:** MAE/RMSE global + MAE banda <90% (prioridad hipoxemia) + Bland-Altman + Pearson pred-vs-ref; reporta por dataset y dual/monocanal. Referencia de tamaño factible (modelo de FC, no SpO2): CNN 26k params ~32 KB int8 (Reiss 2019 PPG-DaLiA).
- **Salidas:** `set_{a,b}_final(.keras/_scaler.joblib/comparison_results.json)` + `_gpu`. Conversión LiteRT FASE 2 con QAT calibrado en desaturaciones (GEMINI-C) para no distorsionar AC/DC.

## 5. Criterios de aceptación

Pipeline corre con solo `bronce/ppg/bidmc` (set_a); set_b reproduce roles Plan_Investigacion; sin fuga por sujeto; curva pred-vs-ref y Bland-Altman persistidos.

> [!NOTE] Posibles mejoras (no probadas, fuera del trabajo hasta decisión):
> - Cohorte propia MAX30102 con apneas/ejercicio y regla ≥3% en 10-90 s (Jung 2018 define caída ≥3% y ventana 10-90 s; es detección de eventos, no calibración R→SpO2) para calibrar R→SpO2.
> - Multitarea PPG→{HR,RR,SpO2,BP} con encoder compartido (VitalDB).
> - Rama FR 30 s en RPi con CapnoBase + VFC/estrés (WESAD sin SpO2).
> - Dual-only train (PTT+SensSmartTech+OpenOx) vs monocanal para cuantificar aporte Rojo/IR.
