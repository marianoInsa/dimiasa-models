# Módulo B — Investigación de Dataset (ECG, pipeline oficial)

> Estado: pipeline oficial definitivo PTB-XL Lead II 250 Hz binario. Reemplaza al diseño anterior MIT-BIH / 125 Hz / 3 clases, que queda obsoleto y no debe usarse como especificación.

## 1. Fuente oficial única: PTB-XL 1.0.3

- Origen: `https://physionet.org/content/ptb-xl/1.0.3/` — ZIP `ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3.zip`.
- Contenido base: 21 799 ECG de 10 s a 500 Hz (`filename_hr`), 12 derivaciones, 71 códigos SCP-ECG, columna `strat_fold` 1–10.
- Filtro aplicado en M1: edad 18–89 → 21 373 ECG; se descartan 403 sin clase diagnóstica → **20 970 ECG** finales.
- Derivación: solo **Lead II** (`signal[:, lead_index]`, se exige longitud original 5000 y `fs == 500`).
- Remuestreo M1: `scipy.signal.resample(signal_II, 2500)` → **250 Hz, 10 s, 2500 muestras**. Sin normalización y sin filtros en M1 (`normalization: None`, `filtering: None` en atributos HDF5).

## 2. Etiqueta oficial binaria

- Mapeo desde `diagnostic_class`: solo `NORM` → `0 = NORMAL`; cualquier otra clase diagnóstica → `1 = ANORMAL`; sin clase → se descarta.
- Distribución final: NORMAL 8 941 (42.64 %) / ANORMAL 12 029 (57.36 %).
- Por partición (conteos M2): TRAIN 16 761 (7 127 N / 9 634 A) · VAL 2 096 (905 N / 1 191 A) · TEST 2 113 (909 N / 1 204 A).
- Particiones por `strat_fold` PTB-XL: folds 1–8 TRAIN, fold 9 VALIDATION, fold 10 TEST. Verificación M1: 0 pacientes repetidos entre particiones.

## 3. Artefactos de datos

HDF5 con datasets `X (20970, 2500) float32`, `y int8`, `ecg_id`, `patient_id`, `age`, `sex`, `strat_fold`, compresión `gzip level 4`, más atributos `dataset=PTB-XL`, `sampling_frequency=250`, `original_sampling_frequency=500`, `lead=II`, `duration_seconds=10`, `samples_per_ecg=2500`, `age_min=18`, `age_max=88`, `label_0=NORMAL`, `label_1=ANORMAL`. Las particiones copian datasets/atributos y agregan `partition` + `source_file`.

## 4. Decisión

- `set` único: PTB-XL Lead II 250 Hz binario. No hay `set_a` MITDB ni `set_b` multicorpus.
- MIT-BIH, CinC2017, Icentia11k, CPSC2021, SHDB-AF, BUT QDB y el esquema 125 Hz / 3 clases quedan fuera del pipeline oficial.
- Experimento opcional pendiente: corrida a 500 Hz (5000 muestras / 10 s) contra estos resultados. No bloquea la aceptación del pipeline 250 Hz.

## 5. Referencias mínimas

Wagner et al. *PTB-XL.* Sci Data 7, 2020. DOI `10.1038/s41597-020-0495-6`; Xie et al. WFDB Python 2023. DOI `10.13026/9njx-6322`.
