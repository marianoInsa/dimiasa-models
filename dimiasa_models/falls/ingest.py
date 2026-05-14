"""Ingesta de datos SisFall (.txt) para el Módulo A — Detección de Caídas."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from dimiasa_models.falls.config import LABEL_MAP, FallsConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Parseo de nombre de archivo
# ---------------------------------------------------------------------------


def parse_filename(filepath: Path) -> tuple[str, str, str, int]:
    """Extrae metadatos del nombre de archivo SisFall.

    Formato esperado: ``{activity}_{subject}_{trial}.txt``
    Ejemplo: ``F01_SA01_R01.txt`` → ``('F01', 'SA01', 'F', 1)``

    Args:
        filepath: Ruta al archivo .txt SisFall.

    Returns:
        Tupla ``(activity_code, subject_id, activity_type, trial_num)``
        donde ``activity_type`` es el prefijo letra (``'D'`` ó ``'F'``).

    Raises:
        ValueError: Si el nombre no respeta el formato esperado.
    """
    stem = filepath.stem  # e.g. "F01_SA01_R01"
    parts = stem.split("_")
    if len(parts) != 3:  # noqa: PLR2004
        raise ValueError(
            f"Nombre de archivo inválido: '{filepath.name}'. "
            "Esperado formato: {{activity}}_{{subject}}_{{trial}}.txt"
        )
    activity_code, subject_id, trial_str = parts
    if not trial_str.startswith("R"):
        raise ValueError(
            f"Componente de trial inválido '{trial_str}' en '{filepath.name}'. "
            "Esperado formato 'R##'."
        )
    trial_num = int(trial_str[1:])
    activity_type = activity_code[0]  # 'D' ó 'F'
    return activity_code, subject_id, activity_type, trial_num


# ---------------------------------------------------------------------------
# Carga de archivo individual
# ---------------------------------------------------------------------------


def load_single_file(
    filepath: Path,
    accel_cols: tuple[int, ...] = (6, 7, 8),
    edge_trim: int = 100,
) -> NDArray[np.float64]:
    """Lee un .txt SisFall y extrae columnas acelerómetro MMA8451Q.

    El archivo SisFall contiene 9 columnas separadas por comas (sin header).
    Columnas 6, 7, 8 → MMA8451Q X, Y, Z (proxy MPU6050).
    Líneas corruptas se omiten con ``on_bad_lines='skip'`` (ver riesgo R4).
    Primeros/últimos ``edge_trim`` samples se descartan (riesgo R3).

    Args:
        filepath: Ruta al archivo .txt.
        accel_cols: Índices de columnas a extraer (default MMA8451Q).
        edge_trim: Número de samples a recortar en cada extremo.

    Returns:
        Array shape ``(N_samples, 3)`` en unidades raw ADC ``float64``.

    Raises:
        ValueError: Si el archivo tiene menos de ``2 * edge_trim + 1`` rows.
    """
    try:
        # SisFall: valores separados por ',' con ';' al final de cada fila.
        # Leer como str, limpiar ';' trailing en última columna, luego castear.
        df = pd.read_csv(
            filepath,
            header=None,
            sep=",",
            skipinitialspace=True,
            on_bad_lines="skip",
            dtype=str,
        )
        # Limpiar ';' al final de la última columna
        df.iloc[:, -1] = df.iloc[:, -1].str.rstrip(";").str.strip()
        df = df.astype(np.float64)
    except Exception as exc:
        logger.warning("Error leyendo '%s': %s. Archivo omitido.", filepath, exc)
        raise

    if df.shape[1] <= max(accel_cols):
        raise ValueError(
            f"Archivo '{filepath}' tiene solo {df.shape[1]} columnas; "
            f"se esperaban al menos {max(accel_cols) + 1}."
        )

    raw = df.iloc[:, list(accel_cols)].to_numpy(dtype=np.float64)

    min_rows = 2 * edge_trim + 1
    if raw.shape[0] < min_rows:
        raise ValueError(
            f"Archivo '{filepath}' tiene {raw.shape[0]} filas, "
            f"insuficiente para recortar {edge_trim} samples en cada extremo."
        )

    # Descartar bordes (riesgo R3: artefactos de inicio/fin de grabación)
    if edge_trim > 0:
        raw = raw[edge_trim:-edge_trim]

    return raw


# ---------------------------------------------------------------------------
# Conversión raw ADC → g
# ---------------------------------------------------------------------------


def convert_to_g(
    raw_signal: NDArray[np.float64],
    accel_range_g: float = 8.0,
    resolution_bits: int = 14,
) -> NDArray[np.float64]:
    """Convierte valores raw ADC a unidades g.

    Fórmula: ``g = raw * (range_g / 2^resolution_bits)``
    Para MMA8451Q 14-bit ±8g: ``g = raw * (8.0 / 16384)``.

    Args:
        raw_signal: Array shape ``(N_samples, 3)`` en raw ADC.
        accel_range_g: Rango del acelerómetro en g (default 8.0).
        resolution_bits: Resolución ADC en bits (default 14 para MMA8451Q).

    Returns:
        Array shape ``(N_samples, 3)`` en g ``float64``.
    """
    scale = accel_range_g / (2**resolution_bits)
    return raw_signal * scale


# ---------------------------------------------------------------------------
# Carga por sujeto
# ---------------------------------------------------------------------------


def load_subject_data(
    subject_dir: Path,
    config: FallsConfig,
) -> list[tuple[NDArray[np.float64], int, str]]:
    """Carga todos los archivos .txt de un directorio de sujeto.

    Cada archivo se lee, recorta bordes, convierte a g y etiqueta según
    prefijo (``'D'`` → 0=ADL, ``'F'`` → 1=Caída).
    Archivos con errores se omiten con warning (robustez riesgo R4).

    Args:
        subject_dir: Directorio del sujeto, e.g. ``data/raw/sisfall/SA01/``.
        config: Instancia de ``FallsConfig`` con parámetros del pipeline.

    Returns:
        Lista de ``(signal_g, label, filename)`` por archivo cargado con éxito.
        ``signal_g`` shape ``(N_samples, 3)`` en g.
    """
    records: list[tuple[NDArray[np.float64], int, str]] = []
    txt_files = sorted(subject_dir.glob("*.txt"))

    if not txt_files:
        logger.warning("Directorio '%s' no contiene archivos .txt.", subject_dir)
        return records

    for filepath in txt_files:
        try:
            _, _, activity_type, _ = parse_filename(filepath)
        except ValueError as exc:
            logger.warning("Nombre inválido '%s': %s. Omitido.", filepath.name, exc)
            continue

        if activity_type not in LABEL_MAP:
            logger.warning(
                "Prefijo desconocido '%s' en '%s'. Omitido.",
                activity_type,
                filepath.name,
            )
            continue

        label = LABEL_MAP[activity_type]

        try:
            raw = load_single_file(
                filepath,
                accel_cols=config.accel_cols,
                edge_trim=config.edge_trim_samples,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("No se pudo cargar '%s': %s. Omitido.", filepath.name, exc)
            continue

        signal_g = convert_to_g(raw, config.accel_range_g, config.accel_resolution)
        records.append((signal_g, label, filepath.name))

    logger.info(
        "Sujeto '%s': %d archivos cargados (%d omitidos).",
        subject_dir.name,
        len(records),
        len(txt_files) - len(records),
    )
    return records
