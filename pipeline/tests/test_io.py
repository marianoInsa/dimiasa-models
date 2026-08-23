"""Tests de la capa de IO local (sin Azure/Colab)."""

import pandas as pd

from pipeline import io_local


def test_roundtrip(tmp_path):
    io_local.BRONZE_DIR = tmp_path
    io_local.PLATA_DIR = tmp_path
    io_local.ORO_DIR = tmp_path

    df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})
    io_local.save_csv_local(df, "x.csv")
    out = io_local.load_csv_local("x.csv")
    assert out["a"].tolist() == [1, 2]


def test_parquet_roundtrip(tmp_path):
    io_local.BRONZE_DIR = tmp_path
    io_local.PLATA_DIR = tmp_path
    io_local.ORO_DIR = tmp_path

    df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})
    io_local.save_parquet_local(df, "y")
    out = pd.read_parquet(io_local.ORO_DIR / "y.parquet")
    assert out["b"].tolist() == [3.0, 4.0]


def test_json_roundtrip(tmp_path):
    io_local.BRONZE_DIR = tmp_path
    io_local.PLATA_DIR = tmp_path
    io_local.ORO_DIR = tmp_path

    io_local.save_json_local({"k": [1, 2]}, "z.json")
    import json

    out = json.loads((io_local.PLATA_DIR / "z.json").read_text())
    assert out == {"k": [1, 2]}
