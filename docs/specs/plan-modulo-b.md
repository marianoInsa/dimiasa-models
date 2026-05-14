# Technical Spec — Módulo B: ECG y Arritmias (AD8232)

| Campo        | Valor                                              |
|--------------|-----------------------------------------------------|
| **Proyecto** | DiMIASA — Dispositivo Inteligente Multisensor IoMT  |
| **Componente** | Módulo B — Clasificación de Arritmias ECG          |
| **Tipo**     | Technical Specification (spec-first)                |
| **Versión**  | 0.1.0-draft                                        |
| **Estado**   | 🟡 En revisión                                     |
| **Autor**    | CInApTIC Research Team                              |
| **Fecha**    | 2026-05-13                                          |
| **Sensor HW**| Analog Devices AD8232 (single-lead)                 |

---

## 1. Arquitectura del Script

### 1.1 Diagrama de flujo

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MÓDULO B — PIPELINE ECG                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌─────────────┐  │
│  │PhysioNet │───▶│  wfdb    │───▶│  scipy    │───▶│Segmentación │  │
│  │ MIT-BIH  │    │ ingesta  │    │ bandpass  │    │  ventanas   │  │
│  │  (API)   │    │.dat/.hea │    │0.5-40 Hz  │    │  beat-ctr   │  │
│  └──────────┘    │  +.atr   │    └───────────┘    └──────┬──────┘  │
│                  └──────────┘                            │         │
│                                                          ▼         │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌─────────────┐  │
│  │Validación│◀───│Entrena-  │◀───│  1D-CNN   │◀───│  Split      │  │
│  │ métricas │    │ miento   │    │  modelo   │    │ train/val/  │  │
│  │ F1/Acc   │    │ Keras    │    │ liviano   │    │   test      │  │
│  └────┬─────┘    └──────────┘    └───────────┘    └─────────────┘  │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────┐    ┌──────────┐                                      │
│  │ Export   │───▶│TFLite /  │  ← objetivo edge (fuera de v0.1)     │
│  │ modelo   │    │ ONNX     │                                      │
│  └──────────┘    └──────────┘                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

data/raw/mitdb/         ← archivos .dat, .hea, .atr descargados
data/interim/           ← señales filtradas en .npy
data/processed/         ← ventanas segmentadas + labels
models/                 ← pesos .keras / .h5
reports/figures/        ← curvas ROC, matrices confusión
```

### 1.2 Principios arquitectónicos

| Principio | Descripción |
|-----------|-------------|
| **Inmutabilidad raw** | `data/raw/` nunca se modifica post-descarga |
| **Reproducibilidad** | Seed global (`42`), versiones pinneadas |
| **Idempotencia** | Re-ejecutar cualquier paso produce mismo resultado |
| **Separación capas** | Ingesta → Procesamiento → Modelado → Evaluación como funciones puras |
| **Edge-aware** | Modelo liviano; meta < 500 KB post-cuantización |

---

## 2. Dependencias Exactas

### 2.1 Runtime

| Paquete | Versión mín. | Propósito |
|---------|-------------|-----------|
| `wfdb` | ≥ 4.3.1 | Lectura PhysioNet `.dat`/`.hea`/`.atr` |
| `numpy` | ≥ 1.26.0 | Arrays señales ECG |
| `scipy` | ≥ 1.14.0 | `signal.butter`, `signal.sosfiltfilt` bandpass |
| `pandas` | ≥ 2.2.0 | Tablas anotaciones, métricas |
| `tensorflow` | ≥ 2.18.0 | Keras integrado, 1D-CNN |
| `scikit-learn` | ≥ 1.5.0 | `train_test_split`, métricas, `class_weight` |
| `matplotlib` | ≥ 3.9.0 | Plots validación |

### 2.2 Desarrollo / Testing

| Paquete | Propósito |
|---------|-----------|
| `pytest` ≥ 8.0 | Framework test |
| `pytest-cov` | Cobertura |
| `ruff` | Lint (ya en proyecto) |

### 2.3 Herramientas NO permitidas

| Herramienta | Motivo exclusión |
|-------------|-----------------|
| CSVs manuales Kaggle | Trazabilidad nula; usar `wfdb` API |
| PyTorch | Proyecto estandarizado en TF/Keras |
| `neurokit2` para ingesta | Solo `wfdb` para lectura; `neurokit2` opcional para R-peak validation |
| Descargas `wget`/`curl` | `wfdb.dl_database()` encapsula descarga |

---

## 3. Estructura de Datos en Memoria

### 3.1 Archivos PhysioNet → Objetos Python

```
MIT-BIH record "100"
├── 100.hea  ──▶  wfdb.Record   (metadata: fs=360, n_sig=2, sig_name, units)
├── 100.dat  ──▶  record.p_signal : np.ndarray  shape=(650000, 2)  float64
└── 100.atr  ──▶  wfdb.Annotation (sample, symbol, aux_note)
```

| Atributo `wfdb.Record` | Tipo | Valor esperado |
|-------------------------|------|----------------|
| `record.fs` | `int` | `360` |
| `record.n_sig` | `int` | `2` (MLII + V1/V2/V5) |
| `record.p_signal` | `np.ndarray` | `(N, 2)` float64, mV |
| `record.sig_name` | `list[str]` | `['MLII', 'V5']` (varía) |

| Atributo `wfdb.Annotation` | Tipo | Descripción |
|-----------------------------|------|-------------|
| `ann.sample` | `np.ndarray[int]` | Índices muestrales de cada latido |
| `ann.symbol` | `list[str]` | Símbolo anotación AAMI (`N`,`L`,`R`,`V`,`/`,`A`,`f`,`F`…) |

### 3.2 Taxonomía de clases AAMI (versión 0.1)

Agrupación estándar ANSI/AAMI EC57 para reducir a 5 superclases:

| Superclase | Símbolos AAMI incluidos | Significado clínico |
|------------|------------------------|---------------------|
| **N** | `N`, `L`, `R`, `e`, `j` | Normal / Bundle Branch |
| **S** | `A`, `a`, `J`, `S` | Supraventricular ectópico |
| **V** | `V`, `E` | Ventricular ectópico |
| **F** | `F` | Fusión |
| **Q** | `/`, `f`, `Q` | Unknown / Paced |

### 3.3 Ventana de segmentación

Cada latido se segmenta centrado en R-peak:

```
         ◄── 90 samples ──►◄── R ──►◄── 90 samples ──►
         |     pre-R       |  peak  |    post-R        |
         └─────────────────┴────────┴──────────────────┘
                      Total: 181 samples
                      @ 360 Hz ≈ 503 ms
```

- **Canal:** MLII (lead 0) — single-lead, compatible AD8232
- **Shape final por beat:** `(181,)` → reshape `(181, 1)` para Conv1D
- **Dataset consolidado:** `X.shape = (N_beats, 181, 1)`, `y.shape = (N_beats,)` con labels 0–4

---

## 4. Plan de Implementación Paso a Paso

### 4.1 Constantes y configuración

```python
# dimiasa_models/ecg/config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ECGConfig:
    db_name: str = "mitdb"
    db_dir: Path = Path("data/raw/mitdb")
    interim_dir: Path = Path("data/interim/ecg")
    processed_dir: Path = Path("data/processed/ecg")
    model_dir: Path = Path("models/ecg")
    fs: int = 360                    # sampling rate Hz
    lowcut: float = 0.5              # bandpass inferior Hz
    highcut: float = 40.0            # bandpass superior Hz
    filter_order: int = 4            # Butterworth order
    window_pre: int = 90             # samples antes R-peak
    window_post: int = 90            # samples después R-peak
    seed: int = 42
    batch_size: int = 128
    epochs: int = 30
    learning_rate: float = 1e-3
    val_split: float = 0.15
    test_split: float = 0.15

AAMI_MAP: dict[str, int] = {
    "N": 0, "L": 0, "R": 0, "e": 0, "j": 0,   # Normal
    "A": 1, "a": 1, "J": 1, "S": 1,             # Supra-V
    "V": 2, "E": 2,                              # Ventricular
    "F": 3,                                       # Fusión
    "/": 4, "f": 4, "Q": 4,                      # Unknown
}

RECORD_IDS: list[str] = [
    "100","101","102","103","104","105","106","107","108","109",
    "111","112","113","114","115","116","117","118","119","121",
    "122","123","124","200","201","202","203","205","207","208",
    "209","210","212","213","214","215","217","219","220","221",
    "222","223","228","230","231","232","233","234",
]
```

### 4.2 Ingesta

```python
# dimiasa_models/ecg/ingest.py
import numpy as np
import wfdb
from pathlib import Path

def download_mitbih(db_name: str, target_dir: Path) -> None:
    """Descarga MIT-BIH completa vía wfdb API a target_dir.
    Idempotente: skip si archivos ya existen.
    """
    ...

def load_record(record_id: str, db_dir: Path) -> tuple[np.ndarray, int]:
    """Lee señal de un record. Retorna (signal_array, fs).
    signal_array shape: (N_samples, n_channels), dtype float64.
    """
    ...

def load_annotations(record_id: str, db_dir: Path) -> tuple[np.ndarray, list[str]]:
    """Lee anotaciones. Retorna (sample_indices, symbols)."""
    ...
```

### 4.3 Filtrado (ETL)

```python
# dimiasa_models/ecg/preprocessing.py
import numpy as np
from numpy.typing import NDArray

def bandpass_filter(
    signal: NDArray[np.float64],
    fs: int,
    lowcut: float,
    highcut: float,
    order: int = 4,
) -> NDArray[np.float64]:
    """Butterworth bandpass (SOS) + sosfiltfilt (zero-phase).
    Input/output shape: (N_samples,) — single channel.
    """
    ...

def normalize_signal(signal: NDArray[np.float64]) -> NDArray[np.float64]:
    """Z-score normalization por registro completo."""
    ...
```

### 4.4 Segmentación

```python
# dimiasa_models/ecg/segmentation.py
import numpy as np
from numpy.typing import NDArray

def segment_beats(
    signal: NDArray[np.float64],
    r_peaks: NDArray[np.intp],
    symbols: list[str],
    aami_map: dict[str, int],
    window_pre: int = 90,
    window_post: int = 90,
) -> tuple[NDArray[np.float64], NDArray[np.int8]]:
    """Extrae ventanas centradas en R-peak.
    Descarta beats cuyo símbolo no está en aami_map.
    Descarta beats en bordes (peak < window_pre o peak + window_post > len).
    Returns: (X: (N_beats, window_size), y: (N_beats,))
    """
    ...

def build_dataset(
    record_ids: list[str],
    db_dir: "Path",
    config: "ECGConfig",
) -> tuple[NDArray[np.float64], NDArray[np.int8], NDArray[np.str_]]:
    """Pipeline completo: load → filter → segment → concat todos los records.
    Returns: (X, y, record_origins) para trazabilidad.
    """
    ...
```

### 4.5 Modelo 1D-CNN

Arquitectura inspirada en `awni/ecg` (Hannun et al., 2019) pero simplificada para edge:

```python
# dimiasa_models/ecg/model.py
from tensorflow import keras

def build_ecg_cnn(
    input_shape: tuple[int, int] = (181, 1),
    num_classes: int = 5,
    num_filters: int = 32,
    kernel_size: int = 7,
    num_residual_blocks: int = 4,
    dropout_rate: float = 0.2,
) -> keras.Model:
    """1D-CNN con bloques residuales simplificados.

    Arquitectura (inspirada awni/ecg, reducida):
      Input (181,1)
      → Conv1D(32, 7) + BN + ReLU
      → [ResBlock(filters, subsample=2)] × 4
         cada ResBlock: BN→ReLU→Conv1D→BN→ReLU→Conv1D + shortcut
      → GlobalAveragePooling1D
      → Dense(num_classes, softmax)

    Total params estimados: ~50K (vs ~500K original awni/ecg)
    """
    ...

def residual_block(
    x: keras.KerasTensor,
    filters: int,
    kernel_size: int,
    subsample: int,
    dropout_rate: float,
    block_idx: int,
) -> keras.KerasTensor:
    """Bloque residual 1D: BN→ReLU→Conv1D→BN→ReLU→Conv1D + skip.
    Skip connection usa MaxPooling1D(subsample) + zero-pad channels
    cuando filters se duplican (cada 2 bloques).
    """
    ...
```

### 4.6 Entrenamiento

```python
# dimiasa_models/ecg/train.py
import numpy as np
from numpy.typing import NDArray
from pathlib import Path

def compute_class_weights(y: NDArray[np.int8]) -> dict[int, float]:
    """Calcula pesos inversamente proporcionales a frecuencia de clase.
    Usa sklearn.utils.class_weight.compute_class_weight.
    """
    ...

def train_model(
    X_train: NDArray[np.float64],
    y_train: NDArray[np.int8],
    X_val: NDArray[np.float64],
    y_val: NDArray[np.int8],
    config: "ECGConfig",
    class_weights: dict[int, float] | None = None,
) -> tuple["keras.Model", "keras.callbacks.History"]:
    """Entrena modelo con EarlyStopping + ReduceLROnPlateau.
    Callbacks:
      - EarlyStopping(monitor='val_loss', patience=5)
      - ReduceLROnPlateau(factor=0.5, patience=3)
      - ModelCheckpoint(save_best_only=True)
    Guarda best model en config.model_dir.
    """
    ...
```

### 4.7 Validación

```python
# dimiasa_models/ecg/evaluate.py
import numpy as np
from numpy.typing import NDArray

def evaluate_model(
    model: "keras.Model",
    X_test: NDArray[np.float64],
    y_test: NDArray[np.int8],
    class_names: list[str] | None = None,
) -> dict[str, float]:
    """Genera classification_report, confusion_matrix, F1 macro/weighted.
    Guarda plots en reports/figures/.
    Returns dict: {accuracy, f1_macro, f1_weighted, precision_macro, recall_macro}
    """
    ...

def plot_confusion_matrix(
    y_true: NDArray[np.int8],
    y_pred: NDArray[np.int8],
    class_names: list[str],
    output_path: "Path",
) -> None:
    """Heatmap normalizado de confusion matrix con matplotlib."""
    ...
```

### 4.8 Estructura de archivos final

```
dimiasa_models/
├── __init__.py
└── ecg/
    ├── __init__.py
    ├── config.py          # ECGConfig dataclass + AAMI_MAP
    ├── ingest.py          # download_mitbih, load_record, load_annotations
    ├── preprocessing.py   # bandpass_filter, normalize_signal
    ├── segmentation.py    # segment_beats, build_dataset
    ├── model.py           # build_ecg_cnn, residual_block
    ├── train.py           # compute_class_weights, train_model
    └── evaluate.py        # evaluate_model, plot_confusion_matrix

tests/
└── ecg/
    ├── __init__.py
    ├── conftest.py        # fixtures: synthetic ECG, mock wfdb
    ├── test_preprocessing.py
    ├── test_segmentation.py
    ├── test_model.py
    └── test_pipeline.py
```

---

## 5. Consideraciones Técnicas / Edge Cases

### 5.1 Riesgos y mitigaciones

| # | Riesgo | Impacto | Prob. | Mitigación |
|---|--------|---------|-------|------------|
| R1 | **Baseline wander** en señales crudas | Clasificación errónea | Alta | Bandpass 0.5 Hz highpass elimina drift DC |
| R2 | **Ruido EMG / powerline** (50/60 Hz) | Features espurias | Media | Highcut 40 Hz elimina powerline; notch filter opcional |
| R3 | **Desbalanceo extremo** clases AAMI | Modelo sesgado a clase N (~70%) | Alta | `class_weight` inversamente proporcional + F1-macro como métrica principal |
| R4 | **Beats en bordes** del registro | Index out of bounds en ventana | Alta | `segment_beats` descarta beats a < `window_pre` del inicio o fin |
| R5 | **Símbolos no mapeados** en `.atr` | Labels desconocidos | Media | Beats con símbolo fuera `AAMI_MAP` descartados silenciosamente + log warning |
| R6 | **Variabilidad inter-paciente** | Overfitting a pacientes train | Alta | Split por record (no por beat) para train/val/test |
| R7 | **Modelo demasiado grande para edge** | No desplegable en MCU | Media | ~50K params; cuantización TFLite en v0.2 |
| R8 | **PhysioNet downtime** | Pipeline no ejecutable | Baja | Cache local `data/raw/`; skip download si existe |

### 5.2 Estrategia de split (inter-paciente)

Records DS1 (train) vs DS2 (test) según convención AAMI EC57:

| Set | Records |
|-----|---------|
| **DS1** (train+val) | 101, 106, 108, 109, 112, 114, 115, 116, 118, 119, 122, 124, 201, 203, 205, 207, 208, 209, 215, 220, 223, 230 |
| **DS2** (test) | 100, 103, 105, 111, 113, 117, 121, 123, 200, 202, 210, 212, 213, 214, 219, 221, 222, 228, 231, 232, 233, 234 |

> Records 102, 104, 107, 217 excluidos (contienen ritmos paced — superclase Q — que sesgan métricas).

### 5.3 Fuera del alcance v0.1

| Item | Razón |
|------|-------|
| Conversión TFLite / ONNX | Requiere benchmarks MCU reales |
| Multi-lead (2 canales) | AD8232 single-lead; mantener coherencia HW |
| Detección R-peak propia | Usar anotaciones ground-truth MIT-BIH |
| Data augmentation avanzada | Evaluar en v0.2 post-baseline |
| Streaming / real-time inference | Scope batch offline |

---

## 6. Estrategia de Testing

### 6.1 Principio: nunca descargar MIT-BIH en CI

| Nivel | Qué testea | Cómo |
|-------|-----------|------|
| **Unit** | `bandpass_filter` | Señal sintética senoidal (5 Hz + 60 Hz noise). Verificar que 60 Hz atenuada > 20 dB |
| **Unit** | `normalize_signal` | Assert mean ≈ 0, std ≈ 1 |
| **Unit** | `segment_beats` | Array fake 1000 samples, R-peaks en [100, 300, 500]. Verificar shapes y bordes |
| **Unit** | `build_ecg_cnn` | Verificar `model.output_shape`, `model.count_params() < 100_000` |
| **Integration** | Pipeline completo | Mock `wfdb.rdrecord` y `wfdb.rdann` con datos sintéticos |
| **Smoke** | Entrenamiento | 2 epochs con 100 samples fake, verificar loss decrece |

### 6.2 Fixtures clave (`conftest.py`)

```python
import numpy as np
import pytest

@pytest.fixture
def synthetic_ecg_signal() -> np.ndarray:
    """Genera 10 seg de señal ECG-like: sinusoide 1 Hz + ruido."""
    fs = 360
    t = np.linspace(0, 10, fs * 10)
    clean = np.sin(2 * np.pi * 1.0 * t)        # simula QRS ~1 Hz
    noise = 0.05 * np.sin(2 * np.pi * 60 * t)   # powerline
    return clean + noise

@pytest.fixture
def fake_r_peaks() -> np.ndarray:
    """R-peaks cada ~360 samples (1 Hz) en señal de 3600 samples."""
    return np.array([360, 720, 1080, 1440, 1800, 2160, 2520, 2880])

@pytest.fixture
def fake_symbols() -> list[str]:
    return ["N", "N", "V", "N", "A", "N", "F", "N"]
```

### 6.3 Mock de wfdb

```python
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_wfdb_record():
    record = MagicMock()
    record.p_signal = np.random.randn(3600, 2).astype(np.float64)
    record.fs = 360
    record.n_sig = 2
    record.sig_name = ["MLII", "V5"]
    return record
```

---

## 7. Checklist de Aprobación

| # | Criterio | Estado |
|---|----------|--------|
| 1 | Diagrama arquitectura revisado por equipo | ⬜ |
| 2 | Dependencias aprobadas (no conflict con módulos A/C) | ⬜ |
| 3 | Taxonomía AAMI 5-clases validada con literatura | ⬜ |
| 4 | Firmas funciones revisadas (type hints completas) | ⬜ |
| 5 | Split inter-paciente DS1/DS2 confirmado | ⬜ |
| 6 | Ventana segmentación (181 samples) justificada | ⬜ |
| 7 | Modelo < 100K params verificado | ⬜ |
| 8 | Test suite pasa sin acceso red | ⬜ |
| 9 | Riesgos R1-R8 aceptados / mitigaciones aprobadas | ⬜ |
| 10 | Spec aprobado → proceder a implementación | ⬜ |

---

> **Referencia principal:** Hannun, A.Y. et al. "Cardiologist-level arrhythmia detection and classification in ambulatory electrocardiograms using a deep neural network." *Nature Medicine* 25(1):65, 2019. Repo: [`awni/ecg`](https://github.com/awni/ecg).
