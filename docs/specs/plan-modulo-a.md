# Technical Spec — Módulo A: Detección de Caídas (MPU6050)

| Campo        | Valor                                              |
|--------------|-----------------------------------------------------|
| **Proyecto** | DiMIASA — Dispositivo Inteligente Multisensor IoMT  |
| **Componente** | Módulo A — Detección de Caídas (Acelerómetro)     |
| **Tipo**     | Technical Specification (spec-first)                |
| **Versión**  | 0.1.0-draft                                        |
| **Estado**   | 🟡 En revisión                                     |
| **Autor**    | CInApTIC Research Team                              |
| **Fecha**    | 2026-05-13                                          |
| **Sensor HW**| InvenSense MPU6050 (acelerómetro 3 ejes)            |

---

## 1. Arquitectura del Script

### 1.1 Diagrama de flujo

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MÓDULO A — PIPELINE CAÍDAS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌─────────────┐  │
│  │ Kaggle / │───▶│ Ingesta  │───▶│  Butter-  │───▶│Segmentación │  │
│  │ SisFall  │    │ .txt →   │    │  worth LP │    │  sliding    │  │
│  │  (.txt)  │    │ DataFrame│    │  5 Hz 4°  │    │  windows    │  │
│  └──────────┘    └──────────┘    └───────────┘    └──────┬──────┘  │
│                                                          │         │
│                                                          ▼         │
│  ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌─────────────┐  │
│  │Validación│◀───│Entrena-  │◀───│ CNN-LSTM  │◀───│  Split por  │  │
│  │ métricas │    │ miento   │    │  modelo   │    │  sujeto     │  │
│  │ F1/Acc   │    │ Keras    │    │ secuencial│    │ train/test  │  │
│  └────┬─────┘    └──────────┘    └───────────┘    └─────────────┘  │
│       │                                                             │
│       ▼                                                             │
│  ┌──────────┐    ┌──────────┐                                      │
│  │ Export   │───▶│TFLite    │  ← objetivo edge (fuera de v0.1)     │
│  │ modelo   │    │ quant.   │                                      │
│  └──────────┘    └──────────┘                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

data/raw/sisfall/         ← archivos .txt originales (SA01–SA23, SE01–SE15)
data/interim/falls/       ← señales filtradas en .npy
data/processed/falls/     ← ventanas segmentadas + labels
models/falls/             ← pesos .keras
reports/figures/          ← matrices confusión, curvas
```

### 1.2 Principios arquitectónicos

| Principio | Descripción |
|-----------|-------------|
| **Inmutabilidad raw** | `data/raw/` nunca se modifica post-descarga |
| **Reproducibilidad** | Seed global (`42`), versiones pinneadas |
| **Idempotencia** | Re-ejecutar cualquier paso produce mismo resultado |
| **Separación capas** | Ingesta → Filtrado → Segmentación → Modelado → Evaluación como funciones puras |
| **Edge-aware** | Modelo liviano CNN-LSTM; meta < 300 KB post-cuantización |

---

## 2. Dependencias Exactas

### 2.1 Runtime

| Paquete | Versión mín. | Propósito |
|---------|-------------|-----------|
| `numpy` | ≥ 1.26.0 | Arrays señales acelerómetro |
| `pandas` | ≥ 2.2.0 | Lectura .txt tabulares, metadatos |
| `scipy` | ≥ 1.14.0 | `signal.butter`, `signal.sosfiltfilt` lowpass |
| `tensorflow` | ≥ 2.18.0 | Keras integrado, CNN-LSTM |
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
| PyTorch | Proyecto estandarizado en TF/Keras |
| `tsfresh` / `tsfel` | Feature engineering manual; CNN-LSTM extrae features automáticamente |
| Notebooks como pipeline | Solo para exploración; pipeline en `.py` |

---

## 3. Estructura de Datos en Memoria

### 3.1 Archivos SisFall → Objetos Python

Estructura de directorios SisFall (post-descarga Kaggle):

```
data/raw/sisfall/
├── SA01/                    ← Sujeto adulto 01
│   ├── D01_SA01_R01.txt     ← ADL tipo 01, sujeto SA01, trial 01
│   ├── D01_SA01_R02.txt
│   ├── ...
│   ├── F01_SA01_R01.txt     ← Caída tipo 01, sujeto SA01, trial 01
│   └── ...
├── SA02/
├── ...
├── SA23/                    ← 23 adultos jóvenes
├── SE01/                    ← Sujeto adulto mayor 01
├── ...
└── SE15/                    ← 15 adultos mayores
```

Cada `.txt` contiene columnas separadas por comas (sin header):

| Columna | Sensor | Unidad | Descripción |
|---------|--------|--------|-------------|
| 0 | ADXL345 Acc-X | raw ADC | Acelerómetro 1 (no usado) |
| 1 | ADXL345 Acc-Y | raw ADC | Acelerómetro 1 (no usado) |
| 2 | ADXL345 Acc-Z | raw ADC | Acelerómetro 1 (no usado) |
| 3 | ITG3200 Gyro-X | raw ADC | Giroscopio (no usado) |
| 4 | ITG3200 Gyro-Y | raw ADC | Giroscopio (no usado) |
| 5 | ITG3200 Gyro-Z | raw ADC | Giroscopio (no usado) |
| **6** | **MMA8451Q Acc-X** | **raw ADC** | **Acelerómetro 2 — eje X** |
| **7** | **MMA8451Q Acc-Y** | **raw ADC** | **Acelerómetro 2 — eje Y** |
| **8** | **MMA8451Q Acc-Z** | **raw ADC** | **Acelerómetro 2 — eje Z** |

> Columnas 6, 7, 8 (MMA8451Q) simulan al MPU6050 por rango similar (±8g). Conversión a g: `valor_g = valor_raw * (8.0 / 2**14)`.

### 3.2 Taxonomía de clases (binaria v0.1)

Clasificación basada en prefijo del nombre de archivo:

| Clase | Prefijo | Códigos | Cantidad actividades | Label |
|-------|---------|---------|---------------------|-------|
| **ADL** | `D` | D01–D19 | 19 tipos | `0` |
| **Caída** | `F` | F01–F15 | 15 tipos | `1` |

### 3.3 Ventana de segmentación (sliding window)

```
  Señal filtrada (3 ejes, ~N samples @ 200 Hz)
  ════════════════════════════════════════════

  ◄──── window_size=200 ────►
  │     (1.0 seg @ 200 Hz)   │
  └──────────────────────────┘
       ◄── overlap 50% ──►
       │                  │
       └──────────────────────────┘
            ventana siguiente

  Shape por ventana:  (200, 3)   ← 200 timesteps × 3 ejes (X,Y,Z)
  Dataset final:      X.shape = (N_ventanas, 200, 3)
                      y.shape = (N_ventanas,)  con labels 0/1
```

---

## 4. Plan de Implementación Paso a Paso

### 4.1 Constantes y configuración

```python
# dimiasa_models/falls/config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class FallsConfig:
    raw_dir: Path = Path("data/raw/sisfall")
    interim_dir: Path = Path("data/interim/falls")
    processed_dir: Path = Path("data/processed/falls")
    model_dir: Path = Path("models/falls")
    reports_dir: Path = Path("reports/figures/falls")
    fs: int = 200                    # sampling rate Hz
    cutoff_freq: float = 5.0        # lowpass cutoff Hz
    filter_order: int = 4           # Butterworth order
    accel_cols: tuple[int, ...] = (6, 7, 8)  # MMA8451Q X,Y,Z
    accel_range_g: float = 8.0      # rango ±8g
    accel_resolution: int = 14      # bits resolución ADC
    window_size: int = 200          # samples por ventana (1 seg)
    overlap: float = 0.5            # 50% overlap
    seed: int = 42
    batch_size: int = 64
    epochs: int = 50
    learning_rate: float = 1e-3
    test_split: float = 0.2         # split por sujeto

# Sujetos adultos jóvenes y adultos mayores
YOUNG_SUBJECTS: list[str] = [f"SA{i:02d}" for i in range(1, 24)]   # SA01-SA23
ELDERLY_SUBJECTS: list[str] = [f"SE{i:02d}" for i in range(1, 16)] # SE01-SE15

LABEL_MAP: dict[str, int] = {"D": 0, "F": 1}  # ADL=0, Fall=1
```

### 4.2 Ingesta

```python
# dimiasa_models/falls/ingest.py
import numpy as np
import pandas as pd
from numpy.typing import NDArray
from pathlib import Path

def parse_filename(filepath: Path) -> tuple[str, str, str, int]:
    """Extrae metadatos del nombre de archivo SisFall.
    Formato: {activity}_{subject}_{trial}.txt
    Returns: (activity_code, subject_id, activity_type, trial_num)
    Ejemplo: 'F01_SA01_R01.txt' → ('F01', 'SA01', 'F', 1)
    """
    ...

def load_single_file(
    filepath: Path,
    accel_cols: tuple[int, ...] = (6, 7, 8),
) -> NDArray[np.float64]:
    """Lee un .txt SisFall y extrae columnas acelerómetro.
    Maneja líneas corruptas con error_bad_lines=False.
    Returns: array shape (N_samples, 3) en raw ADC units.
    """
    ...

def convert_to_g(
    raw_signal: NDArray[np.float64],
    accel_range_g: float = 8.0,
    resolution_bits: int = 14,
) -> NDArray[np.float64]:
    """Convierte valores raw ADC a unidades g.
    Fórmula: g = raw * (range_g / 2^resolution_bits)
    Returns: array shape (N_samples, 3) en g.
    """
    ...

def load_subject_data(
    subject_dir: Path,
    config: "FallsConfig",
) -> list[tuple[NDArray[np.float64], int, str]]:
    """Carga todos los archivos de un sujeto.
    Returns: lista de (signal_g, label, filename) por archivo.
    """
    ...
```

### 4.3 Preprocesamiento

```python
# dimiasa_models/falls/preprocessing.py
import numpy as np
from numpy.typing import NDArray

def lowpass_filter(
    signal: NDArray[np.float64],
    fs: int,
    cutoff: float,
    order: int = 4,
) -> NDArray[np.float64]:
    """Butterworth lowpass (SOS) + sosfiltfilt (zero-phase).
    Input shape: (N_samples, 3) — 3 ejes acelerómetro.
    Aplica filtro independiente por eje.
    Returns: array filtrado misma shape.
    """
    ...

def normalize_signal(
    signal: NDArray[np.float64],
    method: str = "minmax",
) -> NDArray[np.float64]:
    """Normalización por registro completo.
    Methods: 'minmax' → [0,1], 'zscore' → mean=0 std=1.
    Normaliza cada eje independientemente.
    Returns: array normalizado misma shape.
    """
    ...
```

### 4.4 Segmentación

```python
# dimiasa_models/falls/segmentation.py
import numpy as np
from numpy.typing import NDArray

def sliding_window(
    signal: NDArray[np.float64],
    window_size: int = 200,
    overlap: float = 0.5,
) -> NDArray[np.float64]:
    """Segmenta señal en ventanas deslizantes.
    Input shape: (N_samples, 3).
    Step = window_size * (1 - overlap).
    Descarta última ventana si incompleta.
    Returns: array shape (N_ventanas, window_size, 3).
    """
    ...

def build_dataset(
    raw_dir: "Path",
    config: "FallsConfig",
) -> tuple[NDArray[np.float64], NDArray[np.int8], list[str]]:
    """Pipeline completo: load → filter → normalize → segment → concat.
    Returns: (X, y, subject_origins) para trazabilidad.
    X shape: (N_total_ventanas, window_size, 3)
    y shape: (N_total_ventanas,) con 0=ADL, 1=Fall
    """
    ...

def split_by_subject(
    X: NDArray[np.float64],
    y: NDArray[np.int8],
    subject_origins: list[str],
    test_size: float = 0.2,
    seed: int = 42,
) -> tuple[
    NDArray[np.float64], NDArray[np.float64],
    NDArray[np.int8], NDArray[np.int8],
]:
    """Split train/test por sujeto (no por ventana).
    Evita data leakage: ventanas del mismo sujeto nunca en train y test.
    Estratificación por ratio jóvenes/mayores.
    Returns: (X_train, X_test, y_train, y_test)
    """
    ...
```

### 4.5 Modelo CNN-LSTM

Arquitectura inspirada en paper CNN-LSTM SisFall (1saifj repo), simplificada para edge:

```python
# dimiasa_models/falls/model.py
from tensorflow import keras

def build_cnn_lstm(
    input_shape: tuple[int, int] = (200, 3),
    num_filters: int = 64,
    kernel_size: int = 5,
    lstm_units: int = 64,
    dropout_rate: float = 0.3,
) -> keras.Model:
    """CNN-LSTM secuencial para clasificación binaria caída/ADL.

    Arquitectura:
      Input (200, 3)
      → Conv1D(64, 5) + BN + ReLU
      → Conv1D(64, 5) + BN + ReLU
      → MaxPooling1D(2)
      → Dropout(0.3)
      → LSTM(64, return_sequences=False)
      → Dropout(0.3)
      → Dense(32, ReLU)
      → Dense(1, sigmoid)

    Total params estimados: ~80K
    Compilado: Adam + BinaryCrossentropy
    """
    ...
```

### 4.6 Entrenamiento

```python
# dimiasa_models/falls/train.py
import numpy as np
from numpy.typing import NDArray
from pathlib import Path

def compute_class_weights(y: NDArray[np.int8]) -> dict[int, float]:
    """Calcula pesos inversamente proporcionales a frecuencia clase.
    Usa sklearn.utils.class_weight.compute_class_weight.
    Mitiga desbalanceo ADL >> Falls.
    """
    ...

def train_model(
    X_train: NDArray[np.float64],
    y_train: NDArray[np.int8],
    X_val: NDArray[np.float64],
    y_val: NDArray[np.int8],
    config: "FallsConfig",
    class_weights: dict[int, float] | None = None,
) -> tuple["keras.Model", "keras.callbacks.History"]:
    """Entrena modelo con EarlyStopping + ReduceLROnPlateau.
    Callbacks:
      - EarlyStopping(monitor='val_loss', patience=7)
      - ReduceLROnPlateau(factor=0.5, patience=4)
      - ModelCheckpoint(save_best_only=True)
    Guarda best model en config.model_dir.
    Meta: >96% accuracy.
    """
    ...
```

### 4.7 Evaluación

```python
# dimiasa_models/falls/evaluate.py
import numpy as np
from numpy.typing import NDArray

def evaluate_model(
    model: "keras.Model",
    X_test: NDArray[np.float64],
    y_test: NDArray[np.int8],
) -> dict[str, float]:
    """Genera classification_report, confusion_matrix, F1.
    Guarda plots en reports/figures/falls/.
    Returns: {accuracy, f1, precision, recall, specificity}
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
└── falls/
    ├── __init__.py
    ├── config.py          # FallsConfig dataclass + LABEL_MAP
    ├── ingest.py          # parse_filename, load_single_file, convert_to_g
    ├── preprocessing.py   # lowpass_filter, normalize_signal
    ├── segmentation.py    # sliding_window, build_dataset, split_by_subject
    ├── model.py           # build_cnn_lstm
    ├── train.py           # compute_class_weights, train_model
    └── evaluate.py        # evaluate_model, plot_confusion_matrix

tests/
└── falls/
    ├── __init__.py
    ├── conftest.py        # fixtures: synthetic accel, fake subjects
    ├── test_ingest.py
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
| R1 | **Desbalanceo ADL >> Caídas** (19 ADL × más trials vs 15 caídas × menos trials) | Modelo sesgado clase ADL | Alta | `class_weight` + F1 como métrica principal, no accuracy |
| R2 | **Sesgo SE06** — Único adulto mayor con caídas simuladas. Todas ventanas `label=1` en grupo SE son suyas | Sobreajuste masivo a patrón SE06 | Alta | Aislar SE06 en validación separada o tratar con extremo cuidado en train |
| R3 | **Ruido bordes archivo** — primeros/últimos samples pueden tener artefactos de inicio/fin grabación | Features espurias en ventanas borde | Media | Descartar primeros y últimos 100 samples (0.5 seg) de cada archivo |
| R4 | **Líneas corruptas en .txt** — algunos archivos tienen líneas incompletas o caracteres extra | Crash en parseo | Media | `pd.read_csv` con `on_bad_lines='skip'` + log warning |
| R5 | **Data leakage por split aleatorio** | Accuracy inflada artificialmente | Alta | Split por sujeto, nunca por ventana |
| R6 | **Modelo grande para MCU** | No desplegable en ESP32 | Media | ~80K params; cuantización INT8 TFLite en v0.2 |
| R7 | **Variabilidad sensor** — MMA8451Q ≠ MPU6050 exacto | Inferencia real con offset | Baja | Rango ±8g compatible; calibración en v0.2 con HW real |
| R8 | **Overlap genera ventanas redundantes** | Overfitting a patrones repetidos | Media | Split por sujeto mitiga; evaluar overlap 25% como variante |

### 5.2 Estrategia de split (inter-sujeto)

| Set | Sujetos | Criterio |
|-----|---------|----------|
| **Train** (80%) | ~18 SA + ~12 SE | Stratified por tipo (joven/mayor) |
| **Test** (20%) | ~5 SA + ~3 SE | Mismo ratio joven/mayor que train |

> Split determinístico con `seed=42`. Ninguna ventana de sujeto test aparece en train.

### 5.3 Fuera del alcance v0.1

| Item | Razón |
|------|-------|
| Conversión TFLite / cuantización INT8 | Requiere benchmarks MCU reales |
| Reducción tamaño ventana (100 samples/500ms) | Fase crítica caída dura 300-500ms. Experimentar en futuro para mejorar latencia modelo. |
| Reducción fs (11 Hz) | Filtro LP a 5Hz permite downsampling. Vital para ahorrar RAM en ESP32. Optimización Fase 2. |
| Giroscopio (columnas 3–5) | MPU6050 scope solo acelerómetro v0.1 |
| Clasificación multi-clase (tipo caída) | Evaluar en v0.2 post-baseline binario |
| Data augmentation (jitter, rotation) | Evaluar en v0.2 post-baseline |
| Streaming / real-time inference | Scope batch offline |
| Uso de ADXL345 (columnas 0–2) | Solo MMA8451Q compatible con MPU6050 |

---

## 6. Estrategia de Testing

### 6.1 Principio: nunca descargar SisFall en CI

| Nivel | Qué testea | Cómo |
|-------|-----------|------|
| **Unit** | `parse_filename` | Strings hardcoded: `"F01_SA01_R01.txt"` → `('F01','SA01','F',1)` |
| **Unit** | `lowpass_filter` | Señal sintética 3-ejes (2 Hz + 50 Hz noise). Verificar 50 Hz atenuada > 20 dB |
| **Unit** | `normalize_signal` | Assert min ≈ 0, max ≈ 1 (minmax) ó mean ≈ 0, std ≈ 1 (zscore) |
| **Unit** | `sliding_window` | Array fake (1000, 3), window=200, overlap=0.5 → shape (9, 200, 3) |
| **Unit** | `convert_to_g` | Valor raw 4096 → 8.0 * 4096 / 8192 = 4.0g |
| **Unit** | `build_cnn_lstm` | Verificar `model.output_shape`, `model.count_params() < 150_000` |
| **Integration** | Pipeline completo | Archivos .txt fake en tmpdir con estructura SisFall |
| **Smoke** | Entrenamiento | 2 epochs con 50 ventanas fake, verificar loss decrece |

### 6.2 Fixtures clave (`conftest.py`)

```python
import numpy as np
import pytest
from pathlib import Path

@pytest.fixture
def synthetic_accel_signal() -> np.ndarray:
    """Genera 5 seg de señal acelerómetro 3-ejes sintética."""
    fs = 200
    t = np.linspace(0, 5, fs * 5)
    x = np.sin(2 * np.pi * 2.0 * t) + 0.1 * np.random.randn(len(t))
    y = np.cos(2 * np.pi * 1.5 * t) + 0.1 * np.random.randn(len(t))
    z = np.ones(len(t)) + 0.05 * np.random.randn(len(t))  # gravedad ~1g
    return np.column_stack([x, y, z])

@pytest.fixture
def fake_sisfall_file(tmp_path: Path) -> Path:
    """Crea archivo .txt fake con formato SisFall (9 columnas CSV)."""
    data = np.random.randint(-4096, 4096, size=(1000, 9))
    filepath = tmp_path / "SA01" / "D01_SA01_R01.txt"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(filepath, data, delimiter=",", fmt="%d")
    return filepath

@pytest.fixture
def fake_fall_file(tmp_path: Path) -> Path:
    """Crea archivo .txt fake de caída."""
    data = np.random.randint(-4096, 4096, size=(600, 9))
    # Simular impacto en sample 300
    data[295:310, 6:9] = np.random.randint(3000, 4096, size=(15, 3))
    filepath = tmp_path / "SA01" / "F01_SA01_R01.txt"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(filepath, data, delimiter=",", fmt="%d")
    return filepath
```

---

## 7. Checklist de Aprobación

| # | Criterio | Estado |
|---|----------|--------|
| 1 | Diagrama arquitectura revisado por equipo | ⬜ |
| 2 | Dependencias aprobadas (no conflict con módulos B/C) | ⬜ |
| 3 | Columnas MMA8451Q (6,7,8) confirmadas como proxy MPU6050 | ⬜ |
| 4 | Firmas funciones revisadas (type hints completas) | ⬜ |
| 5 | Split inter-sujeto confirmado (no por ventana) | ⬜ |
| 6 | Ventana segmentación (200 samples, 1 seg) justificada | ⬜ |
| 7 | Modelo < 150K params verificado | ⬜ |
| 8 | Test suite pasa sin acceso red | ⬜ |
| 9 | Riesgos R1-R8 aceptados / mitigaciones aprobadas | ⬜ |
| 10 | Spec aprobado → proceder a implementación | ⬜ |

---

> **Referencias:**
> - Sucerquia, A. et al. "SisFall: A Fall and Movement Dataset." *Sensors* 17(1):198, 2017.
> - Repo inspiración: [`1saifj/Fall-Detection-System-SisFall-Dataset-Raspberry-Pi`](https://github.com/1saifj/Fall-Detection-System-SisFall-Dataset-Raspberry-Pi)
> - Dataset Kaggle: [`nvnikhil0001/sis-fall-original-dataset`](https://www.kaggle.com/datasets/nvnikhil0001/sis-fall-original-dataset)
