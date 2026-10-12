#!/usr/bin/env python3
"""Resumen auditable de una corrida del reproductor ESP32.

Lee `results.csv` + `run_metadata.json` de un directorio de corrida y calcula:
- A por trial: matriz de confusion contra etiquetas KFall y contra la
  referencia de reglas del host; sensibilidad/especificidad/precision/F1
  (INDETERMINADO se informa aparte y no entra en la matriz binaria).
- B por registro: matriz contra etiquetas PTB-XL y paridad con la referencia
  del host (checksum del tensor y delta de q).
- Triaje: generado contra etiquetas del manifiesto y contra las salidas
  reales de los agentes; taxonomia de errores (transporte/reglas/ECG/logica).
- Tiempos por etapa (mediana/P95) y memoria (heap).

Uso:
  .venv/bin/python scripts/esp32_simulation/summarize.py \
      --run-dir reports/esp32_validation/full \
      --dataset-dir notebooks/data/esp32_simulation/rule_based/full
"""

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay  # noqa: E402


def _metrics(matrix: dict, positive: str) -> dict:
    """Sens/esp/prec/F1 para una matriz {predicho: {real: n}}."""
    tp = matrix.get(positive, {}).get(positive, 0)
    fp = sum(count for real, count in matrix.get(positive, {}).items() if real != positive)
    fn = sum(row.get(positive, 0) for label, row in matrix.items() if label != positive)
    tn = sum(
        count
        for label, row in matrix.items()
        if label != positive
        for real, count in row.items()
        if real != positive
    )
    sensitivity = tp / (tp + fn) if tp + fn else None
    specificity = tn / (tn + fp) if tn + fp else None
    precision = tp / (tp + fp) if tp + fp else None
    if precision and sensitivity:
        f1 = 2 * precision * sensitivity / (precision + sensitivity)
    else:
        f1 = None
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "sensitivity": sensitivity, "specificity": specificity,
        "precision": precision, "f1": f1,
    }


def _matrix(pairs: list[tuple[str, str]]) -> dict:
    matrix: dict = {}
    for predicted, real in pairs:
        matrix.setdefault(predicted, {})
        matrix[predicted][real] = matrix[predicted].get(real, 0) + 1
    return matrix


def _stats(series: pd.Series) -> dict:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return {"n": 0}
    return {
        "n": int(values.size),
        "median": float(values.median()),
        "p95": float(np.percentile(values, 95)),
        "max": float(values.max()),
    }


def summarize(run_dir: Path, dataset_dir: Path) -> dict:
    import math

    rows = pd.read_csv(run_dir / "results.csv", dtype=str).fillna("")
    metadata = json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))
    summary_ref = json.loads(
        (dataset_dir / "ecg_reference_summary.json").read_text(encoding="utf-8")
    )
    ref_by_id = {int(record["ecg_id"]): record for record in summary_ref["records"]}

    statuses: dict = {}
    for status in rows["status"]:
        statuses[status] = statuses.get(status, 0) + 1

    trial_rows = rows[rows["kind"] == "trial_A"]
    record_rows = rows[rows["kind"] == "record_B"]
    scenario_rows = rows[rows["kind"] == "scenario"]

    a_pairs = [(row["predicted_class"], row["reference_class"]) for _, row in trial_rows.iterrows()]
    a_matrix = _matrix(a_pairs)
    a_indeterminados = int((trial_rows["predicted_class"] == "INDETERMINADO").sum())
    a_valid = trial_rows[trial_rows["predicted_class"].isin(["Fall", "ADL"])]
    a_metrics = _metrics(
        _matrix([(row["predicted_class"], row["reference_class"]) for _, row in a_valid.iterrows()]),
        "Fall",
    )
    a_vs_rules = {
        "matches": 0,
        "total": 0,
        "mismatches": [],
    }
    for _, row in trial_rows.iterrows():
        if row["status"] != "ok":
            continue
        a_vs_rules["total"] += 1
        expected = replay.rule_reference(dataset_dir, row["case_id"])["clase"]
        if expected == row["predicted_class"]:
            a_vs_rules["matches"] += 1
        else:
            a_vs_rules["mismatches"].append(
                {"trial_id": row["case_id"], "device": row["predicted_class"], "rules": expected}
            )

    b_pairs = [(row["predicted_class"], row["reference_class"]) for _, row in record_rows.iterrows()]
    b_metrics = _metrics(_matrix(b_pairs), "ANORMAL")
    b_parity = {"checksum_matches": 0, "q_exact": 0, "q_within_2": 0, "total": 0, "max_abs_delta": 0}
    for _, row in record_rows.iterrows():
        if row["status"] != "ok":
            continue
        ecg_id = int(row["ecg_id"])
        reference = ref_by_id.get(ecg_id)
        if reference is None or "q" not in reference:
            continue
        b_parity["total"] += 1
        expected_fnv = replay.tensor_checksum(dataset_dir, ecg_id)
        if int(row["tensor_fnv"]) == expected_fnv:
            b_parity["checksum_matches"] += 1
        delta = abs(int(row["q"]) - int(reference["q"]))
        b_parity["max_abs_delta"] = max(b_parity["max_abs_delta"], int(math.floor(delta)))
        if delta == 0:
            b_parity["q_exact"] += 1
        if delta <= 2:
            b_parity["q_within_2"] += 1

    output_by_trial = {row["case_id"]: row["predicted_class"] for _, row in trial_rows.iterrows()}
    output_by_ecg = {int(row["ecg_id"]): row["predicted_class"] for _, row in record_rows.iterrows()}
    triage_labels = [(row["predicted_class"], row["reference_class"]) for _, row in scenario_rows.iterrows()]
    triage_outputs_pairs = []
    triage_logic_mismatches = []
    triage_not_evaluable = 0
    for _, row in scenario_rows.iterrows():
        fall_class = output_by_trial.get(row["fall_trial_id"])
        ecg_class = output_by_ecg.get(int(row["ecg_id"]))
        if fall_class is None or ecg_class is None:
            triage_not_evaluable += 1
            continue
        expected = replay.TRIAGE_TABLE.get((fall_class, ecg_class), "INDETERMINADO")
        triage_outputs_pairs.append((row["predicted_class"], expected))
        if expected != row["predicted_class"]:
            triage_logic_mismatches.append(
                {
                    "scenario_id": row["scenario_id"],
                    "device": row["predicted_class"],
                    "expected_from_outputs": expected,
                }
            )

    timings = {
        "fall_us": _stats(trial_rows["fall_us"]),
        "preproc_us": _stats(record_rows["preproc_us"]),
        "infer_us": _stats(record_rows["infer_us"]),
        "triage_us": _stats(scenario_rows["triage_us"]),
    }
    e2e = {
        kind: _stats(rows[rows["kind"] == kind]["e2e_ms"])
        for kind in ("trial_A", "record_B", "scenario")
    }
    heap_values = pd.to_numeric(rows["heap"], errors="coerce").dropna()
    hello = metadata.get("device_hello", [])
    heap_initial = next(
        (int(line.split("heap=")[1].split(",")[0]) for line in hello if "heap=" in line), None
    )
    memory = {
        "heap_initial": heap_initial,
        "heap_min": int(heap_values.min()) if not heap_values.empty else None,
        "heap_max": int(heap_values.max()) if not heap_values.empty else None,
        "heap_last": int(heap_values.iloc[-1]) if not heap_values.empty else None,
    }

    scheduling = None
    if "sched_late_max_ms" in rows.columns:
        paced = rows[rows["sched_late_max_ms"].astype(str) != ""]
        if not paced.empty:
            scheduling = {}
            for kind, group in paced.groupby("kind"):
                scheduling[kind] = {
                    "cases": int(len(group)),
                    "late_median_ms_median": float(
                        pd.to_numeric(group["sched_late_median_ms"], errors="coerce").median()
                    ),
                    "late_p95_ms_max": float(
                        pd.to_numeric(group["sched_late_p95_ms"], errors="coerce").max()
                    ),
                    "late_max_ms_max": float(
                        pd.to_numeric(group["sched_late_max_ms"], errors="coerce").max()
                    ),
                }
    repeats = None
    if "repeat_index" in rows.columns:
        repeat_values = pd.to_numeric(rows["repeat_index"], errors="coerce").dropna()
        if not repeat_values.empty:
            repeats = {
                int(key): int(value)
                for key, value in repeat_values.value_counts().sort_index().items()
            }

    expected_rows = len(trial_rows) + len(record_rows) + len(scenario_rows)
    summary = {
        "run_dir": str(run_dir),
        "dataset_dir": str(dataset_dir),
        "suite": metadata.get("suite"),
        "mode": metadata.get("mode"),
        "rows": int(len(rows)),
        "statuses": statuses,
        "agent_a": {
            "vs_labels": {"matrix": a_matrix, "indeterminados": a_indeterminados, **a_metrics},
            "vs_rules_reference": a_vs_rules,
        },
        "agent_b": {
            "vs_labels": {"matrix": _matrix(b_pairs), **b_metrics},
            "vs_host_reference": b_parity,
        },
        "triage": {
            "generated_vs_labels": {
                "matrix": _matrix(triage_labels),
                "matches": sum(1 for a, b in triage_labels if a == b),
                "total": len(triage_labels),
            },
            "generated_vs_outputs": {
                "matrix": _matrix(triage_outputs_pairs),
                "matches": sum(1 for a, b in triage_outputs_pairs if a == b),
                "total": len(triage_outputs_pairs),
                "not_evaluable": triage_not_evaluable,
                "mismatches": triage_logic_mismatches,
            },
        },
        "errors": {
            "transport": expected_rows - statuses.get("ok", 0),
            "a_vs_rules_mismatches": a_vs_rules["total"] - a_vs_rules["matches"],
            "b_checksum_mismatches": b_parity["total"] - b_parity["checksum_matches"],
            "triage_logic_mismatches": len(triage_logic_mismatches),
        },
        "timings_us": timings,
        "e2e_ms": e2e,
        "memory": memory,
        "scheduling": scheduling,
        "repeats": repeats,
    }
    return summary


def print_summary(summary: dict) -> None:
    print(f"== corrida {summary['run_dir']} ({summary['suite']}, {summary['mode']})")
    print(f"filas={summary['rows']} estados={summary['statuses']}")
    a = summary["agent_a"]
    print(
        f"A por trial: matriz={a['vs_labels']['matrix']} indeterminados={a['vs_labels']['indeterminados']} "
        f"sens={a['vs_labels']['sensitivity']} esp={a['vs_labels']['specificity']} "
        f"prec={a['vs_labels']['precision']} F1={a['vs_labels']['f1']}"
    )
    print(
        f"A vs reglas host: {a['vs_rules_reference']['matches']}/{a['vs_rules_reference']['total']} "
        f"discrepancias={a['vs_rules_reference']['mismatches']}"
    )
    b = summary["agent_b"]
    print(
        f"B por registro: matriz={b['vs_labels']['matrix']} sens={b['vs_labels']['sensitivity']} "
        f"esp={b['vs_labels']['specificity']} prec={b['vs_labels']['precision']} "
        f"F1={b['vs_labels']['f1']}"
    )
    parity = b["vs_host_reference"]
    print(
        f"B vs host: checksum {parity['checksum_matches']}/{parity['total']}, "
        f"q exacto {parity['q_exact']}/{parity['total']}, |dq|<=2 {parity['q_within_2']}/{parity['total']}, "
        f"max|dq|={parity['max_abs_delta']}"
    )
    triage = summary["triage"]
    print(
        f"Triaje vs etiquetas: {triage['generated_vs_labels']['matches']}/{triage['generated_vs_labels']['total']} "
        f"matriz={triage['generated_vs_labels']['matrix']}"
    )
    outputs = triage["generated_vs_outputs"]
    print(
        f"Triaje vs salidas reales: {outputs['matches']}/{outputs['total']} "
        f"no_evaluables={outputs.get('not_evaluable', 0)} matriz={outputs['matrix']}"
    )
    print(f"Errores: {summary['errors']}")
    for stage, stats in summary["timings_us"].items():
        print(f"tiempo {stage}: {stats}")
    print(f"heap: {summary['memory']}")
    if summary.get("scheduling"):
        print(f"planificacion (retraso vs calendario): {summary['scheduling']}")
    if summary.get("repeats"):
        print(f"repeticiones: {summary['repeats']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None, help="por defecto <run-dir>/summary.json")
    args = parser.parse_args()
    summary = summarize(args.run_dir, args.dataset_dir)
    output = args.output or (args.run_dir / "summary.json")
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print_summary(summary)
    print(f"summary: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
