"""Tests unitarios para dimiasa_models.falls.model."""

import pytest

# Skip todo el módulo si tensorflow no está instalado
tf = pytest.importorskip("tensorflow", reason="tensorflow no instalado")


class TestBuildCnnLstm:
    """Tests para build_cnn_lstm — spec §6.1 Unit."""

    @pytest.fixture(scope="class")
    def model(self):
        """Importación lazy de TF para evitar overhead en otros tests."""
        from dimiasa_models.falls.model import build_cnn_lstm

        return build_cnn_lstm()

    def test_output_shape(self, model) -> None:
        """Output shape debe ser (None, 1) — clasificación binaria."""
        assert model.output_shape == (None, 1)

    def test_input_shape(self, model) -> None:
        """Input shape debe ser (None, 200, 3)."""
        assert model.input_shape == (None, 200, 3)

    def test_param_count_below_150k(self, model) -> None:
        """Meta del spec: < 150_000 parámetros (§6.1 + §7 criterio 7)."""
        n_params = model.count_params()
        assert n_params < 150_000, (
            f"Modelo tiene {n_params:,} params, supera límite 150K. "
            "Reducir num_filters o lstm_units."
        )

    def test_model_compiled(self, model) -> None:
        """Modelo debe estar compilado (optimizer asignado)."""
        assert model.optimizer is not None

    def test_custom_input_shape(self) -> None:
        from dimiasa_models.falls.model import build_cnn_lstm

        m = build_cnn_lstm(input_shape=(100, 3), num_filters=32, lstm_units=32)
        assert m.input_shape == (None, 100, 3)
        assert m.output_shape == (None, 1)
