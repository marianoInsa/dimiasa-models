#!/usr/bin/env python3
"""Create replay datasets for the ESP32 rule-based fall agent (A) and TinyECGNet (B).

Inputs
------
- KFall-Reduced.csv with Subject, Activity_Label, Activity_Code, Trial,
  Sample_Index, Ax, Ay, Az, Gx, Gy, Gz at the dataset's native 100 Hz,
  in g and degrees/s.
- HDF5 with X (N, 2500), y, ecg_id, patient_id and strat_fold datasets.

Outputs (under --out)
---------------------
- fall_stream.csv: whole KFall trials, original six axes at 100 Hz, trimmed to a
  whole number of 100-sample windows. Replay one trial at a time; never join
  trial boundaries.
- fall_trial_manifest.csv: one row per trial with source/sent sample counts.
- ecg_records.csv: metadata for selected complete ECG records.
- ecg_stream.csv: 2,500 Lead-II samples per record at 250 Hz, original value plus
  an optional simulated 12-bit ADC count using one global affine scale.
- scenario_manifest.csv: synthetic fall-trial/ECG pairings covering the four
  triage table cells, referencing fall_trial_id (not windows).
- summary.json: counts, source hashes, assumptions and warnings.

This script does NOT filter, resample or quantize model inputs. Do that in the
firmware, using exactly the same preprocessing as the trained model. Requires
numpy, pandas, h5py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd

FALL_COLUMNS = ["Ax", "Ay", "Az", "Gx", "Gy", "Gz"]
FALL_RATE_HZ = 100
FALL_WINDOW_SAMPLES = 100
ECG_WINDOW = 2500
TRIAGE_BY_CELL = {
    ("Fall", "ANORMAL"): "ROJO",
    ("Fall", "NORMAL"): "AMARILLO",
    ("ADL", "ANORMAL"): "AMARILLO",
    ("ADL", "NORMAL"): "VERDE",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fall-csv", required=True, type=Path, help="Path to KFall-Reduced.csv")
    p.add_argument("--ecg-h5", required=True, type=Path, help="Path to the HDF5 ECG dataset")
    p.add_argument("--out", required=True, type=Path, help="Output directory")
    p.add_argument("--fall-trials-per-class", type=int, default=10,
                   help="Number of Fall and ADL trials to select (default: 10 each)")
    p.add_argument("--ecg-records-per-class", type=int, default=20,
                   help="Number of ECG records per class from fold 10 (default: 20 each)")
    p.add_argument("--scenarios-per-cell", type=int, default=5,
                   help="Synthetic pairings per each of the four decision-table cells (default: 5)")
    p.add_argument("--seed", type=int, default=20261010, help="Random seed")
    p.add_argument("--h5-x-key", default="X")
    p.add_argument("--h5-y-key", default="y")
    p.add_argument("--h5-ecg-id-key", default="ecg_id")
    p.add_argument("--h5-patient-id-key", default="patient_id")
    p.add_argument("--h5-fold-key", default="strat_fold")
    p.add_argument("--test-fold", type=int, default=10,
                   help="Held-out fold to sample from (default: 10)")
    p.add_argument("--no-adc-simulation", action="store_true",
                   help="Do not generate the simulated 12-bit adc_count column")
    return p.parse_args()


def decode_scalar(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, np.bytes_):
        return bytes(value).decode("utf-8", errors="replace")
    if isinstance(value, np.generic):
        return value.item()
    return value


def class_from_activity(label: Any) -> str:
    s = str(decode_scalar(label)).strip().lower()
    if "fall" in s:
        return "Fall"
    if "adl" in s or "daily" in s or "walking" in s or "sitting" in s or "standing" in s:
        return "ADL"
    raise ValueError(
        f"No puedo interpretar Activity_Label={label!r} como Fall/ADL. "
        "Inspeccioná los valores y adaptá class_from_activity() si el CSV usa otros nombres."
    )


def balanced_trial_selection(
    groups: list[tuple[tuple[Any, ...], pd.DataFrame]], n_per_class: int, rng: np.random.Generator
) -> list[tuple[tuple[Any, ...], pd.DataFrame, str]]:
    candidates: dict[str, list[tuple[tuple[Any, ...], pd.DataFrame]]] = {"Fall": [], "ADL": []}
    for key, frame in groups:
        if len(frame) < FALL_WINDOW_SAMPLES:
            continue
        cls = class_from_activity(frame["Activity_Label"].iloc[0])
        candidates[cls].append((key, frame))

    chosen: list[tuple[tuple[Any, ...], pd.DataFrame, str]] = []
    for cls in ("Fall", "ADL"):
        pool = candidates[cls]
        if len(pool) < n_per_class:
            raise ValueError(
                f"Hay solo {len(pool)} trials {cls} con al menos {FALL_WINDOW_SAMPLES} muestras; "
                f"se solicitaron {n_per_class}. Reducí --fall-trials-per-class."
            )
        perm = rng.permutation(len(pool))
        # Prefer one trial per subject before reusing a subject.
        ordered = [pool[i] for i in perm]
        first_pass: list[tuple[tuple[Any, ...], pd.DataFrame]] = []
        deferred: list[tuple[tuple[Any, ...], pd.DataFrame]] = []
        subjects: set[str] = set()
        for item in ordered:
            subj = str(decode_scalar(item[1]["Subject"].iloc[0]))
            if subj not in subjects:
                first_pass.append(item)
                subjects.add(subj)
            else:
                deferred.append(item)
        for key, frame in (first_pass + deferred)[:n_per_class]:
            chosen.append((key, frame, cls))
    return chosen


def prepare_fall(args: argparse.Namespace, rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    df = pd.read_csv(args.fall_csv)
    required = ["Subject", "Activity_Label", "Activity_Code", "Trial", "Sample_Index", *FALL_COLUMNS]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el CSV de caídas: {missing}")

    group_cols = ["Subject", "Activity_Label", "Activity_Code", "Trial"]
    grouped = [(key if isinstance(key, tuple) else (key,), frame.sort_values("Sample_Index").reset_index(drop=True))
               for key, frame in df.groupby(group_cols, sort=False, dropna=False)]
    selected = balanced_trial_selection(grouped, args.fall_trials_per_class, rng)

    stream_rows: list[pd.DataFrame] = []
    manifest_rows: list[dict[str, Any]] = []
    trial_counts = {"Fall": 0, "ADL": 0}
    for seq, (key, trial, trial_cls) in enumerate(selected, start=1):
        trial_id = f"KTR{seq:04d}"
        trial_counts[trial_cls] += 1
        values = trial[FALL_COLUMNS].apply(pd.to_numeric, errors="coerce")
        if values.isna().any().any():
            raise ValueError(f"Valores no numéricos/ausentes en trial {key}; limpiá el CSV antes de continuar.")
        arr = values.to_numpy(dtype=np.float32)
        if not np.isfinite(arr).all():
            raise ValueError(f"Valores no finitos en trial {key}; limpiá el CSV antes de continuar.")

        source_samples = int(len(trial))
        stream_samples = (source_samples // FALL_WINDOW_SAMPLES) * FALL_WINDOW_SAMPLES
        if stream_samples < FALL_WINDOW_SAMPLES:
            raise ValueError(f"El trial {key} no alcanza una ventana completa de {FALL_WINDOW_SAMPLES} muestras.")

        # Se envían solo ventanas completas de 100 muestras; el resto queda
        # registrado en el manifiesto. Un bloque truncado por el transporte no
        # puede producir ADL (ver contrato del firmware).
        trimmed = trial.iloc[:stream_samples]
        src = trimmed.copy()
        src.insert(0, "trial_id", trial_id)
        src.insert(1, "trial_label", trial_cls)
        src["stream_sample"] = np.arange(stream_samples, dtype=np.int32)
        src = src[["trial_id", "Subject", "Activity_Label", "Activity_Code", "Trial",
                   "trial_label", "stream_sample", "Sample_Index", *FALL_COLUMNS]]
        stream_rows.append(src)

        manifest_rows.append({
            "trial_id": trial_id,
            "subject": decode_scalar(trial["Subject"].iloc[0]),
            "activity_code": decode_scalar(trial["Activity_Code"].iloc[0]),
            "activity_label": decode_scalar(trial["Activity_Label"].iloc[0]),
            "trial_number": int(trial["Trial"].iloc[0]),
            "trial_label": trial_cls,
            "source_samples": source_samples,
            "stream_samples": stream_samples,
            "trim_remainder": source_samples - stream_samples,
            "windows": stream_samples // FALL_WINDOW_SAMPLES,
            "rate_hz": FALL_RATE_HZ,
        })

    stream = pd.concat(stream_rows, ignore_index=True)
    trials = pd.DataFrame(manifest_rows)
    return stream, trials, {
        "source_rows": int(len(df)),
        "selected_trials": int(len(selected)),
        "selected_trials_by_label": trial_counts,
        "stream_samples": int(len(stream)),
        "windows": int(len(stream) // FALL_WINDOW_SAMPLES),
        "input_rate_hz": FALL_RATE_HZ,
        "window_samples": FALL_WINDOW_SAMPLES,
        "window_seconds": 1.0,
        "trim_policy": (
            "each trial keeps floor(samples/100)*100 samples so every delivered window is complete; "
            "trim_remainder is recorded per trial and no sample is resampled or filtered"
        ),
        "warning": (
            "Declared prototype mount is the waist (pelvic/lumbar zone), consistent with KFall's "
            "lower-back IMU; the donor sketch's chest comment does not apply to this run. "
            "KFall-Reduced has no impact-time anchor, so A is evaluated per trial and no event "
            "latency is reported."
        ),
    }


def read_h5_vector(h5: h5py.File, key: str) -> np.ndarray:
    if key not in h5:
        raise KeyError(f"No existe la clave HDF5 {key!r}; claves disponibles: {list(h5.keys())}")
    return np.asarray(h5[key]).reshape(-1)


def prepare_ecg(args: argparse.Namespace, rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    with h5py.File(args.ecg_h5, "r") as h5:
        required_keys = [args.h5_x_key, args.h5_y_key, args.h5_ecg_id_key,
                         args.h5_patient_id_key, args.h5_fold_key]
        missing = [k for k in required_keys if k not in h5]
        if missing:
            raise KeyError(f"Faltan claves HDF5: {missing}. Claves disponibles: {list(h5.keys())}")
        X = np.asarray(h5[args.h5_x_key])
        y = read_h5_vector(h5, args.h5_y_key).astype(int)
        ecg_ids = read_h5_vector(h5, args.h5_ecg_id_key)
        patient_ids = read_h5_vector(h5, args.h5_patient_id_key)
        folds = read_h5_vector(h5, args.h5_fold_key).astype(int)

    if X.ndim != 2 or X.shape[1] != ECG_WINDOW:
        raise ValueError(f"Se esperaba X de forma (N, {ECG_WINDOW}); se recibió {X.shape}.")
    n = X.shape[0]
    if any(len(v) != n for v in (y, ecg_ids, patient_ids, folds)):
        raise ValueError("Las longitudes de X, y, ecg_id, patient_id y strat_fold no coinciden.")
    if not set(np.unique(y)).issubset({0, 1}):
        raise ValueError(f"Se esperaban etiquetas binarias 0/1; se encontraron {np.unique(y).tolist()}.")

    eligible = np.flatnonzero(folds == args.test_fold)
    selected_idx: list[int] = []
    for label in (0, 1):
        candidates = eligible[y[eligible] == label]
        if len(candidates) < args.ecg_records_per_class:
            raise ValueError(
                f"Fold {args.test_fold}: hay {len(candidates)} registros clase {label}; "
                f"se solicitaron {args.ecg_records_per_class}. Reducí --ecg-records-per-class o comprobá el fold."
            )
        selected_idx.extend(rng.choice(candidates, size=args.ecg_records_per_class, replace=False).tolist())
    selected_idx = sorted(selected_idx, key=lambda i: (int(y[i]), str(decode_scalar(ecg_ids[i]))))
    X_sel = np.asarray(X[selected_idx], dtype=np.float32)

    # Optional affine mapping to plausible 12-bit ADC counts. This is a replay adapter,
    # NOT a physical calibration of a specific AD8232 circuit. One scale is shared across records.
    peak = float(np.nanmax(np.abs(X_sel))) if X_sel.size else 0.0
    if not np.isfinite(peak) or peak <= 0:
        raise ValueError("Las señales ECG seleccionadas contienen valores inválidos o amplitud nula.")
    gain = 1600.0 / peak

    metadata_rows: list[dict[str, Any]] = []
    sample_frames: list[pd.DataFrame] = []
    for idx, signal in zip(selected_idx, X_sel):
        eid = decode_scalar(ecg_ids[idx])
        pid = decode_scalar(patient_ids[idx])
        label = int(y[idx])
        cls = "NORMAL" if label == 0 else "ANORMAL"
        metadata_rows.append({
            "ecg_id": eid,
            "patient_id": pid,
            "strat_fold": int(folds[idx]),
            "label_int": label,
            "label_name": cls,
            "samples": ECG_WINDOW,
            "frequency_hz": 250,
            "duration_seconds": 10.0,
        })
        frame = pd.DataFrame({
            "ecg_id": [eid] * ECG_WINDOW,
            "patient_id": [pid] * ECG_WINDOW,
            "strat_fold": [int(folds[idx])] * ECG_WINDOW,
            "label_int": [label] * ECG_WINDOW,
            "label_name": [cls] * ECG_WINDOW,
            "sample_index": np.arange(ECG_WINDOW, dtype=np.int32),
            "time_seconds": np.arange(ECG_WINDOW, dtype=np.float32) / 250.0,
            "lead_ii_value_original": signal,
        })
        if not args.no_adc_simulation:
            adc = np.rint(2048.0 + np.nan_to_num(signal, nan=0.0) * gain)
            frame["adc_count_sim"] = np.clip(adc, 0, 4095).astype(np.uint16)
        sample_frames.append(frame)

    records = pd.DataFrame(metadata_rows)
    samples = pd.concat(sample_frames, ignore_index=True)
    return records, samples, {
        "source_records": int(n),
        "selected_records": int(len(selected_idx)),
        "selected_records_by_label": {
            "NORMAL": int(sum(y[i] == 0 for i in selected_idx)),
            "ANORMAL": int(sum(y[i] == 1 for i in selected_idx)),
        },
        "test_fold": int(args.test_fold),
        "unique_patients_selected": int(records["patient_id"].nunique()),
        "samples_per_record": ECG_WINDOW,
        "input_rate_hz": 250,
        "duration_seconds": 10.0,
        "simulated_adc": not args.no_adc_simulation,
        "adc_mapping": None if args.no_adc_simulation else {
            "formula": "round(2048 + sample * (1600 / max_abs_selected_sample)) clipped to [0,4095]",
            "global_max_abs_sample": peak,
            "gain": gain,
            "warning": "Synthetic 12-bit replay scaling only; not calibrated to a physical AD8232. The firmware must use the same signal path expected by the model, including window-wise z-score."
        },
        "warning": "Label 1 means ANORMAL according to the dataset mapping, not specifically tachycardia. Confirm the model's training label semantics."
    }


def make_scenario_manifest(trials: pd.DataFrame, records: pd.DataFrame,
                           per_cell: int, rng: np.random.Generator) -> pd.DataFrame:
    by_trial_label = {cls: trials[trials["trial_label"] == cls] for cls in ("Fall", "ADL")}
    by_ecg_label = {cls: records[records["label_name"] == cls] for cls in ("NORMAL", "ANORMAL")}
    for cls, group in {**{f"trial {k}": v for k, v in by_trial_label.items()},
                       **{f"ecg {k}": v for k, v in by_ecg_label.items()}}.items():
        if group.empty:
            raise ValueError(f"No hay ejemplos para {cls}; no se puede crear scenario_manifest.csv.")

    out: list[dict[str, Any]] = []
    seq = 1
    for (fall_cls, ecg_cls), triage in TRIAGE_BY_CELL.items():
        t_group = by_trial_label[fall_cls].reset_index(drop=True)
        e_group = by_ecg_label[ecg_cls].reset_index(drop=True)
        t_perm = rng.permutation(len(t_group))
        e_perm = rng.permutation(len(e_group))
        for i in range(per_cell):
            trial = t_group.iloc[int(t_perm[i % len(t_group)])]
            record = e_group.iloc[int(e_perm[i % len(e_group)])]
            out.append({
                "scenario_id": f"S{seq:04d}",
                "fall_trial_id": trial["trial_id"],
                "fall_reference_label": fall_cls,
                "ecg_id": record["ecg_id"],
                "ecg_reference_label": ecg_cls,
                "expected_triage_from_reference_labels": triage,
                "pairing_type": "SYNTHETIC_UNSYNCHRONIZED",
            })
            seq += 1
    return pd.DataFrame(out)


def validate_dataset(stream: pd.DataFrame, trials: pd.DataFrame, records: pd.DataFrame,
                     ecg_stream: pd.DataFrame, scenarios: pd.DataFrame, per_cell: int) -> None:
    errors: list[str] = []

    if trials["trial_id"].duplicated().any():
        errors.append("trial_id duplicado en fall_trial_manifest.csv")
    if not set(trials["trial_label"]).issubset({"Fall", "ADL"}):
        errors.append("trial_label fuera de {Fall, ADL}")
    for trial_id, frame in stream.groupby("trial_id", sort=False):
        row = trials.loc[trials["trial_id"] == trial_id].iloc[0]
        expected = int(row["stream_samples"])
        if len(frame) != expected:
            errors.append(f"{trial_id}: stream_samples={len(frame)} != manifiesto={expected}")
        if not np.array_equal(frame["stream_sample"].to_numpy(), np.arange(expected)):
            errors.append(f"{trial_id}: stream_sample no es consecutivo 0..N-1")
        if not np.array_equal(frame["Sample_Index"].to_numpy(), np.arange(1, expected + 1)):
            errors.append(f"{trial_id}: Sample_Index no es consecutivo 1..N")
        if expected != int(row["windows"]) * FALL_WINDOW_SAMPLES:
            errors.append(f"{trial_id}: stream_samples no es múltiplo de {FALL_WINDOW_SAMPLES}")
    if set(stream["trial_id"]) != set(trials["trial_id"]):
        errors.append("trial_id del stream y del manifiesto no coinciden")
    if not np.isfinite(stream[FALL_COLUMNS].to_numpy(dtype=np.float64)).all():
        errors.append("valores no finitos en fall_stream.csv")

    if records["ecg_id"].duplicated().any():
        errors.append("ecg_id duplicado en ecg_records.csv")
    if not set(records["label_name"]).issubset({"NORMAL", "ANORMAL"}):
        errors.append("label_name fuera de {NORMAL, ANORMAL}")
    for ecg_id, frame in ecg_stream.groupby("ecg_id", sort=False):
        if len(frame) != ECG_WINDOW:
            errors.append(f"ecg_id {ecg_id}: {len(frame)} muestras != {ECG_WINDOW}")
        if not np.array_equal(frame["sample_index"].to_numpy(), np.arange(ECG_WINDOW)):
            errors.append(f"ecg_id {ecg_id}: sample_index no es consecutivo 0..N-1")
    merged_finite = np.isfinite(ecg_stream["lead_ii_value_original"].to_numpy(dtype=np.float64))
    if not merged_finite.all():
        errors.append("valores no finitos en ecg_stream.csv")
    if "adc_count_sim" in ecg_stream.columns:
        adc = ecg_stream["adc_count_sim"].to_numpy()
        if adc.min() < 0 or adc.max() > 4095:
            errors.append("adc_count_sim fuera de [0, 4095]")

    if scenarios["scenario_id"].duplicated().any():
        errors.append("scenario_id duplicado en scenario_manifest.csv")
    merged = scenarios.merge(
        trials[["trial_id", "trial_label"]], left_on="fall_trial_id", right_on="trial_id",
        how="left", validate="many_to_one")
    if merged["trial_id"].isna().any():
        errors.append("scenario_manifest.csv referencia fall_trial_id huérfanos")
    if (merged["fall_reference_label"] != merged["trial_label"]).any():
        errors.append("fall_reference_label no coincide con el trial referenciado")
    merged = scenarios.merge(
        records[["ecg_id", "label_name"]], on="ecg_id", how="left", validate="many_to_one")
    if merged["label_name"].isna().any():
        errors.append("scenario_manifest.csv referencia ecg_id huérfanos")
    if (merged["ecg_reference_label"] != merged["label_name"]).any():
        errors.append("ecg_reference_label no coincide con el registro referenciado")
    expected_triage = [
        TRIAGE_BY_CELL[(f, e)]
        for f, e in zip(scenarios["fall_reference_label"], scenarios["ecg_reference_label"])
    ]
    if (scenarios["expected_triage_from_reference_labels"].to_numpy() != np.asarray(expected_triage)).any():
        errors.append("expected_triage_from_reference_labels no coincide con la tabla congelada")
    cell_counts = scenarios.groupby(
        ["fall_reference_label", "ecg_reference_label"]).size().to_dict()
    if len(cell_counts) != 4 or any(v != per_cell for v in cell_counts.values()):
        errors.append(f"recuento por celda != {per_cell}: {cell_counts}")

    if errors:
        raise ValueError("Validación de integridad falló:\n- " + "\n- ".join(errors))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    if args.fall_trials_per_class < 1 or args.ecg_records_per_class < 1 or args.scenarios_per_cell < 1:
        raise ValueError("Los tamaños y repeticiones deben ser >= 1.")
    args.out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    fall_stream, fall_trials, fall_summary = prepare_fall(args, rng)
    ecg_records, ecg_stream, ecg_summary = prepare_ecg(args, rng)
    scenarios = make_scenario_manifest(fall_trials, ecg_records, args.scenarios_per_cell, rng)

    validate_dataset(fall_stream, fall_trials, ecg_records, ecg_stream, scenarios, args.scenarios_per_cell)

    fall_stream.to_csv(args.out / "fall_stream.csv", index=False)
    fall_trials.to_csv(args.out / "fall_trial_manifest.csv", index=False)
    ecg_records.to_csv(args.out / "ecg_records.csv", index=False)
    ecg_stream.to_csv(args.out / "ecg_stream.csv", index=False)
    scenarios.to_csv(args.out / "scenario_manifest.csv", index=False)

    summary = {
        "seed": args.seed,
        "files": {
            "fall_stream.csv": "Whole KFall trials, six axes at native 100 Hz, trimmed to 100-sample windows; replay one trial at a time and never join trial boundaries.",
            "fall_trial_manifest.csv": "One row per selected trial: source/sent samples, windows, trim remainder.",
            "ecg_records.csv": "Selected ECG record metadata, labels, and fold.",
            "ecg_stream.csv": "2,500 Lead-II samples per record at 250 Hz, unfiltered; includes a simulated ADC count unless disabled.",
            "scenario_manifest.csv": "Test combinations for the decision table referencing fall_trial_id; pairs are synthetic, not synchronized clinical events."
        },
        "sources": {
            "fall_csv": str(args.fall_csv),
            "fall_csv_sha256": sha256_file(args.fall_csv),
            "ecg_h5": str(args.ecg_h5),
            "ecg_h5_sha256": sha256_file(args.ecg_h5),
        },
        "fall": fall_summary,
        "ecg": ecg_summary,
        "scenarios": {
            "rows": int(len(scenarios)),
            "by_expected_triage": {str(k): int(v) for k, v in scenarios["expected_triage_from_reference_labels"].value_counts().to_dict().items()},
            "interpretation": "Integration/table tests only: KFall and PTB-XL are unrelated recordings with no shared patient/time axis. Do not use these pairs to claim clinical fusion accuracy or reduced real-world false positives."
        }
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
