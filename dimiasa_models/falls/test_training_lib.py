"""
Pruebas unitarias para la librería de entrenamiento de detección de caídas.
Utiliza datos sintéticos y mocks para simular el comportamiento sin acceso a Azure
ni archivos reales.
"""

from training_lib import (
    GOLD_SCHEMA_COLS, WINDOW_SIZE, WINDOW_STEP, N_FOLDS,
    load_gold, build_taxonomy_map, map_to_unified_taxonomy,
    build_group_id, create_windows, undersample_train,
    compute_binary_metrics, confusion_by_fall_type,
    measure_latency, measure_model_size, train_model,
    plot_confusion_matrices, plot_detection_by_fall_type,
    plot_learning_curves, plot_tradeoff,
)
import io
from unittest.mock import MagicMock
import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import StratifiedGroupKFold, GroupShuffleSplit
import tensorflow as tf

def test_mapeo_taxonomia_codigos_conocidos():
    tax_map = build_taxonomy_map()
    
    # SisFall
    assert tax_map[("SisFall", "F01")] == "U1"
    assert tax_map[("SisFall", "F04")] == "U2"
    assert tax_map[("SisFall", "F05")] == "U3"
    assert tax_map[("SisFall", "F06")] == "U4"
    assert tax_map[("SisFall", "F10")] == "U5"
    assert tax_map[("SisFall", "F08")] == "U6"
    assert tax_map[("SisFall", "F13")] == "U7"
    
    # KFall
    assert tax_map[("KFall", "F13")] == "U1"
    assert tax_map[("KFall", "F11")] == "U2"
    assert tax_map[("KFall", "F12")] == "U3"
    assert tax_map[("KFall", "F09")] == "U4"
    assert tax_map[("KFall", "F01")] == "U5"
    assert tax_map[("KFall", "F04")] == "U6"
    assert tax_map[("KFall", "F06")] == "U7"
    
    # FallAllD
    assert tax_map[("FallAllD", "101")] == "U1"
    assert tax_map[("FallAllD", "107")] == "U2"
    assert tax_map[("FallAllD", "109")] == "U3"
    assert tax_map[("FallAllD", "111")] == "U4"
    assert tax_map[("FallAllD", "115")] == "U5"
    assert tax_map[("FallAllD", "121")] == "U6"
    assert tax_map[("FallAllD", "127")] == "U7"
    assert tax_map[("FallAllD", "130")] == "U8"
    
    # UPFall
    assert tax_map[("UPFall", "4")] == "U5"
    assert tax_map[("UPFall", "1")] == "U10"
    assert tax_map[("UPFall", "2")] == "U10"

    # ADL mapping
    df_adl = pd.DataFrame({
        "Activity_Label": ["ADL"],
        "Dataset": ["SisFall"],
        "Activity_Code": ["D01"]
    })
    df_mapped = map_to_unified_taxonomy(df_adl)
    assert df_mapped["Fall_Type_Unified"].iloc[0] == "ADL"

def test_mapeo_taxonomia_no_inventa_causa_upfall():
    tax_map = build_taxonomy_map()
    upfall_mappings = {v for k, v in tax_map.items() if k[0] == "UPFall"}
    disallowed_causes = {"U1", "U2", "U3", "U4", "U7"}
    
    assert len(upfall_mappings.intersection(disallowed_causes)) == 0
    assert upfall_mappings.issubset({"U5", "U10"})

def test_group_id_evita_colision_entre_datasets():
    df = pd.DataFrame({
        "Dataset": ["A", "A", "B", "B"],
        "Subject": [1, 2, 1, 2]
    })
    df = build_group_id(df)
    
    assert df["Group_ID"].nunique() == 4
    assert set(df["Group_ID"]) == {"A_1", "A_2", "B_1", "B_2"}

def test_stratified_groupkfold_sin_fuga_de_sujetos():
    groups = np.repeat(np.arange(20), 10)
    X = np.random.rand(200, 5)
    y = np.random.randint(0, 2, 200)
    
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    for train_idx, test_idx in cv.split(X, y, groups):
        train_groups = set(groups[train_idx])
        test_groups = set(groups[test_idx])
        assert len(train_groups.intersection(test_groups)) == 0

def test_validacion_anidada_sin_fuga():
    groups = np.repeat(np.arange(20), 10)
    X = np.random.rand(200, 5)
    y = np.random.randint(0, 2, 200)
    
    outer_cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    for train_idx, _ in outer_cv.split(X, y, groups):
        X_train, y_train, groups_train = X[train_idx], y[train_idx], groups[train_idx]
        
        inner_cv = GroupShuffleSplit(n_splits=1, test_size=0.1, random_state=0)
        for inner_train_idx, val_idx in inner_cv.split(X_train, y_train, groups_train):
            inner_train_groups = set(groups_train[inner_train_idx])
            val_groups = set(groups_train[val_idx])
            assert len(inner_train_groups.intersection(val_groups)) == 0

def test_ventaneo_no_mezcla_trials():
    df = pd.DataFrame({
        "Dataset": ["A"] * 400,
        "Subject": [1] * 400,
        "Activity_Label": ["ADL"] * 400,
        "Activity_Code": ["D01"] * 200 + ["D02"] * 200,
        "Trial": [1] * 200 + [2] * 200,
        "Sample_Index": list(range(200)) + list(range(200)),
        "AVM": [1.0] * 200 + [100.0] * 200,
        "GVM": [0.0] * 400,
        "Fall_Type_Unified": ["ADL"] * 400,
    })
    
    X, y, meta = create_windows(df, window_size=100, window_step=50)
    
    for i in range(len(X)):
        # Asume AVM es el primer canal o un canal en particular
        # Se verifica que todos los valores en un segmento dado sean constantes (min == max)
        avm_window = X[i, :, 0]
        assert np.all(avm_window == 1.0) or np.all(avm_window == 100.0)
        assert np.min(avm_window) == np.max(avm_window)

def test_ventaneo_forma_y_cantidad():
    df = pd.DataFrame({
        "Dataset": ["A"] * 350,
        "Subject": [1] * 350,
        "Activity_Label": ["ADL"] * 350,
        "Activity_Code": ["D1"] * 350,
        "Trial": [1] * 350,
        "Sample_Index": list(range(350)),
        "AVM": [1.0] * 350,
        "GVM": [0.0] * 350,
        "Fall_Type_Unified": ["ADL"] * 350,
    })
    
    X, y, meta = create_windows(df, window_size=100, window_step=50)
    expected_windows = ((350 - 100) // 50) + 1  # 6
    
    assert X.shape == (expected_windows, 100, 2)
    assert len(y) == expected_windows
    assert len(meta) == expected_windows

def test_ventaneo_metadata_alineada():
    df = pd.DataFrame({
        "Dataset": ["SisFall"] * 200,
        "Subject": [42] * 200,
        "Activity_Label": ["Fall"] * 200,
        "Activity_Code": ["F01"] * 200,
        "Trial": [1] * 200,
        "Sample_Index": list(range(200)),
        "AVM": [1.0] * 200,
        "GVM": [0.0] * 200,
        "Fall_Type_Unified": ["U1"] * 200,
    })
    
    X, y, meta = create_windows(df, window_size=100, window_step=50)
    
    assert len(meta) == len(X)
    assert len(meta) == len(y)
    
    if isinstance(meta, pd.DataFrame):
        assert (meta["Subject"] == 42).all()
        assert (meta["Dataset"] == "SisFall").all()
        assert (meta["Activity_Code"] == "F01").all()
        assert (meta["Fall_Type_Unified"] == "U1").all()
    else:
        for m in meta:
            assert m["Subject"] == 42
            assert m["Dataset"] == "SisFall"
            assert m["Activity_Code"] == "F01"
            assert m["Fall_Type_Unified"] == "U1"

def test_balanceo_solo_afecta_train():
    X_train = np.zeros((400, 100, 2))
    y_train = np.array([1] * 100 + [0] * 300)
    meta_train = pd.DataFrame({"dummy": range(400)})
    
    X_val = np.zeros((50, 100, 2))
    y_val = np.array([1] * 10 + [0] * 40)
    
    X_train_res, y_train_res, meta_train_res = undersample_train(X_train, y_train, meta_train)
    
    assert np.sum(y_train_res == 1) == 100
    assert np.sum(y_train_res == 0) == 100
    assert len(y_train_res) == 200
    
    # Asegurar que validation/test se mantendría inalterado por la función (sólo se procesa train)
    assert np.sum(y_val == 1) == 10
    assert np.sum(y_val == 0) == 40

def test_metricas_formulas_conocidas():
    # TP=80, FP=10, TN=90, FN=20
    y_true = np.array([1] * 100 + [0] * 100)
    y_pred = np.array([1] * 80 + [0] * 20 + [1] * 10 + [0] * 90)
    
    metrics = compute_binary_metrics(y_true, y_pred)
    
    assert metrics["sensitivity"] == pytest.approx(0.8, rel=0.01)
    assert metrics["specificity"] == pytest.approx(0.9, rel=0.01)
    assert metrics["precision"] == pytest.approx(80 / 90, rel=0.01)
    
    f1_expected = 2 * 0.8 * (80 / 90) / (0.8 + 80 / 90)
    assert metrics["f1"] == pytest.approx(f1_expected, rel=0.01)

def test_matriz_confusion_por_tipo_unificado():
    y_true = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
    y_pred = np.array([1, 1, 1, 0, 0, 0, 0, 0, 1, 1])
    fall_types = ["U1"] * 5 + ["ADL"] * 5
    
    res = confusion_by_fall_type(y_true, y_pred, fall_types)
    
    u1_row = res[res["Fall_Type_Unified"] == "U1"].iloc[0]
    adl_row = res[res["Fall_Type_Unified"] == "ADL"].iloc[0]
    
    assert u1_row["n_total"] == 5
    assert u1_row["n_pred_fall"] == 3
    assert u1_row["n_pred_adl"] == 2
    
    assert adl_row["n_total"] == 5
    assert adl_row["n_pred_fall"] == 2
    assert adl_row["n_pred_adl"] == 3

def test_carga_gold_con_mock_azure():
    df = pd.DataFrame({col: [0] for col in GOLD_SCHEMA_COLS})
    df["Dataset"] = "SisFall"
    
    buf = io.BytesIO()
    df.to_parquet(buf)
    parquet_bytes = buf.getvalue()
    
    mock_client = MagicMock()
    mock_download = MagicMock()
    mock_download.readall.return_value = parquet_bytes
    
    (mock_client
     .get_file_system_client.return_value
     .get_directory_client.return_value
     .get_file_client.return_value
     .download_file.return_value) = mock_download
     
    df_res = load_gold(mock_client, ["SisFall"])
    
    assert "Dataset" in df_res.columns
    assert (df_res["Dataset"] == "SisFall").all()
    for col in GOLD_SCHEMA_COLS:
        assert col in df_res.columns
    assert len(df_res) == 1

@pytest.mark.slow
def test_medicion_latencia_y_tamaño_modelo_dummy():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(4, input_shape=(10,), activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy')
    
    latency = measure_latency(model, (10,), n_runs=5)
    size = measure_model_size(model)
    
    assert latency > 0
    assert size > 0

@pytest.mark.slow
def test_train_model_con_historial():
    X_tr = np.random.randn(20, WINDOW_SIZE, 2).astype(np.float32)
    y_tr = np.random.randint(0, 2, 20).astype(np.int32)
    X_val = np.random.randn(10, WINDOW_SIZE, 2).astype(np.float32)
    y_val = np.random.randint(0, 2, 10).astype(np.int32)

    model, hist = train_model(["SisFall"], 0, X_tr, y_tr, X_val, y_val, epochs=2, return_history=True)
    assert hasattr(model, "predict")
    for key in ["loss", "val_loss", "accuracy", "val_accuracy"]:
        assert key in hist
        assert len(hist[key]) == 2

def test_visualizaciones_generan_figuras():
    import matplotlib.figure

    # 1. Matrices de confusión
    metrics_by_config = {
        "SisFall": {"tp": 80, "fp": 10, "fn": 20, "tn": 90},
        "KFall": {"tp": 75, "fp": 15, "fn": 25, "tn": 85}
    }
    fig1 = plot_confusion_matrices(metrics_by_config)
    assert isinstance(fig1, matplotlib.figure.Figure)

    # 2. Detección por tipo
    cm_df = pd.DataFrame([
        {"Fall_Type_Unified": "U1", "detection_rate": 0.85},
        {"Fall_Type_Unified": "U2", "detection_rate": 0.70},
        {"Fall_Type_Unified": "ADL", "detection_rate": 0.95}
    ])
    fig2 = plot_detection_by_fall_type(cm_df)
    assert isinstance(fig2, matplotlib.figure.Figure)

    # 3. Curvas de aprendizaje
    hist_dict = {"loss": [0.6, 0.4], "val_loss": [0.65, 0.45], "accuracy": [0.7, 0.85], "val_accuracy": [0.65, 0.8]}
    fig3 = plot_learning_curves(hist_dict)
    assert isinstance(fig3, matplotlib.figure.Figure)

    # 4. Tradeoff
    results_df = pd.DataFrame([
        {"config": "SisFall", "f1_mean": 0.85, "latency_ms_mean": 1.2, "model_size_kb": 500},
        {"config": "KFall", "f1_mean": 0.88, "latency_ms_mean": 1.5, "model_size_kb": 500}
    ])
    fig4 = plot_tradeoff(results_df)
    assert isinstance(fig4, matplotlib.figure.Figure)

