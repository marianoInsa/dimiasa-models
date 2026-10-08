# Pipeline ECG oficial — PTB-XL Lead II 250 Hz + TinyECGNet Sequential

> Fuente de verdad: `notebooks/fase_1/modulo_b_ecg/00_M1_Creacion_Dataset_PTB-XL_Lead-II_250Hz.ipynb` (37 celdas) y `01_M2_Entrenamiento_TinyECGNet_Sequential_PTB-XL.ipynb` (47 celdas). Snapshots de Colab con Drive y GPU T4, TF 2.20.0.

## M1 — dataset

PTB-XL 1.0.3 → `wfdb.rdsamp(filename_hr)`, exige `fs == 500`, Lead II presente y 5000 muestras. `resample(signal_II, 2500)`, `float32`, sin normalizar ni filtrar. X `(20970, 2500)`, 0 NaN/Inf, 0 errores. HDF5 `X, y, ecg_id, patient_id, age, sex, strat_fold` + atributos (`sampling_frequency=250`, `original=500`, `lead=II`, `duration=10`, `normalization=None`, `filtering=None`). Particiones `strat_fold` 1–8/9/10 sin solape de pacientes. Tamaños: completo 195 833 857 B · TRAIN 156 108 739 B · VAL 19 558 533 B · TEST 19 717 052 B.

## M2 — señal, modelo y entrenamiento

Señal por bloques de 256: bandpass 0.5–40 Hz orden 4 + notch 50 Hz Q30, z-score por ECG. Forma `(N, 2500, 1)`. Augment de entrenamiento (ganancia 0.90–1.10, ruido 0.01, shift ±25), identidad en inferencia.

TinyECGNet Sequential: Conv1D 12×k15 s2 + BN/ReLU, SepConv 16×k15 + BN/ReLU + Pool2 + Dropout 0.10, SepConv 24×k15 + BN/ReLU + Pool2 + Dropout 0.15, SepConv 32×k15 + BN/ReLU + Pool3, GAP + Dropout 0.50 + Dense sigmoid. 2 673 parámetros en inferencia. Adam 2e-4, BCE `label_smoothing=0.02`, batch 64, máx 50 épocas (30 ejecutadas), checkpoint/early-stopping por `val_pr_auc`, seed 42.

## Conversión

FP32 20 976 B con paridad total (diff máx 1.788e-07). INT8 full-integer con 500 TRAIN: in scale 0.08170621 zp −18, out scale 0.00390625 zp −128, 18 584 B, 53 tensores / 34 ops, tensor-mem 282 898 B (estimación). FP32→INT8: 22 cambios (1.0412 %). Threshold 0.5 → INT8 0 → 0.5. Header C idéntico al TFLite.

## Resultados TEST (2113, umbral 0.5)

Keras: Acc 0.7894 · Prec 0.8853 · Sens 0.7243 · Espec 0.8757 · F1 0.7967 · ROC-AUC 0.882407 · PR-AUC 0.918584 · 796/113/332/872.
INT8: Acc 0.7960 · Prec 0.8838 · Sens 0.7392 · Espec 0.8713 · F1 0.8051 · ROC-AUC 0.882092 · PR-AUC 0.917556 · 792/117/314/890.

## Limitaciones

Remuestreo Fourier `resample` sin anti-alias dedicado en M1; filtrado recién en M2. Binario NORMAL/ANORMAL, no 3 clases. Sin clase ruido/lead-off. Solo PTB-XL clínico; falta validación en AD8232 real y experimento opcional 500 Hz.
