"""Preprocesamiento de señales acelerómetro para el Módulo A."""

import numpy as np
from numpy.typing import NDArray
from scipy import signal


# ---------------------------------------------------------------------------
# Filtrado paso-bajo
# ---------------------------------------------------------------------------


def lowpass_filter(
    sig: NDArray[np.float64],
    fs: int,
    cutoff: float,
    order: int = 4,
) -> NDArray[np.float64]:
    """Butterworth lowpass (SOS) con zero-phase via ``sosfiltfilt``.

    Aplica el filtro independientemente a cada eje (columna).
    Usa ``sosfiltfilt`` para evitar desfase de fase y mejorar estabilidad
    numérica respecto a ``lfilter`` con coeficientes ba.

    Args:
        sig: Señal cruda shape ``(N_samples, 3)``.
        fs: Frecuencia de muestreo en Hz.
        cutoff: Frecuencia de corte lowpass en Hz.
        order: Orden del filtro Butterworth.

    Returns:
        Señal filtrada misma shape ``(N_samples, 3)``, dtype ``float64``.

    Raises:
        ValueError: Si ``cutoff >= fs / 2`` (violación Nyquist).
    """
    nyq = fs / 2.0
    if cutoff >= nyq:
        raise ValueError(
            f"cutoff ({cutoff} Hz) debe ser menor que Nyquist ({nyq} Hz)."
        )
    sos = signal.butter(order, cutoff / nyq, btype="low", output="sos")
    filtered = np.apply_along_axis(
        lambda col: signal.sosfiltfilt(sos, col),
        axis=0,
        arr=sig,
    )
    return filtered.astype(np.float64)


# ---------------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------------


def normalize_signal(
    sig: NDArray[np.float64],
    method: str = "minmax",
) -> NDArray[np.float64]:
    """Normalización por registro completo, eje a eje.

    Args:
        sig: Array shape ``(N_samples, n_axes)``.
        method: ``'minmax'`` → [0, 1]; ``'zscore'`` → mean=0, std=1.

    Returns:
        Array normalizado misma shape ``float64``.

    Raises:
        ValueError: Si ``method`` no es ``'minmax'`` ni ``'zscore'``.
        RuntimeWarning: (vía numpy) si std=0 en zscore (constante).
    """
    sig = sig.astype(np.float64)
    result = np.empty_like(sig)

    if method == "minmax":
        for ax in range(sig.shape[1]):
            col = sig[:, ax]
            col_min, col_max = col.min(), col.max()
            rng = col_max - col_min
            result[:, ax] = (col - col_min) / rng if rng != 0.0 else np.zeros_like(col)
    elif method == "zscore":
        for ax in range(sig.shape[1]):
            col = sig[:, ax]
            mu, std = col.mean(), col.std()
            result[:, ax] = (col - mu) / std if std != 0.0 else np.zeros_like(col)
    else:
        raise ValueError(
            f"Método de normalización desconocido: '{method}'. "
            "Opciones válidas: 'minmax', 'zscore'."
        )

    return result
