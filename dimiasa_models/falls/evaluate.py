"""Evaluación y visualización del modelo CNN-LSTM (Módulo A)."""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from tensorflow import keras

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Evaluación completa
# ---------------------------------------------------------------------------


def evaluate_model(
    model: keras.Model,
    X_test: NDArray[np.float64],
    y_test: NDArray[np.int8],
    output_dir: Path | None = None,
    class_names: list[str] | None = None,
) -> dict[str, float]:
    """Evalúa modelo y genera reporte + plots de validación.

    Genera:
    - ``classification_report`` en log (nivel INFO)
    - Gráfico matriz confusión → ``output_dir/confusion_matrix.png``
    - Gráfico curva loss/accuracy → ``output_dir/training_curves.png`` (si se provee history)

    Args:
        model: Modelo Keras entrenado.
        X_test: Array shape ``(N_test, window_size, 3)``.
        y_test: Labels ground truth shape ``(N_test,)``.
        output_dir: Directorio donde guardar figuras. Si ``None``, no guarda.
        class_names: Nombres de clases para plots. Default ``['ADL', 'Fall']``.

    Returns:
        Diccionario con métricas escalares::

            {
                'accuracy': float,
                'f1': float,
                'precision': float,
                'recall': float,
                'specificity': float,
            }
    """
    if class_names is None:
        class_names = ["ADL", "Fall"]

    # Predicciones
    y_prob = model.predict(X_test, verbose=0).squeeze()
    y_pred = (y_prob >= 0.5).astype(np.int8)

    # Métricas escalares
    accuracy = float((y_pred == y_test).mean())
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))

    # Especificidad = TN / (TN + FP)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp = cm[0, 0], cm[0, 1]
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    metrics = {
        "accuracy": accuracy,
        "f1": f1,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
    }

    # Log report completo
    report = classification_report(y_test, y_pred, target_names=class_names)
    logger.info("Classification report:\n%s", report)
    logger.info("Métricas resumen: %s", metrics)

    # Guardar figuras
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        cm_path = output_dir / "confusion_matrix.png"
        plot_confusion_matrix(
            y_test,
            y_pred,
            class_names=class_names,
            output_path=cm_path,
        )

    return metrics


# ---------------------------------------------------------------------------
# Confusion matrix heatmap
# ---------------------------------------------------------------------------


def plot_confusion_matrix(
    y_true: NDArray[np.int8],
    y_pred: NDArray[np.int8],
    class_names: list[str],
    output_path: Path,
) -> None:
    """Genera y guarda heatmap normalizado de la matriz confusión.

    Args:
        y_true: Labels verdaderos shape ``(N,)``.
        y_pred: Labels predichos shape ``(N,)``.
        class_names: Lista de nombres de clases (e.g. ``['ADL', 'Fall']``).
        output_path: Ruta de destino para la figura PNG.
    """
    cm = confusion_matrix(y_true, y_pred, normalize="true")

    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, colorbar=True, cmap="Blues", values_format=".2f")
    ax.set_title("Confusion Matrix (normalized) — Módulo A", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Confusion matrix guardada en '%s'.", output_path)


# ---------------------------------------------------------------------------
# Curvas de entrenamiento
# ---------------------------------------------------------------------------


def plot_training_curves(
    history: keras.callbacks.History,
    output_path: Path,
) -> None:
    """Genera gráfico de curvas loss y accuracy (train vs val).

    Args:
        history: Objeto History retornado por ``model.fit``.
        output_path: Ruta destino PNG.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Loss
    axes[0].plot(history.history["loss"], label="train")
    axes[0].plot(history.history["val_loss"], label="val")
    axes[0].set_title("Binary Crossentropy Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()

    # Accuracy
    axes[1].plot(history.history["accuracy"], label="train")
    axes[1].plot(history.history["val_accuracy"], label="val")
    axes[1].set_title("Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].legend()

    plt.suptitle("Módulo A — Curvas de Entrenamiento", fontsize=13)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Training curves guardadas en '%s'.", output_path)
