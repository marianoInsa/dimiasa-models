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

# Full-scale ranges (g / °/s) por dataset según paper jpm-15-00210-v2 §4.1.3 y
# corrección de ingeniería: UMAFall usa ±8g / ±256°/s, el resto ±16g / ±2000°/s.
ACC_FS = {"SisFall": 16, "FallAllD": 16, "UMAFall": 8, "UPFall": 16, "KFall": 16}
GYRO_FS = {"SisFall": 2000, "FallAllD": 2000, "UMAFall": 256, "UPFall": 2000, "KFall": 2000}


def _sat(df: pd.DataFrame, cols: list[str], fs: float) -> dict:
    """Fracción de muestras por canal en el 99% superior del rango full-scale."""
    return {f"{c}_sat_frac": float((df[c].abs() >= 0.99 * fs).mean()) for c in cols}


def saturation_report(df: pd.DataFrame, ds_name: str) -> dict:
    """Fracciones de saturación/clipping por diferencia de full-scale."""
    return {
        **_sat(df, ["Ax", "Ay", "Az"], ACC_FS[ds_name]),
        **_sat(df, ["Gx", "Gy", "Gz"], GYRO_FS[ds_name]),
    }


def check_sanity(df: pd.DataFrame, ds_name: str) -> dict:
    """Auditoría de unidades físicas: NaNs, gravedad, canales muertos y saturación."""
    nan = int(df[SENSOR_COLS].isna().sum().sum())
    avm = np.sqrt(df["Ax"] ** 2 + df["Ay"] ** 2 + df["Az"] ** 2)
    avm_median_g = float(avm.median())
    dead_channels = [c for c in SENSOR_COLS if df[c].std() == 0]
    return {
        "nan": nan,
        "avm_median_g": avm_median_g,
        "dead_channels": dead_channels,
        **saturation_report(df, ds_name),
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


# Z-score normalizador (paper §4.3). El fit de µ/σ se hace SOLO en train para
# evitar leakage; NO se aplica en el oro.
# ponytail: sigma 0 -> 1.0 para evitar división por cero.
def fit_normalizer(train_df: pd.DataFrame, cols: list[str]) -> dict:
    return {
        "mu": {c: float(train_df[c].mean()) for c in cols},
        "sigma": {c: (float(train_df[c].std()) or 1.0) for c in cols},
    }


def apply_normalizer(df: pd.DataFrame, stats: dict, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = (out[c] - stats["mu"][c]) / stats["sigma"][c]
    return out


# Umbrales de outlier documentados como constantes (ver memory/OUTLIERS.md).
# El IQR usa 1.5; el z-score usa 3 sigma. Los outliers de caída se tratan como
# impactos reales (no ruido) y NO se eliminan.
IQR_K = 1.5
Z_K = 3.0


def outlier_report(df: pd.DataFrame, cols: list[str], method: str = "iqr") -> dict:
    """Conteo de outliers por canal para EDA. method: 'iqr' o 'z'."""
    rep: dict = {}
    for c in cols:
        x = df[c].astype(float)
        if method == "iqr":
            q1, q3 = x.quantile(0.25), x.quantile(0.75)
            iqr = q3 - q1
            lo, hi = q1 - IQR_K * iqr, q3 + IQR_K * iqr
        else:  # 'z'
            mu, sd = x.mean(), x.std()
            lo, hi = mu - Z_K * sd, mu + Z_K * sd
        mask = (x < lo) | (x > hi)
        rep[c] = {
            "n_outliers": int(mask.sum()),
            "frac": float(mask.mean()),
            "bounds": [float(lo), float(hi)],
        }
    return rep
