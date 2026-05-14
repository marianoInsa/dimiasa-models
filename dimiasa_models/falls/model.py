"""Arquitectura CNN-LSTM para detección binaria de caídas (Módulo A)."""

from tensorflow import keras


def build_cnn_lstm(
    input_shape: tuple[int, int] = (200, 3),
    num_filters: int = 64,
    kernel_size: int = 5,
    lstm_units: int = 64,
    dropout_rate: float = 0.3,
) -> keras.Model:
    """Construye modelo CNN-LSTM secuencial para clasificación caída/ADL.

    Arquitectura (edge-aware, ~80K params):

    .. code-block:: text

        Input (200, 3)
        → Conv1D(64, 5, padding='same') + BatchNorm + ReLU
        → Conv1D(64, 5, padding='same') + BatchNorm + ReLU
        → MaxPooling1D(2)
        → Dropout(0.3)
        → LSTM(64, return_sequences=False)
        → Dropout(0.3)
        → Dense(32, ReLU)
        → Dense(1, sigmoid)

    Compilado con Adam + BinaryCrossentropy + métricas accuracy y AUC.

    Args:
        input_shape: Forma de cada muestra ``(window_size, n_axes)``.
        num_filters: Número de filtros en capas Conv1D.
        kernel_size: Tamaño de kernel en capas Conv1D.
        lstm_units: Unidades en la capa LSTM.
        dropout_rate: Tasa de dropout aplicada después de pooling y LSTM.

    Returns:
        Modelo Keras compilado listo para entrenamiento.
    """
    inputs = keras.Input(shape=input_shape, name="accel_input")

    # Bloque CNN 1
    x = keras.layers.Conv1D(
        filters=num_filters,
        kernel_size=kernel_size,
        padding="same",
        name="conv1",
    )(inputs)
    x = keras.layers.BatchNormalization(name="bn1")(x)
    x = keras.layers.ReLU(name="relu1")(x)

    # Bloque CNN 2
    x = keras.layers.Conv1D(
        filters=num_filters,
        kernel_size=kernel_size,
        padding="same",
        name="conv2",
    )(x)
    x = keras.layers.BatchNormalization(name="bn2")(x)
    x = keras.layers.ReLU(name="relu2")(x)

    x = keras.layers.MaxPooling1D(pool_size=2, name="maxpool")(x)
    x = keras.layers.Dropout(rate=dropout_rate, name="drop1")(x)

    # LSTM
    x = keras.layers.LSTM(units=lstm_units, return_sequences=False, name="lstm")(x)
    x = keras.layers.Dropout(rate=dropout_rate, name="drop2")(x)

    # Clasificador
    x = keras.layers.Dense(32, activation="relu", name="dense1")(x)
    outputs = keras.layers.Dense(1, activation="sigmoid", name="output")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="cnn_lstm_falls")

    model.compile(
        optimizer=keras.optimizers.Adam(),
        loss="binary_crossentropy",
        metrics=[
            "accuracy",
            keras.metrics.AUC(name="auc"),
        ],
    )
    return model
