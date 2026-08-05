"""
test_preprocessing_lib.py

Tests unitarios para preprocessing_lib.py utilizando pytest y unittest.mock.
Verifica la funcionalidad del pipeline de preprocesamiento sobre datos sintéticos.
"""

import io
from unittest.mock import MagicMock
import numpy as np
import pandas as pd
import pytest

from preprocessing_lib import (
    FS_TARGET,
    KAISER_BETA,
    GOLD_SCHEMA_COLS,
    RAW_SCHEMA_COLS,
    SCHEMA_COLS,
    filter_valid_trials,
    get_poly_factors,
    load_csv_from_bronze,
    peak_attenuation_pct,
    pearson_inband,
    resample_signal,
    resample_trial_df,
    save_parquet_to_gold,
    validate_labels,
    validate_schema,
)


# --- Fixtures y Funciones de Ayuda para Datos Sintéticos -----------------------
def make_sine_signal(
    fs: int = 200, duration_sec: float = 2.0, freq_hz: float = 2.0
) -> np.ndarray:
    """Genera una señal senoidal sintética pura."""
    t = np.linspace(0, duration_sec, int(fs * duration_sec), endpoint=False)
    return np.sin(2 * np.pi * freq_hz * t) + 1.5  # Desplazamiento positivo


def make_synthetic_trial_df(
    subject: str = "S01",
    activity_label: str = "Fall",
    activity_code: str = "F01",
    trial: int = 1,
    fs: int = 200,
    duration_sec: float = 2.0,
) -> pd.DataFrame:
    """Genera un DataFrame sintético para un trial individual."""
    n_samples = int(fs * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    ax = np.sin(2 * np.pi * 1.5 * t)
    ay = np.cos(2 * np.pi * 1.5 * t)
    az = np.sin(2 * np.pi * 3.0 * t) + 1.0
    gx = np.sin(2 * np.pi * 0.5 * t) * 10
    gy = np.cos(2 * np.pi * 0.5 * t) * 10
    gz = np.zeros(n_samples)

    return pd.DataFrame(
        {
            "Subject": subject,
            "Activity_Label": activity_label,
            "Activity_Code": activity_code,
            "Trial": trial,
            "Sample_Index": np.arange(n_samples),
            "Ax": ax,
            "Ay": ay,
            "Az": az,
            "Gx": gx,
            "Gy": gy,
            "Gz": gz,
        }
    )


# --- 1. Factor de reducción de resampleo ---------------------------------------
def test_poly_factors_reduccion():
    """get_poly_factors devuelve factores reducidos al MCD para pares conocidos."""
    # 200 -> 100 Hz
    up, down = get_poly_factors(200, 100)
    assert (up, down) == (1, 2)

    # 238 -> 100 Hz (gcd(100, 238) = 2 -> up=50, down=119)
    up, down = get_poly_factors(238, 100)
    assert (up, down) == (50, 119)

    # 100 -> 100 Hz
    up, down = get_poly_factors(100, 100)
    assert (up, down) == (1, 1)


# --- 2. Passthrough a misma frecuencia -----------------------------------------
def test_resample_passthrough_misma_frecuencia():
    """Si fs_orig == fs_target (KFall/UPFall), no cambia cantidad de muestras ni introduce NaNs."""
    signal = make_sine_signal(fs=100, duration_sec=3.0, freq_hz=2.0)
    resampled = resample_signal(signal, fs_orig=100, fs_target=100)

    assert len(resampled) == len(signal)
    assert not np.isnan(resampled).any()
    # La señal debe coincidir casi exactamente
    assert resampled == pytest.approx(signal, rel=0.05, abs=0.05)


# --- 3. Métricas para señal idéntica -------------------------------------------
def test_metricas_señal_identica():
    """Comparar señal sintética contra sí misma -> pearson_r ≈ 1.0, peak_attenuation_pct ≈ 0."""
    sig = make_sine_signal(fs=100, duration_sec=2.0, freq_hz=2.0)
    r = pearson_inband(sig, sig, fs_orig=100, fs_target=100)
    atten = peak_attenuation_pct(sig, sig, fs_orig=100, fs_target=100)

    assert r == pytest.approx(1.0, rel=1e-2)
    assert atten == pytest.approx(0.0, abs=1e-2)


# --- 4. Métricas para señal degradada -----------------------------------------
def test_metricas_señal_degradada():
    """Comparar señal sintética contra versión ruidosa/atenuada -> métricas reflejan degradación."""
    sig_orig = make_sine_signal(fs=200, duration_sec=2.0, freq_hz=3.0)
    sig_resampled = resample_signal(sig_orig, fs_orig=200, fs_target=100)

    # Inyectar ruido gaussiano fuerte y atenuar
    rng = np.random.default_rng(42)
    noise = rng.normal(0, 1.5, len(sig_resampled))
    sig_degraded = (sig_resampled * 0.4) + noise

    r = pearson_inband(sig_orig, sig_degraded, fs_orig=200, fs_target=100)
    atten = peak_attenuation_pct(sig_orig, sig_degraded, fs_orig=200, fs_target=100)

    # La correlación cae y/o la atenuación es alta
    assert r < 0.85 or atten > 25.0


# --- 5. Filtrado de trials por calidad -----------------------------------------
def test_filtrado_descarta_trial_malo_y_conserva_bueno():
    """filter_valid_trials conserva trial bueno y descarta trial malo."""
    df_raw = pd.DataFrame(
        [
            {
                "Subject": "S01",
                "Activity_Code": "F01",
                "Trial": 1,
                "Activity_Label": "Fall",
            },
            {
                "Subject": "S01",
                "Activity_Code": "F01",
                "Trial": 2,
                "Activity_Label": "Fall",
            },
        ]
    )

    df_metrics = pd.DataFrame(
        [
            # Trial 1: Bueno (pasa todos los umbrales)
            {
                "Subject": "S01",
                "Activity_Code": "F01",
                "Trial": 1,
                "pearson_r": 0.95,
                "phase_shift_ms": 10.0,
                "peak_atten_pct": 5.0,
            },
            # Trial 2: Malo (falla pearson_r < 0.85)
            {
                "Subject": "S01",
                "Activity_Code": "F01",
                "Trial": 2,
                "pearson_r": 0.60,
                "phase_shift_ms": 150.0,
                "peak_atten_pct": 30.0,
            },
        ]
    )

    valid_ids, n_valid, n_discarded = filter_valid_trials(
        df_raw, df_metrics, pearson_min=0.85, phase_ms_max=100.0, atten_pct_max=25.0
    )

    assert n_valid == 1
    assert n_discarded == 1
    assert valid_ids == [["S01", "F01", 1]]


# --- 6. Validación de etiquetas: valor inesperado ------------------------------
def test_validacion_labels_detecta_valor_inesperado():
    """validate_labels reporta valores fuera de {'Fall', 'ADL'}."""
    df = pd.DataFrame(
        {
            "Subject": ["S01", "S01", "S02"],
            "Activity_Code": ["F01", "F02", "A01"],
            "Trial": [1, 1, 1],
            "Activity_Label": ["Fall", "Faint", "ADL"],
        }
    )

    res = validate_labels(df)
    assert "Faint" in res["unexpected_labels"]


# --- 7. Validación de etiquetas: trial mixto ----------------------------------
def test_validacion_labels_detecta_trial_mixto():
    """validate_labels detecta trial que mezcla 'Fall' y 'ADL'."""
    df = pd.DataFrame(
        {
            "Subject": ["S01", "S01", "S01", "S01"],
            "Activity_Code": ["F01", "F01", "F01", "F01"],
            "Trial": [1, 1, 1, 1],
            "Activity_Label": ["Fall", "Fall", "ADL", "Fall"],
        }
    )

    res = validate_labels(df)
    assert len(res["mixed_trials"]) == 1


# --- 8. Esquema de salida: columnas y orden ------------------------------------
def test_esquema_salida_columnas_y_orden():
    """DataFrame resampleado tiene exactamente las 7 columnas AVM/GVM en el orden requerido."""
    trial_df = make_synthetic_trial_df(fs=200)
    out_df = resample_trial_df(trial_df, fs_orig=200, fs_target=100)

    assert list(out_df.columns) == GOLD_SCHEMA_COLS
    assert validate_schema(out_df)
    assert SCHEMA_COLS == GOLD_SCHEMA_COLS


def test_resample_trial_df_genera_avm_y_gvm():
    """resample_trial_df debe derivar magnitudes y descartar ejes crudos en salida."""
    trial_df = make_synthetic_trial_df(fs=200)
    out_df = resample_trial_df(trial_df, fs_orig=200, fs_target=100)

    assert list(out_df.columns) == [
        "Subject",
        "Activity_Label",
        "Activity_Code",
        "Trial",
        "Sample_Index",
        "AVM",
        "GVM",
    ]
    assert len(out_df) == 200
    assert np.isfinite(out_df[["AVM", "GVM"]].to_numpy()).all()
    assert (out_df["AVM"] >= 0).all()
    assert (out_df["GVM"] >= 0).all()


# --- 9. Reinicio de Sample_Index -----------------------------------------------
def test_sample_index_reinicia_por_trial():
    """Sample_Index es una secuencia 0..N-1 sin huecos tras el resampleo."""
    trial_df = make_synthetic_trial_df(fs=200, duration_sec=2.0)
    out_df = resample_trial_df(trial_df, fs_orig=200, fs_target=100)

    n_samples = len(out_df)
    assert n_samples == 200  # 2.0s a 100 Hz
    np.testing.assert_array_equal(out_df["Sample_Index"].values, np.arange(n_samples))


# --- 10. Carga desde bronce con mock de Azure ----------------------------------
def test_carga_bronce_con_mock_azure():
    """Carga CSV desde bronce usando cliente Azure mockeado."""
    synthetic_csv = (
        "Subject,Activity_Label,Activity_Code,Trial,Sample_Index,Ax,Ay,Az,Gx,Gy,Gz\n"
        "S01,Fall,F01,1,0,0.1,0.2,9.8,0.0,0.0,0.0\n"
    ).encode("utf-8")

    # Mocks en cascada
    mock_file_client = MagicMock()
    mock_file_client.download_file.return_value.readall.return_value = (
        synthetic_csv
    )

    mock_dir_client = MagicMock()
    mock_dir_client.get_file_client.return_value = mock_file_client

    mock_fs_client = MagicMock()
    mock_fs_client.get_directory_client.return_value = mock_dir_client

    mock_service_client = MagicMock()
    mock_service_client.get_file_system_client.return_value = mock_fs_client

    df = load_csv_from_bronze(
        mock_service_client, "bronce", "falls", "SisFall-Reduced.csv"
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert list(df.columns) == RAW_SCHEMA_COLS


# --- 11. Guardado en oro con mock de Azure -------------------------------------
def test_guardado_oro_con_mock_azure():
    """Verifica que save_parquet_to_gold sube datos Parquet válidos."""
    trial_df = make_synthetic_trial_df(fs=100, duration_sec=1.0)
    out_df = resample_trial_df(trial_df, fs_orig=100, fs_target=100)

    mock_file_client = MagicMock()

    mock_dir_client = MagicMock()
    mock_dir_client.get_file_client.return_value = mock_file_client

    mock_fs_client = MagicMock()
    mock_fs_client.get_directory_client.return_value = mock_dir_client

    mock_service_client = MagicMock()
    mock_service_client.get_file_system_client.return_value = mock_fs_client

    bytes_written = save_parquet_to_gold(
        mock_service_client, out_df, "SisFall", "oro", "falls"
    )

    assert bytes_written > 0
    mock_file_client.upload_data.assert_called_once()

    # Inspeccionar bytes subidos
    args, kwargs = mock_file_client.upload_data.call_args
    uploaded_bytes = args[0]
    df_read = pd.read_parquet(io.BytesIO(uploaded_bytes))
    assert list(df_read.columns) == SCHEMA_COLS
    assert len(df_read) == 100
