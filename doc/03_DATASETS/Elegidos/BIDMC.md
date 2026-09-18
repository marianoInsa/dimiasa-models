Fecha: 18 September 2026

- Dataset: BIDMC PPG and Respiration Dataset v1.0.0 — PhysioNet, open access, 207.7 MB. DOI `10.13026/C2208R`. https://physionet.org/content/bidmc/1.0.0/
- [Fuente local](../../02_FUENTES/Fuentes.md)
- Cita: Pimentel, M. A. F., Johnson, A. E. W., Charlton, P. H., Birrenkott, D., Watkinson, P. J., Tarassenko, L., & Clifton, D. A. (2017). Toward a robust estimation of respiratory rate from pulse oximeters. *IEEE Transactions on Biomedical Engineering, 64*(8), 1914–1923. https://doi.org/10.1109/TBME.2016.2613124

---

# Identidad

BIDMC PPG and Respiration Dataset v1.0.0 (PhysioNet, open access, 207.7 MB; DOI del dataset `10.13026/C2208R`). Publicado por Pimentel et al. (2017), DOI `10.1109/TBME.2016.2613124` (cita ya registrada en `doc/02_FUENTES/Fuentes.md`).

# Contenido

* 53 registros de 8 min (480 s) provenientes de la UCI (MIMIC-II).
* Señales PPG (PLETH), RESP y ECG a 125 Hz + numéricos HR/PULSE/RESP/SpO2 a 1 Hz.
* 53 registros = **46 sujetos** MIMIC reales (s03386 ×4: registros 06–09; s11342 ×4: 20–23; s25323 ×2: 38–39; el resto, un registro por sujeto).

# Archivo reducido en el repo

`notebooks/data/bronce/ppg/BIDMC-Reduced.csv` (gitignored). El original queda en `datasets/ppg/00-Finales/`.

Esquema exacto:

```text
Record,Subject,Sample_Index,Time_s,PLETH,HR,PULSE,RR,SpO2
```

# Unidades

* PLETH: adimensional (valores NU de la distribución; sin reescalar).
* HR / PULSE: bpm.
* RR: resp/min.
* SpO2: %.

# Decisiones de la reducción (D1–D10)

Resumen fiel; el detalle completo está en `datasets\ppg\unify\SPEC_bidmc.md`.

* **D1** — Fuente: CSV oficiales por registro (`bidmc_csv/`); no WFDB/MAT.
* **D2** — Salida: un único CSV `BIDMC-Reduced.csv`, formato largo, todos los registros apilados.
* **D3** — Solo se conserva PLETH; ECG (II/AVR/V) y onda RESP quedan en el raw (alcance del proyecto: PPG).
* **D4** — `Subject` = fuente MIMIC-II de `Fix.txt` (evita fuga en validación sujeto-wise).
* **D5** — Numéricos 1 Hz → 125 Hz por step-hold por segundo sobre la grilla 125 Hz; `Sample_Index = sample_idx + 1`. Sin interpolación.
* **D6** — Sin reescalado ni z-score.
* **D7** — Se omiten `*_Breaths.csv` y SQI.
* **D8** — Formato: CSV; PLETH 6 decimales, `Time_s` 3 decimales.
* **D9** — Copia a bronce dejando el original en `datasets/ppg/00-Finales/`.
* **D10** — Faltantes: forward-fill por columna, back-fill al inicio; mismo criterio para segundos ausentes. El crudo tiene NaN en PULSE/SpO2 de bidmc_01/05/19/25/44, RR de 13/15/19 y HR de 27; además, los numéricos de bidmc_23 abarcan t=-1..479 mientras sus señales llegan a t=480. Una columna todo-NaN lanza error.

# Conteos verificados

* 53 records
* 3.180.053 filas totales
* 60.001 filas por record
* 46 subjects

# Rol en Módulo C

`set_a` del pipeline C1 (validación de procesamiento PPG, FC y calidad). El entrenamiento SpO2 queda bloqueado hasta contar con GT independiente (ver `doc/00_PLAN/Plan_Implementacion_Módulo_C.md`).

# Reproducción

Script: `D:\CARRERA\CINAPTIC\datasets\ppg\unify\extract_bidmc.py` (stdlib, TDD con 100% de cobertura).

```powershell
cd datasets\ppg\unify
python -m pytest --cov=. --cov-report=term-missing
python extract_bidmc.py
```

# Limitaciones

* Normoxia: SpO2 global 83–100, mayoría 95–100.
* PLETH monocanal procesado por el monitor (sin Rojo/IR).
* Sin ACC (no se puede validar SQI de movimiento).
* Registros de UCI inmóvil.
