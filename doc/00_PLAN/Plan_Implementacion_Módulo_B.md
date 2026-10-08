# Módulo B — Plan de Implementación (pipeline oficial PTB-XL 250 Hz)

> Pipeline final definitivo. Fuente de verdad: `notebooks/fase_1/modulo_b_ecg/` + artefactos en `notebooks/data/oro/ecg/ptb_xl_250hz_lead_ii/` y `notebooks/data/modelos/ecg/tinyecgnet_ptb_xl_250hz/`. Los notebooks son snapshots de Colab (Drive + GPU T4, TF 2.20.0); no se modifica su contenido.

## 1. Estructura

```text
notebooks/fase_1/modulo_b_ecg/
  00_M1_Creacion_Dataset_PTB-XL_Lead-II_250Hz.ipynb
  01_M2_Entrenamiento_TinyECGNet_Sequential_PTB-XL.ipynb
notebooks/data/oro/ecg/ptb_xl_250hz_lead_ii/
  PTB_XL_senal_250Hz_derivacion_II.h5            (20970, 2500)
  TRAIN_PTB_XL_senal_250Hz_derivacion_II.h5      (16761, 2500)
  VAL_PTB_XL_senal_250Hz_derivacion_II.h5        (2096, 2500)
  TEST_PTB_XL_senal_250Hz_derivacion_II.h5       (2113, 2500)
notebooks/data/modelos/ecg/tinyecgnet_ptb_xl_250hz/
  mejor_tiny_ecgnet_sequential.keras
  modelo_final_tiny_ecgnet_sequential.keras
  results/resultados_test_keras_sequential.npz
  results/historial_entrenamiento.npy
  tflite/agent1_tinyecgnet_sequential_fp32.tflite
  tflite/agent1_tinyecgnet_sequential_int8.tflite
  firmware/agent1_ecg_sequential_config.h
  firmware/agent1_tinyecgnet_sequential_int8_model.h
```

`notebooks/data/` está ignorado por Git; solo notebooks y docs se versionan.

## 2. M1 — dataset (sin filtro ni normalización)

Entrada: ZIP PTB-XL 1.0.3 → `wfdb.rdsamp(filename_hr)`, exige `fs == 500`, presencia de `II` y 5000 muestras. `resample(signal_II, 2500)`, cast `float32`, sin z-score. Salida X `(20970, 2500)`, 0 NaN/Inf, 0 errores. Partición por `strat_fold` con 0 solape de pacientes.

## 3. M2 — preprocesamiento, modelo y entrenamiento

- Preprocesamiento M2 por bloques de 256: bandpass Butterworth orden 4 `0.5–40 Hz` (`sosfiltfilt`) + notch 50 Hz Q30 (`filtfilt`), luego z-score por ECG (`eps 1e-8`). Shape final `(N, 2500, 1)`.
- Augment solo en entrenamiento: ganancia 0.90–1.10, ruido gaussiano `std 0.01`, shift ±25 muestras; identidad en inferencia (verificado diff 0.0).
- Arquitectura `Agent1_TinyECGNet_Sequential`: Input `(2500, 1)` → Conv1D 12×k15 s2 + BN + ReLU → SeparableConv1D 16×k15 + BN + ReLU + MaxPool2 + SpatialDropout 0.10 → SeparableConv1D 24×k15 + BN + ReLU + MaxPool2 + SpatialDropout 0.15 → SeparableConv1D 32×k15 + BN + ReLU + MaxPool3 → GlobalAveragePooling1D → Dropout 0.50 → Dense 1 sigmoid. Inferencia: misma red sin capa de augment, 2 673 parámetros.
- Entrenamiento: `seed 42`, Adam `lr 2e-4`, `BinaryCrossentropy(label_smoothing=0.02)`, batch 64, máx 50 épocas (historial: 30), `ModelCheckpoint(monitor=val_pr_auc)`, `EarlyStopping(patience=6, min_delta=0.002, restore_best)`, `ReduceLROnPlateau(factor=0.5, patience=2, min_lr=1e-6)`.

## 4. Conversión y firmware

- TFLite FP32 desde modelo de inferencia: 20 976 bytes (20.48 KB). Paridad Keras: diff máx 1.788e-07, 0 cambios de clase.
- INT8 full-integer calibrado con 500 TRAIN (`default_rng(42)`): entrada int8 `[1, 2500, 1]` scale 0.08170621 zp −18; salida int8 `[1, 1]` scale 0.00390625 zp −128. Tamaño 18 584 bytes (18.15 KB). 53 tensores / 34 ops (EXPAND_DIMS, CONV_2D, RESHAPE, DEPTHWISE_CONV_2D, MAX_POOL_2D, MEAN, FULLY_CONNECTED, LOGISTIC, DELEGATE). Memoria de tensores 282 898 bytes (276.27 KB, estimación, no arena TFLite Micro).
- FP32 vs INT8: diff máx 0.03683, media 0.00738, RMSE 0.009949, 22 clases cambian (1.0412 %).
- Threshold: float 0.5 → INT8 0 → reconstruido 0.5 exacto. Header C verificado byte-idéntico al `.tflite`.

## 5. Resultados TEST (n = 2113, threshold 0.5)

| Modelo | Acc | Prec | Sens | Espec | F1 | ROC-AUC | PR-AUC | TN/FP/FN/TP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Keras | 0.7894 | 0.8853 | 0.7243 | 0.8757 | 0.7967 | 0.882407 | 0.918584 | 796/113/332/872 |
| TFLite FP32 | 0.7894 | 0.8853 | 0.7243 | 0.8757 | 0.7967 | — | — | idéntico a Keras |
| TFLite INT8 | 0.7960 | 0.8838 | 0.7392 | 0.8713 | 0.8051 | 0.882092 | 0.917556 | 792/117/314/890 |

Keras además: FPR 0.1243, FNR 0.2757. Keras `.keras` 118 542 bytes c/u.

## 6. Criterios de aceptación

Pipeline corre desde HDF5 oficiales; particiones sin fuga por paciente; métricas y matrices persistidas en `.npz`; TFLite + headers generados y verificados.

## 7. Experimento opcional 500 Hz

Notebook separado en `notebooks/experiments/ecg/`, artefactos separados. Mantener 10 s, etiquetas, particiones, semilla e hiperparámetros; entrada `(5000, 1)`. Comparar contra tabla §5. No sobrescribir M1/M2 ni modelos 250 Hz.
