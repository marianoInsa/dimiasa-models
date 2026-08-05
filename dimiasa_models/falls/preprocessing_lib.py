"""
preprocessing_lib.py

Módulo reutilizable y testeable para el pipeline ETL de preprocesamiento de datos de caídas.
Transforma datos crudos (capa bronce) a datos resampleados a 100 Hz (capa oro) con filtrado
de calidad de resampleo (capa plata).
"""

import io
import json
from math import gcd
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy.signal import resample_poly, butter, filtfilt
from scipy.stats import pearsonr
from dtaidistance import dtw as dtw_lib

# --- Constantes Globales por Defecto -------------------------------------------
FS_TARGET = 100
KAISER_BETA = 5.0
THR_PEARSON_MIN = 0.85
THR_PHASE_MS_MAX = 100.0
THR_ATTEN_PCT_MAX = 25.0
EVAL_WINDOW_SEC = 2.0

VALID_LABELS = {"Fall", "ADL"}

DATASETS_META = {
    "UPFall": {"fs": 100, "csv": "UPFall-Reduced.csv"},
    "KFall": {"fs": 100, "csv": "KFall-Reduced.csv"},
    "FallAllD": {"fs": 238, "csv": "FallAllD-Reduced.csv"},
    "SisFall": {"fs": 200, "csv": "SisFall-Reduced.csv"},
}

RAW_SCHEMA_COLS = [
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
]

GOLD_SCHEMA_COLS = [
    "Subject",
    "Activity_Label",
    "Activity_Code",
    "Trial",
    "Sample_Index",
    "AVM",
    "GVM",
]

SCHEMA_COLS = GOLD_SCHEMA_COLS

SENSOR_COLS = ["Ax", "Ay", "Az", "Gx", "Gy", "Gz"]
META_COLS = ["Subject", "Activity_Label", "Activity_Code", "Trial"]


# --- Resampleo y Polinomios ---------------------------------------------------
def get_poly_factors(fs_orig: int, fs_target: int = FS_TARGET) -> tuple[int, int]:
    """Devuelve (up, down) reducidos al mínimo común divisor."""
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
    fs_target: int = FS_TARGET,
    kaiser_beta: float = KAISER_BETA,
    schema_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Calcula AVM/GVM desde las 6 señales crudas, resamplea ambas magnitudes y
    reconstruye el DataFrame final.
    """
    if schema_cols is None:
        schema_cols = GOLD_SCHEMA_COLS

    meta = {c: trial_df[c].iloc[0] for c in META_COLS if c in trial_df.columns}

    if not all(col in trial_df.columns for col in SENSOR_COLS):
        missing_cols = [col for col in SENSOR_COLS if col not in trial_df.columns]
        raise ValueError(f"Faltan columnas de señal para calcular AVM/GVM: {missing_cols}")

    avm = np.sqrt(
        trial_df["Ax"].values.astype(float) ** 2
        + trial_df["Ay"].values.astype(float) ** 2
        + trial_df["Az"].values.astype(float) ** 2
    )
    gvm = np.sqrt(
        trial_df["Gx"].values.astype(float) ** 2
        + trial_df["Gy"].values.astype(float) ** 2
        + trial_df["Gz"].values.astype(float) ** 2
    )

    avm_resampled = resample_signal(avm, fs_orig, fs_target, kaiser_beta)
    gvm_resampled = resample_signal(gvm, fs_orig, fs_target, kaiser_beta)

    out = pd.DataFrame({"AVM": avm_resampled, "GVM": gvm_resampled})
    n_out = len(out)
    for c, val in meta.items():
        out[c] = val
    out["Sample_Index"] = np.arange(n_out)

    return out[schema_cols]


# --- Filtro y Métricas de Fidelidad -------------------------------------------
def lowpass(
    signal: np.ndarray,
    fs: int,
    cutoff: float | None = None,
    fs_target: int = FS_TARGET,
) -> np.ndarray:
    """
    Aplica filtro pasa-bajos Butterworth a la señal original para llevarla a la
    misma frecuencia de corte que el objetivo (Nyquist de target = FS_TARGET / 2).
    """
    if cutoff is None:
        cutoff = fs_target / 2.0 - 0.5
    nyq = fs / 2.0

    if cutoff >= nyq * 0.99:
        return signal.copy()
    b, a = butter(8, cutoff / nyq, btype="low")
    return filtfilt(b, a, signal)


def snr_inband(
    orig: np.ndarray,
    resampled: np.ndarray,
    fs_orig: int,
    fs_target: int = FS_TARGET,
) -> float:
    """Calcula SNR (dB) en la banda [0, FS_TARGET/2] Hz."""
    n_orig = len(orig)
    n_res = len(resampled)
    t_orig = np.linspace(0, 1, n_orig)
    t_res = np.linspace(0, 1, n_res)
    resampled_interp = np.interp(t_orig, t_res, resampled)

    orig_filtered = lowpass(orig, fs_orig, fs_target=fs_target)
    noise = orig_filtered - resampled_interp
    power_signal = np.mean(orig_filtered**2)
    power_noise = np.mean(noise**2)
    if power_noise == 0:
        return float("inf")
    return float(10 * np.log10(power_signal / power_noise))


def pearson_inband(
    orig: np.ndarray,
    resampled: np.ndarray,
    fs_orig: int,
    fs_target: int = FS_TARGET,
) -> float:
    """Calcula correlación de Pearson entre original filtrada y resampleada."""
    n_orig = len(orig)
    n_res = len(resampled)
    t_orig = np.linspace(0, 1, n_orig)
    t_res = np.linspace(0, 1, n_res)
    resampled_interp = np.interp(t_orig, t_res, resampled)
    orig_filtered = lowpass(orig, fs_orig, fs_target=fs_target)
    r, _ = pearsonr(orig_filtered, resampled_interp)
    return float(r)


def dtw_normalized(
    orig: np.ndarray,
    resampled: np.ndarray,
    fs_orig: int,
    fs_target: int = FS_TARGET,
    kaiser_beta: float = KAISER_BETA,
) -> float:
    """Distancia DTW normalizada entre original resampleada y señal resampleada."""
    up, down = get_poly_factors(fs_orig, fs_target)
    orig_resample = resample_poly(
        orig, up=up, down=down, window=("kaiser", kaiser_beta)
    )

    def zscore(x):
        s = x.std()
        return (x - x.mean()) / s if s > 0 else x - x.mean()

    a = zscore(orig_resample).astype(np.double)
    b = zscore(resampled).astype(np.double)
    max_len = 500
    if len(a) > max_len:
        a = a[:max_len]
        b = b[:max_len]
    dist = dtw_lib.distance_fast(a, b)
    return float(dist / max(len(a), len(b)))


def peak_phase_shift_ms(
    orig: np.ndarray,
    resampled: np.ndarray,
    fs_orig: int,
    fs_target: int = FS_TARGET,
) -> float:
    """Calcula desfase de pico en milisegundos."""
    t_peak_orig = orig.argmax() / fs_orig
    t_peak_res = resampled.argmax() / fs_target
    return float(abs(t_peak_orig - t_peak_res) * 1000.0)


def peak_attenuation_pct(
    orig: np.ndarray,
    resampled: np.ndarray,
    fs_orig: int,
    fs_target: int = FS_TARGET,
) -> float:
    """Calcula atenuación porcentual del pico relativo a original filtrada."""
    orig_filtered = lowpass(orig, fs_orig, fs_target=fs_target)
    max_orig = np.max(orig_filtered)
    n_res = len(resampled)
    n_orig = len(orig)
    t_orig = np.linspace(0, 1, n_orig)
    t_res = np.linspace(0, 1, n_res)
    resampled_interp = np.interp(t_orig, t_res, resampled)
    max_res = np.max(resampled_interp)
    if max_orig > 0:
        return float(abs(max_orig - max_res) / max_orig * 100.0)
    return 0.0


def analyze_trial(
    trial_df: pd.DataFrame,
    fs_orig: int,
    fs_target: int = FS_TARGET,
    kaiser_beta: float = KAISER_BETA,
    eval_window_sec: float = EVAL_WINDOW_SEC,
) -> dict | None:
    """Analiza un trial calculando métricas de fidelidad para AVM y GVM."""
    avm = np.sqrt(
        trial_df["Ax"] ** 2 + trial_df["Ay"] ** 2 + trial_df["Az"] ** 2
    ).values
    gvm = np.sqrt(
        trial_df["Gx"] ** 2 + trial_df["Gy"] ** 2 + trial_df["Gz"] ** 2
    ).values

    if len(avm) < fs_orig:
        return None

    avm_r = resample_signal(avm, fs_orig, fs_target, kaiser_beta)
    gvm_r = resample_signal(gvm, fs_orig, fs_target, kaiser_beta)

    w = int(eval_window_sec / 2.0 * fs_target)
    peak_r = avm_r.argmax()
    s, e = max(0, peak_r - w), min(len(avm_r), peak_r + w)

    peak_o = avm.argmax()
    wo = int(eval_window_sec / 2.0 * fs_orig)
    so, eo = max(0, peak_o - wo), min(len(avm), peak_o + wo)

    win_avm_orig, win_avm_res = avm[so:eo], avm_r[s:e]
    win_gvm_orig, win_gvm_res = gvm[so:eo], gvm_r[s:e]

    result = {}
    for sensor, orig, resampled in [
        ("AVM", win_avm_orig, win_avm_res),
        ("GVM", win_gvm_orig, win_gvm_res),
    ]:
        result[sensor] = {
            "snr_db": snr_inband(orig, resampled, fs_orig, fs_target),
            "pearson_r": pearson_inband(orig, resampled, fs_orig, fs_target),
            "dtw_norm": dtw_normalized(orig, resampled, fs_orig, fs_target, kaiser_beta),
            "phase_shift_ms": peak_phase_shift_ms(orig, resampled, fs_orig, fs_target),
            "peak_atten_pct": peak_attenuation_pct(orig, resampled, fs_orig, fs_target),
        }
    return result


def run_trial_metrics(
    df: pd.DataFrame,
    fs_orig: int,
    fs_target: int = FS_TARGET,
    label: str = "Fall",
) -> pd.DataFrame:
    """Itera sobre todos los trials de la clase indicada y calcula métricas."""
    falls = df[df["Activity_Label"] == label]
    trials = falls[["Subject", "Activity_Code", "Trial"]].drop_duplicates()

    rows = []
    for _, row in trials.iterrows():
        mask = (
            (falls["Subject"] == row["Subject"])
            & (falls["Activity_Code"] == row["Activity_Code"])
            & (falls["Trial"] == row["Trial"])
        )
        trial_df = falls[mask]
        res = analyze_trial(trial_df, fs_orig, fs_target)
        if res is None:
            continue
        for sensor in ("AVM", "GVM"):
            rows.append(
                {
                    "Subject": row["Subject"],
                    "Activity_Code": row["Activity_Code"],
                    "Trial": row["Trial"],
                    "sensor": sensor,
                    **res[sensor],
                }
            )
    return pd.DataFrame(rows)


# --- Validación e Integridad --------------------------------------------------
def validate_labels(
    df: pd.DataFrame, valid_labels: set[str] | None = None
) -> dict:
    """Verifica que Activity_Label contenga solo valores esperados y no haya mezcla."""
    if valid_labels is None:
        valid_labels = VALID_LABELS

    unique_labels = set(df["Activity_Label"].unique())
    unexpected = unique_labels - valid_labels

    trial_counts = (
        df.groupby(["Subject", "Activity_Code", "Trial"])["Activity_Label"]
        .nunique()
    )
    mixed_trials = trial_counts[trial_counts > 1]

    return {
        "unexpected_labels": unexpected,
        "mixed_trials": mixed_trials,
    }


def filter_valid_trials(
    df_raw: pd.DataFrame,
    df_metrics_acc: pd.DataFrame,
    pearson_min: float = THR_PEARSON_MIN,
    phase_ms_max: float = THR_PHASE_MS_MAX,
    atten_pct_max: float = THR_ATTEN_PCT_MAX,
) -> tuple[list[list], int, int]:
    """
    Cruza trials de clase Fall con sus métricas ACC y filtra trials que no
    cumplen con los umbrales de calidad.
    """
    falls = df_raw[df_raw["Activity_Label"] == "Fall"]
    trial_ids = (
        falls[["Subject", "Activity_Code", "Trial"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    acc_metrics = df_metrics_acc[
        [
            "Subject",
            "Activity_Code",
            "Trial",
            "pearson_r",
            "phase_shift_ms",
            "peak_atten_pct",
        ]
    ]

    merged = trial_ids.merge(
        acc_metrics, on=["Subject", "Activity_Code", "Trial"], how="left"
    )

    discard_mask = (
        merged["pearson_r"].isna()
        | (merged["pearson_r"] < pearson_min)
        | (merged["phase_shift_ms"] > phase_ms_max)
        | (merged["peak_atten_pct"] > atten_pct_max)
    )

    valid_ids = merged.loc[
        ~discard_mask, ["Subject", "Activity_Code", "Trial"]
    ].values.tolist()
    n_valid = len(valid_ids)
    n_discarded = int(discard_mask.sum())

    return valid_ids, n_valid, n_discarded


def validate_schema(df: pd.DataFrame, schema_cols: list[str] | None = None) -> bool:
    """Verifica que el DataFrame contenga exactamente las columnas en el orden indicado."""
    if schema_cols is None:
        schema_cols = SCHEMA_COLS
    return list(df.columns) == schema_cols


# --- Persistencia y Operaciones con Azure Data Lake (Cliente Inyectado) -------
def load_csv_from_bronze(
    service_client,
    container_name: str = "bronce",
    directory_name: str = "falls",
    filename: str = "SisFall-Reduced.csv",
) -> pd.DataFrame:
    """Descarga un CSV desde la capa bronce de Azure Data Lake."""
    fs_client = service_client.get_file_system_client(container_name)
    dir_client = fs_client.get_directory_client(directory_name)
    file_client = dir_client.get_file_client(filename)

    downloaded_bytes = file_client.download_file().readall()
    return pd.read_csv(io.BytesIO(downloaded_bytes))


def save_parquet_to_gold(
    service_client,
    df: pd.DataFrame,
    ds_name: str,
    container_name: str = "oro",
    directory_name: str = "falls",
) -> int:
    """Exporta un DataFrame en formato Parquet a la capa oro de Azure Data Lake."""
    if not validate_schema(df, GOLD_SCHEMA_COLS):
        raise ValueError(
            f"El esquema del DataFrame no coincide con GOLD_SCHEMA_COLS. Columnas actuales: {list(df.columns)}"
        )

    buf = io.BytesIO()
    df.to_parquet(buf, index=False, engine="pyarrow")
    parquet_bytes = buf.getvalue()

    fs_client = service_client.get_file_system_client(container_name)
    dir_client = fs_client.get_directory_client(directory_name)
    file_client = dir_client.get_file_client(f"{ds_name}.parquet")
    file_client.upload_data(parquet_bytes, overwrite=True, length=len(parquet_bytes))

    return len(parquet_bytes)


def save_json_to_silver(
    service_client,
    data: dict,
    filename: str,
    container_name: str = "plata",
    directory_name: str = "falls",
) -> int:
    """Guarda un diccionario JSON en la capa plata de Azure Data Lake."""

    def _to_native(obj):
        if isinstance(obj, dict):
            return {k: _to_native(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_to_native(i) for i in obj]
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return obj

    data_native = _to_native(data)
    json_str = json.dumps(data_native, indent=2, ensure_ascii=False)
    json_bytes = json_str.encode("utf-8")

    fs_client = service_client.get_file_system_client(container_name)
    dir_client = fs_client.get_directory_client(directory_name)
    file_client = dir_client.get_file_client(filename)
    file_client.upload_data(json_bytes, overwrite=True, length=len(json_bytes))

    return len(json_bytes)


def save_csv_to_silver(
    service_client,
    df: pd.DataFrame,
    filename: str,
    container_name: str = "plata",
    directory_name: str = "falls",
) -> int:
    """Guarda un DataFrame CSV en la capa plata de Azure Data Lake."""
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    csv_bytes = buf.getvalue().encode("utf-8")

    fs_client = service_client.get_file_system_client(container_name)
    dir_client = fs_client.get_directory_client(directory_name)
    file_client = dir_client.get_file_client(filename)
    file_client.upload_data(csv_bytes, overwrite=True, length=len(csv_bytes))

    return len(csv_bytes)
