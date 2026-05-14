"""Fixtures compartidas para tests del Módulo A."""

import numpy as np
import pytest
from pathlib import Path


# ---------------------------------------------------------------------------
# Señales sintéticas
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_accel_signal() -> np.ndarray:
    """5 segundos de señal acelerómetro 3-ejes sintética @ 200 Hz.

    Canal X: componente 2 Hz + ruido.
    Canal Y: componente 1.5 Hz + ruido.
    Canal Z: gravedad constante ~1g + ruido suave.
    """
    rng = np.random.default_rng(42)
    fs = 200
    t = np.linspace(0, 5, fs * 5, endpoint=False)
    x = np.sin(2 * np.pi * 2.0 * t) + 0.1 * rng.standard_normal(len(t))
    y = np.cos(2 * np.pi * 1.5 * t) + 0.1 * rng.standard_normal(len(t))
    z = np.ones(len(t)) + 0.05 * rng.standard_normal(len(t))
    return np.column_stack([x, y, z])


@pytest.fixture
def synthetic_accel_signal_with_noise() -> np.ndarray:
    """Señal con componente 50 Hz (ruido HF) para test de filtrado.

    Mezcla: 2 Hz (señal útil) + 50 Hz (ruido que el LP debe atenuar).
    """
    rng = np.random.default_rng(0)
    fs = 200
    t = np.linspace(0, 5, fs * 5, endpoint=False)
    signal_2hz = np.sin(2 * np.pi * 2.0 * t)
    noise_50hz = 0.5 * np.sin(2 * np.pi * 50.0 * t)  # justo en Nyquist
    # Se usa una frecuencia de ruido que el filtro LP a 5 Hz debe suprimir
    noise_30hz = 0.5 * np.sin(2 * np.pi * 30.0 * t)
    x = signal_2hz + noise_30hz
    y = signal_2hz + noise_30hz
    z = np.ones(len(t)) + noise_30hz
    return np.column_stack([x, y, z])


# ---------------------------------------------------------------------------
# Archivos SisFall fake
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_sisfall_adl_file(tmp_path: Path) -> Path:
    """Archivo .txt fake de ADL (9 columnas, formato SisFall)."""
    rng = np.random.default_rng(1)
    data = rng.integers(-4096, 4096, size=(1000, 9))
    filepath = tmp_path / "SA01" / "D01_SA01_R01.txt"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(filepath, data, delimiter=",", fmt="%d")
    return filepath


@pytest.fixture
def fake_sisfall_fall_file(tmp_path: Path) -> Path:
    """Archivo .txt fake de caída con pico de impacto simulado."""
    rng = np.random.default_rng(2)
    data = rng.integers(-2048, 2048, size=(600, 9))
    # Simular impacto brusco en sample ~300 (pico caída)
    data[295:310, 6:9] = rng.integers(3000, 4096, size=(15, 3))
    filepath = tmp_path / "SA01" / "F01_SA01_R01.txt"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(filepath, data, delimiter=",", fmt="%d")
    return filepath


@pytest.fixture
def fake_subject_dir(tmp_path: Path) -> Path:
    """Directorio de sujeto SA01 con 2 archivos ADL y 1 caída."""
    rng = np.random.default_rng(3)
    subj_dir = tmp_path / "SA01"
    subj_dir.mkdir(parents=True, exist_ok=True)

    for trial in range(1, 3):
        data = rng.integers(-4096, 4096, size=(1000, 9))
        filepath = subj_dir / f"D01_SA01_R{trial:02d}.txt"
        np.savetxt(filepath, data, delimiter=",", fmt="%d")

    # 1 caída
    data_fall = rng.integers(-4096, 4096, size=(800, 9))
    data_fall[400:420, 6:9] = rng.integers(3000, 4096, size=(20, 3))
    filepath_fall = subj_dir / "F01_SA01_R01.txt"
    np.savetxt(filepath_fall, data_fall, delimiter=",", fmt="%d")

    return subj_dir
