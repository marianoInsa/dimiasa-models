#!/usr/bin/env python3
"""Referencia Python de B (ECG) y exportación de coeficientes para el firmware.

- Replica paso a paso `sosfiltfilt`/`filtfilt` de SciPy sobre la cadena del
  entrenamiento (Butterworth 0,5-40 Hz + notch 50 Hz/Q30 + z-score), para que
  el C++ del firmware la reproduzca sin depender de SciPy.
- Exporta coeficientes, condiciones iniciales y padlens a un header C++
  (`firmware/esp32_validation/ecg_filter_coeffs.h`).
- Genera vectores de referencia por registro usando la ruta `adc_count_sim` en
  `notebooks/data/esp32_simulation/rule_based/<suite>/ecg_reference.csv` más un
  resumen con hashes; la inferencia TFLite INT8 es opcional.

Uso:
  .venv/bin/python scripts/esp32_simulation/reference.py --self-check --export-header
  .venv/bin/python scripts/esp32_simulation/reference.py --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, iirnotch, lfilter_zi, sosfilt_zi, sosfiltfilt

FS = 250
FRECUENCIA_BAJA = 0.5
FRECUENCIA_ALTA = 40.0
ORDEN_BANDPASS = 4
FRECUENCIA_NOTCH = 50.0
FACTOR_Q_NOTCH = 30.0
WINDOW_SAMPLES = 2500
DEFAULT_HEADER = Path("firmware/esp32_validation/ecg_filter_coeffs.h")
DEFAULT_TFLITE = Path(
    "notebooks/data/modelos/ecg/tinyecgnet_ptb_xl_250hz/tflite/agent1_tinyecgnet_sequential_int8.tflite"
)

SOS = butter(ORDEN_BANDPASS, [FRECUENCIA_BAJA, FRECUENCIA_ALTA], btype="bandpass", fs=FS, output="sos")
NOTCH_B, NOTCH_A = iirnotch(w0=FRECUENCIA_NOTCH, Q=FACTOR_Q_NOTCH, fs=FS)
SOS_ZI = sosfilt_zi(SOS)
NOTCH_ZI = lfilter_zi(NOTCH_B, NOTCH_A)
SOS_NTAPS = 2 * SOS.shape[0] + 1 - min(int((SOS[:, 2] == 0).sum()), int((SOS[:, 5] == 0).sum()))
SOS_PADLEN = 3 * SOS_NTAPS
NOTCH_PADLEN = 3 * max(len(NOTCH_A), len(NOTCH_B))


def _odd_ext(x: np.ndarray, n: int) -> np.ndarray:
    left_end = x[0:1]
    left_ext = x[n:0:-1]
    right_end = x[-1:]
    right_ext = x[-2 : -(n + 2) : -1]
    return np.concatenate((2.0 * left_end - left_ext, x, 2.0 * right_end - right_ext))


def _lfilter(b: np.ndarray, a: np.ndarray, x: np.ndarray, zi: np.ndarray | None = None):
    n_states = max(len(a), len(b)) - 1
    states = np.zeros(n_states, dtype=np.float64)
    if zi is not None:
        states[:] = zi
    bb = np.zeros(n_states + 1, dtype=np.float64)
    aa = np.zeros(n_states + 1, dtype=np.float64)
    bb[: len(b)] = b
    aa[: len(a)] = a
    if aa[0] != 1.0:
        bb /= aa[0]
        aa /= aa[0]
    y = np.empty_like(x, dtype=np.float64)
    for i, xi in enumerate(x):
        out = bb[0] * xi + states[0]
        for k in range(1, n_states + 1):
            states[k - 1] = bb[k] * xi - aa[k] * out + (states[k] if k < n_states else 0.0)
        y[i] = out
    return y, states


def _sosfilt(sos: np.ndarray, x: np.ndarray, zi: np.ndarray | None = None):
    states = np.zeros((sos.shape[0], 2), dtype=np.float64)
    if zi is not None:
        states[:] = zi
    y = np.array(x, dtype=np.float64)
    for s in range(sos.shape[0]):
        b0, b1, b2, a1, a2 = sos[s, 0], sos[s, 1], sos[s, 2], sos[s, 4], sos[s, 5]
        z0 = states[s, 0]
        z1 = states[s, 1]
        for i in range(y.size):
            xi = y[i]
            yi = b0 * xi + z0
            z0 = b1 * xi - a1 * yi + z1
            z1 = b2 * xi - a2 * yi
            y[i] = yi
        states[s, 0] = z0
        states[s, 1] = z1
    return y, states


def _sosfiltfilt(sos: np.ndarray, x: np.ndarray, zi_step: np.ndarray, padlen: int) -> np.ndarray:
    ext = _odd_ext(x, padlen)
    y, _ = _sosfilt(sos, ext, zi=zi_step * ext[0])
    y = y[::-1]
    y, _ = _sosfilt(sos, y, zi=zi_step * y[0])
    y = y[::-1]
    return y[padlen:-padlen]


def _filtfilt(b: np.ndarray, a: np.ndarray, x: np.ndarray, zi_step: np.ndarray, padlen: int) -> np.ndarray:
    ext = _odd_ext(x, padlen)
    y, _ = _lfilter(b, a, ext, zi=zi_step * ext[0])
    y = y[::-1]
    y, _ = _lfilter(b, a, y, zi=zi_step * y[0])
    y = y[::-1]
    return y[padlen:-padlen]


def preprocess_ecg(adc_counts: np.ndarray) -> np.ndarray:
    x = np.asarray(adc_counts, dtype=np.float64)
    y = _sosfiltfilt(SOS, x, SOS_ZI, SOS_PADLEN)
    y = _filtfilt(NOTCH_B, NOTCH_A, y, NOTCH_ZI, NOTCH_PADLEN)
    media = float(np.mean(y))
    desviacion = float(np.std(y))
    if desviacion < 1e-8:
        desviacion = 1e-8
    return (y - media) / desviacion


def quantize_ecg(signal: np.ndarray, escala: float, cero: int) -> tuple[np.ndarray, int]:
    scaled = np.rint(np.asarray(signal, dtype=np.float64) / escala) + cero
    saturados = int(((scaled < -128) | (scaled > 127)).sum())
    return np.clip(scaled, -128, 127).astype(np.int8), saturados


def self_check() -> None:
    rng = np.random.default_rng(20261011)
    x = rng.standard_normal(4000).cumsum() * 10.0
    y_ref = sosfiltfilt(SOS, x)
    y_manual = _sosfiltfilt(SOS, x, SOS_ZI, SOS_PADLEN)
    err = float(np.max(np.abs(y_ref - y_manual)))
    assert err < 1e-9, f"sosfiltfilt manual difiere de SciPy: {err}"
    y_ref = filtfilt(NOTCH_B, NOTCH_A, y_manual)
    y_manual = _filtfilt(NOTCH_B, NOTCH_A, y_manual, NOTCH_ZI, NOTCH_PADLEN)
    err = float(np.max(np.abs(y_ref - y_manual)))
    assert err < 1e-9, f"filtfilt manual difiere de SciPy: {err}"

    adc = np.clip(np.rint(2048 + 500 * rng.standard_normal(2500)), 0, 4095).astype(np.uint16)
    directa = filtfilt(NOTCH_B, NOTCH_A, sosfiltfilt(SOS, adc.astype(np.float64)))
    directa = (directa - directa.mean()) / directa.std()
    manual = preprocess_ecg(adc)
    err = float(np.max(np.abs(directa - manual)))
    assert err < 1e-9, f"cadena completa difiere: {err}"
    print(
        f"self-check OK: sosfiltfilt {SOS_PADLEN=} filtfilt {NOTCH_PADLEN=} "
        f"error manual-vs-SciPy < 1e-9"
    )


def export_header(path: Path, escala: float, cero: int) -> None:
    def arr(values: np.ndarray, fmt: str = "%.17g") -> str:
        return ", ".join(fmt % float(v) for v in np.asarray(values).reshape(-1))

    rows = ",\n    ".join("{" + arr(row) + "}" for row in SOS)
    text = f"""// Generado por scripts/esp32_simulation/reference.py. No editar.
#ifndef ECG_FILTER_COEFFS_H
#define ECG_FILTER_COEFFS_H

/* Cadena congelada del entrenamiento: Butterworth orden {ORDEN_BANDPASS} bandpass {FRECUENCIA_BAJA}-{FRECUENCIA_ALTA} Hz (filtfilt),
   notch {FRECUENCIA_NOTCH} Hz Q={FACTOR_Q_NOTCH} (filtfilt), z-score por ventana y cuantizacion INT8. */

#define ECG_WINDOW_SAMPLES {WINDOW_SAMPLES}
#define ECG_SOS_SECTIONS {SOS.shape[0]}
#define ECG_SOS_PADLEN {SOS_PADLEN}
#define ECG_NOTCH_PADLEN {NOTCH_PADLEN}

static const double ECG_SOS[ECG_SOS_SECTIONS][6] = {{
    {rows}
}};

static const double ECG_SOS_ZI[ECG_SOS_SECTIONS][2] = {{
    {{{arr(SOS_ZI[0])}}},
    {{{arr(SOS_ZI[1])}}},
    {{{arr(SOS_ZI[2])}}},
    {{{arr(SOS_ZI[3])}}}
}};

static const double ECG_NOTCH_B[3] = {{{arr(NOTCH_B)}}};
static const double ECG_NOTCH_A[3] = {{{arr(NOTCH_A)}}};
static const double ECG_NOTCH_ZI[2] = {{{arr(NOTCH_ZI)}}};

#define ECG_QUANT_SCALE {escala:.17g}
#define ECG_QUANT_ZERO_POINT {cero}

#endif
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"header exportado: {path}")


def read_int8_scale(tflite_path: Path) -> tuple[float, int]:
    import tensorflow as tf

    interprete = tf.lite.Interpreter(model_path=str(tflite_path))
    interprete.allocate_tensors()
    detalle = interprete.get_input_details()[0]
    escala, cero = detalle["quantization"]
    if detalle["dtype"] != np.int8:
        raise ValueError(f"Se esperaba entrada INT8; se recibio {detalle['dtype']}")
    return float(escala), int(cero)


def build_reference(dataset_dir: Path, tflite_path: Path | None, with_inference: bool) -> None:
    records = pd.read_csv(dataset_dir / "ecg_records.csv")
    stream = pd.read_csv(dataset_dir / "ecg_stream.csv")
    if not set(stream["ecg_id"]).issubset(set(records["ecg_id"])):
        raise ValueError("ecg_stream.csv contiene registros ausentes de ecg_records.csv")
    escala, cero = read_int8_scale(tflite_path) if tflite_path else (0.081706210970878601, -18)

    interprete = None
    if with_inference:
        import tensorflow as tf

        interprete = tf.lite.Interpreter(model_path=str(tflite_path))
        interprete.allocate_tensors()

    salida = []
    resumen = []
    digest = hashlib.sha256()
    for ecg_id, frame in stream.groupby("ecg_id", sort=False):
        adc = frame["adc_count_sim"].to_numpy(dtype=np.uint16)
        if adc.size != WINDOW_SAMPLES:
            raise ValueError(f"ecg_id {ecg_id}: {adc.size} muestras != {WINDOW_SAMPLES}")
        filtrada = preprocess_ecg(adc)
        tensor, saturados = quantize_ecg(filtrada, escala, cero)
        digest.update(tensor.tobytes())
        fila = {
            "ecg_id": int(ecg_id),
            "int8_sha256": hashlib.sha256(tensor.tobytes()).hexdigest(),
            "saturated": saturados,
            "float_min": float(filtrada.min()),
            "float_max": float(filtrada.max()),
        }
        if interprete is not None:
            entrada = interprete.get_input_details()[0]
            salida_det = interprete.get_output_details()[0]
            interprete.set_tensor(entrada["index"], tensor.reshape(entrada["shape"]))
            interprete.invoke()
            q = int(interprete.get_tensor(salida_det["index"]).reshape(-1)[0])
            out_scale, out_zero = salida_det["quantization"]
            p = (q - int(out_zero)) * float(out_scale)
            fila.update({"q": q, "p": p, "clase": "ANORMAL" if p >= 0.5 else "NORMAL"})
        resumen.append(fila)
        salida.append(
            pd.DataFrame({
                "ecg_id": int(ecg_id),
                "sample_index": frame["sample_index"].to_numpy(),
                "adc_count_sim": adc,
                "filtered_zscore": filtrada,
                "int8": tensor,
            })
        )

    all_rows = pd.concat(salida, ignore_index=True)
    all_rows.to_csv(dataset_dir / "ecg_reference.csv", index=False, float_format="%.17g")
    resumen_global = {
        "dataset_dir": str(dataset_dir),
        "scale": escala,
        "zero_point": cero,
        "window_samples": WINDOW_SAMPLES,
        "sos_padlen": SOS_PADLEN,
        "notch_padlen": NOTCH_PADLEN,
        "int8_sha256_all_records": digest.hexdigest(),
        "records": resumen,
    }
    (dataset_dir / "ecg_reference_summary.json").write_text(
        json.dumps(resumen_global, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"referencia: {dataset_dir}/ecg_reference.csv "
        f"({len(salida)} registros, {len(all_rows)} filas) | "
        f"int8 sha256 {digest.hexdigest()[:16]}... | "
        f"saturados max {max(r['saturated'] for r in resumen)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true", help="Compara la version manual contra SciPy")
    parser.add_argument("--export-header", action="store_true", help="Exporta ecg_filter_coeffs.h")
    parser.add_argument("--header", type=Path, default=DEFAULT_HEADER)
    parser.add_argument("--dataset-dir", type=Path, help="Suite con ecg_records.csv/ecg_stream.csv")
    parser.add_argument("--tflite", type=Path, default=DEFAULT_TFLITE)
    parser.add_argument("--no-inference", action="store_true", help="Omite la inferencia TFLite en el resumen")
    args = parser.parse_args()

    if args.self_check:
        self_check()
    if args.export_header or not any([args.self_check, args.dataset_dir]):
        tflite = args.tflite if args.tflite.exists() else None
        escala, cero = read_int8_scale(tflite) if tflite else (0.081706210970878601, -18)
        if not math.isclose(escala, 0.081706210970878601, rel_tol=1e-15):
            raise ValueError(f"Escala inesperada del modelo: {escala!r}")
        export_header(args.header, escala, cero)
    if args.dataset_dir:
        build_reference(args.dataset_dir, args.tflite if args.tflite.exists() else None,
                        with_inference=not args.no_inference)


if __name__ == "__main__":
    main()
