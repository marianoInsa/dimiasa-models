"""Segmentación y construcción del dataset para el Módulo A."""

import logging
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from sklearn.model_selection import train_test_split

from dimiasa_models.falls.config import ALL_SUBJECTS, FallsConfig
from dimiasa_models.falls.ingest import load_subject_data
from dimiasa_models.falls.preprocessing import lowpass_filter, normalize_signal

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Ventana deslizante
# ---------------------------------------------------------------------------


def sliding_window(
    sig: NDArray[np.float64],
    window_size: int = 200,
    overlap: float = 0.5,
) -> NDArray[np.float64]:
    """Segmenta señal multi-eje en ventanas deslizantes.

    ``step = window_size * (1 - overlap)`` (redondeado a entero).
    Última ventana incompleta se descarta.

    Args:
        sig: Señal shape ``(N_samples, n_axes)``.
        window_size: Tamaño de ventana en samples.
        overlap: Fracción de solapamiento [0, 1).

    Returns:
        Array shape ``(N_ventanas, window_size, n_axes)`` ``float64``.

    Raises:
        ValueError: Si ``sig`` tiene menos samples que ``window_size``.
    """
    n_samples, n_axes = sig.shape
    if n_samples < window_size:
        raise ValueError(
            f"Señal con {n_samples} samples es menor que window_size={window_size}."
        )

    step = int(window_size * (1.0 - overlap))
    if step < 1:
        step = 1

    starts = range(0, n_samples - window_size + 1, step)
    windows = np.stack([sig[s : s + window_size] for s in starts], axis=0)
    return windows.astype(np.float64)


# ---------------------------------------------------------------------------
# Pipeline completo de construcción de dataset
# ---------------------------------------------------------------------------


def build_dataset(
    raw_dir: Path,
    config: FallsConfig,
) -> tuple[NDArray[np.float64], NDArray[np.int8], list[str]]:
    """Pipeline completo: load → filter → normalize → segment → concat.

    Itera sobre todos los directorios de sujeto encontrados en ``raw_dir``.
    Solo procesa sujetos cuyo nombre esté en ``ALL_SUBJECTS``.

    Args:
        raw_dir: Directorio raíz SisFall (contiene SA01/, SE01/, ...).
        config: Instancia de ``FallsConfig``.

    Returns:
        Tupla ``(X, y, subject_origins)`` donde:

        - ``X`` shape ``(N_ventanas, window_size, 3)``
        - ``y`` shape ``(N_ventanas,)`` con 0=ADL, 1=Caída
        - ``subject_origins`` lista de longitud ``N_ventanas`` con el
          ID de sujeto de origen de cada ventana (trazabilidad / split).
    """
    X_chunks: list[NDArray[np.float64]] = []
    y_chunks: list[NDArray[np.int8]] = []
    origins: list[str] = []

    subject_dirs = sorted(
        [d for d in raw_dir.iterdir() if d.is_dir() and d.name in ALL_SUBJECTS]
    )

    if not subject_dirs:
        raise FileNotFoundError(
            f"No se encontraron directorios de sujeto SisFall en '{raw_dir}'. "
            "Verificar descarga del dataset."
        )

    for subj_dir in subject_dirs:
        records = load_subject_data(subj_dir, config)
        for sig_g, label, _fname in records:
            # Filtrado paso-bajo
            sig_filtered = lowpass_filter(
                sig_g,
                fs=config.fs,
                cutoff=config.cutoff_freq,
                order=config.filter_order,
            )
            # Normalización minmax
            sig_norm = normalize_signal(sig_filtered, method="minmax")
            # Segmentación
            try:
                windows = sliding_window(
                    sig_norm,
                    window_size=config.window_size,
                    overlap=config.overlap,
                )
            except ValueError:
                logger.warning(
                    "Señal muy corta en sujeto '%s' tras filtrado. Omitida.",
                    subj_dir.name,
                )
                continue

            n_wins = windows.shape[0]
            X_chunks.append(windows)
            y_chunks.append(np.full(n_wins, label, dtype=np.int8))
            origins.extend([subj_dir.name] * n_wins)

    if not X_chunks:
        raise RuntimeError("Dataset vacío: ningún archivo procesado con éxito.")

    X = np.concatenate(X_chunks, axis=0)
    y = np.concatenate(y_chunks, axis=0)
    logger.info(
        "Dataset construido: %d ventanas, %d caídas, %d ADL.",
        len(y),
        int(y.sum()),
        int((y == 0).sum()),
    )
    return X, y, origins


# ---------------------------------------------------------------------------
# Split inter-sujeto (evita data leakage — riesgo R5)
# ---------------------------------------------------------------------------


def split_by_subject(
    X: NDArray[np.float64],
    y: NDArray[np.int8],
    subject_origins: list[str],
    test_size: float = 0.2,
    seed: int = 42,
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.int8],
    NDArray[np.int8],
]:
    """Split train/test por sujeto para evitar data leakage (riesgo R5).

    Nunca mezcla ventanas del mismo sujeto entre train y test.
    Estratificación por tipo de sujeto (joven/mayor) usando prefijo SA/SE.

    Args:
        X: Array shape ``(N_ventanas, window_size, 3)``.
        y: Array shape ``(N_ventanas,)`` con labels 0/1.
        subject_origins: Lista de IDs de sujeto por ventana.
        test_size: Fracción de sujetos para test.
        seed: Semilla aleatoria para reproducibilidad.

    Returns:
        Tupla ``(X_train, X_test, y_train, y_test)``.
    """
    origins_arr = np.array(subject_origins)
    unique_subjects = np.unique(origins_arr)

    # Estratificación: SA → 0, SE → 1
    strat_groups = np.array(
        [0 if s.startswith("SA") else 1 for s in unique_subjects]
    )

    train_subjects, test_subjects = train_test_split(
        unique_subjects,
        test_size=test_size,
        random_state=seed,
        stratify=strat_groups,
    )

    train_mask = np.isin(origins_arr, train_subjects)
    test_mask = np.isin(origins_arr, test_subjects)

    logger.info(
        "Split sujetos — train: %s | test: %s",
        sorted(train_subjects.tolist()),
        sorted(test_subjects.tolist()),
    )

    return X[train_mask], X[test_mask], y[train_mask], y[test_mask]
