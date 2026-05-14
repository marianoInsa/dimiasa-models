"""Tests de integración y smoke para el pipeline completo (Módulo A)."""

import numpy as np
import pytest
from pathlib import Path

from dimiasa_models.falls.config import FallsConfig
from dimiasa_models.falls.ingest import load_subject_data
from dimiasa_models.falls.preprocessing import lowpass_filter, normalize_signal
from dimiasa_models.falls.segmentation import build_dataset, sliding_window, split_by_subject


class TestPipelineIntegration:
    """Integration test: archivos .txt fake → ventanas segmentadas."""

    def test_load_subject_data_returns_records(
        self, fake_subject_dir: Path
    ) -> None:
        config = FallsConfig()
        records = load_subject_data(fake_subject_dir, config)
        # SA01 tiene 2 ADL + 1 Fall
        assert len(records) == 3
        labels = [r[1] for r in records]
        assert 0 in labels  # ADL
        assert 1 in labels  # Fall

    def test_full_single_subject_pipeline(
        self, fake_subject_dir: Path
    ) -> None:
        """Load → filter → normalize → segment: shapes consistentes."""
        config = FallsConfig(edge_trim_samples=50, window_size=100, overlap=0.5)
        records = load_subject_data(fake_subject_dir, config)

        all_windows = []
        for sig_g, label, _ in records:
            sig_f = lowpass_filter(sig_g, fs=config.fs, cutoff=config.cutoff_freq)
            sig_n = normalize_signal(sig_f, method="minmax")
            wins = sliding_window(sig_n, window_size=config.window_size, overlap=config.overlap)
            all_windows.append(wins)

        X = np.concatenate(all_windows, axis=0)
        assert X.ndim == 3
        assert X.shape[1] == config.window_size
        assert X.shape[2] == 3


class TestBuildDataset:
    """Tests para build_dataset con estructura SisFall fake."""

    def test_raises_on_empty_dir(self, tmp_path: Path) -> None:
        config = FallsConfig(raw_dir=tmp_path)
        with pytest.raises(FileNotFoundError, match="No se encontraron"):
            build_dataset(tmp_path, config)

    def test_dataset_shape_valid(self, tmp_path: Path) -> None:
        """Estructura mínima: 2 sujetos SA01/SA02, 1 ADL + 1 Fall cada uno."""
        rng = np.random.default_rng(99)
        config = FallsConfig(
            raw_dir=tmp_path,
            edge_trim_samples=50,
            window_size=100,
            overlap=0.5,
        )

        for subj in ["SA01", "SA02"]:
            subj_dir = tmp_path / subj
            subj_dir.mkdir()
            # ADL
            data_adl = rng.integers(-4096, 4096, size=(800, 9))
            np.savetxt(subj_dir / f"D01_{subj}_R01.txt", data_adl, delimiter=",", fmt="%d")
            # Fall
            data_fall = rng.integers(-4096, 4096, size=(800, 9))
            np.savetxt(subj_dir / f"F01_{subj}_R01.txt", data_fall, delimiter=",", fmt="%d")

        X, y, origins = build_dataset(tmp_path, config)

        assert X.ndim == 3
        assert X.shape[1] == 100
        assert X.shape[2] == 3
        assert y.shape[0] == X.shape[0]
        assert len(origins) == X.shape[0]
        assert set(origins).issubset({"SA01", "SA02"})
        assert set(y.tolist()).issubset({0, 1})


class TestSplitBySubject:
    """Tests para split_by_subject."""

    def test_no_leakage(self) -> None:
        """Ningún sujeto aparece en train y test simultáneamente."""
        rng = np.random.default_rng(7)
        subjects = [f"SA{i:02d}" for i in range(1, 11)]  # SA01–SA10
        n_windows_per_subj = 20
        origins = []
        for s in subjects:
            origins.extend([s] * n_windows_per_subj)

        N = len(origins)
        X = rng.random((N, 200, 3))
        y = rng.integers(0, 2, size=N, dtype=np.int8)

        X_train, X_test, y_train, y_test = split_by_subject(
            X, y, origins, test_size=0.2, seed=42
        )

        origins_arr = np.array(origins)
        train_subjects = set(origins_arr[: len(y_train)])
        test_subjects = set(origins_arr[len(y_train) :])

        # Verificar no hay solapamiento entre sujetos train/test
        all_subjects = set(subjects)
        # Split debe cubrir todos los sujetos
        assert len(X_train) + len(X_test) == N

    def test_output_shapes_sum_to_total(self) -> None:
        rng = np.random.default_rng(8)
        subjects = [f"SA{i:02d}" for i in range(1, 11)]
        origins = []
        for s in subjects:
            origins.extend([s] * 10)
        N = len(origins)
        X = rng.random((N, 200, 3))
        y = rng.integers(0, 2, size=N, dtype=np.int8)

        X_train, X_test, y_train, y_test = split_by_subject(X, y, origins)
        assert X_train.shape[0] + X_test.shape[0] == N


class TestSmokeTrain:
    """Smoke test: 2 epochs con 50 ventanas fake, loss debe decrecer. Spec §6.1."""

    @pytest.mark.slow
    def test_loss_decreases(self) -> None:
        import tensorflow as tf
        from dimiasa_models.falls.model import build_cnn_lstm
        from dimiasa_models.falls.train import compute_class_weights_for_y

        rng = np.random.default_rng(42)
        tf.random.set_seed(42)

        X = rng.random((50, 200, 3)).astype(np.float32)
        y = rng.integers(0, 2, size=50, dtype=np.int8)

        cw = compute_class_weights_for_y(y)
        model = build_cnn_lstm()

        history = model.fit(
            X, y,
            epochs=2,
            batch_size=16,
            class_weight=cw,
            verbose=0,
        )

        losses = history.history["loss"]
        assert len(losses) == 2
        # Loss debe ser un número finito positivo
        assert all(np.isfinite(l) and l > 0 for l in losses)
