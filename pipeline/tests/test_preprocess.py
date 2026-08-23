import numpy as np
import pandas as pd
from pipeline.preprocess import resample_trial_df, SCHEMA_COLS, saturation_report, check_sanity, fit_normalizer, apply_normalizer


def test_schema_and_resample():
    t = pd.DataFrame(
        {
            "Subject": [1] * 200,
            "Activity_Label": ["Fall"] * 200,
            "Activity_Code": [1] * 200,
            "Trial": [1] * 200,
            "Sample_Index": range(200),
            "Ax": np.ones(200),
            "Ay": np.zeros(200),
            "Az": np.zeros(200),
            "Gx": np.zeros(200),
            "Gy": np.zeros(200),
            "Gz": np.zeros(200),
        }
    )
    out = resample_trial_df(t, fs_orig=200, ds_name="SisFall")
    assert list(out.columns) == SCHEMA_COLS
    assert len(out) == 100
    # AVM derivada de los ejes: ~1g para constante unitaria en Ax (tolerancia al
    # ripple del filtro Kaiser anti-alias de resample_poly).
    assert abs(out["AVM"].mean() - 1.0) < 0.1
    assert out["Dataset"].iloc[0] == "SisFall"


def test_saturation_detects_clip():
    # 7.95 >= 0.99*8 (7.92) -> clipping contado. (Corregido: 7.9 < 7.92 no contaba.)
    df = pd.DataFrame({"Ax": [7.95] * 100 + [0.0] * 100, "Ay": [0] * 200, "Az": [0] * 200,
        "Gx": [0] * 200, "Gy": [0] * 200, "Gz" : [0] * 200})
    r = saturation_report(df, "UMAFall")  # ACC_FS UMAFall=8
    assert r["Ax_sat_frac"] > 0.4


def test_check_sanity_basic():
    # Canal variado (std>0) para no ser marcado dead; mediana AVM = 1.0 g.
    # (Corregido: canales constantes tienen std==0 y check_sanity los marca dead.)
    df = pd.DataFrame({
        "Ax": [1.0] * 49 + [2.0],
        "Ay": [0.0] * 49 + [0.5],
        "Az": [0.0] * 49 + [0.3],
        "Gx": [0.0] * 49 + [10.0],
        "Gy": [0.0] * 49 + [20.0],
        "Gz": [0.0] * 49 + [5.0],
    })
    r = check_sanity(df, "SisFall")
    assert r["nan"] == 0 and r["dead_channels"] == [] and abs(r["avm_median_g"] - 1.0) < 1e-9


def test_normalizer_zero_mean_unit_std():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"Ax": rng.normal(5.0, 3.0, 2000)})
    st = fit_normalizer(df, ["Ax"])
    out = apply_normalizer(df, st, ["Ax"])
    assert abs(out["Ax"].mean()) < 1e-9
    assert abs(out["Ax"].std() - 1.0) < 1e-9


def test_normalizer_sigma_guard():
    df = pd.DataFrame({"Ax": [1.0] * 10})
    st = fit_normalizer(df, ["Ax"])
    assert st["sigma"]["Ax"] == 1.0  # evita división por cero
