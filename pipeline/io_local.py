"""Capa de IO local para el pipeline ETL de caídas.

Reemplaza Azure Data Lake / Google Colab por lectura y escritura
directa desde el disco (capas bronce/plata/oro).
"""

from __future__ import annotations

import json
import pathlib

import pandas as pd

BRONZE_DIR = pathlib.Path("datasets/bronce")
PLATA_DIR = pathlib.Path("data/plata/falls")
ORO_DIR = pathlib.Path("data/oro/falls")


def load_csv_local(name: str) -> pd.DataFrame:
    """Lee un CSV desde la capa bronce."""
    return pd.read_csv(BRONZE_DIR / name)


def save_parquet_local(df: pd.DataFrame, name: str) -> int:
    """Guarda un DataFrame como Parquet en la capa oro (index=False)."""
    ORO_DIR.mkdir(parents=True, exist_ok=True)
    path = ORO_DIR / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path.stat().st_size


def save_csv_local(df: pd.DataFrame, name: str) -> int:
    """Guarda un DataFrame como CSV en la capa plata (index=False)."""
    PLATA_DIR.mkdir(parents=True, exist_ok=True)
    path = PLATA_DIR / name
    df.to_csv(path, index=False)
    return path.stat().st_size


def save_json_local(data: dict, name: str) -> int:
    """Guarda un diccionario como JSON en la capa plata."""
    PLATA_DIR.mkdir(parents=True, exist_ok=True)
    path = PLATA_DIR / name
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return path.stat().st_size
