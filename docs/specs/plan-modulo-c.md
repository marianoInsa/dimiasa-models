# Especificación Técnica — Pipeline PPG/SpO2 (Dataset BIDMC vía `wfdb`)

**Proyecto:** DiMIASA — Prototipo IoMT
**Componente:** `bidmc_ppg_pipeline.py` (script de validación)
**Tipo:** Pipeline de ingesta + limpieza + extracción de características (sin modelado predictivo)
**Versión Spec:** 0.3
**Estado:** Borrador — pendiente de aprobación

**Changelog v0.1 → v0.2:**
- §1, §3, §5: clarificada estructura de 5 archivos WFDB por sujeto (`.dat` / `.hea` / `.breath` × waveforms+numerics).
- §3.4: tabla actualizada con los 5 archivos y herramienta `wfdb` correspondiente para cada uno.
- §5.1: `pn_dir` confirmado como `bidmc-ppg-and-respiration-dataset/1.0.0`.
- §5.5: lectura de `.breath` añadida como out-of-scope explícito de v0.1.

**Changelog v0.2 → v0.3:**
- §4.1: añadido `tests/test_bidmc_ppg_pipeline.py` al layout.
- §4.5: añadido manejo seguro de rutas con `pathlib.Path` en `plot_ppg_window`.
- §6: nueva sección "Estrategia de Testing" con pytest, mocking de wfdb, y fixtures sintéticas.

---

## 1. Arquitectura del Script

### 1.1 Flujo de datos (diagrama textual)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PhysioNet (remoto)                            │
│         bidmc-ppg-and-respiration-dataset / 1.0.0 / bidmc##          │
│                                                                      │
│   5 archivos por sujeto (## = 01..53):                               │
│     ├─ bidmc##.hea    → header waveforms (fs=125 Hz)                 │
│     ├─ bidmc##.dat    → waveforms PPG/ECG/RESP                       │
│     ├─ bidmc##.breath → anotaciones manuales de respiración          │
│     ├─ bidmc##n.hea   → header numerics  (fs=1 Hz)                   │
│     └─ bidmc##n.dat   → numerics HR/SpO2/RESP                        │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  wfdb.rdrecord()  (HTTPS)
                                │  wfdb.rdann()     (solo si v0.2+)
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [STAGE 1] INGESTA                                                    │
│  - rdrecord("bidmc01",  pn_dir=PN_DIR) → waveforms record (125 Hz)   │
│  - rdrecord("bidmc01n", pn_dir=PN_DIR) → numerics  record (1 Hz)     │
│  - .breath: NO se lee en v0.1 (documentado como future work)         │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [STAGE 2] DEMULTIPLEX POR FRECUENCIA                                 │
│  - Waveforms → DataFrame 125 Hz (PPG, ECG, RESP)                     │
│  - Numerics  → DataFrame 1 Hz   (HR, SpO2, RESP)                     │
│  - Índices temporales independientes (TimedeltaIndex)                │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [STAGE 3] LIMPIEZA PPG                                               │
│  - nk.ppg_clean(ppg_raw, sampling_rate=125, method="elgendi")        │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [STAGE 4] DETECCIÓN DE PICOS                                         │
│  - nk.ppg_findpeaks(ppg_clean, sampling_rate=125, method="elgendi")  │
│  - Salida: índices muestrales de picos sistólicos                    │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [STAGE 5] VALIDACIÓN                                                 │
│  - Console: SpO2 (mediana / serie 1 Hz), HR estimado vs HR clínico   │
│  - Plot:   ventana 10 s — PPG cruda vs limpia + peaks                │
│  - Export: reports/figures/bidmc01_ppg_window10s.png                 │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Principios arquitectónicos

- **Pure functions:** cada stage es una función sin efectos secundarios salvo I/O explícito (descarga, plot, print).
- **Determinismo:** mismo `record_id` → mismo output.
- **Separation of concerns:** ingesta (`wfdb`) y procesamiento (`NeuroKit2`) no se mezclan.
- **Fail-fast:** validar schema (nombres de canales, `fs`) al inicio.

---

## 2. Dependencias Exactas

### 2.1 Runtime (`pyproject.toml`)

| Paquete       | Versión mínima | Rol                                                                     |
|---------------|----------------|-------------------------------------------------------------------------|
| `python`      | `>=3.10`       | Tipado moderno (`X \| None`), `match`                                   |
| `wfdb`        | `>=4.1.2`      | Ingesta exclusiva desde PhysioNet (`.dat` / `.hea` / `.breath`)         |
| `neurokit2`   | `>=0.2.7`      | `ppg_clean`, `ppg_findpeaks`                                            |
| `numpy`       | `>=1.26`       | Arrays, slicing temporal                                                |
| `pandas`      | `>=2.1`        | DataFrames con `TimedeltaIndex` por frecuencia                          |
| `scipy`       | `>=1.11`       | Soporte interno NeuroKit2 + utilidades de señal                         |
| `matplotlib`  | `>=3.8`       | Plot de validación visual                                               |

### 2.2 Opcionales

| Paquete | Uso                                                           |
|---------|---------------------------------------------------------------|
| `pyPPG` | Detección alternativa de picos (benchmark)                    |
| `tqdm`  | Progreso si se itera sobre múltiples pacientes                |

### 2.3 No permitidos (criterio del proyecto)

- ❌ `requests` / `urllib` para bajar `.dat` (debe ser `wfdb` exclusivamente — requisito crítico).
- ❌ CSVs pre-procesados del BIDMC (Kaggle / mirrors). Source of truth = PhysioNet vía `wfdb`.

---

## 3. Estructura de Datos en Memoria

BIDMC publica **5 archivos por sujeto**, agrupados en dos *records* WFDB lógicos:

### 3.1 Mapeo archivo → record WFDB → memoria

| Archivo en PhysioNet | Tipo WFDB     | Función `wfdb`                          | Carga en memoria                                          | Usado en v0.1 |
|----------------------|---------------|------------------------------------------|-----------------------------------------------------------|---------------|
| `bidmc##.hea`        | Header        | (implícito en `rdrecord`)                | metadata: `fs=125`, `sig_name`, `units`, `n_sig`, etc.   | ✅            |
| `bidmc##.dat`        | Signal data   | `wfdb.rdrecord("bidmc##")`               | `np.ndarray (N_samples, N_channels)` continuo a 125 Hz   | ✅            |
| `bidmc##.breath`     | Annotation    | `wfdb.rdann("bidmc##", extension="breath")` | `wfdb.Annotation` con `sample`, `aux_note` (resp manual) | ❌ (v0.2)     |
| `bidmc##n.hea`       | Header        | (implícito en `rdrecord`)                | metadata: `fs=1`, `sig_name=['HR','SpO2','RESP',...]`    | ✅            |
| `bidmc##n.dat`       | Signal data   | `wfdb.rdrecord("bidmc##n")`              | `np.ndarray (N_seconds, N_numerics)` a 1 Hz              | ✅            |

> Nota: `wfdb.rdrecord()` lee **automáticamente** la pareja `.hea` + `.dat` con el mismo nombre base. No hay que invocar el header por separado.

### 3.2 Canal continuo — 125 Hz (de `bidmc##.dat`)

```python
ppg_signals: pd.DataFrame
# index:   TimedeltaIndex(freq="8ms")  →  1/125 s
# columns: ["PPG", "ECG", "RESP"]   (orden según wf_record.sig_name)
# dtype:   float64
# shape:   (~60_000, 3)  para un registro de 8 min
```

Acceso a la señal PPG cruda:
```python
ppg_raw: np.ndarray = ppg_signals["PPG"].to_numpy()
fs_ppg: int = 125
```

### 3.3 Canal numérico clínico — 1 Hz (de `bidmc##n.dat`)

```python
numerics: pd.DataFrame
# index:   TimedeltaIndex(freq="1s")
# columns: ["HR", "SpO2", "RESP"]   (según num_record.sig_name)
# dtype:   float64 (con posibles NaN)
# shape:   (~480, 3)
```

### 3.4 Anotaciones de respiración (`.breath`) — fuera de v0.1

Si en v0.2 se requieren:
```python
breath_ann = wfdb.rdann(record_name="bidmc01", extension="breath", pn_dir=PN_DIR)
# breath_ann.sample   → np.ndarray[int] (índices de muestra @ 125 Hz)
# breath_ann.aux_note → list[str] (etiquetas manuales)
```

### 3.5 Alineación temporal

Ambos DataFrames (125 Hz y 1 Hz) comparten **t=0** en el inicio del registro. Unión cross-frecuencia **a demanda**, sin upsampling/downsampling persistente:

```python
ppg_win  = ppg_signals.loc[pd.Timedelta(t0, "s"):pd.Timedelta(t1, "s"), "PPG"]
spo2_win = numerics.loc[pd.Timedelta(t0, "s"):pd.Timedelta(t1, "s"), "SpO2"]
```

No se persiste un DataFrame "joined" — duplicar 124 muestras por segundo es ineficiente y semánticamente incorrecto (SpO2 no varía a 125 Hz).

---

## 4. Plan de Implementación Paso a Paso

### 4.1 Layout del módulo

```
dimiasa_models/
└── pipelines/
    └── bidmc_ppg_pipeline.py
reports/
└── figures/
    └── bidmc01_ppg_window10s.png   # output del run
tests/
└── test_bidmc_ppg_pipeline.py
```

### 4.2 Constantes módulo

```python
PN_DIR: str = "bidmc-ppg-and-respiration-dataset/1.0.0"
DEFAULT_RECORD_ID: str = "bidmc01"
EXPECTED_FS_WAVEFORM: int = 125
EXPECTED_FS_NUMERICS: int = 1
PPG_CHANNEL_CANDIDATES: tuple[str, ...] = ("PLETH", "PPG", "Pleth")
SPO2_CHANNEL_CANDIDATES: tuple[str, ...] = ("SpO2", "SPO2", "SpO2_")
```

### 4.3 Funciones (firmas + responsabilidad)

```python
# ---------- Stage 1: Ingesta ----------
def fetch_bidmc_record(
    record_id: str = DEFAULT_RECORD_ID,
    pn_dir: str = PN_DIR,
) -> tuple[wfdb.Record, wfdb.Record]:
    """
    Lee desde PhysioNet vía wfdb:
      - record_id        → waveforms (bidmc##.hea + bidmc##.dat)
      - record_id + "n"  → numerics  (bidmc##n.hea + bidmc##n.dat)
    Devuelve (wf_record, num_record). NO lee .breath en v0.1.
    """

# ---------- Stage 2: Demultiplex ----------
def split_signals_by_fs(
    wf_record: wfdb.Record,
    num_record: wfdb.Record,
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """
    Construye DataFrames continuo (125 Hz) y numérico (1 Hz)
    con TimedeltaIndex. Valida fs y presencia de PPG/SpO2.
    Devuelve (df_125hz, df_1hz, fs_ppg).
    """

# ---------- Helper interno ----------
def _resolve_channel(record: wfdb.Record, candidates: tuple[str, ...]) -> str:
    """
    Busca el primer nombre de canal disponible (case-insensitive)
    en record.sig_name. Lanza KeyError si ninguno coincide.
    """

# ---------- Stage 3: Limpieza ----------
def clean_ppg(ppg_raw: np.ndarray, fs: int = EXPECTED_FS_WAVEFORM) -> np.ndarray:
    """
    Wrapper sobre nk.ppg_clean(method='elgendi').
    Band-pass 0.5–8 Hz Butterworth 3rd order.
    Salida: float64, misma longitud que entrada.
    """

# ---------- Stage 4: Picos ----------
def find_ppg_peaks(ppg_clean: np.ndarray, fs: int = EXPECTED_FS_WAVEFORM) -> np.ndarray:
    """
    Wrapper sobre nk.ppg_findpeaks(method='elgendi').
    Extrae dict["PPG_Peaks"]. Salida: np.ndarray[int] (índices muestrales).
    """

# ---------- Stage 5a: Validación consola ----------
def report_spo2(numerics: pd.DataFrame) -> dict:
    """
    Imprime: SpO2 mediana (nanmedian), min/max, % NaN, rango temporal.
    Devuelve dict con métricas (testeable).
    """

# ---------- Stage 5b: Validación visual ----------
def plot_ppg_window(
    ppg_raw: np.ndarray,
    ppg_clean: np.ndarray,
    peaks: np.ndarray,
    fs: int,
    t_start_s: float = 30.0,
    duration_s: float = 10.0,
    out_path: str | None = None,
) -> None:
    """
    Dos subplots: (a) cruda, (b) limpia + peaks marcados.
    Eje X en segundos relativos al inicio de la ventana.
    Usa pathlib.Path para asegurar que el directorio de out_path exista (mkdir(parents=True, exist_ok=True)) antes de guardar PNG.
    Guarda PNG si out_path se provee.
    """

# ---------- Orquestador ----------
def main(record_id: str = DEFAULT_RECORD_ID) -> None:
    """Llama stages 1→5 en orden. Único entry point CLI."""

if __name__ == "__main__":
    main()
```

### 4.4 Orden de ejecución en `main()`

1. `fetch_bidmc_record("bidmc01")` → `wf_rec`, `num_rec`
2. `split_signals_by_fs(wf_rec, num_rec)` → `df_125`, `df_1`, `fs=125`
3. `ppg_raw = df_125["PPG"].to_numpy()`
4. `ppg_clean_arr = clean_ppg(ppg_raw, fs=125)`
5. `peaks = find_ppg_peaks(ppg_clean_arr, fs=125)`
6. `report_spo2(df_1)` → console output
7. `plot_ppg_window(ppg_raw, ppg_clean_arr, peaks, 125, t_start_s=30, duration_s=10, out_path="reports/figures/bidmc01_ppg_window10s.png")`

### 4.5 Criterios de aceptación

- [ ] Corre `python -m dimiasa_models.pipelines.bidmc_ppg_pipeline` sin excepciones.
- [ ] Consola muestra: `SpO2 mediana = XX.X %`, `n_peaks = NNN`, `HR_estimada ≈ XX bpm`.
- [ ] PNG generado en `reports/figures/`.
- [ ] HR estimada (de peaks) cae dentro de ±5 bpm de HR clínico del numerics.

---

## 5. Consideraciones Técnicas / Edge Cases

### 5.1 Ingesta con `wfdb` (5 archivos por sujeto)

| #  | Riesgo                                                              | Mitigación                                                                                                                       |
|----|---------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| 1  | `pn_dir` exacto                                                     | Hardcodeado y documentado: `PN_DIR = "bidmc-ppg-and-respiration-dataset/1.0.0"`. Verificable con `wfdb.get_record_list(PN_DIR)`. |
| 2  | `rdrecord("bidmc01")` requiere **ambos** `.hea` y `.dat` accesibles | `wfdb` los descarga atómicamente. Si uno falla, propagar excepción clara (no silenciar).                                         |
| 3  | Numerics record nombre = `bidmc01n` (sufijo `n`, convención PhysioNet) | Construir explícitamente: `numerics_id = f"{record_id}n"`. No inferir por listado.                                              |
| 4  | `.breath` se descarga aparte (`rdann`, no `rdrecord`)               | v0.1: ignorado. Documentar en docstring que `rdann(extension="breath")` es la vía cuando se necesite.                            |
| 5  | Pérdida de conexión / timeout HTTPS                                 | Try/except sobre `wfdb.rdrecord` con mensaje claro. Sin reintentos automáticos en v0.1 (KISS).                                   |
| 6  | Caché local                                                         | `wfdb.dl_database(PN_DIR, dl_dir="data/raw/bidmc/")` opcional. Mantener `data/raw/` en `.gitignore`.                             |
| 7  | Nombres de canales no canónicos (`'PLETH'` vs `'PPG'`)              | `_resolve_channel(record, PPG_CHANNEL_CANDIDATES)` con `str.upper()`.                                                            |
| 8  | `fs` real distinto de 125 Hz en algún registro                      | Leer `record.fs` y propagar. Constante `EXPECTED_FS_WAVEFORM=125` solo como default/assert.                                      |

### 5.2 Señal biomédica

| #  | Riesgo                                                          | Mitigación                                                                                                                       |
|----|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| 9  | NaN al inicio/fin del waveform (sensor settling)                | `np.isnan(ppg_raw).any()` → recortar leading/trailing NaN o interpolar lineal corto (< 5 muestras). Loggear.                     |
| 10 | Artefactos de movimiento → picos falsos                         | v0.1: aceptar y reportar `n_peaks`. v0.2: filtro IBI fuera de [0.3 s, 2.0 s].                                                    |
| 11 | Saturación / clipping del ADC                                   | Warning si > 1% de muestras saturadas (`ppg_raw == ppg_raw.max()` consecutivos).                                                 |
| 12 | DC drift / wandering baseline                                   | `nk.ppg_clean(method="elgendi")` ya hace band-pass 0.5–8 Hz → mitigado por diseño.                                              |
| 13 | SpO2 = NaN cuando el monitor pierde lectura                     | `np.nanmedian` + reportar `% NaN`. No imputar.                                                                                  |
| 14 | Desalineación temporal entre waveform y numerics                | Asumir t=0 compartido (estándar BIDMC). Validar `record.base_time` / `record.base_date` si presentes.                            |

### 5.3 NeuroKit2

| #  | Riesgo                                                           | Mitigación                                                                                              |
|----|------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| 15 | Cambios de API entre versiones < 0.2.7                           | Pin `neurokit2>=0.2.7`. Documentar en `pyproject.toml`.                                                |
| 16 | `ppg_findpeaks` devuelve dict, no array                          | Extraer `["PPG_Peaks"]` explícitamente.                                                                |
| 17 | Longitud de `ppg_clean` distinta a `ppg_raw` en bordes           | `assert len(ppg_clean) == len(ppg_raw)`. Si difiere, paddear o reproc.                                 |

### 5.4 Rendimiento y reproducibilidad

| #  | Riesgo                                                                 | Mitigación                                                                                              |
|----|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| 18 | Descargas repetidas en cada `pytest`                                   | Mockear `wfdb.rdrecord` en tests o fixture cacheado en `data/raw/`.                                    |
| 19 | Plot bloquea en entornos sin display (CI)                              | `matplotlib.use("Agg")` cuando `out_path` se provee. No llamar `plt.show()` en modo headless.          |
| 20 | Memoria: ~60k × 3 × 8 B ≈ 1.5 MB por registro                          | Despreciable single-record. Multi-paciente: `del` entre iteraciones.                                   |

### 5.5 Fuera de alcance v0.1 (explícito)

- ❌ Lectura de `bidmc##.breath` (anotaciones respiratorias manuales).
- ❌ Cálculo de SpO2 a partir de PPG raw (BIDMC no provee dos longitudes de onda).
- ❌ Estimación de tasa respiratoria a partir de PPG.
- ❌ Procesamiento multi-paciente / batch sobre los 53 sujetos.
- ❌ Modelado predictivo o ML.
- ❌ Persistencia de features en parquet/DB.

---

## 6. Estrategia de Testing

- Usa `pytest` para tests unitarios.
- Intercepta llamadas a `wfdb.rdrecord` y `wfdb.rdann` con `unittest.mock` (o `pytest-mock`).
- Tests unitarios nunca hacen peticiones HTTP reales a PhysioNet.
- Crea fixture con señal senoidal sintética usando NumPy para probar `find_ppg_peaks()` y limpieza. Señal senoidal simula pulsos PPG con frecuencia conocida (ej. 1.2 Hz para ~72 bpm), amplitud modulada, ruido gaussiano añadido. Verifica que peaks detectados correspondan a ciclos esperados, limpieza reduzca ruido sin distorsionar forma.

---

## 7. Checklist de Aprobación

- [ ] Confirmar `PN_DIR = "bidmc-ppg-and-respiration-dataset/1.0.0"`.
- [ ] Confirmar que **solo** `.dat`+`.hea` (×2) se leen en v0.1 (`.breath` queda diferido).
- [ ] Confirmar paciente de prueba: `bidmc01`.
- [ ] Confirmar ventana de plot: 10 s desde t=30 s.
- [ ] Confirmar método de limpieza: `elgendi`.
- [ ] Confirmar layout: `dimiasa_models/pipelines/bidmc_ppg_pipeline.py`.
- [ ] Confirmar estrategia de testing con pytest, mocking, y fixtures sintéticas.

---

**Una vez apruebes** → toggle to Act mode → genero `bidmc_ppg_pipeline.py` + tests + update `pyproject.toml`.