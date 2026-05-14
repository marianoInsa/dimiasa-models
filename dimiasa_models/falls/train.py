"""Entrenamiento del modelo CNN-LSTM para el Módulo A — Detección de Caídas."""

import logging
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from sklearn.utils.class_weight import compute_class_weight
from tensorflow import keras

from dimiasa_models.falls.config import FallsConfig
from dimiasa_models.falls.model import build_cnn_lstm

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pesos de clase (mitiga desbalanceo ADL >> Caídas — riesgo R1)
# ---------------------------------------------------------------------------


def compute_class_weights_for_y(y: NDArray[np.int8]) -> dict[int, float]:
    """Pesos inversamente proporcionales a frecuencia de clase.

    Usa ``sklearn.utils.class_weight.compute_class_weight`` con
    ``class_weight='balanced'``. Mitiga desbalanceo ADL >> Caídas (riesgo R1).

    Args:
        y: Array 1D de labels ``{0, 1}``.

    Returns:
        Diccionario ``{0: peso_ADL, 1: peso_Fall}``.
    """
    classes = np.unique(y)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=y,
    )
    cw = dict(zip(classes.tolist(), weights.tolist()))
    logger.info("Class weights: %s", cw)
    return cw


# ---------------------------------------------------------------------------
# Entrenamiento principal
# ---------------------------------------------------------------------------


def train_model(
    X_train: NDArray[np.float64],
    y_train: NDArray[np.int8],
    X_val: NDArray[np.float64],
    y_val: NDArray[np.int8],
    config: FallsConfig,
    class_weights: dict[int, float] | None = None,
) -> tuple[keras.Model, keras.callbacks.History]:
    """Entrena modelo CNN-LSTM con callbacks y guarda mejor checkpoint.

    Callbacks usados:

    - ``EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True)``
    - ``ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-6)``
    - ``ModelCheckpoint(save_best_only=True)``

    El mejor modelo se guarda en ``config.model_dir / 'best_model.keras'``.

    Args:
        X_train: Array shape ``(N_train, window_size, 3)``.
        y_train: Labels train shape ``(N_train,)``.
        X_val: Array shape ``(N_val, window_size, 3)``.
        y_val: Labels val shape ``(N_val,)``.
        config: Instancia de ``FallsConfig``.
        class_weights: Si ``None``, se calculan automáticamente desde ``y_train``.

    Returns:
        Tupla ``(model, history)`` con el modelo entrenado y el historial Keras.
    """
    # Directorios
    config.model_dir.mkdir(parents=True, exist_ok=True)
    best_model_path = config.model_dir / "best_model.keras"

    # Pesos de clase
    if class_weights is None:
        class_weights = compute_class_weights_for_y(y_train)

    # Modelo
    model = build_cnn_lstm(
        input_shape=(config.window_size, len(config.accel_cols)),
    )
    # Sobreescribir learning rate desde config
    model.optimizer.learning_rate.assign(config.learning_rate)

    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=7,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=4,
            min_lr=1e-6,
            verbose=1,
        ),
        keras.callbacks.ModelCheckpoint(
            filepath=str(best_model_path),
            monitor="val_loss",
            save_best_only=True,
            verbose=1,
        ),
    ]

    logger.info(
        "Iniciando entrenamiento: %d epochs, batch=%d, lr=%.0e",
        config.epochs,
        config.batch_size,
        config.learning_rate,
    )

    history = model.fit(
        X_train,
        y_train,
        validation_data=(X_val, y_val),
        epochs=config.epochs,
        batch_size=config.batch_size,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=2,
    )

    logger.info("Modelo guardado en '%s'.", best_model_path)
    return model, history
