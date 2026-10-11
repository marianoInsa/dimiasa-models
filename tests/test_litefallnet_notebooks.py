import ast
import json
from pathlib import Path

import numpy as np
import pytest

NOTEBOOKS = Path(__file__).resolve().parents[1] / "notebooks"


def load_notebook(name: str) -> dict:
    path = NOTEBOOKS / name
    return json.loads(path.read_text(encoding="utf-8"))


def notebook_source(name: str) -> str:
    notebook = load_notebook(name)
    return "\n".join(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] in {"markdown", "code"}
    )


def test_training_notebook_has_valid_structure_and_no_saved_outputs():
    notebook = load_notebook("03_Entrenamiento_LiteFallNet_SisFall.ipynb")
    assert notebook["nbformat"] == 4
    assert notebook["cells"]
    assert all(cell["cell_type"] in {"markdown", "code"} for cell in notebook["cells"])
    assert all(not cell.get("outputs") for cell in notebook["cells"] if cell["cell_type"] == "code")


def test_quantization_notebook_has_int8_artifact_contract():
    name = "04_Cuantizacion_LiteFallNet_LiteRT_ESP32.ipynb"
    notebook = load_notebook(name)
    assert notebook["nbformat"] == 4
    assert notebook["cells"]
    assert all(cell["cell_type"] in {"markdown", "code"} for cell in notebook["cells"])
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert all(not cell.get("outputs") for cell in code_cells)
    for cell in code_cells:
        ast.parse("".join(cell["source"]), filename=f"{name}:{cell['id']}")

    source = notebook_source(name)
    for value in (
        "litefallnet_sisfall_int8.tflite",
        "litefallnet_sisfall_int8_model.h",
        "litefallnet_sisfall_int8_report.json",
        "tf.lite.TFLiteConverter",
        "tf.lite.Optimize.DEFAULT",
        "TFLITE_BUILTINS_INT8",
        "tf.int8",
        "representative_dataset",
        "x_calibration",
        "len(x_calibration) != 1000",
        "[400, 600]",
        "validar_ventanas_y_etiquetas",
        "ventanas.ndim != 3",
        "etiquetas.ndim != 1",
        "len(etiquetas) != len(ventanas)",
        "np.isin(etiquetas, [0, 1])",
        "np.isfinite(ventanas).all()",
        "x_validation",
        "x_test",
        "x_upfall",
        "candidato_listo",
        "if candidato_listo:",
        "CAIDA_MAXIMA_PERMITIDA = 0.02",
        "OPERADORES_ESP32_LITERT_MICRO",
        "TensorType.INT8",
        "TensorType.INT32",
        "if forma_salida != [1, 1]:",
        "usos_int32",
        "codigo.Version()",
        "versiones_flatbuffer",
        "VERSION_ESP_TFLITE_MICRO = '1.4.1'",
        "nombres_operadores_builtin",
        "version_esp_tflite_micro",
        "usos_int32_permitidos",
        "prechequeo_estatico",
        "prechequeo estático",
        "memoria fija para guardar los tensores",
        "QAT",
        "esp-tflite-micro",
        "-DESP_NN",
        "arena",
    ):
        assert value in source
    assert "modelo.fit(" not in source
    assert "SELECT_TF_OPS" not in source
    assert "tensorflow_model_optimization" not in source
    assert "EJECUTAR_QAT" not in source
    assert "convertidor.allow_custom_ops = False" in source

    ids = [cell.get("id") for cell in notebook["cells"]]
    assert ids.index("litefallnet-metricas-code") < ids.index("litefallnet-validacion-code")
    assert ids.index("litefallnet-int8-validar-code") < ids.index("litefallnet-int8-cargar-code")
    cells = {cell["id"]: "".join(cell["source"]) for cell in notebook["cells"]}
    assert "validar_ventanas_y_etiquetas('Calibración'" in cells["litefallnet-int8-cargar-code"]
    assert "validar_ventanas_y_etiquetas('Validación'" in cells["litefallnet-int8-cargar-code"]
    assert "validar_ventanas_y_etiquetas(nombre, x_grupo, y_grupo)" in cells["litefallnet-validacion-code"]
    assert cells["litefallnet-validacion-code"].index("validar_ventanas_y_etiquetas(") < cells[
        "litefallnet-validacion-code"
    ].index("modelo.predict(")


def test_quantization_not_ready_gate_skips_holdout_files_and_checks_output_shape(tmp_path):
    name = "04_Cuantizacion_LiteFallNet_LiteRT_ESP32.ipynb"
    notebook = load_notebook(name)
    cells = {cell["id"]: "".join(cell["source"]) for cell in notebook["cells"]}
    ruta_npz = tmp_path / "no_existe.npz"
    entorno = {"np": np, "candidato_listo": False, "RUTA_EVALUACION": ruta_npz}

    exec(compile(cells["litefallnet-validacion-code"], "rama_no_lista", "exec"), entorno)

    assert not ruta_npz.exists()
    assert entorno["evaluaciones_finales"] == {
        "sisfall_prueba": None,
        "upfall": None,
    }
    assert not {"x_test", "y_test", "x_upfall", "y_upfall", "grupos_finales"} & entorno.keys()
    assert "if forma_salida != [1, 1]:" in cells["litefallnet-int8-flatbuffer-code"]


@pytest.mark.parametrize(
    ("problema", "mensaje"),
    [
        ("etiquetas_2d", "una dimensión"),
        ("etiqueta_no_binaria", "solo pueden ser 0"),
        ("senal_forma_invalida", "señales deben tener forma"),
        ("senal_no_finita", "valores no finitos"),
    ],
)
def test_quantization_array_helper_rejects_malformed_arrays(problema, mensaje):
    name = "04_Cuantizacion_LiteFallNet_LiteRT_ESP32.ipynb"
    notebook = load_notebook(name)
    cells = {cell["id"]: "".join(cell["source"]) for cell in notebook["cells"]}
    source = cells.get("litefallnet-int8-validar-code")
    assert source is not None, "Falta la celda que define la validación de arreglos."

    entorno = {"np": np, "TAMANO_VENTANA": 150, "CANALES": ["AVM", "GVM"]}
    exec(compile(source, "validar_arreglos", "exec"), entorno)
    ventanas = np.zeros((2, 150, 2), dtype=np.float32)
    etiquetas = np.array([0, 1], dtype=np.int8)
    if problema == "etiquetas_2d":
        etiquetas = np.array([[0, 1], [1, 0]], dtype=np.int8)
    elif problema == "etiqueta_no_binaria":
        etiquetas[1] = 2
    elif problema == "senal_forma_invalida":
        ventanas = np.zeros((2, 149, 2), dtype=np.float32)
    else:
        ventanas[0, 0, 0] = np.nan

    with pytest.raises(ValueError, match=mensaje):
        entorno["validar_ventanas_y_etiquetas"]("Prueba", ventanas, etiquetas)


def test_final_groups_validate_before_any_prediction(tmp_path):
    name = "04_Cuantizacion_LiteFallNet_LiteRT_ESP32.ipynb"
    notebook = load_notebook(name)
    cells = {cell["id"]: "".join(cell["source"]) for cell in notebook["cells"]}
    x_final = np.zeros((2, 150, 2), dtype=np.float32)
    y_test = np.array([0, 1], dtype=np.int8)
    y_upfall = np.array([0, 256], dtype=np.int16)
    ruta_npz = tmp_path / "sisfall_y_upfall_invalido.npz"
    np.savez(ruta_npz, x_test=x_final, y_test=y_test, x_upfall=x_final, y_upfall=y_upfall)

    class ModeloConRegistro:
        def __init__(self):
            self.llamadas = 0

        def predict(self, ventanas, **kwargs):
            self.llamadas += 1
            return np.full((len(ventanas), 1), 0.5, dtype=np.float32)

    modelo = ModeloConRegistro()
    llamadas_int8 = []

    def inferir_int8(ventanas):
        llamadas_int8.append(len(ventanas))
        return np.full(len(ventanas), 0.5, dtype=np.float32)

    def calcular_metricas(etiquetas, probabilidades):
        return {nombre: 0.5 for nombre in ("accuracy", "precision", "recall_caidas", "specificity", "f1")}

    entorno = {"np": np, "TAMANO_VENTANA": 150, "CANALES": ["AVM", "GVM"]}
    exec(compile(cells["litefallnet-int8-validar-code"], "validar_arreglos", "exec"), entorno)
    entorno.update({
        "candidato_listo": True,
        "RUTA_EVALUACION": ruta_npz,
        "modelo": modelo,
        "inferir_int8": inferir_int8,
        "calcular_metricas": calcular_metricas,
    })
    with pytest.raises(ValueError, match="etiquetas solo pueden ser 0"):
        exec(compile(cells["litefallnet-validacion-code"], "grupos_finales_invalidos", "exec"), entorno)

    assert modelo.llamadas == 0
    assert llamadas_int8 == []


def test_training_notebook_uses_the_approved_dataset_contract():
    notebook = load_notebook("03_Entrenamiento_LiteFallNet_SisFall.ipynb")
    source = notebook_source("03_Entrenamiento_LiteFallNet_SisFall.ipynb")
    for value in (
        "AVM",
        "GVM",
        "SisFall",
        "UPFall",
        "150",
        "75",
        "sin la capa GRU",
        "artículo",
        "litefallnet_sisfall.keras",
        "litefallnet_sisfall_metadata.json",
        "litefallnet_sisfall_eval.npz",
        "x_calibration",
        "y_calibration",
        "x_validation",
        "y_validation",
        "x_test",
        "y_test",
        "x_upfall",
        "y_upfall",
    ):
        assert value in source

    sources = {
        cell["id"]: "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    }
    entorno = {}
    for cell_id in (
        "litefallnet-imports",
        "litefallnet-funciones-code",
        "litefallnet-prueba-sintetica-code",
    ):
        exec(compile(sources[cell_id], cell_id, "exec"), entorno)

    assert entorno["ids_por_particion"]["train"].isdisjoint(
        entorno["ids_por_particion"]["validation"]
    )
    assert entorno["ids_por_particion"]["train"].isdisjoint(
        entorno["ids_por_particion"]["test"]
    )
    assert entorno["ids_por_particion"]["validation"].isdisjoint(
        entorno["ids_por_particion"]["test"]
    )
    assert entorno["x_sintetico"].shape == (50, 150, 2)
    assert np.isclose(
        entorno["df_sintetico"].loc[
            entorno["df_sintetico"]["Subject"] == "Fall-0", "AVM"
        ].max(),
        15 / np.sqrt(3 * 16**2),
    )
    assert np.isclose(
        entorno["df_sintetico"].loc[
            entorno["df_sintetico"]["Subject"] == "ADL-0", "GVM"
        ].iloc[0],
        100 / np.sqrt(3 * 2000**2),
    )
    np.testing.assert_array_equal(
        np.bincount(entorno["y_aumentado"], minlength=2), [35, 45]
    )
    assert tuple(entorno["salida_sintetica"].shape) == (2, 1)
    assert entorno["modelo_prueba"].count_params() == 14_635
    leaky_relu = [
        layer
        for layer in entorno["modelo_prueba"].layers
        if isinstance(layer, entorno["layers"].LeakyReLU)
    ]
    assert len(leaky_relu) == 4
    assert all(layer.negative_slope == 0.2 for layer in leaky_relu)

    assert entorno["x_calibration_sintetico"].shape == (1000, 150, 2)
    np.testing.assert_array_equal(
        np.bincount(entorno["y_calibration_sintetico"], minlength=2), [400, 600]
    )
    metricas = entorno["calcular_metricas"](
        np.array([0, 0, 1, 1]), np.array([0.1, 0.8, 0.3, 0.9])
    )
    assert {"accuracy", "precision", "recall", "specificity", "f1", "auc"} <= metricas.keys()

    grupo_caida = entorno["df_sintetico"].loc[
        entorno["df_sintetico"]["Subject"] == "Fall-0"
    ].copy()
    duplicado = grupo_caida.copy()
    duplicado.loc[duplicado.index[1], "Sample_Index"] = duplicado.iloc[0]["Sample_Index"]
    with pytest.raises(ValueError, match="duplicados"):
        entorno["crear_ventanas"](duplicado)
    discontinuo = grupo_caida.copy()
    discontinuo.loc[discontinuo.index[10], "Sample_Index"] = 1000
    with pytest.raises(ValueError, match="consecutivos"):
        entorno["crear_ventanas"](discontinuo)

    save_source = sources["litefallnet-guardar-code"]
    save_source_compacto = " ".join(save_source.split())
    assert "seleccionar_calibracion( x_train_original, y_train_original )" in save_source_compacto
    assert "y_calibration=y_calibration" in save_source
    assert "x_calibration=x_calibration" in save_source
    assert "tensorflow_model_optimization" not in source
    assert "EJECUTAR_QAT" not in source


def test_training_dataset_rejects_non_finite_sensor_values():
    name = "03_Entrenamiento_LiteFallNet_SisFall.ipynb"
    notebook = load_notebook(name)
    cells = {cell["id"]: "".join(cell["source"]) for cell in notebook["cells"]}
    entorno = {}
    for cell_id in ("litefallnet-imports", "litefallnet-funciones-code"):
        exec(compile(cells[cell_id], cell_id, "exec"), entorno)

    df = entorno["pd"].DataFrame(
        {
            "Dataset": ["SisFall"],
            "Subject": ["ADL-0"],
            "Activity_Code": ["D01"],
            "Trial": [1],
            "Activity_Label": ["ADL"],
            "Sample_Index": [0],
            "AVM": [1.0],
            "GVM": [2.0],
        }
    )
    for canal, valor in (("AVM", np.inf), ("GVM", -np.inf)):
        with pytest.raises(ValueError, match="valores no finitos"):
            entorno["validar_dataset"](df.assign(**{canal: valor}))
