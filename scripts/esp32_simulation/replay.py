#!/usr/bin/env python3
"""Reproductor de señales guardadas desde una computadora hacia la ESP32.

Envia un trial KFall (agente A), un registro ECG (agente B) o un escenario
CASE con las dos entradas, y comprueba AGENT/RESULT/ACK contra la referencia
Python y el manifiesto. Cerrar el Monitor Serie de Arduino antes de usarlo.

Ejemplos:
  .venv/bin/python scripts/esp32_simulation/replay.py hello --port /dev/ttyUSB0
  .venv/bin/python scripts/esp32_simulation/replay.py block --port /dev/ttyUSB0 \
      --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --trial KTR0001
  .venv/bin/python scripts/esp32_simulation/replay.py block --port /dev/ttyUSB0 \
      --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --agent B --ecg-id 14501
  .venv/bin/python scripts/esp32_simulation/replay.py scenario --port /dev/ttyUSB0 \
      --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --ids S0002,S0006
  .venv/bin/python scripts/esp32_simulation/replay.py scenario --port /dev/ttyUSB0 \
      --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --ids S0002 --drop-b
  .venv/bin/python scripts/esp32_simulation/replay.py run --port /dev/ttyUSB0 \
      --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --mode fast \
      --output reports/esp32_validation/smoke
  .venv/bin/python scripts/esp32_simulation/replay.py run --port /dev/ttyUSB0 \
      --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --mode paced \
      --trials KTR0002,KTR0004 --ecgs 14501 --scenarios S0007 --repeat 3 \
      --output reports/esp32_validation/paced
  .venv/bin/python scripts/esp32_simulation/replay.py resilience --port /dev/ttyUSB0 \
      --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke \
      --output reports/esp32_validation/resilience
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

WINDOW_SAMPLES_B = 2500


def open_port(port: str, baud: int):
    try:
        import serial
    except ImportError as exc:
        raise SystemExit(
            "Falta pyserial. Instalalo con: .venv/bin/python -m pip install pyserial"
        ) from exc
    ser = serial.Serial(port=port, baudrate=baud, timeout=0.2, write_timeout=2.0)
    ser.dtr = False
    ser.rts = False
    time.sleep(1.5)
    while True:
        raw = ser.readline()
        if not raw:
            break
        line = raw.decode("utf-8", errors="replace").strip()
        if line:
            print(f"< {line}")
    ser.reset_input_buffer()
    return ser


def read_until(ser, deadline: float, stop=None) -> list[str]:
    lines: list[str] = []
    while time.monotonic() < deadline:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        print(f"< {line}")
        lines.append(line)
        if stop is not None and stop(line):
            break
    return lines


def send(ser, text: str) -> None:
    print(f"> {text}")
    ser.write((text + "\n").encode("utf-8"))
    ser.flush()


def handshake(ser, retries: int = 2) -> list[str]:
    """Devuelve las lineas del HELLO (incluye INFO y READY); lista vacia si falla."""
    for attempt in range(retries):
        send(ser, "HELLO,1")
        lines = read_until(
            ser,
            time.monotonic() + 3.0,
            stop=lambda line: line.startswith("READY") or line.startswith("ERROR"),
        )
        if "READY,1" in lines:
            return lines
        print(f"sin READY,1 (intento {attempt + 1})")
    return []


def load_trial(dataset_dir: Path, trial_id: str) -> tuple[int, str, list[str]]:
    import pandas as pd

    manifest = pd.read_csv(dataset_dir / "fall_trial_manifest.csv")
    row = manifest.loc[manifest["trial_id"] == trial_id]
    if row.empty:
        raise SystemExit(f"{trial_id} no esta en {dataset_dir}/fall_trial_manifest.csv")
    count = int(row.iloc[0]["stream_samples"])
    label = str(row.iloc[0]["trial_label"])
    stream = pd.read_csv(dataset_dir / "fall_stream.csv")
    stream = stream.loc[stream["trial_id"] == trial_id].sort_values("stream_sample")
    lines = [
        "S,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f"
        % (
            int(r.stream_sample),
            r.Ax,
            r.Ay,
            r.Az,
            r.Gx,
            r.Gy,
            r.Gz,
        )
        for r in stream.itertuples()
    ]
    return count, label, lines


def rule_reference(dataset_dir: Path, trial_id: str) -> dict:
    """Aplica las reglas de caída al stream de un ensayo como referencia local."""
    import numpy as np
    import pandas as pd

    stream = pd.read_csv(dataset_dir / "fall_stream.csv")
    frame = stream.loc[stream["trial_id"] == trial_id].sort_values("stream_sample")
    acc = np.sqrt(frame["Ax"] ** 2 + frame["Ay"] ** 2 + frame["Az"] ** 2).to_numpy()
    gyro = np.sqrt(frame["Gx"] ** 2 + frame["Gy"] ** 2 + frame["Gz"] ** 2).to_numpy()
    state = "NORMAL"
    still = 0
    post_impact = 0
    confirmed = False
    windows = 0
    for w in range(len(acc) // 100):
        ar = float(acc[w * 100 : (w + 1) * 100].max() - acc[w * 100 : (w + 1) * 100].min())
        gr = float(gyro[w * 100 : (w + 1) * 100].max() - gyro[w * 100 : (w + 1) * 100].min())
        impact = ar >= 2.0 and gr >= 150.0
        quiet = ar < 0.40 and gr < 30.0
        if state == "NORMAL":
            still = 0
            post_impact = 0
            if impact:
                state = "IMPACTO"
                post_impact = 0
                still = 0
        elif state == "IMPACTO":
            post_impact += 1
            if quiet:
                still = 1
                state = "POSIBLE_CAIDA"
            elif post_impact >= 3:
                state, still, post_impact = "NORMAL", 0, 0
        else:
            if quiet:
                still += 1
                if still >= 2:
                    confirmed = True
                    state, still, post_impact = "NORMAL", 0, 0
            else:
                state, still, post_impact = "NORMAL", 0, 0
        windows += 1
    if confirmed:
        clase = "Fall"
    elif state != "NORMAL":
        clase = "INDETERMINADO"
    else:
        clase = "ADL"
    return {
        "clase": clase,
        "estado": state,
        "confirmado": 1 if confirmed else 0,
        "ventanas": windows,
    }


def load_ecg(dataset_dir: Path, ecg_id: int) -> tuple[int, list[str]]:
    import pandas as pd

    stream = pd.read_csv(dataset_dir / "ecg_stream.csv")
    frame = stream.loc[stream["ecg_id"] == ecg_id].sort_values("sample_index")
    if len(frame) != WINDOW_SAMPLES_B:
        raise SystemExit(f"ecg_id {ecg_id}: {len(frame)} muestras != {WINDOW_SAMPLES_B}")
    lines = [
        "S,%d,%d" % (int(r.sample_index), int(r.adc_count_sim)) for r in frame.itertuples()
    ]
    return WINDOW_SAMPLES_B, lines


TRIAGE_TABLE = {
    ("Fall", "ANORMAL"): "ROJO",
    ("Fall", "NORMAL"): "AMARILLO",
    ("ADL", "ANORMAL"): "AMARILLO",
    ("ADL", "NORMAL"): "VERDE",
}


def expected_case_triage(dataset_dir: Path, fall_trial_id: str, ecg_id: int) -> tuple[str, str, str]:
    """Triaje esperado a partir de las salidas reales de los agentes (no etiquetas)."""
    fall_class = rule_reference(dataset_dir, fall_trial_id)["clase"]
    ecg_class = load_reference(dataset_dir, ecg_id)["clase"]
    return TRIAGE_TABLE.get((fall_class, ecg_class), "INDETERMINADO"), fall_class, ecg_class


def load_scenario(dataset_dir: Path, scenario_id: str) -> dict:
    import pandas as pd

    manifest = pd.read_csv(dataset_dir / "scenario_manifest.csv")
    row = manifest.loc[manifest["scenario_id"] == scenario_id]
    if row.empty:
        raise SystemExit(f"{scenario_id} no esta en {dataset_dir}/scenario_manifest.csv")
    return row.iloc[0].to_dict()


def load_reference(dataset_dir: Path, ecg_id: int) -> dict:
    summary = json.loads((dataset_dir / "ecg_reference_summary.json").read_text())
    for record in summary.get("records", []):
        if record["ecg_id"] == ecg_id and "q" in record:
            return record
    raise SystemExit(f"sin referencia con inferencia para ecg_id {ecg_id}")


def tensor_checksum(dataset_dir: Path, ecg_id: int) -> int:
    """FNV-1a 32 bits del tensor INT8 de referencia, igual que el firmware."""
    import numpy as np
    import pandas as pd

    frame = pd.read_csv(dataset_dir / "ecg_reference.csv")
    frame = frame.loc[frame["ecg_id"] == ecg_id].sort_values("sample_index")
    fnv = 2166136261
    for value in frame["int8"].to_numpy(dtype=np.int8):
        fnv ^= int(value) & 0xFF
        fnv = (fnv * 16777619) & 0xFFFFFFFF
    return fnv


def check_agent_a(line: str | None, case_id: str, count: int, expected: dict):
    if line is None:
        return False, "sin linea AGENT,A"
    fields = line.split(",")
    if len(fields) != 10 or fields[1] != "A":
        return False, f"AGENT,A mal formado: {line}"
    ok = (
        fields[2] == case_id
        and fields[3] == expected["clase"]
        and fields[4] == expected["estado"]
        and fields[5] == str(expected["confirmado"])
        and fields[6] == str(count)
        and fields[7] == str(expected["ventanas"])
    )
    detail = (
        f"clase={fields[3]} (referencia {expected['clase']}, etiqueta {expected['label']}) "
        f"estado={fields[4]} (ref {expected['estado']}) confirmado={fields[5]} "
        f"muestras={fields[6]} ventanas={fields[7]} fall_us={fields[8]} heap={fields[9]}"
    )
    return ok, detail


def check_agent_b(line: str | None, case_id: str, count: int, expected: dict, expected_fnv: int):
    if line is None:
        return False, "sin linea AGENT,B"
    fields = line.split(",")
    if len(fields) != 14 or fields[1] != "B":
        return False, f"AGENT,B mal formado: {line}"
    q = int(fields[4])
    p = float(fields[5])
    tensor_fnv = int(fields[8])
    checksum_ok = tensor_fnv == expected_fnv
    class_ok = fields[3] == expected["clase"]
    counters_ok = fields[6] == str(count) and fields[7] == str(expected["saturated"])
    q_delta = q - expected["q"]
    # Se toleran hasta dos unidades de diferencia por redondeo, siempre que el
    # tensor INT8 y la clase coincidan con la referencia local.
    q_ok = q_delta == 0 or (checksum_ok and class_ok and abs(q_delta) <= 2)
    ok = checksum_ok and class_ok and counters_ok and q_ok
    warnings = []
    if not checksum_ok:
        warnings.append(f"TS={tensor_fnv} ref={expected_fnv}")
    if q_delta != 0:
        warnings.append(f"q={q} ref={expected['q']} (delta {q_delta:+d} TFLM/TFLite)")
    zmin, zmax = float(fields[9]), float(fields[10])
    if abs(zmin - expected["float_min"]) > 1e-4 or abs(zmax - expected["float_max"]) > 1e-4:
        warnings.append(f"z=[{zmin},{zmax}] ref=[{expected['float_min']},{expected['float_max']}]")
    warning = (" (" + "; ".join(warnings) + ")") if warnings else ""
    detail = (
        f"clase={fields[3]} (esperada {expected['clase']}) q={q} (ref {expected['q']}) "
        f"p={p:.8g} (ref {expected['p']:.8g}) TS={tensor_fnv} recibidas={fields[6]} "
        f"saturados={fields[7]} preproc_us={fields[11]} infer_us={fields[12]} "
        f"heap={fields[13]}{warning}"
    )
    return ok, detail


def run_scenario(args: argparse.Namespace) -> int:
    dataset_dir = Path(args.dataset_dir)
    scenario_ids = [s.strip() for s in args.ids.split(",") if s.strip()]
    ser = open_port(args.port, args.baud)
    all_ok = True
    try:
        if not handshake(ser):
            return 1
        for scenario_id in scenario_ids:
            row = load_scenario(dataset_dir, scenario_id)
            fall_id = str(row["fall_trial_id"])
            ecg_id = int(row["ecg_id"])
            count_a, label_a, fall_lines = load_trial(dataset_dir, fall_id)
            count_b, ecg_lines = load_ecg(dataset_dir, ecg_id)
            expected_color, exp_a, exp_b = expected_case_triage(dataset_dir, fall_id, ecg_id)
            expected_a = rule_reference(dataset_dir, fall_id)
            expected_a["label"] = label_a
            expected_b = load_reference(dataset_dir, ecg_id)
            expected_fnv = tensor_checksum(dataset_dir, ecg_id)
            label_expected = str(row.get("expected_triage_from_reference_labels", "?"))
            print(
                f"== {scenario_id}: {fall_id} ({label_a}, reglas {exp_a}) + "
                f"ECG {ecg_id} ({exp_b}) -> esperado por salidas reales {expected_color} "
                f"(etiquetas del manifiesto: {label_expected})"
            )

            send(ser, f"CASE,{scenario_id},{fall_id},{ecg_id}")
            send(ser, f"BEGIN,A,{fall_id},{count_a}")
            sent = 0
            for line in fall_lines:
                if args.truncate and sent >= args.truncate:
                    break
                send(ser, line)
                sent += 1
            if args.truncate:
                lines = read_until(
                    ser, time.monotonic() + 8.0, stop=lambda line: line.startswith("ERROR")
                )
                ok = any(line.startswith("ERROR,TIMEOUT") for line in lines) and not any(
                    line.startswith("RESULT") for line in lines
                )
                print(
                    "RESULTADO:",
                    "PASS" if ok else "FAIL",
                    f"A parcial: esperado ERROR,TIMEOUT,{fall_id} sin RESULT",
                )
                all_ok = all_ok and ok
                continue

            send(ser, f"END,{fall_id}")
            lines_a = read_until(
                ser,
                time.monotonic() + 10.0,
                stop=lambda line: line.startswith("ACK") or line.startswith("ERROR"),
            )
            if args.drop_b:
                lines = read_until(
                    ser, time.monotonic() + 8.0, stop=lambda line: line.startswith("ERROR")
                )
                ok = any(line.startswith("ERROR,TIMEOUT") for line in lines) and not any(
                    line.startswith("RESULT") for line in lines_a + lines
                )
                print(
                    "RESULTADO:",
                    "PASS" if ok else "FAIL",
                    f"B ausente: esperado ERROR,TIMEOUT,{scenario_id} sin RESULT",
                )
                all_ok = all_ok and ok
                continue

            send(ser, f"BEGIN,B,{ecg_id},{count_b}")
            for line in ecg_lines:
                send(ser, line)
            if args.bad_end_b:
                send(ser, "END,ID_INCORRECTO")
                lines = read_until(
                    ser, time.monotonic() + 5.0, stop=lambda line: line.startswith("ERROR")
                )
                ok = any(line.startswith("ERROR,END") for line in lines) and not any(
                    line.startswith("RESULT") for line in lines
                )
                print(
                    "RESULTADO:",
                    "PASS" if ok else "FAIL",
                    f"END de B invalido: esperado ERROR,END,{ecg_id} sin RESULT",
                )
                all_ok = all_ok and ok
                continue

            send(ser, f"END,{ecg_id}")
            lines_b = read_until(
                ser,
                time.monotonic() + 15.0,
                stop=lambda line: line.startswith("RESULT") or line.startswith("ERROR"),
            )
            agent_a = next((line for line in lines_a if line.startswith("AGENT,A,")), None)
            agent_b = next((line for line in lines_b if line.startswith("AGENT,B,")), None)
            result_line = next((line for line in lines_b if line.startswith("RESULT,")), None)
            ack_a = f"ACK,{fall_id},{count_a}" in lines_a
            ack_b = f"ACK,{ecg_id},{count_b}" in lines_b
            a_ok, a_detail = check_agent_a(agent_a, fall_id, count_a, expected_a)
            b_ok, b_detail = check_agent_b(agent_b, ecg_id, count_b, expected_b, expected_fnv)
            result_ok = False
            result_detail = "sin RESULT"
            if result_line is not None:
                fields = result_line.split(",")
                if len(fields) == 6:
                    result_ok = (
                        fields[1] == scenario_id
                        and fields[2] == expected_color
                        and fields[3] == exp_a
                        and fields[4] == exp_b
                    )
                    result_detail = (
                        f"RESULT color={fields[2]} (esperado {expected_color}) "
                        f"triage_us={fields[5]}"
                    )
                else:
                    result_detail = f"RESULT mal formado: {result_line}"
            ok = ack_a and ack_b and a_ok and b_ok and result_ok
            print("RESULTADO:", "PASS" if ok else "FAIL", f"A[{a_detail}] B[{b_detail}] {result_detail}")
            all_ok = all_ok and ok
        return 0 if all_ok else 1
    finally:
        ser.close()


RESULTS_COLUMNS = [
    "case_id",
    "kind",
    "fall_trial_id",
    "ecg_id",
    "scenario_id",
    "reference_class",
    "predicted_class",
    "match",
    "state",
    "confirmed",
    "q",
    "p",
    "tensor_fnv",
    "expected_samples",
    "received_samples",
    "fall_us",
    "preproc_us",
    "infer_us",
    "triage_us",
    "e2e_ms",
    "heap",
    "repeat_index",
    "sched_late_median_ms",
    "sched_late_p95_ms",
    "sched_late_max_ms",
    "status",
    "error",
    "mode",
]


def parse_agent_a(line: str):
    fields = line.split(",")
    if len(fields) != 10 or fields[0] != "AGENT" or fields[1] != "A":
        return None
    try:
        return {
            "id": fields[2],
            "clase": fields[3],
            "estado": fields[4],
            "confirmado": int(fields[5]),
            "muestras": int(fields[6]),
            "ventanas": int(fields[7]),
            "fall_us": int(fields[8]),
            "heap": int(fields[9]),
        }
    except ValueError:
        return None


def parse_agent_b(line: str):
    fields = line.split(",")
    if len(fields) != 14 or fields[0] != "AGENT" or fields[1] != "B":
        return None
    try:
        return {
            "id": fields[2],
            "clase": fields[3],
            "q": int(fields[4]),
            "p": float(fields[5]),
            "recibidas": int(fields[6]),
            "saturados": int(fields[7]),
            "tensor_fnv": int(fields[8]),
            "zmin": float(fields[9]),
            "zmax": float(fields[10]),
            "preproc_us": int(fields[11]),
            "infer_us": int(fields[12]),
            "heap": int(fields[13]),
        }
    except ValueError:
        return None


def parse_result_line(line: str):
    fields = line.split(",")
    if len(fields) != 6 or fields[0] != "RESULT":
        return None
    try:
        triage_us = int(fields[5])
    except ValueError:
        return None
    return {
        "id": fields[1],
        "color": fields[2],
        "fall": fields[3],
        "ecg": fields[4],
        "triage_us": triage_us,
    }


def first_error(lines: list[str]) -> str:
    return next((line for line in lines if line.startswith("ERROR")), "")


def parse_id_filter(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def late_stats(lates: list[float]) -> tuple:
    """Mediana/P95/max del retraso real frente al calendario (ms)."""
    import numpy as np

    if not lates:
        return ("", "", "")
    values = np.asarray(lates, dtype=float)
    return (
        round(float(np.median(values)), 3),
        round(float(np.percentile(values, 95)), 3),
        round(float(values.max()), 3),
    )


def write_results(rows: list[dict], path: Path) -> None:
    import csv

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULTS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in RESULTS_COLUMNS})


def send_block(
    ser,
    agent: str,
    case_id: str,
    count: int,
    sample_lines: list[str],
    deadline: float,
    stop,
    period_s: float = 0.0,
) -> tuple[list[str], list[float]]:
    """Envia un bloque; con period_s>0 programa cada muestra sobre reloj monotónico y
    devuelve el retraso real (ms) de cada envío frente a su instante programado."""
    send(ser, f"BEGIN,{agent},{case_id},{count}")
    lates: list[float] = []
    if period_s > 0.0:
        start = time.monotonic()
        for index, line in enumerate(sample_lines):
            target = start + index * period_s
            wait = target - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            lates.append(max(0.0, time.monotonic() - target) * 1000.0)
            ser.write((line + "\n").encode("utf-8"))
        ser.flush()
    else:
        for line in sample_lines:
            send(ser, line)
    send(ser, f"END,{case_id}")
    return read_until(ser, time.monotonic() + deadline, stop), lates


def run_suite(args: argparse.Namespace) -> int:
    import platform

    import numpy as np
    import pandas as pd
    import serial as pyserial

    dataset_dir = Path(args.dataset_dir)
    suite = args.suite or dataset_dir.name
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    output = (
        Path(args.output)
        if args.output
        else Path("reports/esp32_validation") / f"{suite}_{timestamp}"
    )
    output.mkdir(parents=True, exist_ok=True)

    trials = pd.read_csv(dataset_dir / "fall_trial_manifest.csv")
    records = pd.read_csv(dataset_dir / "ecg_records.csv")
    scenarios = pd.read_csv(dataset_dir / "scenario_manifest.csv")

    trial_filter = parse_id_filter(args.trials)
    ecg_filter = [int(value) for value in parse_id_filter(args.ecgs)]
    scenario_filter = parse_id_filter(args.scenarios)
    if trial_filter:
        trials = trials[trials["trial_id"].isin(trial_filter)]
        if len(trials) != len(trial_filter):
            raise SystemExit("--trials no resuelve todos los ids")
    if ecg_filter:
        records = records[records["ecg_id"].isin(ecg_filter)]
        if len(records) != len(ecg_filter):
            raise SystemExit("--ecgs no resuelve todos los ids")
    if scenario_filter:
        scenarios = scenarios[scenarios["scenario_id"].isin(scenario_filter)]
        if len(scenarios) != len(scenario_filter):
            raise SystemExit("--scenarios no resuelve todos los ids")

    repeats = max(1, int(args.repeat))
    period_a = 0.01 if args.mode == "paced" else 0.0
    period_b = 0.004 if args.mode == "paced" else 0.0

    def for_each(frame):
        return (
            (repeat_index, item)
            for repeat_index in range(1, repeats + 1)
            for _, item in frame.iterrows()
        )

    def stop_block(line: str) -> bool:
        return line.startswith("ACK,") or line.startswith("ERROR")

    def stop_result(line: str) -> bool:
        return line.startswith("RESULT,") or line.startswith("ERROR")

    base = {column: "" for column in RESULTS_COLUMNS}
    base["mode"] = args.mode
    rows: list[dict] = []
    ser = open_port(args.port, args.baud)
    hello_lines: list[str] = []
    started = time.time()
    try:
        hello_lines = handshake(ser)
        if not hello_lines:
            print("sin READY,1; se aborta la corrida")
            return 1
        print(
            f"== suite {suite}: {len(trials)} trials A, {len(records)} registros B, "
            f"{len(scenarios)} escenarios | modo {args.mode} | repeticiones {repeats}"
        )

        for repeat_index, trial in for_each(trials):
            trial_id = str(trial["trial_id"])
            count = int(trial["stream_samples"])
            reference = str(trial["trial_label"])
            _, _, sample_lines = load_trial(dataset_dir, trial_id)
            row = dict(base)
            row.update(
                case_id=trial_id, kind="trial_A", fall_trial_id=trial_id,
                reference_class=reference, expected_samples=count, repeat_index=repeat_index,
            )
            start = time.monotonic()
            block, lates = send_block(
                ser, "A", trial_id, count, sample_lines, 20.0, stop_block, period_a
            )
            row["e2e_ms"] = round((time.monotonic() - start) * 1000, 3)
            (
                row["sched_late_median_ms"],
                row["sched_late_p95_ms"],
                row["sched_late_max_ms"],
            ) = late_stats(lates)
            error = first_error(block)
            agent = next((line for line in block if line.startswith("AGENT,A,")), "")
            parsed = parse_agent_a(agent) if agent else None
            if error:
                row["status"], row["error"] = "error", error
            elif f"ACK,{trial_id},{count}" not in block:
                row["status"], row["error"] = "timeout", "sin ACK"
            elif parsed is None:
                row["status"], row["error"] = "missing_agent", "ACK sin AGENT"
            else:
                row["status"] = "ok"
                row["predicted_class"] = parsed["clase"]
                row["match"] = "1" if parsed["clase"] == reference else "0"
                row["state"] = parsed["estado"]
                row["confirmed"] = parsed["confirmado"]
                row["received_samples"] = parsed["muestras"]
                row["fall_us"] = parsed["fall_us"]
                row["heap"] = parsed["heap"]
            rows.append(row)
            print(f"== trial {trial_id}: {row['status']} -> {row['predicted_class'] or '-'} "
                  f"(ref {reference}) {row['error']}")

        for repeat_index, record in for_each(records):
            ecg_id = int(record["ecg_id"])
            reference = str(record["label_name"])
            count, sample_lines = load_ecg(dataset_dir, ecg_id)
            row = dict(base)
            row.update(
                case_id=str(ecg_id), kind="record_B", ecg_id=ecg_id,
                reference_class=reference, expected_samples=count, repeat_index=repeat_index,
            )
            start = time.monotonic()
            block, lates = send_block(
                ser, "B", str(ecg_id), count, sample_lines, 40.0, stop_block, period_b
            )
            row["e2e_ms"] = round((time.monotonic() - start) * 1000, 3)
            (
                row["sched_late_median_ms"],
                row["sched_late_p95_ms"],
                row["sched_late_max_ms"],
            ) = late_stats(lates)
            error = first_error(block)
            agent = next((line for line in block if line.startswith("AGENT,B,")), "")
            parsed = parse_agent_b(agent) if agent else None
            if error:
                row["status"], row["error"] = "error", error
            elif f"ACK,{ecg_id},{count}" not in block:
                row["status"], row["error"] = "timeout", "sin ACK"
            elif parsed is None:
                row["status"], row["error"] = "missing_agent", "ACK sin AGENT"
            else:
                row["status"] = "ok"
                row["predicted_class"] = parsed["clase"]
                row["match"] = "1" if parsed["clase"] == reference else "0"
                row["q"] = parsed["q"]
                row["p"] = parsed["p"]
                row["tensor_fnv"] = parsed["tensor_fnv"]
                row["received_samples"] = parsed["recibidas"]
                row["preproc_us"] = parsed["preproc_us"]
                row["infer_us"] = parsed["infer_us"]
                row["heap"] = parsed["heap"]
            rows.append(row)
            print(f"== registro {ecg_id}: {row['status']} -> {row['predicted_class'] or '-'} "
                  f"(ref {reference}) {row['error']}")

        for repeat_index, scenario in for_each(scenarios):
            scenario_id = str(scenario["scenario_id"])
            fall_id = str(scenario["fall_trial_id"])
            ecg_id = int(scenario["ecg_id"])
            reference = str(scenario["expected_triage_from_reference_labels"])
            count_a, _, fall_lines = load_trial(dataset_dir, fall_id)
            count_b, ecg_lines = load_ecg(dataset_dir, ecg_id)
            row = dict(base)
            row.update(
                case_id=scenario_id, kind="scenario", fall_trial_id=fall_id,
                ecg_id=ecg_id, scenario_id=scenario_id, reference_class=reference,
                expected_samples=count_a, repeat_index=repeat_index,
            )
            start = time.monotonic()
            send(ser, f"CASE,{scenario_id},{fall_id},{ecg_id}")
            lines_a, lates_a = send_block(
                ser, "A", fall_id, count_a, fall_lines, 20.0, stop_block, period_a
            )
            error = first_error(lines_a)
            if not error:
                lines_b, lates_b = send_block(
                    ser, "B", str(ecg_id), count_b, ecg_lines, 40.0, stop_result, period_b
                )
                error = first_error(lines_b)
            else:
                lines_b = []
                lates_b = []
            row["e2e_ms"] = round((time.monotonic() - start) * 1000, 3)
            (
                row["sched_late_median_ms"],
                row["sched_late_p95_ms"],
                row["sched_late_max_ms"],
            ) = late_stats(lates_a + lates_b)
            agent_a = parse_agent_a(
                next((line for line in lines_a if line.startswith("AGENT,A,")), "")
            )
            agent_b = parse_agent_b(
                next((line for line in lines_b if line.startswith("AGENT,B,")), "")
            )
            result = parse_result_line(
                next((line for line in lines_b if line.startswith("RESULT,")), "")
            )
            ack_a = f"ACK,{fall_id},{count_a}" in lines_a
            ack_b = f"ACK,{ecg_id},{count_b}" in lines_b
            if error:
                row["status"], row["error"] = "error", error
            elif result is not None:
                row["status"] = "ok" if agent_a is not None else "partial"
                row["predicted_class"] = result["color"]
                row["match"] = "1" if result["color"] == reference else "0"
                row["triage_us"] = result["triage_us"]
                heap_source = agent_b or agent_a
                if heap_source is not None:
                    row["heap"] = heap_source["heap"]
                if agent_a is not None:
                    row["received_samples"] = agent_a["muestras"]
                    row["fall_us"] = agent_a["fall_us"]
                else:
                    row["error"] = "AGENT,A corrupto o ausente; RESULT presente"
            elif ack_a and ack_b:
                row["status"], row["error"] = "missing_agent", "ACK sin RESULT"
            else:
                row["status"], row["error"] = "timeout", "sin ACK/RESULT"
            rows.append(row)
            print(f"== escenario {scenario_id}: {row['status']} -> "
                  f"{row['predicted_class'] or '-'} (ref {reference}) {row['error']}")

        write_results(rows, output / "results.csv")
        tflite = Path(
            "notebooks/data/modelos/ecg/tinyecgnet_ptb_xl_250hz/tflite/"
            "agent1_tinyecgnet_sequential_int8.tflite"
        )
        summary = json.loads((dataset_dir / "summary.json").read_text(encoding="utf-8"))
        metadata = {
            "suite": suite,
            "mode": args.mode,
            "pacing": {
                "repeats": repeats,
                "period_a_s": period_a,
                "period_b_s": period_b,
                "late_definition": (
                    "retraso real de cada envio frente a su instante programado, en ms"
                ),
            },
            "port": args.port,
            "baud": args.baud,
            "dataset_dir": str(dataset_dir),
            "output_dir": str(output),
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "elapsed_s": round(time.time() - started, 3),
            "versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "pandas": pd.__version__,
                "pyserial": pyserial.__version__,
            },
            "device_hello": hello_lines,
            "dataset_source_hashes": summary.get("sources", {}),
            "tflite_sha256": (
                hashlib_sha256(tflite) if tflite.exists() else ""
            ),
            "counts": {
                "rows": len(rows),
                "trials": len(trials),
                "records": len(records),
                "scenarios": len(scenarios),
            },
            "notes": (
                "reference_class usa etiquetas de origen; el triaje desde salidas reales se "
                "reconstruye uniendo trial_A/record_B por fall_trial_id y ecg_id. "
                "status distingue ok/partial/error/timeout/missing_agent; un timeout o una "
                "linea corrupta nunca es prediccion."
            ),
        }
        (output / "run_metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        expected_rows = (len(trials) + len(records) + len(scenarios)) * repeats
        statuses = {}
        for row in rows:
            statuses[row["status"]] = statuses.get(row["status"], 0) + 1
        matches = sum(1 for row in rows if row["match"] == "1")
        ok = len(rows) == expected_rows and statuses.get("ok", 0) == expected_rows
        print(
            f"RESULTADO: {'PASS' if ok else 'FAIL'} filas={len(rows)}/{expected_rows} "
            f"estados={statuses} coincidencias_con_etiquetas={matches}"
        )
        print(f"resultados: {output / 'results.csv'} y {output / 'run_metadata.json'}")
        return 0 if ok else 1
    finally:
        ser.close()


def run_resilience(args: argparse.Namespace) -> int:
    """Inyecciones de fallo + caso valido de recuperacion tras cada una."""
    dataset_dir = Path(args.dataset_dir)
    output = (
        Path(args.output)
        if args.output
        else Path("reports/esp32_validation")
        / f"resilience_{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    )
    output.mkdir(parents=True, exist_ok=True)

    scenario = load_scenario(dataset_dir, args.scenario)
    fall_id = str(scenario["fall_trial_id"])
    ecg_id = int(scenario["ecg_id"])
    count_a, _, fall_lines = load_trial(dataset_dir, fall_id)
    count_b, ecg_lines = load_ecg(dataset_dir, ecg_id)

    def stop_block(line: str) -> bool:
        return line.startswith("ACK,") or line.startswith("ERROR")

    def stop_result(line: str) -> bool:
        return line.startswith("RESULT,") or line.startswith("ERROR")

    steps = []
    started = time.time()
    ser = open_port(args.port, args.baud)
    try:
        hello = handshake(ser)
        steps.append({"step": "hello", "ok": bool(hello), "observed": hello})

        def read_error(deadline: float = 8.0) -> list[str]:
            return read_until(
                ser, time.monotonic() + deadline, stop=lambda line: line.startswith("ERROR")
            )

        def drain(seconds: float = 1.0) -> None:
            read_until(ser, time.monotonic() + seconds)

        def valid_case() -> tuple[bool, list[str]]:
            send(ser, f"CASE,{args.scenario},{fall_id},{ecg_id}")
            lines_a, _ = send_block(ser, "A", fall_id, count_a, fall_lines, 20.0, stop_block)
            if first_error(lines_a):
                return False, lines_a
            lines_b, _ = send_block(ser, "B", str(ecg_id), count_b, ecg_lines, 40.0, stop_result)
            result = next((line for line in lines_b if line.startswith("RESULT,")), "")
            return bool(result) and not first_error(lines_b), lines_a + lines_b

        send(ser, f"CASE,{args.scenario},{fall_id},{ecg_id}")
        send(ser, f"BEGIN,A,{fall_id},{count_a}")
        for index in range(5):
            send(ser, fall_lines[index])
        ser.write(b"S,5,")
        send(ser, "0.0,0.0,1.0")
        observed = read_error(5.0)
        drain()
        step = {
            "step": "linea_truncada",
            "injection": "prefijo 'S,5,' sin salto + continuacion: la linea queda con 5 campos",
            "expected": f"ERROR,SAMPLE,{fall_id}",
            "observed": observed,
            "ok": any(line.startswith("ERROR,SAMPLE") for line in observed),
        }
        recovery_ok, recovery_lines = valid_case()
        step["recovery_ok"] = recovery_ok
        step["recovery_observed"] = [line for line in recovery_lines if line.startswith(("RESULT,", "ACK,"))]
        steps.append(step)

        send(ser, f"CASE,{args.scenario},{fall_id},{ecg_id}")
        send(ser, f"BEGIN,A,{fall_id},{count_a}")
        for index in [0, 1, 2, 3, 4, 6]:
            send(ser, fall_lines[index])
        observed = read_error(5.0)
        drain()
        step = {
            "step": "muestra_omitida",
            "injection": "salto de indice (falta la muestra 5)",
            "expected": f"ERROR,SAMPLE,{fall_id}",
            "observed": observed,
            "ok": any(line.startswith("ERROR,SAMPLE") for line in observed),
        }
        recovery_ok, recovery_lines = valid_case()
        step["recovery_ok"] = recovery_ok
        step["recovery_observed"] = [line for line in recovery_lines if line.startswith(("RESULT,", "ACK,"))]
        steps.append(step)

        send(ser, f"CASE,{args.scenario},{fall_id},{ecg_id}")
        send(ser, f"BEGIN,A,{fall_id},{count_a}")
        for index in range(5):
            send(ser, fall_lines[index])
        observed = read_error(9.0)
        drain()
        step = {
            "step": "timeout",
            "injection": "bloque A incompleto sin mas lineas",
            "expected": f"ERROR,TIMEOUT,{fall_id}",
            "observed": observed,
            "ok": any(line.startswith("ERROR,TIMEOUT") for line in observed),
        }
        recovery_ok, recovery_lines = valid_case()
        step["recovery_ok"] = recovery_ok
        step["recovery_observed"] = [line for line in recovery_lines if line.startswith(("RESULT,", "ACK,"))]
        steps.append(step)

        send(ser, f"CASE,{args.scenario},{fall_id},{ecg_id}")
        send(ser, f"BEGIN,A,{fall_id},{count_a}")
        for index in range(5):
            send(ser, fall_lines[index])
        ser.close()
        print("puerto cerrado en mitad del bloque; esperando al timeout del dispositivo")
        time.sleep(7.0)
        ser = open_port(args.port, args.baud)
        hello2 = handshake(ser)
        recovery_ok, recovery_lines = valid_case()
        step = {
            "step": "host_desconectado",
            "injection": "cierre del puerto con el bloque A a medias; reconexion tras 7 s",
            "expected": "HELLO/READY tras reconectar y caso valido sin estado residual",
            "observed": hello2,
            "ok": bool(hello2),
            "recovery_ok": recovery_ok,
            "recovery_observed": [line for line in recovery_lines if line.startswith(("RESULT,", "ACK,"))],
        }
        steps.append(step)
    finally:
        try:
            ser.close()
        except Exception:
            pass

    all_ok = all(
        step["ok"] and step.get("recovery_ok", True) for step in steps
    )
    record = {
        "dataset_dir": str(dataset_dir),
        "scenario": args.scenario,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "elapsed_s": round(time.time() - started, 3),
        "steps": steps,
        "all_ok": all_ok,
    }
    (output / "resilience.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    for step in steps:
        print(
            f"== {step['step']}: {'PASS' if step['ok'] and step.get('recovery_ok', True) else 'FAIL'} "
            f"| observado: {step['observed']}"
        )
    print(f"RESULTADO: {'PASS' if all_ok else 'FAIL'} | {output / 'resilience.json'}")
    return 0 if all_ok else 1


def hashlib_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def run_hello(args: argparse.Namespace) -> int:
    ser = open_port(args.port, args.baud)
    try:
        ok = bool(handshake(ser))
    finally:
        ser.close()
    print("RESULTADO:", "READY,1 confirmado" if ok else "FALLO")
    return 0 if ok else 1


def run_block(args: argparse.Namespace) -> int:
    dataset_dir = Path(args.dataset_dir)
    if args.agent == "A":
        if not args.trial:
            raise SystemExit("el agente A requiere --trial")
        count, label, lines_to_send = load_trial(dataset_dir, args.trial)
        expected = rule_reference(dataset_dir, args.trial)
        expected["label"] = label
        case_id = args.trial
    else:
        if args.ecg_id is None:
            raise SystemExit("el agente B requiere --ecg-id")
        count, lines_to_send = load_ecg(dataset_dir, args.ecg_id)
        case_id = str(args.ecg_id)
        expected = load_reference(dataset_dir, args.ecg_id)
        expected_fnv = tensor_checksum(dataset_dir, args.ecg_id)

    ser = open_port(args.port, args.baud)
    try:
        if not handshake(ser):
            return 1
        send(ser, f"BEGIN,{args.agent},{case_id},{count}")
        sent = 0
        for line in lines_to_send:
            if args.truncate and sent >= args.truncate:
                break
            send(ser, line)
            sent += 1
        if args.truncate:
            print(f"bloque truncado en {sent}/{count}; esperando ERROR del dispositivo")
            lines = read_until(
                ser, time.monotonic() + 8.0, stop=lambda line: line.startswith("ERROR")
            )
            ok = any(line.startswith("ERROR,TIMEOUT") for line in lines)
            print("RESULTADO:", "ERROR,TIMEOUT recibido" if ok else "sin ERROR,TIMEOUT")
            return 0 if ok else 1
        if args.bad_end:
            send(ser, "END,ID_INCORRECTO")
            lines = read_until(
                ser, time.monotonic() + 3.0, stop=lambda line: line.startswith("ERROR")
            )
            ok = any(line.startswith("ERROR,END") for line in lines)
            print("RESULTADO:", "ERROR,END recibido" if ok else "sin ERROR,END")
            return 0 if ok else 1

        send(ser, f"END,{case_id}")
        lines = read_until(
            ser,
            time.monotonic() + 10.0,
            stop=lambda line: line.startswith("ACK") or line.startswith("ERROR"),
        )
        ack_ok = f"ACK,{case_id},{count}" in lines
        agent_line = next((line for line in lines if line.startswith("AGENT,")), None)
        if args.agent == "A":
            agent_ok, detail = check_agent_a(agent_line, case_id, count, expected)
        else:
            agent_ok, detail = check_agent_b(agent_line, case_id, count, expected, expected_fnv)
        ok = ack_ok and agent_ok
        if not ack_ok:
            detail = "sin ACK exacto; " + detail
        print("RESULTADO:", "PASS" if ok else "FAIL", detail)
        return 0 if ok else 1
    finally:
        ser.close()


def main() -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--port", default="/dev/ttyUSB0")
    common.add_argument("--baud", type=int, default=115200)

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("hello", parents=[common], help="HELLO,1 -> READY,1")
    block = sub.add_parser(
        "block",
        parents=[common],
        help="envia un trial A (--trial) o un registro B (--agent B --ecg-id) y comprueba AGENT/ACK",
    )
    block.add_argument("--dataset-dir", required=True)
    block.add_argument("--agent", choices=["A", "B"], default="A")
    block.add_argument("--trial", help="trial KFall del manifiesto (agente A)")
    block.add_argument("--ecg-id", type=int, help="registro ECG del stream (agente B)")
    block.add_argument("--truncate", type=int, default=0, help="corta el bloque tras N muestras")
    block.add_argument("--bad-end", action="store_true", help="envia END con id incorrecto")
    scenario = sub.add_parser(
        "scenario", parents=[common], help="escenario CASE (A+B) -> AGENT/RESULT"
    )
    scenario.add_argument("--dataset-dir", required=True)
    scenario.add_argument("--ids", required=True, help="scenario_id separados por coma")
    scenario.add_argument(
        "--drop-b", action="store_true", help="omite B y espera ERROR,TIMEOUT sin RESULT"
    )
    scenario.add_argument(
        "--truncate", type=int, default=0, help="corta el bloque A tras N muestras"
    )
    scenario.add_argument(
        "--bad-end-b", action="store_true", help="envia END incorrecto en el bloque B"
    )
    run = sub.add_parser(
        "run",
        parents=[common],
        help="corrida completa del dataset: trials A, registros B y escenarios -> results.csv",
    )
    run.add_argument("--dataset-dir", required=True)
    run.add_argument("--mode", choices=["fast", "paced"], default="fast")
    run.add_argument(
        "--suite", default=None, help="etiqueta de la corrida (por defecto, el nombre del dataset-dir)"
    )
    run.add_argument(
        "--output",
        default=None,
        help="directorio de salida (por defecto reports/esp32_validation/<suite>_<UTC>)",
    )
    run.add_argument("--trials", default=None, help="subconjunto de trial_id separados por coma")
    run.add_argument("--ecgs", default=None, help="subconjunto de ecg_id separados por coma")
    run.add_argument("--scenarios", default=None, help="subconjunto de scenario_id separados por coma")
    run.add_argument(
        "--repeat", type=int, default=1, help="repeticiones del conjunto seleccionado"
    )
    resilience = sub.add_parser(
        "resilience",
        parents=[common],
        help="inyecciones (linea truncada, muestra omitida, timeout, desconexion) y recuperacion",
    )
    resilience.add_argument("--dataset-dir", required=True)
    resilience.add_argument("--scenario", default="S0007", help="escenario valido de recuperacion")
    resilience.add_argument("--output", default=None)
    args = parser.parse_args()
    if args.command == "hello":
        return run_hello(args)
    if args.command == "scenario":
        return run_scenario(args)
    if args.command == "run":
        return run_suite(args)
    if args.command == "resilience":
        return run_resilience(args)
    return run_block(args)


if __name__ == "__main__":
    sys.exit(main())
