"""
training_lib.py

Training pipeline library for binary fall detection using CNN-LSTM.
Loads preprocessed data from Azure gold layer, maps to unified taxonomy,
performs subject-wise cross-validation with windowing and class balancing,
trains tf.keras models, and evaluates with detailed per-fall-type metrics.
"""

import io
import json
import os
import tempfile
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, GroupShuffleSplit

# =============================================================================
# Constants
# =============================================================================
WINDOW_SIZE = 100   # samples (= 1s at 100 Hz)
WINDOW_STEP = 50    # 50% overlap
N_FOLDS = 5
GOLD_SCHEMA_COLS = ["Subject", "Activity_Label", "Activity_Code", "Trial", "Sample_Index", "AVM", "GVM"]
VALID_DATASETS = {"SisFall", "FallAllD", "KFall", "UPFall"}

# =============================================================================
# Azure IO and Data Loading
# =============================================================================
def _get_file_client(service_client, container_name, directory_name, filename):
    """
    Retorna un cliente de archivo de Azure Data Lake.
    """
    return service_client.get_file_system_client(container_name) \
                         .get_directory_client(directory_name) \
                         .get_file_client(filename)

def load_gold(service_client, dataset_names, container_name="oro", directory_name="falls"):
    """
    Carga y concatena los datasets indicados desde la capa gold (formato parquet).
    Agrega la columna 'Dataset' a cada conjunto.
    """
    dfs = []
    for name in dataset_names:
        if name not in VALID_DATASETS:
            continue
        filename = f"{name}.parquet"
        file_client = _get_file_client(service_client, container_name, directory_name, filename)
        content = file_client.download_file().readall()
        df = pd.read_parquet(io.BytesIO(content))
        df["Dataset"] = name
        dfs.append(df)
    
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

# =============================================================================
# Taxonomy & Grouping
# =============================================================================
def build_taxonomy_map():
    """
    Construye y devuelve un diccionario que mapea (Dataset, Activity_Code)
    a la clase unificada de tipo de caída.
    """
    mapping = {}
    
    # SisFall
    sisfall_groups = {
        "U1": ["F01", "F02", "F03"],
        "U2": ["F04"],
        "U3": ["F05"],
        "U4": ["F06", "F07"],
        "U5": ["F10", "F11", "F12"],
        "U6": ["F08", "F09"],
        "U7": ["F13", "F14", "F15"]
    }
    for u_code, f_codes in sisfall_groups.items():
        for f in f_codes:
            mapping[("SisFall", f)] = u_code

    # KFall
    kfall_groups = {
        "U1": ["F13", "F14", "F15"],
        "U2": ["F11"],
        "U3": ["F12"],
        "U4": ["F09", "F10"],
        "U5": ["F01", "F02", "F03"],
        "U6": ["F04", "F05"],
        "U7": ["F06", "F07", "F08"]
    }
    for u_code, f_codes in kfall_groups.items():
        for f in f_codes:
            mapping[("KFall", f)] = u_code

    # FallAllD
    fallalld_groups = {
        "U1": ["101", "102", "103", "104", "105", "106"],
        "U2": ["107", "108"],
        "U3": ["109", "110"],
        "U4": ["111", "112", "113", "114"],
        "U5": ["115", "116", "117", "118", "119", "120"],
        "U6": ["121", "122", "123", "124", "125", "126"],
        "U7": ["127", "128", "129"],
        "U8": ["130", "131"]
    }
    for u_code, f_codes in fallalld_groups.items():
        for f in f_codes:
            mapping[("FallAllD", f)] = u_code

    # UPFall
    upfall_groups = {
        "U5": ["4"],
        "U10": ["1", "2", "3", "5"]
    }
    for u_code, f_codes in upfall_groups.items():
        for f in f_codes:
            mapping[("UPFall", f)] = u_code
            
    return mapping

def map_to_unified_taxonomy(df):
    """
    Añade la columna 'Fall_Type_Unified' usando el mapeo de taxonomía.
    Asigna 'ADL' para actividades normales y 'UNMAPPED' si el código de caída no está.
    """
    taxonomy = build_taxonomy_map()
    df_mapped = df.copy()
    
    datasets = df_mapped["Dataset"].values
    act_codes = df_mapped["Activity_Code"].astype(str).values
    act_labels = df_mapped["Activity_Label"].values
    
    unified_types = [
        "ADL" if label == "ADL" else taxonomy.get((ds, code), "UNMAPPED")
        for ds, code, label in zip(datasets, act_codes, act_labels)
    ]
    df_mapped["Fall_Type_Unified"] = unified_types
    return df_mapped

def build_group_id(df):
    """
    Crea un identificador único por sujeto agrupando Dataset y Subject.
    """
    df_grouped = df.copy()
    df_grouped["Group_ID"] = df_grouped["Dataset"] + "_" + df_grouped["Subject"].astype(str)
    return df_grouped

# =============================================================================
# Preprocessing & Data Generation
# =============================================================================
def create_windows(df, window_size=WINDOW_SIZE, window_step=WINDOW_STEP):
    """
    Genera ventanas deslizantes para los datos.
    Agrupa por Dataset, Subject, Activity_Code, y Trial para no mezclar ensayos.
    """
    X_list = []
    y_list = []
    meta_list = []
    
    for keys, group in df.groupby(["Dataset", "Subject", "Activity_Code", "Trial"]):
        group = group.sort_values("Sample_Index")
        n_samples = len(group)
        if n_samples < window_size:
            continue
            
        avm = group["AVM"].values
        gvm = group["GVM"].values
        data = np.stack([avm, gvm], axis=-1)
        
        label_val = group["Activity_Label"].iloc[0]
        binary_label = 1 if label_val == "Fall" else 0
        fall_type = group["Fall_Type_Unified"].iloc[0] if "Fall_Type_Unified" in group.columns else None
        
        for i in range(0, n_samples - window_size + 1, window_step):
            window = data[i:i + window_size]
            X_list.append(window)
            y_list.append(binary_label)
            meta_list.append({
                "Subject": keys[1],
                "Dataset": keys[0],
                "Activity_Code": keys[2],
                "Fall_Type_Unified": fall_type
            })
            
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    meta = pd.DataFrame(meta_list)
    return X, y, meta

def undersample_train(X, y, meta, random_state=42):
    """
    Realiza submuestreo aleatorio de la clase mayoritaria (ADL=0)
    para que su cantidad sea igual a la de caídas (Fall=1).
    """
    np.random.seed(random_state)
    
    idx_fall = np.where(y == 1)[0]
    idx_adl = np.where(y == 0)[0]
    
    if len(idx_adl) > len(idx_fall):
        idx_adl = np.random.choice(idx_adl, size=len(idx_fall), replace=False)
        
    idx_balanced = np.concatenate([idx_fall, idx_adl])
    np.random.shuffle(idx_balanced)
    
    return X[idx_balanced], y[idx_balanced], meta.iloc[idx_balanced].reset_index(drop=True)

# =============================================================================
# Evaluation Metrics
# =============================================================================
def compute_binary_metrics(y_true, y_pred):
    """
    Calcula métricas binarias estándar. (Caída=1, ADL=0)
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    f1 = 0.0
    if precision + sensitivity > 0:
        f1 = 2 * (precision * sensitivity) / (precision + sensitivity)
        
    return {
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "precision": float(precision),
        "f1": float(f1),
        "tp": int(tp),
        "fn": int(fn),
        "tn": int(tn),
        "fp": int(fp)
    }

def confusion_by_fall_type(y_true, y_pred, fall_types):
    """
    Desglosa los aciertos y fallos por tipo de caída unificado.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    fall_types = np.asarray(fall_types)
    
    unique_types = np.unique(fall_types)
    rows = []
    
    for ftype in unique_types:
        idx = np.where(fall_types == ftype)[0]
        n_total = len(idx)
        n_pred_fall = int(np.sum(y_pred[idx] == 1))
        n_pred_adl = int(np.sum(y_pred[idx] == 0))
        
        if ftype == "ADL":
            det_rate = n_pred_adl / n_total if n_total > 0 else 0.0
        else:
            det_rate = n_pred_fall / n_total if n_total > 0 else 0.0
            
        rows.append({
            "Fall_Type_Unified": ftype,
            "n_total": n_total,
            "n_pred_fall": n_pred_fall,
            "n_pred_adl": n_pred_adl,
            "detection_rate": float(det_rate)
        })
        
    return pd.DataFrame(rows)

# =============================================================================
# Modelling & Profiling (TensorFlow lazy load)
# =============================================================================
def build_cnn_lstm(window_size=WINDOW_SIZE, n_channels=2):
    """
    Construye y compila el modelo CNN-LSTM de TensorFlow/Keras.
    """
    import tensorflow as tf
    
    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(64, 3, activation='relu', padding='same', input_shape=(window_size, n_channels)),
        tf.keras.layers.Conv1D(64, 3, activation='relu', padding='same'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(128, 3, activation='relu', padding='same'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.LSTM(64),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_model(dataset_names, fold_idx, X_train, y_train, X_val, y_val, window_size=WINDOW_SIZE, n_channels=2, epochs=50, batch_size=32, return_history=False):
    """
    Entrena el modelo de detección de caídas. Opcionalmente retorna el historial de entrenamiento.
    """
    import tensorflow as tf
    
    model = build_cnn_lstm(window_size=window_size, n_channels=n_channels)
    
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=5, restore_best_weights=True
    )
    
    config_name = "_".join(dataset_names)
    print(f"Training config: {config_name} - Fold: {fold_idx}")
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[early_stopping],
        verbose=0
    )
    if return_history:
        return model, history.history
    return model

def measure_latency(model, input_shape, n_runs=100):
    """
    Mide el tiempo de inferencia promedio en milisegundos.
    """
    import tensorflow as tf
    
    dummy_input = np.random.randn(1, *input_shape).astype(np.float32)
    
    # Warmup
    for _ in range(5):
        model.predict(dummy_input, verbose=0)
        
    start = time.perf_counter()
    for _ in range(n_runs):
        model.predict(dummy_input, verbose=0)
    end = time.perf_counter()
    
    latency_ms = ((end - start) / n_runs) * 1000
    return float(latency_ms)

def measure_model_size(model):
    """
    Mide el tamaño del modelo serializado en bytes.
    """
    import tensorflow as tf
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        model_path = os.path.join(tmp_dir, "temp.keras")
        model.save(model_path)
        return os.path.getsize(model_path)

# =============================================================================
# Visualizations (Pure Matplotlib)
# =============================================================================
def plot_confusion_matrices(metrics_dict_by_config):
    """
    Dibuja matrices de confusión 2x2 para cada configuración experimental.
    """
    import matplotlib.pyplot as plt

    n_configs = len(metrics_dict_by_config)
    fig, axes = plt.subplots(1, n_configs, figsize=(4 * n_configs, 3.5), squeeze=False)

    for idx, (config_name, m) in enumerate(metrics_dict_by_config.items()):
        ax = axes[0, idx]
        cm = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
        im = ax.imshow(cm, cmap="Blues")
        
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black" if cm[i, j] < (cm.max()/2) else "white")

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["ADL (0)", "Fall (1)"])
        ax.set_yticklabels(["ADL (0)", "Fall (1)"])
        ax.set_title(config_name, fontsize=11, fontweight="bold")
        ax.set_xlabel("Predicción")
        if idx == 0:
            ax.set_ylabel("Valor Real")

    plt.tight_layout()
    return fig

def plot_detection_by_fall_type(confusion_df):
    """
    Dibuja la tasa de detección por tipo de caída unificado (U1-U10, ADL).
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    df_sorted = confusion_df.sort_values("detection_rate", ascending=True)

    y_labels = df_sorted["Fall_Type_Unified"].values
    rates = df_sorted["detection_rate"].values

    bars = ax.barh(y_labels, rates, color="#2b5c8f")
    ax.set_xlim(0, 1.15)
    ax.set_title("Tasa de Detección por Tipo Unificado de Caída", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tasa de Detección (0.0 a 1.0)")
    ax.set_ylabel("Tipo de Caída / Actividad")

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.01, bar.get_y() + bar.get_height() / 2, f"{width:.1%}",
                ha="left", va="center", fontsize=9)

    plt.tight_layout()
    return fig

def plot_learning_curves(history_dict):
    """
    Dibuja curvas de aprendizaje (Loss y Accuracy vs Épocas).
    """
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    epochs = range(1, len(history_dict.get("loss", [])) + 1)

    ax1.plot(epochs, history_dict.get("loss", []), label="Train Loss", marker="o", markersize=3, color="#d95f02")
    ax1.plot(epochs, history_dict.get("val_loss", []), label="Val Loss", marker="s", markersize=3, color="#7570b3")
    ax1.set_title("Pérdida (Loss) vs Épocas", fontweight="bold")
    ax1.set_xlabel("Época")
    ax1.set_ylabel("Pérdida")
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.6)

    ax2.plot(epochs, history_dict.get("accuracy", []), label="Train Accuracy", marker="o", markersize=3, color="#1b9e77")
    ax2.plot(epochs, history_dict.get("val_accuracy", []), label="Val Accuracy", marker="s", markersize=3, color="#e7298a")
    ax2.set_title("Precisión (Accuracy) vs Épocas", fontweight="bold")
    ax2.set_xlabel("Época")
    ax2.set_ylabel("Precisión")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    return fig

def plot_tradeoff(results_df):
    """
    Scatter plot de F1-Score vs Latencia (ms) con tamaño de punto por Tamaño en KB.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 4.5))

    for _, row in results_df.iterrows():
        f1 = row.get("f1_mean", row.get("f1", 0))
        lat = row.get("latency_ms_mean", row.get("latency_ms", 0))
        size = row.get("model_size_kb", row.get("model_size_bytes", 1024) / 1024)
        name = row.get("config", "Config")

        ax.scatter(lat, f1, s=size * 2, alpha=0.7, edgecolors="black", linewidth=1.5)
        ax.annotate(name, (lat, f1), textcoords="offset points", xytext=(8, 5), fontsize=10, fontweight="bold")

    ax.set_title("Compromiso entre F1-Score y Latencia de Inferencia", fontsize=12, fontweight="bold")
    ax.set_xlabel("Latencia Promedio por Ventana (ms)")
    ax.set_ylabel("F1-Score")
    ax.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    return fig

# =============================================================================
# Outputs and Artifact Saving
# =============================================================================
def _to_native(obj):
    """
    Convierte tipos de NumPy o recursivos a tipos nativos de Python para JSON.
    """
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set, np.ndarray)):
        return [_to_native(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    else:
        return obj

def save_metrics_json(service_client, metrics_dict, config_name, fold_idx, container_name="modelos", directory_name="falls/metricas"):
    """
    Sube las métricas serializadas como JSON a Azure Data Lake.
    """
    filename = f"{config_name}_fold{fold_idx}.json"
    file_client = _get_file_client(service_client, container_name, directory_name, filename)
    
    json_bytes = json.dumps(_to_native(metrics_dict), indent=4).encode("utf-8")
    file_client.upload_data(json_bytes, overwrite=True)
    return len(json_bytes)

def save_model_keras(service_client, model, config_name, container_name="modelos", directory_name="falls"):
    """
    Sube el modelo entrenado en formato .keras a Azure Data Lake.
    """
    import tensorflow as tf
    
    filename = f"{config_name}_final.keras"
    file_client = _get_file_client(service_client, container_name, directory_name, filename)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        model_path = os.path.join(tmp_dir, "model.keras")
        model.save(model_path)
        with open(model_path, "rb") as f:
            model_bytes = f.read()
            
    file_client.upload_data(model_bytes, overwrite=True)
    return len(model_bytes)

def save_comparison_csv(service_client, results_df, container_name="modelos", directory_name="falls/metricas"):
    """
    Guarda el DataFrame de resultados resumidos en un CSV en Azure.
    """
    filename = "tabla_comparativa.csv"
    file_client = _get_file_client(service_client, container_name, directory_name, filename)
    
    csv_bytes = results_df.to_csv(index=False).encode("utf-8")
    file_client.upload_data(csv_bytes, overwrite=True)
    return len(csv_bytes)
