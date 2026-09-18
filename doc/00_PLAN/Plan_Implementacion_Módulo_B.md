# Módulo B — Plan de Implementación (Preprocesamiento, EDA y Modelado ECG)

> Réplica la arquitectura Módulo A (`bronce/plata/oro` + `00_Preprocesamiento / 01_Entrenamiento CPU+GPU`). Fs común **125 Hz**. Filtro **0.5-40 Hz** (FASE 1). Todo umbral con respaldo citado; lo no probado va como nota.

## 1. Estructura de datos y notebooks

```text
notebooks/data/
  bronce/ecg/   ← WFDB crudos inmutables (mitdb, challenge-2017, icentia-subset, cpsc2021, shdb-af, ptb-xl-leadI, butqdb-aux)
  plata/ecg/    ← métricas calidad por registro + mapeo etiquetas + lista IDs subset (JSON/CSV)
  oro/ecg/      ← set_a.parquet (MITDB) + set_b.parquet (combinado) a 125 Hz
  modelos/ecg/  ← set_{a,b}_final(.keras, _scaler.joblib, comparison_results.json) + variantes _gpu
notebooks/fase_1/
  00_Preprocesamiento-ECG.ipynb
  01_Entrenamiento-ECG.ipynb        (CPU, subsampleo acotado)
  01-Entrenamiento-ECG-GPU.ipynb    (GPU, dataset completo)
```

Esquema oro (14→8 columnas, análogo a las 14 de caídas):

```text
Dataset, Subject, Record, Sample_Index, ECG, AAMI_Orig, Label3, Quality_Flag
# ECG en mV filtrado 0.5-40 Hz a 125 Hz; Label3 ∈ {Normal, Anormal, No-clasificable}; Quality_Flag ∈ {ok, noisy, lead-off}
```

## 2. Preprocesamiento (`00_Preprocesamiento-ECG.ipynb`)

1. **Ingesta** — lee WFDB con `wfdb` desde `bronce/ecg`. Un canal por registro según §3 Plan_Investigacion (MITDB MLII, Icentia Lead I mod., CinC17 single, CPSC Lead I/II, SHDB CC5, PTB-XL Lead I, BUT single).
2. **Auditoría física** — NaN, flatline (>2 s varianza ~0), saturación (>±5 mV sostenido), ganancia/unidades mV. Reporta tasa por dataset.
3. **Filtro pasa-banda 0.5-40 Hz** — Butterworth orden 4 zero-phase (`sosfiltfilt`). Respaldo: FASE 1 + estándar QRS (elimina deriva <0.5 Hz y EMG/red >40 Hz) sin distorsionar ST-T para clasificación rítmica.
4. **Validación y mapeo de etiquetas** — tabla versionada en `plata/ecg/label_map.json`: AAMI N→Normal; VEB/SVEB/F (PVC/PAC/AF/flutter/AT/TSV/MI/STTC/CD/HYP)→Anormal; CinC17 Too Noisy / BUT calidad 3 / lead-off→No-clasificable. Rechaza registros con mezcla incoherente ventana (audita % por dataset como A hacía con Fall/ADL).
5. **Métricas de fidelidad por registro** (sobre QRS, análogo a AVM/GVM en caídas) — compara original vs resampleado a 125 Hz: SNR banda útil (dB), Pearson r, desfase pico R (ms), atenuación pico R (%), stats pre/post. Persiste `resampling_metrics_per_record_125hz.csv`.
6. **Filtrado de calidad** — descarta registro/ventana si: Pearson r<0.85, desfase R>100 ms, atenuación>25%, política **OR≥2** (igual que A) o demasiado corto. Umbrales heredados de Módulo A para coherencia metodológica; EDA valida si QRS exige desfase más estricto en iteración futura.
7. **Resampleo definitivo** — `resample_poly` Kaiser β=5 a 125 Hz (igual que A). Orden: anti-alias → resample → bandpass final.
8. **Exportación** — `set_a.parquet` (MITDB) + `set_b.parquet` (combinado con columna Dataset para splits y validación externa SHDB-AF).

## 3. EDA obligatoria (sección del notebook)

Distribución Label3 por dataset/sujeto; HR y duración QRS; SNR y tasa No-clasificable; matriz de confusión de anotadores donde aplique (MITDB adjudicado vs Icentia tecnólogos); histogramas Pearson/desfase/atenuación para justificar umbrales §2.6; chequeo shift (MITDB 70s vs SHDB-AF 2019-23).

## 4. Ventaneo y modelado (`01_Entrenamiento*.ipynb`)

- **Ventana 10 s (1.250 muestras @125 Hz), solape 50% (5 s).** Justificación: preserva contexto AF/episodio como CinC17 (30 s) y PTB-XL (10 s) pero cabe en SRAM (~5 KB float32 monocanal, cálculo GEMINI-B); etiqueta ventana por ritmo mayoritario, Ruido si Quality_Flag.
- **Split sujeto-wise** — `StratifiedGroupKFold(K=5)` sobre `Dataset_Subject` + 10% val interna. `StandardScaler` solo en train (igual que A). SHDB-AF reservado como hold-out externo en set_b (no entra en folds).
- **Modelo 1D-CNN** (<1 MB): Conv1D con referencia `awni/ecg` Stanford (FASE 1); el BiLSTM es añadido propio (el repo original no lo incluye), variante depthwise-separable para ahorrar >60% MACs con 1 canal (GEMINI-B). Salida softmax 3 clases, `CategoricalCrossentropy`, `class_weight` (CPU fijo / GPU dinámico por fold), `EarlyStopping` + `ReduceLROnPlateau`.
- **Variantes:** CPU = subsampleo 15.000 ventanas/clase, 12 épocas (igual que A); GPU = completo, 40 épocas, batch 512, patience 10, `mixed_float16` si hay GPU (igual que A).
- **Métricas:** Sensibilidad/Especificidad/Precisión agregadas + matriz 3×3 + top confusiones Anormal; prioridad Sensibilidad (triaje). Reporta además accuracy en SHDB-AF externo.
- **Salidas:** `set_{a,b}_final(.keras/_scaler.joblib/comparison_results.json)` + variantes `_gpu`. Conversión LiteRT <1 MB queda para FASE 2 (PTQ/QAT int8 reduce ~4×, GEMINI-B).

## 5. Criterios de aceptación

Pipeline corre con solo `bronce/ecg/mitdb` (set_a); set_b reproduce roles Plan_Investigacion; sin fuga por sujeto (test de IDs); métricas y matrices persistidas.

> [!NOTE] Posibles mejoras (no probadas, fuera del trabajo hasta decisión):
> - Ventana dual 2 s beat-centered + 30 s ritmo en ensemble.
> - Desfase R ≤20 ms en vez de 100 ms (QRS ~80-120 ms) si EDA lo respalda.
> - Cascada SQA <50 KB previa al diagnóstico con BUT QDB + clase Ruido CinC17.
> - SSL/contrastivo en Icentia11k + fine-tuning (GEMINI-B) y CutMix1D con ruido real.
