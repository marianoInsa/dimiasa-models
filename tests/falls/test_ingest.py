"""Tests unitarios para dimiasa_models.falls.ingest."""

import numpy as np
import pytest
from pathlib import Path

from dimiasa_models.falls.ingest import (
    convert_to_g,
    load_single_file,
    parse_filename,
)


class TestParseFilename:
    """Tests para parse_filename — spec §6.1 Unit."""

    def test_fall_file(self) -> None:
        path = Path("F01_SA01_R01.txt")
        code, subject, atype, trial = parse_filename(path)
        assert code == "F01"
        assert subject == "SA01"
        assert atype == "F"
        assert trial == 1

    def test_adl_file(self) -> None:
        path = Path("D19_SE15_R03.txt")
        code, subject, atype, trial = parse_filename(path)
        assert code == "D19"
        assert subject == "SE15"
        assert atype == "D"
        assert trial == 3

    def test_invalid_format_too_few_parts(self) -> None:
        with pytest.raises(ValueError, match="formato"):
            parse_filename(Path("D01_SA01.txt"))

    def test_invalid_trial_format(self) -> None:
        with pytest.raises(ValueError, match="trial"):
            parse_filename(Path("D01_SA01_01.txt"))

    def test_trial_number_double_digit(self) -> None:
        _, _, _, trial = parse_filename(Path("F15_SA23_R12.txt"))
        assert trial == 12


class TestConvertToG:
    """Tests para convert_to_g — spec §6.1 Unit."""

    def test_known_value_14bit_8g(self) -> None:
        """raw 4096 @ 14-bit ±8g → 2.0g."""
        raw = np.array([[4096, 4096, 4096]], dtype=np.float64)
        result = convert_to_g(raw, accel_range_g=8.0, resolution_bits=14)
        # 8.0 / 2^14 = 8/16384 ≈ 0.000488; 4096 * 0.000488 = 2.0
        np.testing.assert_allclose(result, [[2.0, 2.0, 2.0]], rtol=1e-6)

    def test_spec_example_value(self) -> None:
        """Ejemplo del spec: raw * (8.0 / 2^14). raw=8192 → 4.0g."""
        raw = np.array([[8192, 0, -8192]], dtype=np.float64)
        result = convert_to_g(raw, accel_range_g=8.0, resolution_bits=14)
        np.testing.assert_allclose(result[0, 0], 4.0, rtol=1e-6)
        np.testing.assert_allclose(result[0, 1], 0.0, atol=1e-10)
        np.testing.assert_allclose(result[0, 2], -4.0, rtol=1e-6)

    def test_output_shape_preserved(self) -> None:
        raw = np.random.randint(-8192, 8192, size=(500, 3)).astype(np.float64)
        result = convert_to_g(raw)
        assert result.shape == (500, 3)

    def test_zero_raw_is_zero_g(self) -> None:
        raw = np.zeros((10, 3), dtype=np.float64)
        result = convert_to_g(raw)
        np.testing.assert_array_equal(result, np.zeros((10, 3)))


class TestLoadSingleFile:
    """Tests para load_single_file."""

    def test_loads_correct_columns(self, fake_sisfall_adl_file: Path) -> None:
        result = load_single_file(fake_sisfall_adl_file, accel_cols=(6, 7, 8))
        assert result.ndim == 2
        assert result.shape[1] == 3

    def test_edge_trim_applied(self, fake_sisfall_adl_file: Path) -> None:
        """1000 samples − 2*100 trim = 800."""
        result = load_single_file(
            fake_sisfall_adl_file, accel_cols=(6, 7, 8), edge_trim=100
        )
        assert result.shape[0] == 800

    def test_no_trim(self, fake_sisfall_adl_file: Path) -> None:
        result = load_single_file(
            fake_sisfall_adl_file, accel_cols=(6, 7, 8), edge_trim=0
        )
        assert result.shape[0] == 1000

    def test_output_dtype_float64(self, fake_sisfall_adl_file: Path) -> None:
        result = load_single_file(fake_sisfall_adl_file)
        assert result.dtype == np.float64
