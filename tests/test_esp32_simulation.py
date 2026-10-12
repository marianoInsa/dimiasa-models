"""Pruebas offline del reproductor ESP32 (sin placa): reglas, triaje, parser y CSV."""

import csv
import json
from pathlib import Path
import sys

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts" / "esp32_simulation"
sys.path.insert(0, str(SCRIPTS))

import replay  # noqa: E402
import summarize  # noqa: E402


def _write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def make_dataset(tmp_path: Path) -> Path:
    """Dataset sintetico minimo: 3 trials, 1 ECG y 3 escenarios."""
    base = tmp_path / "smoke"
    base.mkdir()

    trials = {
        "KTR0001": ("Fall", "impact_still", 300),
        "KTR0002": ("ADL", "quiet", 200),
        "KTR0003": ("Fall", "impact_pending", 200),
    }
    fall_header = [
        "trial_id", "Subject", "Activity_Label", "Activity_Code", "Trial", "trial_label",
        "stream_sample", "Sample_Index", "Ax", "Ay", "Az", "Gx", "Gy", "Gz",
    ]
    manifest_header = [
        "trial_id", "subject", "activity_code", "activity_label", "trial_number",
        "trial_label", "source_samples", "stream_samples", "trim_remainder", "windows",
        "rate_hz",
    ]
    fall_rows, manifest_rows = [], []
    for trial_id, (label, kind, count) in trials.items():
        for i in range(count):
            if kind != "quiet" and i < 100:
                strong = i % 2 == 1
                values = (0, 0, 3.5, 0, 200, 0) if strong else (0, 0, 1, 0, 0, 0)
            else:
                values = (0, 0, 1, 0, 0, 0)
            fall_rows.append(
                [trial_id, "S1", label, "X", 1, label, i, i,
                 *[f"{value:.6f}" for value in values]]
            )
        manifest_rows.append(
            [trial_id, "S1", "X", label, 1, label, count, count, 0, count // 100, 100]
        )
    _write_csv(base / "fall_stream.csv", fall_header, fall_rows)
    _write_csv(base / "fall_trial_manifest.csv", manifest_header, manifest_rows)

    ecg_id = 7
    _write_csv(
        base / "ecg_records.csv",
        ["ecg_id", "patient_id", "strat_fold", "label_int", "label_name", "samples",
         "frequency_hz", "duration_seconds"],
        [[ecg_id, 1.0, 10, 0, "NORMAL", 2500, 250, 10.0]],
    )
    _write_csv(
        base / "ecg_stream.csv",
        ["ecg_id", "patient_id", "strat_fold", "label_int", "label_name", "sample_index",
         "time_seconds", "lead_ii_value_original", "adc_count_sim"],
        [[ecg_id, 1.0, 10, 0, "NORMAL", i, i / 250, 0.0, 2048] for i in range(2500)],
    )
    _write_csv(
        base / "ecg_reference.csv",
        ["ecg_id", "sample_index", "adc_count_sim", "filtered_zscore", "int8"],
        [[ecg_id, i, 2048, 0.0, 0] for i in range(2500)],
    )
    (base / "ecg_reference_summary.json").write_text(
        json.dumps(
            {
                "records": [
                    {
                        "ecg_id": ecg_id,
                        "int8_sha256": "0" * 64,
                        "saturated": 0,
                        "float_min": -1.0,
                        "float_max": 1.0,
                        "q": -5,
                        "p": 0.48046875,
                        "clase": "NORMAL",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        base / "scenario_manifest.csv",
        ["scenario_id", "fall_trial_id", "fall_reference_label", "ecg_id",
         "ecg_reference_label", "expected_triage_from_reference_labels", "pairing_type"],
        [
            ["S0001", "KTR0001", "Fall", ecg_id, "NORMAL", "ROJO", "SYNTHETIC_UNSYNCHRONIZED"],
            ["S0002", "KTR0002", "ADL", ecg_id, "NORMAL", "VERDE", "SYNTHETIC_UNSYNCHRONIZED"],
            ["S0003", "KTR0003", "Fall", ecg_id, "NORMAL", "ROJO", "SYNTHETIC_UNSYNCHRONIZED"],
        ],
    )
    (base / "summary.json").write_text(
        json.dumps({"sources": {"fall_csv_sha256": "a" * 64, "ecg_h5_sha256": "b" * 64}}),
        encoding="utf-8",
    )
    return base


def test_rule_reference_tres_caminos(tmp_path):
    dataset = make_dataset(tmp_path)
    fall = replay.rule_reference(dataset, "KTR0001")
    assert (fall["clase"], fall["estado"], fall["confirmado"], fall["ventanas"]) == (
        "Fall", "NORMAL", 1, 3,
    )
    adl = replay.rule_reference(dataset, "KTR0002")
    assert (adl["clase"], adl["confirmado"]) == ("ADL", 0)
    indeterminate = replay.rule_reference(dataset, "KTR0003")
    assert (indeterminate["clase"], indeterminate["estado"]) == (
        "INDETERMINADO", "POSIBLE_CAIDA",
    )


def test_tabla_triaje_cuatro_reglas():
    assert replay.TRIAGE_TABLE[("Fall", "ANORMAL")] == "ROJO"
    assert replay.TRIAGE_TABLE[("Fall", "NORMAL")] == "AMARILLO"
    assert replay.TRIAGE_TABLE[("ADL", "ANORMAL")] == "AMARILLO"
    assert replay.TRIAGE_TABLE[("ADL", "NORMAL")] == "VERDE"


def test_triaje_esperado_desde_salidas_reales(tmp_path):
    dataset = make_dataset(tmp_path)
    color, fall_class, ecg_class = replay.expected_case_triage(dataset, "KTR0001", 7)
    assert (color, fall_class, ecg_class) == ("AMARILLO", "Fall", "NORMAL")
    color, _, _ = replay.expected_case_triage(dataset, "KTR0003", 7)
    assert color == "INDETERMINADO"


def test_asociaciones_de_manifiestos(tmp_path):
    dataset = make_dataset(tmp_path)
    scenario = replay.load_scenario(dataset, "S0001")
    assert scenario["fall_trial_id"] == "KTR0001"
    assert int(scenario["ecg_id"]) == 7
    assert scenario["expected_triage_from_reference_labels"] == "ROJO"

    count, label, sample_lines = replay.load_trial(dataset, "KTR0001")
    assert (count, label, len(sample_lines)) == (300, "Fall", 300)
    assert sample_lines[0].startswith("S,0,")

    count_b, ecg_lines = replay.load_ecg(dataset, 7)
    assert (count_b, len(ecg_lines)) == (2500, 2500)
    assert ecg_lines[-1] == "S,2499,2048"

    with pytest.raises(SystemExit):
        replay.load_trial(dataset, "KTR9999")
    with pytest.raises(SystemExit):
        replay.load_scenario(dataset, "S9999")


def test_parser_host_de_lineas():
    agent_a = replay.parse_agent_a("AGENT,A,t1,Fall,NORMAL,1,300,3,900,123456")
    assert agent_a is not None
    assert (agent_a["clase"], agent_a["ventanas"], agent_a["fall_us"]) == ("Fall", 3, 900)
    assert replay.parse_agent_a("AGENT,A,t1,Fall") is None
    assert replay.parse_agent_a("AGENT,B,x,NORMAL,-5,0.48,2500,0,1,0,1,2,3,4") is None

    agent_b = replay.parse_agent_b(
        "AGENT,B,x,NORMAL,-5,0.48046875,2500,0,99,0.1,5.6,108000,1113000,194000"
    )
    assert agent_b is not None
    assert (agent_b["q"], agent_b["tensor_fnv"]) == (-5, 99)
    assert replay.parse_agent_b(
        "AGENT,B,x,NORMAL,-5,no,2500,0,99,0.1,5.6,108000,1113000,194000"
    ) is None

    result = replay.parse_result_line("RESULT,S0001,ROJO,Fall,ANORMAL,7")
    assert result is not None
    assert (result["color"], result["triage_us"]) == ("ROJO", 7)
    assert replay.parse_result_line("RESULT,S0001,ROJO,Fall") is None


def test_filtros_y_estadisticas_de_planificacion():
    assert replay.parse_id_filter("a, b,,c") == ["a", "b", "c"]
    assert replay.parse_id_filter(None) == []
    assert replay.late_stats([]) == ("", "", "")
    median, p95, maximum = replay.late_stats([1.0, 2.0, 3.0, 4.0])
    assert (median, p95, maximum) == (2.5, 3.85, 4.0)
    for column in ("repeat_index", "sched_late_max_ms"):
        assert column in replay.RESULTS_COLUMNS


def test_esquema_y_escritura_de_results(tmp_path):
    rows = [
        {"case_id": "KTR0001", "kind": "trial_A", "predicted_class": "Fall",
         "status": "ok", "mode": "fast"},
        {"case_id": "7", "kind": "record_B", "predicted_class": "NORMAL", "q": -5,
         "status": "ok", "mode": "fast"},
    ]
    path = tmp_path / "results.csv"
    replay.write_results(rows, path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        data = list(reader)
        fieldnames = reader.fieldnames
    assert fieldnames == replay.RESULTS_COLUMNS
    assert len(data) == 2
    assert data[0]["case_id"] == "KTR0001"
    assert data[1]["q"] == "-5"
    assert data[0]["fall_trial_id"] == ""
    assert data[0]["mode"] == "fast"


def test_metrics_matrices_m7():
    matrix_a = {"Fall": {"Fall": 7, "ADL": 1}, "ADL": {"ADL": 7}}
    metrics = summarize._metrics(matrix_a, "Fall")
    assert (metrics["tp"], metrics["fp"], metrics["fn"], metrics["tn"]) == (7, 1, 0, 7)
    assert metrics["sensitivity"] == pytest.approx(1.0)
    assert metrics["specificity"] == pytest.approx(0.875)
    assert metrics["precision"] == pytest.approx(0.875)

    matrix_b = {
        "NORMAL": {"NORMAL": 17, "ANORMAL": 4},
        "ANORMAL": {"NORMAL": 3, "ANORMAL": 16},
    }
    metrics = summarize._metrics(matrix_b, "ANORMAL")
    assert (metrics["tp"], metrics["fp"], metrics["fn"], metrics["tn"]) == (16, 3, 4, 17)
    assert metrics["sensitivity"] == pytest.approx(0.8)
    assert metrics["specificity"] == pytest.approx(0.85)
    assert metrics["precision"] == pytest.approx(16 / 19)
    assert metrics["f1"] == pytest.approx(0.8205128205128205)
