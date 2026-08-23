"""Test end-to-end del pipeline ETL sobre CSVs sintéticos (SisFall + UMAFall).

Valida el flujo: carga (io_local) -> check_sanity -> saturation_report ->
resample_trial_df con esquema de oro de 14 columnas.
"""

import numpy as np
import pandas as pd

import pipeline.io_local as io_local
import pipeline.preprocess as pp

COLS = [
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


def _write_dataset(path, n1, n2, saturate, seed):
    rng = np.random.default_rng(seed)

    def block(n):
        return pd.DataFrame(
            {
                "Subject": np.ones(n, dtype=int),
                "Activity_Label": ["Fall"] * n,
                "Activity_Code": np.ones(n, dtype=int),
                "Sample_Index": np.arange(n),
                "Ax": rng.normal(0.0, 2.0, n),
                "Ay": rng.normal(0.0, 2.0, n),
                "Az": rng.normal(1.0, 1.0, n),
                "Gx": rng.normal(0.0, 50.0, n),
                "Gy": rng.normal(0.0, 50.0, n),
                "Gz": rng.normal(0.0, 50.0, n),
            }
        )

    t1 = block(n1)
    t1["Trial"] = 1
    t2 = block(n2)
    t2["Trial"] = 2
    df = pd.concat([t1, t2], ignore_index=True)
    if saturate:
        # Muestras cerca de +-8g para ejercitar saturación (UMAFall ACC_FS=8).
        idx = df.sample(30, random_state=seed).index
        df.loc[idx, "Ax"] = 7.95
    df.to_csv(path, index=False)


def test_e2e_sis_and_uma(tmp_path, monkeypatch):
    io_local.BRONZE_DIR = tmp_path
    io_local.PLATA_DIR = tmp_path / "plata"
    io_local.ORO_DIR = tmp_path / "oro"

    sis_path = tmp_path / "SisFall-Reduced.csv"
    uma_path = tmp_path / "UMAFall-Reduced.csv"
    _write_dataset(sis_path, n1=200, n2=100, saturate=False, seed=1)
    _write_dataset(uma_path, n1=200, n2=100, saturate=True, seed=2)

    # Flujo SisFall: 200 muestras a 200Hz -> 100 Hz (100 muestras).
    sis = io_local.load_csv_local("SisFall-Reduced.csv")
    sanity = pp.check_sanity(sis, "SisFall")
    assert sanity["nan"] == 0

    trial_df = sis[sis["Trial"] == 1].reset_index(drop=True)
    out = pp.resample_trial_df(trial_df, fs_orig=200, ds_name="SisFall")

    assert out.shape[1] == 14
    assert list(out.columns) == pp.SCHEMA_COLS
    assert out["Dataset"].iloc[0] == "SisFall"
    assert out.isna().sum().sum() == 0
    assert len(out) == 100

    # UMAFall: saturación reportada por muestras cerca de +-8g.
    uma = io_local.load_csv_local("UMAFall-Reduced.csv")
    sat = pp.saturation_report(uma, "UMAFall")
    assert sat["Ax_sat_frac"] > 0
