from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import resample_poly

FS_TARGET = 100
KAISER_BETA = 5.0

SENSOR_COLS = ["Ax", "Ay", "Az", "Gx", "Gy", "Gz"]
META_COLS = ["Subject", "Activity_Label", "Activity_Code", "Trial"]

SCHEMA_COLS = [
    "Dataset",
    "Subject",
    "Activity_Label",
    "Activity_Code",
    "Trial",
    "Sample_Index",
    "Ax",
    "Ay",
    "Az",
    "Gx",
    "Gy",
    "Gz",
    "AVM",
    "GVM",
]

DATASETS_META = {
    "UPFall": {"fs": 100, "csv": "UPFall-Reduced.csv"},
    "KFall": {"fs": 100, "csv": "KFall-Reduced.csv"},
    "FallAllD": {"fs": 238, "csv": "FallAllD-Reduced.csv"},
    "SisFall": {"fs": 200, "csv": "SisFall-Reduced.csv"},
    "UMAFall": {"fs": 200, "csv": "UMAFall-Reduced.csv"},
}


def get_poly_factors(fs_orig: int, fs_target: int = FS_TARGET) -> tuple[int, int]:
    """Devuelve (up, down) reducidos al mínimo común divisor."""
    from math import gcd

    g = gcd(fs_target, fs_orig)
    return fs_target // g, fs_orig // g


def resample_signal(
    signal: np.ndarray,
    fs_orig: int,
    fs_target: int = FS_TARGET,
    kaiser_beta: float = KAISER_BETA,
) -> np.ndarray:
    """Resamplea un vector 1D usando resample_poly y ventana Kaiser."""
    up, down = get_poly_factors(fs_orig, fs_target)
    return resample_poly(signal, up=up, down=down, window=("kaiser", kaiser_beta))


def resample_trial_df(
    trial_df: pd.DataFrame,
    fs_orig: int,
    ds_name: str,
    fs_target: int = FS_TARGET,
    kaiser_beta: float = KAISER_BETA,
    schema_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Resamplea los 6 canales crudos y deriva AVM/GVM, con esquema de oro."""
    if schema_cols is None:
        schema_cols = SCHEMA_COLS

    meta = {c: trial_df[c].iloc[0] for c in META_COLS if c in trial_df.columns}

    rs = {
        c: resample_signal(trial_df[c].astype(float).values, fs_orig, fs_target, kaiser_beta)
        for c in SENSOR_COLS
    }

    avm = np.sqrt(rs["Ax"] ** 2 + rs["Ay"] ** 2 + rs["Az"] ** 2)
    gvm = np.sqrt(rs["Gx"] ** 2 + rs["Gy"] ** 2 + rs["Gz"] ** 2)

    out = pd.DataFrame({**rs, "AVM": avm, "GVM": gvm})
    out["Dataset"] = ds_name
    for c, val in meta.items():
        out[c] = val
    out["Sample_Index"] = np.arange(len(out))

    return out[schema_cols]
