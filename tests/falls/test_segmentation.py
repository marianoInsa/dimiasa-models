"""Tests unitarios para dimiasa_models.falls.segmentation."""

import numpy as np
import pytest

from dimiasa_models.falls.segmentation import sliding_window


class TestSlidingWindow:
    """Tests para sliding_window — spec §6.1 Unit."""

    def test_spec_example_shape(self) -> None:
        """Array (1000, 3), window=200, overlap=0.5 → (9, 200, 3). Spec §6.1."""
        sig = np.random.default_rng(0).random((1000, 3))
        result = sliding_window(sig, window_size=200, overlap=0.5)
        assert result.shape == (9, 200, 3)

    def test_no_overlap(self) -> None:
        """1000 samples, window=200, overlap=0 → 5 ventanas."""
        sig = np.ones((1000, 3))
        result = sliding_window(sig, window_size=200, overlap=0.0)
        assert result.shape == (5, 200, 3)

    def test_exact_fit(self) -> None:
        """400 samples, window=200, overlap=0 → 2 ventanas (sin descarte)."""
        sig = np.ones((400, 3))
        result = sliding_window(sig, window_size=200, overlap=0.0)
        assert result.shape == (2, 200, 3)

    def test_incomplete_last_window_discarded(self) -> None:
        """350 samples, window=200, step=200 → 1 ventana (última incompleta descartada)."""
        sig = np.ones((350, 3))
        result = sliding_window(sig, window_size=200, overlap=0.0)
        assert result.shape[0] == 1

    def test_window_content_correct(self) -> None:
        """Primera ventana debe contener samples 0:200."""
        sig = np.arange(600).reshape(-1, 3).astype(np.float64)
        result = sliding_window(sig, window_size=10, overlap=0.0)
        np.testing.assert_array_equal(result[0], sig[0:10])

    def test_output_dtype_float64(self) -> None:
        sig = np.ones((500, 3), dtype=np.float32)
        result = sliding_window(sig, window_size=100, overlap=0.5)
        assert result.dtype == np.float64

    def test_raises_if_signal_shorter_than_window(self) -> None:
        sig = np.ones((100, 3))
        with pytest.raises(ValueError, match="menor que window_size"):
            sliding_window(sig, window_size=200)
