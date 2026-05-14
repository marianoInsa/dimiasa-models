"""
Punto de entrada para el pipeline de detección de caídas — Módulo A.

Uso:
    uv run python main.py

Requisito previo:
    Dataset SisFall descargado en data/raw/sisfall/
    (al menos 5 sujetos SA0x/ y 5 SE0x/)
"""

import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURACIÓN — editar aquí para ajustar el pipeline
# ---------------------------------------------------------------------------
# Importar la clase de configuración con todos los parámetros del pipeline.
# Puedes instanciar FallsConfig con overrides, por ejemplo:
#   config = FallsConfig(epochs=10, batch_size=32, learning_rate=5e-4)
from dimiasa_models.falls.config import CLASS_NAMES, FallsConfig

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("falls.main")

# ---------------------------------------------------------------------------
# PASO 1: Dataset construction (ingest + preprocess + segment)
# ---------------------------------------------------------------------------
# build_dataset itera sobre los directorios de sujeto en raw_dir,
# aplica filtro Butterworth (lowpass), normalización minmax y ventaneo
# deslizante (window_size, overlap), retornando arrays X/y listos para el modelo.
from dimiasa_models.falls.segmentation import build_dataset, split_by_subject

# ---------------------------------------------------------------------------
# PASO 2: Entrenamiento (train)
# ---------------------------------------------------------------------------
# train_model construye el CNN-LSTM, calcula class_weights para mitigar el
# desbalanceo ADL >> Caídas, y entrena con EarlyStopping + ReduceLROnPlateau.
# El mejor checkpoint se guarda en models/falls/best_model.keras.
from dimiasa_models.falls.train import train_model

# ---------------------------------------------------------------------------
# PASO 3: Evaluación (evaluate)
# ---------------------------------------------------------------------------
# evaluate_model calcula accuracy, F1, precision, recall y especificidad
# sobre el conjunto de test. Guarda confusion_matrix.png y training_curves.png.
from dimiasa_models.falls.evaluate import evaluate_model, plot_training_curves


def main() -> None:
    # Instanciar config (todos los parámetros editables en FallsConfig):
    #   - raw_dir       → dónde están los datos SisFall
    #   - fs / cutoff_freq / filter_order → señal
    #   - window_size / overlap           → segmentación
    #   - epochs / batch_size / learning_rate / test_split → entrenamiento
    config = FallsConfig()

    logger.info("=== Pipeline Módulo A — Detección de Caídas ===")
    logger.info("Config: %s", config)

    # ------------------------------------------------------------------
    # PASO 1: Construcción del dataset
    # Carga archivos .txt SisFall, convierte a g, filtra, normaliza y
    # segmenta en ventanas de %d samples con %d%% overlap.
    # ------------------------------------------------------------------
    logger.info(
        "PASO 1 — Construyendo dataset desde '%s'...",
        config.raw_dir,
    )

    raw_dir = Path(config.raw_dir)
    if not raw_dir.exists():
        logger.error(
            "Directorio de datos no encontrado: '%s'. "
            "Descarga SisFall y coloca los sujetos en esa ruta.",
            raw_dir,
        )
        sys.exit(1)

    X, y, origins = build_dataset(raw_dir, config)
    logger.info("Dataset: X=%s, y=%s", X.shape, y.shape)

    # ------------------------------------------------------------------
    # PASO 2: Split train/test por sujeto
    # Divide los sujetos (no las ventanas) en train/test para evitar
    # data leakage. test_split controla la fracción de sujetos para test.
    # ------------------------------------------------------------------
    logger.info("PASO 2 — Split train/test por sujeto (test_split=%.0f%%)...",
                config.test_split * 100)

    X_train, X_test, y_train, y_test = split_by_subject(
        X, y, origins,
        test_size=config.test_split,
        seed=config.seed,
    )
    logger.info("Train: %d ventanas | Test: %d ventanas", len(y_train), len(y_test))

    # ------------------------------------------------------------------
    # PASO 3: Entrenamiento del modelo CNN-LSTM
    # Usa los últimos 20% del train como validación interna.
    # Para cambiar la arquitectura, editar dimiasa_models/falls/model.py.
    # ------------------------------------------------------------------
    logger.info("PASO 3 — Entrenando modelo CNN-LSTM...")

    # Split interno train → train+val (80/20) para callbacks
    val_split_idx = int(len(y_train) * 0.8)
    X_tr, X_val = X_train[:val_split_idx], X_train[val_split_idx:]
    y_tr, y_val = y_train[:val_split_idx], y_train[val_split_idx:]

    model, history = train_model(X_tr, y_tr, X_val, y_val, config)

    # ------------------------------------------------------------------
    # PASO 4: Evaluación sobre test set
    # Calcula métricas finales y guarda figuras en reports_dir.
    # Para ajustar el umbral de decisión (0.5 por defecto), editar evaluate.py.
    # ------------------------------------------------------------------
    logger.info("PASO 4 — Evaluando modelo en test set...")

    reports_dir = Path(config.reports_dir)
    metrics = evaluate_model(
        model, X_test, y_test,
        output_dir=reports_dir,
        class_names=CLASS_NAMES,
    )

    curves_path = reports_dir / "training_curves.png"
    plot_training_curves(history, output_path=curves_path)

    # ------------------------------------------------------------------
    # Resumen final
    # ------------------------------------------------------------------
    logger.info("=== Resultados finales ===")
    for name, value in metrics.items():
        logger.info("  %-15s %.4f", name, value)
    logger.info("Modelo guardado en '%s'.", config.model_dir / "best_model.keras")
    logger.info("Figuras guardadas en '%s'.", reports_dir)


if __name__ == "__main__":
    main()
