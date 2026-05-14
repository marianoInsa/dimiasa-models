"""Configuración global para el pipeline de detección de caídas (Módulo A)."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FallsConfig:
    """Parámetros inmutables del pipeline Módulo A."""

    raw_dir: Path = Path("data/raw/sisfall")
    interim_dir: Path = Path("data/interim/falls")
    processed_dir: Path = Path("data/processed/falls")
    model_dir: Path = Path("models/falls")
    reports_dir: Path = Path("reports/figures/falls")
    # Señal
    fs: int = 200  # sampling rate Hz (SisFall)
    cutoff_freq: float = 5.0  # lowpass cutoff Hz
    filter_order: int = 4  # Butterworth order
    accel_cols: tuple[int, ...] = (6, 7, 8)  # MMA8451Q X,Y,Z
    accel_range_g: float = 8.0  # rango ±8 g
    accel_resolution: int = 14  # bits resolución ADC MMA8451Q
    # Borde de grabación a descartar (samples)
    edge_trim_samples: int = 100  # primeros/últimos 0.5 seg → mitiga artefactos R3
    # Segmentación
    window_size: int = 200  # samples por ventana (1 seg @ 200 Hz)
    overlap: float = 0.5  # 50 % overlap
    # Entrenamiento
    seed: int = 42
    batch_size: int = 64
    epochs: int = 50
    learning_rate: float = 1e-3
    test_split: float = 0.2  # fracción de sujetos para test


# ---------------------------------------------------------------------------
# Listas de sujetos SisFall
# ---------------------------------------------------------------------------

YOUNG_SUBJECTS: list[str] = [f"SA{i:02d}" for i in range(1, 24)]  # SA01–SA23
ELDERLY_SUBJECTS: list[str] = [f"SE{i:02d}" for i in range(1, 16)]  # SE01–SE15
ALL_SUBJECTS: list[str] = YOUNG_SUBJECTS + ELDERLY_SUBJECTS

# ---------------------------------------------------------------------------
# Mapeo de etiquetas
# ---------------------------------------------------------------------------

LABEL_MAP: dict[str, int] = {"D": 0, "F": 1}  # ADL=0, Caída=1
CLASS_NAMES: list[str] = ["ADL", "Fall"]


    