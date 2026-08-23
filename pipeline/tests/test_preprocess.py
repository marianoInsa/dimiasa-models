import numpy as np
import pandas as pd
from pipeline.preprocess import resample_trial_df, SCHEMA_COLS


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
