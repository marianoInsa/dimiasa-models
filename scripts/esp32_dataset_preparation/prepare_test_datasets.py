#!/usr/bin/env python3
"""Create small, reproducible, sensor-like replay datasets for ESP32 fall/ECG models.

Inputs
------
- UMAFall-Reduced.csv with Subject, Activity_Label, Activity_Code, Trial,
  Sample_Index, Ax, Ay, Az, Gx, Gy, Gz.
- HDF5 with X (N, 2500), y, ecg_id, patient_id and strat_fold datasets.

Outputs (under --out)
----------------------
- fall_stream.csv: selected full trials, original six axes, sensor-like samples at 20 Hz.
- fall_window_manifest.csv: sliding 60-sample windows, hop 30, and reference labels.
- ecg_records.csv: metadata for selected complete ECG records.
- ecg_stream.csv: samples of each selected record at 250 Hz, original value plus
  an optional simulated 12-bit ADC count using one global affine scale.
- scenario_manifest.csv: synthetic combinations covering the four triage rules.
- summary.json: counts, assumptions and warnings.

This script does NOT filter/resample/quantize model inputs. Do that in the firmware,
using exactly the same preprocessing as the trained model. Requires numpy, pandas, h5py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd

FALL_COLUMNS = ["Ax", "Ay", "Az", "Gx", "Gy", "Gz"]
FALL_WINDOW = 60       # 3 s * 20 Hz
FALL_HOP = 30          # 1.5 s * 20 Hz
FALL_POS_RADIUS = 30   # center within +/- 1.5 s of AVM peak at 20 Hz
ECG_WINDOW = 2500      # 10 s * 250 Hz


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fall-csv", required=True, type=Path, help="Path to UMAFall-Reduced.csv")
    p.add_argument("--ecg-h5", required=True, type=Path, help="Path to the HDF5 ECG dataset")
    p.add_argument("--out", required=True, type=Path, help="Output directory")
    p.add_argument("--fall-trials-per-class", type=int, default=10,
                   help="Number of Fall and ADL trials to select (default: 10 each)")
    p.add_argument("--ecg-records-per-class", type=int, default=20,
                   help="Number of ECG records per class from fold 10 (default: 20 each)")
    p.add_argument("--scenario-repetitions", type=int, default=5,
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
        if len(frame) < FALL_WINDOW:
            continue
        cls = class_from_activity(frame["Activity_Label"].iloc[0])
        candidates[cls].append((key, frame))

    chosen: list[tuple[tuple[Any, ...], pd.DataFrame, str]] = []
    for cls in ("Fall", "ADL"):
        pool = candidates[cls]
        if len(pool) < n_per_class:
            raise ValueError(
                f"Hay solo {len(pool)} trials {cls} con al menos {FALL_WINDOW} muestras; "
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
    window_rows: list[dict[str, Any]] = []
    trial_counts = {"Fall": 0, "ADL": 0}
    for seq, (key, trial, trial_cls) in enumerate(selected, start=1):
        trial_id = f"FTR{seq:04d}"
        trial_counts[trial_cls] += 1
        values = trial[FALL_COLUMNS].apply(pd.to_numeric, errors="coerce")
        if values.isna().any().any():
            raise ValueError(f"Valores no numéricos/ausentes en trial {key}; limpiá el CSV antes de continuar.")
        arr = values.to_numpy(dtype=np.float32)
        # Peak proxy for the training-window target rule: magnitude of the three acceleration axes.
        avm = np.sqrt(np.sum(arr[:, :3] ** 2, axis=1))
        peak_pos = int(np.argmax(avm)) if trial_cls == "Fall" else -1

        src = trial.copy()
        src.insert(0, "trial_id", trial_id)
        src.insert(1, "trial_label", trial_cls)
        src["stream_sample"] = np.arange(len(src), dtype=np.int32)
        src = src[["trial_id", "Subject", "Activity_Label", "Activity_Code", "Trial",
                   "trial_label", "stream_sample", "Sample_Index", *FALL_COLUMNS]]
        stream_rows.append(src)

        start = 0
        while start + FALL_WINDOW <= len(trial):
            center = start + FALL_WINDOW // 2
            if trial_cls == "Fall":
                distance = abs(center - peak_pos)
                model_target = "Fall" if distance <= FALL_POS_RADIUS else "ADL"
            else:
                distance = None
                model_target = "ADL"
            window_rows.append({
                "window_id": f"{trial_id}_W{start:05d}",
                "trial_id": trial_id,
                "subject": decode_scalar(trial["Subject"].iloc[0]),
                "trial_label": trial_cls,
                "model_target_reference": model_target,
                "source_start_sample": int(trial["Sample_Index"].iloc[start]),
                "source_center_sample": int(trial["Sample_Index"].iloc[center]),
                "start_stream_sample": start,
                "center_stream_sample": center,
                "peak_stream_sample": peak_pos if peak_pos >= 0 else None,
                "center_to_peak_distance_samples": distance,
                "window_samples_20hz": FALL_WINDOW,
                "hop_samples_20hz": FALL_HOP,
            })
            start += FALL_HOP

    stream = pd.concat(stream_rows, ignore_index=True)
    windows = pd.DataFrame(window_rows)
    if not (windows["model_target_reference"] == "Fall").any():
        raise ValueError("No se generaron ventanas positivas Fall; revisá duración y etiquetas de los trials seleccionados.")
    return stream, windows, {
        "source_rows": int(len(df)),
        "selected_trials": int(len(selected)),
        "selected_trials_by_label": trial_counts,
        "stream_samples": int(len(stream)),
        "reference_windows": int(len(windows)),
        "reference_windows_by_model_target": {
            str(k): int(v) for k, v in windows["model_target_reference"].value_counts().to_dict().items()
        },
        "input_rate_hz": 20,
        "window_samples": FALL_WINDOW,
        "window_seconds": 3.0,
        "hop_samples": FALL_HOP,
        "hop_seconds": 1.5,
        "positive_rule": "Fall trial and window center within +/- 30 original samples (1.5 s) of the AVM-magnitude peak; all ADL-trial windows are ADL.",
        "warning": "AVM peak from raw axes is a proxy. Confirm it matches the exact peak/label-generation code used to train LiteFallNet. Trial label and per-window training target can differ."
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


def make_scenario_manifest(windows: pd.DataFrame, records: pd.DataFrame,
                           repetitions: int, rng: np.random.Generator) -> pd.DataFrame:
    fall_pos = windows[windows["model_target_reference"] == "Fall"]
    fall_neg = windows[windows["model_target_reference"] == "ADL"]
    ecg_norm = records[records["label_name"] == "NORMAL"]
    ecg_abn = records[records["label_name"] == "ANORMAL"]
    if min(len(fall_pos), len(fall_neg), len(ecg_norm), len(ecg_abn)) == 0:
        raise ValueError("No hay ejemplos para una o más clases; no se puede crear scenario_manifest.csv.")

    specs = [
        ("Fall", "ANORMAL", "ROJO"),
        ("Fall", "NORMAL", "AMARILLO"),
        ("ADL", "ANORMAL", "AMARILLO"),
        ("ADL", "NORMAL", "VERDE"),
    ]
    fall_groups = {"Fall": fall_pos, "ADL": fall_neg}
    ecg_groups = {"NORMAL": ecg_norm, "ANORMAL": ecg_abn}
    out: list[dict[str, Any]] = []
    seq = 1
    for fall_cls, ecg_cls, triage in specs:
        fg = fall_groups[fall_cls]
        eg = ecg_groups[ecg_cls]
        for _ in range(repetitions):
            fw = fg.iloc[int(rng.integers(0, len(fg)))]
            er = eg.iloc[int(rng.integers(0, len(eg)))]
            out.append({
                "scenario_id": f"S{seq:04d}",
                "fall_window_id": fw["window_id"],
                "fall_trial_id": fw["trial_id"],
                "fall_reference_label": fall_cls,
                "ecg_id": er["ecg_id"],
                "ecg_reference_label": ecg_cls,
                "expected_triage_from_reference_labels": triage,
                "pairing_type": "SYNTHETIC_UNSYNCHRONIZED",
            })
            seq += 1
    return pd.DataFrame(out)


def main() -> None:
    args = parse_args()
    if args.fall_trials_per_class < 1 or args.ecg_records_per_class < 1 or args.scenario_repetitions < 1:
        raise ValueError("Los tamaños y repeticiones deben ser >= 1.")
    args.out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    fall_stream, fall_windows, fall_summary = prepare_fall(args, rng)
    ecg_records, ecg_stream, ecg_summary = prepare_ecg(args, rng)
    scenarios = make_scenario_manifest(fall_windows, ecg_records, args.scenario_repetitions, rng)

    fall_stream.to_csv(args.out / "fall_stream.csv", index=False)
    fall_windows.to_csv(args.out / "fall_window_manifest.csv", index=False)
    ecg_records.to_csv(args.out / "ecg_records.csv", index=False)
    ecg_stream.to_csv(args.out / "ecg_stream.csv", index=False)
    scenarios.to_csv(args.out / "scenario_manifest.csv", index=False)

    summary = {
        "seed": args.seed,
        "files": {
            "fall_stream.csv": "Raw six-axis trial samples in source order, 20 Hz; replay one trial at a time, do not join trial boundaries.",
            "fall_window_manifest.csv": "Reference labels for 60-sample/3-second fall windows, hop 30 samples.",
            "ecg_records.csv": "Selected ECG record metadata, labels, and fold.",
            "ecg_stream.csv": "2,500 Lead-II samples per record at 250 Hz, unfiltered; includes a simulated ADC count unless disabled.",
            "scenario_manifest.csv": "Test combinations for the decision table; pairs are synthetic, not synchronized clinical events."
        },
        "fall": fall_summary,
        "ecg": ecg_summary,
        "scenarios": {
            "rows": int(len(scenarios)),
            "by_expected_triage": {str(k): int(v) for k, v in scenarios["expected_triage_from_reference_labels"].value_counts().to_dict().items()},
            "interpretation": "Integration/table tests only: UMAFall and PTB-XL are unrelated recordings with no shared patient/time axis. Do not use these pairs to claim clinical fusion accuracy or reduced real-world false positives."
        }
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
