# PTB-XL (Módulo B — dataset oficial)

- Fuente: `https://physionet.org/content/ptb-xl/1.0.3/` — ZIP `ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3.zip`.
- Base: 21 799 ECG clínicos de 10 s a 500 Hz (`filename_hr`), 12 derivaciones, 71 códigos SCP-ECG, `strat_fold` 1–10.
- Uso oficial: solo **Lead II**, remuestreado a **250 Hz** (`scipy.signal.resample` 5000→2500), 10 s / 2500 muestras, sin filtros ni normalización en dataset.
- Filtro de cohorte M1: edad 18–89 → 21 373; 403 sin clase diagnóstica descartados → **20 970 ECG**.
- Etiqueta binaria: `NORM` → 0 NORMAL (8 941); otra clase diagnóstica → 1 ANORMAL (12 029).
- Particiones por `strat_fold`: TRAIN folds 1–8 (16 761) · VAL fold 9 (2 096) · TEST fold 10 (2 113); 0 pacientes compartidos.
- Artefactos: `notebooks/data/oro/ecg/ptb_xl_250hz_lead_ii/*.h5` (completo + TRAIN/VAL/TEST), `gzip level 4`.
- Referencia: Wagner et al. *PTB-XL.* Sci Data 7, 2020. DOI `10.1038/s41597-020-0495-6`.
