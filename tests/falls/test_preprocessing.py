"""Tests unitarios para dimiasa_models.falls.preprocessing."""

import numpy as np
import pytest
from scipy.fft import rfft, rfftfreq

from dimiasa_models.falls.preprocessing import lowpass_filter, normalize_signal


class TestLowpassFilter:
    """Tests para lowpass_filter — spec §6.1 Unit."""

    def test_output_shape_unchanged(self, synthetic_accel_signal: np.ndarray) -> None:
        result = lowpass_filter(synthetic_accel_signal, fs=200, cutoff=5.0, order=4)
        assert result.shape == synthetic_accel_signal.shape

    def test_output_dtype_float64(self, synthetic_accel_signal: np.ndarray) -> None:
        result = lowpass_filter(synthetic_accel_signal, fs=200, cutoff=5.0)
        assert result.dtype == np.float64

    def test_attenuation_above_cutoff(
        self, synthetic_accel_signal_with_noise: np.ndarray
    ) -> None:
        """Componente 30 Hz debe atenuarse > 20 dB con LP a 5 Hz."""
        fs = 200
        cutoff = 5.0
        sig = synthetic_accel_signal_with_noise
        filtered = lowpass_filter(sig, fs=fs, cutoff=cutoff, order=4)

        # Analizar primer eje
        n = sig.shape[0]
        freqs = rfftfreq(n, d=1.0 / fs)

        mag_orig = np.abs(rfft(sig[:, 0]))
        mag_filt = np.abs(rfft(filtered[:, 0]))

        # Potencia en banda de ruido (25–35 Hz)
        noise_mask = (freqs >= 25) & (freqs <= 35)
        power_orig = np.mean(mag_orig[noise_mask] ** 2)
        power_filt = np.mean(mag_filt[noise_mask] ** 2)

        # Ratio debe ser > 100 (≈ 20 dB)
        assert power_orig > 0, "Potencia original debe ser >0"
        ratio = power_orig / (power_filt + 1e-12)
        assert ratio > 100, f"Atenuación insuficiente: ratio={ratio:.1f} (esperado >100)"

    def test_raises_on_nyquist_violation(
        self, synthetic_accel_signal: np.ndarray
    ) -> None:
        with pytest.raises(ValueError, match="Nyquist"):
            lowpass_filter(synthetic_accel_signal, fs=200, cutoff=100.0)


class TestNormalizeSignal:
    """Tests para normalize_signal — spec §6.1 Unit."""

    def test_minmax_range(self, synthetic_accel_signal: np.ndarray) -> None:
        result = normalize_signal(synthetic_accel_signal, method="minmax")
        assert result.min() >= 0.0 - 1e-9
        assert result.max() <= 1.0 + 1e-9

    def test_minmax_per_axis(self, synthetic_accel_signal: np.ndarray) -> None:
        result = normalize_signal(synthetic_accel_signal, method="minmax")
        for ax in range(3):
            assert result[:, ax].max() <= 1.0 + 1e-9
            assert result[:, ax].min() >= 0.0 - 1e-9

    def test_zscore_mean_zero(self, synthetic_accel_signal: np.ndarray) -> None:
        result = normalize_signal(synthetic_accel_signal, method="zscore")
        for ax in range(3):
            np.testing.assert_allclose(result[:, ax].mean(), 0.0, atol=1e-10)

    def test_zscore_std_one(self, synthetic_accel_signal: np.ndarray) -> None:
        result = normalize_signal(synthetic_accel_signal, method="zscore")
        for ax in range(3):
            np.testing.assert_allclose(result[:, ax].std(), 1.0, atol=1e-6)

    def test_output_shape_unchanged(self, synthetic_accel_signal: np.ndarray) -> None:
        result = normalize_signal(synthetic_accel_signal, method="minmax")
        assert result.shape == synthetic_accel_signal.shape

    def test_invalid_method_raises(self, synthetic_accel_signal: np.ndarray) -> None:
        with pytest.raises(ValueError, match="desconocido"):
            normalize_signal(synthetic_accel_signal, method="l2norm")

    def test_constant_column_no_crash(self) -> None:
        """Señal constante no debe causar división por cero."""
        sig = np.ones((100, 3), dtype=np.float64)
        result_mm = normalize_signal(sig, method="minmax")
        assert not np.any(np.isnan(result_mm))
        result_z = normalize_signal(sig, method="zscore")
        assert not np.any(np.isnan(result_z))
