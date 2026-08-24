# Futuro: Entrenamiento CNN-BiLSTM para Detección de Caídas

> Tareas pendientes extraídas del plan de implementación (2026-08-24).
> Prerequisito: Task 1 (Butterworth en `00_Preproc`) ya completada — oro regenerado con señales filtradas.

---

## Task 2: Reconstruir `01_Entrenamiento.ipynb`

**Files:**
- Create (overwrite): `notebooks/pipeline/01_Entrenamiento.ipynb`

**Decisiones de diseño confirmadas:**
- **Ventana:** 3.0s = 150 timesteps @50Hz, 50% overlap (75 steps)
- **Canales:** 8 → `[Ax, Ay, Az, Gx, Gy, Gz, AVM, GVM]`
- **Balanceo:** Focal Loss (gamma=2.0, alpha=0.75) — sin undersampling
- **Normalización:** Z-score (fit solo en train, transform en val/test)
- **Arquitectura:** Conv1D(32, k=3) → BatchNorm → ReLU → Conv1D(32) → BatchNorm → ReLU → MaxPool(2) → Bi-LSTM(64) → Dropout(0.3) → Dense(1, sigmoid)
- **Split:** StratifiedGroupKFold(5) + GroupShuffleSplit(10% val)
- **Métricas:** Sensibilidad, Especificidad, Precisión
- **Configs:** 2 modelos — `set_a` (5 ds) vs `set_b` (4 ds sin UMAFall)

**Notebook debe ser autocontenido (sin imports de módulos del proyecto, sin Azure).**

### Estructura de celdas del notebook

**Celda 1 (code): Imports y constantes**
```python
import numpy as np
import pandas as pd
import tensorflow as tf
import gc
import time
import os
import json
import pathlib
from sklearn.model_selection import StratifiedGroupKFold, GroupShuffleSplit
from sklearn.preprocessing import StandardScaler

FS = 50
WINDOW_SEC = 3.0
WINDOW_SIZE = int(FS * WINDOW_SEC)  # 150
WINDOW_STEP = WINDOW_SIZE // 2      # 75
N_FOLDS = 5

CHANNEL_COLS = ["Ax", "Ay", "Az", "Gx", "Gy", "Gz", "AVM", "GVM"]
N_CHANNELS = len(CHANNEL_COLS)  # 8

ORO_DIR = pathlib.Path("../data/oro/falls")
MODELS_DIR = pathlib.Path("../data/modelos/falls")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

CONFIGS = {
    "set_a": ORO_DIR / "set_a.parquet",
    "set_b": ORO_DIR / "set_b.parquet",
}
```

**Celda IO (code): Carga local**
```python
def load_oro(path: pathlib.Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    print(f"  Cargado: {path.name} → {df.shape[0]:,} filas, {sorted(df.Dataset.unique())}")
    return df
```

**Celda Windowing (code):**
```python
def build_group_id(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Group_ID"] = df["Dataset"] + "_" + df["Subject"].astype(str)
    return df

def create_windows(df, window_size=WINDOW_SIZE, window_step=WINDOW_STEP, channel_cols=CHANNEL_COLS):
    X_list, y_list, meta_list = [], [], []
    for keys, group in df.groupby(["Dataset", "Subject", "Activity_Code", "Trial"], sort=False):
        group = group.sort_values("Sample_Index")
        n_samples = len(group)
        if n_samples < window_size:
            continue
        data = group[channel_cols].values
        label = 1 if group["Activity_Label"].iloc[0] == "Fall" else 0
        for i in range(0, n_samples - window_size + 1, window_step):
            X_list.append(data[i : i + window_size])
            y_list.append(label)
            meta_list.append({"Dataset": keys[0], "Subject": keys[1], "Activity_Code": keys[2]})
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    meta = pd.DataFrame(meta_list)
    print(f"  Ventanas: {len(X):,} (Fall={y.sum():,}, ADL={(y==0).sum():,})")
    return X, y, meta
```

**Celda Z-score (code):**
```python
def fit_scaler(X_train):
    n, t, c = X_train.shape
    scaler = StandardScaler()
    scaler.fit(X_train.reshape(-1, c))
    return scaler

def apply_scaler(X, scaler):
    n, t, c = X.shape
    return scaler.transform(X.reshape(-1, c)).reshape(n, t, c).astype(np.float32)
```

**Celda Focal Loss + Modelo (code):**
```python
class FocalLoss(tf.keras.losses.Loss):
    def __init__(self, gamma=2.0, alpha=0.75, **kwargs):
        super().__init__(**kwargs)
        self.gamma = gamma
        self.alpha = alpha

    def call(self, y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.clip_by_value(y_pred, 1e-7, 1.0 - 1e-7)
        bce = -(y_true * tf.math.log(y_pred) + (1 - y_true) * tf.math.log(1 - y_pred))
        p_t = y_true * y_pred + (1 - y_true) * (1 - y_pred)
        alpha_t = y_true * self.alpha + (1 - y_true) * (1 - self.alpha)
        return tf.reduce_mean(alpha_t * tf.pow(1 - p_t, self.gamma) * bce)

def build_cnn_bilstm(window_size=WINDOW_SIZE, n_channels=N_CHANNELS):
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(window_size, n_channels)),
        tf.keras.layers.Conv1D(32, kernel_size=3, padding="same", use_bias=False),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.Conv1D(32, kernel_size=3, padding="same", use_bias=False),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        tf.keras.layers.MaxPooling1D(pool_size=2),
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss=FocalLoss(gamma=2.0, alpha=0.75), metrics=["accuracy"])
    return model
```

**Celda Métricas (code):**
```python
def compute_metrics(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    return {"sensitivity": round(sensitivity, 4), "specificity": round(specificity, 4),
            "precision": round(precision, 4), "tp": tp, "fn": fn, "tn": tn, "fp": fp}
```

**Celda Entrenamiento (code):**
```python
def run_experiment(config_name, df):
    df = build_group_id(df)
    groups = df["Group_ID"].values
    y_binary = (df["Activity_Label"] == "Fall").astype(int).values
    sgkf = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    fold_results = []

    for fold_idx, (train_idx, test_idx) in enumerate(sgkf.split(np.zeros(len(df)), y_binary, groups)):
        print(f"\n--- Fold {fold_idx + 1}/{N_FOLDS} ---")
        train_df, test_df = df.iloc[train_idx], df.iloc[test_idx]
        gss = GroupShuffleSplit(n_splits=1, test_size=0.1, random_state=fold_idx)
        inner_train_idx, val_idx = next(gss.split(
            np.zeros(len(train_df)),
            (train_df["Activity_Label"] == "Fall").astype(int).values,
            train_df["Group_ID"].values))
        train_inner_df, val_df = train_df.iloc[inner_train_idx], train_df.iloc[val_idx]

        X_train, y_train, _ = create_windows(train_inner_df)
        X_val, y_val, _ = create_windows(val_df)
        X_test, y_test, _ = create_windows(test_df)

        scaler = fit_scaler(X_train)
        X_train, X_val, X_test = apply_scaler(X_train, scaler), apply_scaler(X_val, scaler), apply_scaler(X_test, scaler)

        model = build_cnn_bilstm()
        history = model.fit(X_train, y_train, validation_data=(X_val, y_val),
                            epochs=50, batch_size=32,
                            callbacks=[tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)],
                            verbose=0)
        y_pred = (model.predict(X_test, verbose=0).flatten() >= 0.5).astype(int)
        metrics = compute_metrics(y_test, y_pred)
        fold_results.append(metrics)
        print(f"  Sens: {metrics['sensitivity']:.4f}  Spec: {metrics['specificity']:.4f}  Prec: {metrics['precision']:.4f}")
        del model, X_train, X_val, X_test; gc.collect(); tf.keras.backend.clear_session()

    agg = {}
    for m in ["sensitivity", "specificity", "precision"]:
        vals = [r[m] for r in fold_results]
        agg[f"{m}_mean"], agg[f"{m}_std"] = round(np.mean(vals), 4), round(np.std(vals), 4)
    return {"config": config_name, "folds": fold_results, "summary": agg}
```

**Celda Ejecución (code):**
```python
results = {}
for config_name, parquet_path in CONFIGS.items():
    df = load_oro(parquet_path)
    results[config_name] = run_experiment(config_name, df)
    del df; gc.collect()
```

**Celda Comparación (code):**
```python
rows = []
for config_name, res in results.items():
    s = res["summary"]
    rows.append({"Config": config_name,
                 "Sensibilidad": f"{s['sensitivity_mean']:.4f} ± {s['sensitivity_std']:.4f}",
                 "Especificidad": f"{s['specificity_mean']:.4f} ± {s['specificity_std']:.4f}",
                 "Precisión": f"{s['precision_mean']:.4f} ± {s['precision_std']:.4f}"})
print(pd.DataFrame(rows).set_index("Config").to_string())
json.dump(results, open(MODELS_DIR / "comparison_results.json", "w"), indent=2, default=str)
```

---

## Task 3: Ejecutar Entrenamiento y Validar

Ejecutar `01_Entrenamiento.ipynb` headless:
```powershell
.\.venv\Scripts\python.exe -c "
import nbformat
from nbclient import NotebookClient
nb = nbformat.read('notebooks/pipeline/01_Entrenamiento.ipynb', as_version=4)
NotebookClient(nb, timeout=7200, kernel_name='python3', resources={'metadata':{'path':'.'}}).execute()
nbformat.write(nb, 'notebooks/pipeline/01_Entrenamiento.ipynb')
print('TRAINING COMPLETE')
"
```

Validar resultados en `data/modelos/falls/comparison_results.json`.

---

## Task 4: Verificación Final

Checklist:
- [ ] `00_Preproc` aplica Butterworth 4º @8Hz
- [ ] `01_Entren` IO local, 8ch, 3s ventana, Z-score, Focal Loss, CNN-BiLSTM+BN
- [ ] Split por sujetos, métricas = Sensibilidad/Especificidad/Precisión
- [ ] 2 modelos comparados (set_a vs set_b)
- [ ] Actualizar `memory/`
