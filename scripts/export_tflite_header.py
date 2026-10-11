"""Exporta un modelo .tflite INT8 a dos headers C para firmware ESP32.

Escribe un header con el binario del modelo (``static const`` + ``alignas(16)``
para que el linker lo ubique en ``.rodata`` y no en RAM) y un header aparte con
las constantes de cuantizacion, leidas del propio .tflite con
``tf.lite.Interpreter`` (deprecado, pero es lo unico disponible mientras
``ai-edge-litert`` no este instalado).

Uso minimo:

    python scripts/export_tflite_header.py MODELO.tflite --frecuencia-hz 250
"""

import argparse
import hashlib
from pathlib import Path
import sys
import warnings

import numpy as np
import tensorflow as tf

BYTES_POR_LINEA = 12
UMBRAL_POR_DEFECTO = 0.5


def numero(valor):
    """Representa un float en C sin perder digitos ni notacion exponencial ambigua.

    El sufijo ``f`` es obligatorio: sin el, cada constante ocupa 8 bytes en flash
    en vez de 4 y el compilador inserta conversiones implicitas.
    """
    return f"{valor:.17g}f"


def leer_cuantizacion(ruta_modelo):
    """Devuelve (binario, detalle_entrada, detalle_salida) o falla con un error claro."""
    if not ruta_modelo.is_file():
        raise ValueError(f"No existe el modelo .tflite: {ruta_modelo}")

    modelo = ruta_modelo.read_bytes()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        try:
            interprete = tf.lite.Interpreter(model_content=modelo)
            interprete.allocate_tensors()
        except (ValueError, RuntimeError) as error:
            raise ValueError(
                f"El archivo no es un .tflite valido para tf.lite.Interpreter: {error}"
            ) from error
        entradas = interprete.get_input_details()
        salidas = interprete.get_output_details()

    if len(entradas) != 1 or len(salidas) != 1:
        raise ValueError(
            f"El modelo debe tener una entrada y una salida, no {len(entradas)} y {len(salidas)}."
        )
    return modelo, entradas[0], salidas[0]


def validar(detalle_entrada, detalle_salida):
    """Verifica tipos y formas INT8 y devuelve (forma_entrada, forma_salida)."""
    if detalle_entrada["dtype"] != np.int8 or detalle_salida["dtype"] != np.int8:
        raise ValueError(
            "La entrada y la salida deben ser INT8, no "
            f"{detalle_entrada['dtype']} y {detalle_salida['dtype']}."
        )

    forma_entrada = [int(dim) for dim in detalle_entrada["shape"]]
    forma_salida = [int(dim) for dim in detalle_salida["shape"]]
    if len(forma_entrada) != 3 or forma_entrada[0] != 1:
        raise ValueError(
            f"La entrada debe tener forma [1, muestras, canales], no {forma_entrada}."
        )
    if forma_entrada[1] < 1 or forma_entrada[2] < 1:
        raise ValueError(f"La entrada tiene una dimension vacia: {forma_entrada}.")
    if forma_salida != [1, 1]:
        raise ValueError(f"La salida debe tener forma [1, 1], no {forma_salida}.")
    return forma_entrada, forma_salida


def escribir_header(ruta_salida, guarda, origen, lineas):
    """Envuelve las lineas en un include guard y las escribe en disco."""
    contenido = "\n".join(
        [
            f"#ifndef {guarda}",
            f"#define {guarda}",
            "",
            f"/* Generado por scripts/export_tflite_header.py desde {origen}. No editar. */",
            "",
            *lineas,
            "",
            "#endif",
            "",
        ]
    )
    ruta_salida.write_text(contenido, encoding="utf-8")
    return ruta_salida


def main():
    parser = argparse.ArgumentParser(
        description="Exporta un .tflite INT8 a headers C para firmware ESP32."
    )
    parser.add_argument("modelo", type=Path, help="Ruta del archivo .tflite.")
    parser.add_argument(
        "--nombre-base",
        default=None,
        help="Nombre base de los simbolos C (por defecto, el nombre del archivo).",
    )
    parser.add_argument(
        "--directorio-salida",
        type=Path,
        default=None,
        help="Donde escribir los headers (por defecto, junto al .tflite).",
    )
    parser.add_argument(
        "--frecuencia-hz",
        type=int,
        required=True,
        help="Frecuencia de muestreo en Hz. No se puede leer del .tflite.",
    )
    parser.add_argument(
        "--paso-muestras",
        type=int,
        default=None,
        help="Salto entre ventanas (por defecto, la ventana completa sin solapamiento).",
    )
    parser.add_argument(
        "--umbral",
        type=float,
        default=UMBRAL_POR_DEFECTO,
        help=f"Umbral de decision en el dominio real (por defecto {UMBRAL_POR_DEFECTO}).",
    )
    argumentos = parser.parse_args()

    ruta_modelo = argumentos.modelo
    nombre_base = argumentos.nombre_base or ruta_modelo.stem
    if not nombre_base.isidentifier():
        raise ValueError(f"El nombre base {nombre_base!r} no es un identificador valido de C.")

    modelo, detalle_entrada, detalle_salida = leer_cuantizacion(ruta_modelo)
    forma_entrada, forma_salida = validar(detalle_entrada, detalle_salida)

    paso_muestras = argumentos.paso_muestras or forma_entrada[1]
    if argumentos.frecuencia_hz < 1 or paso_muestras < 1:
        raise ValueError(
            f"La frecuencia ({argumentos.frecuencia_hz} Hz) y el paso ({paso_muestras} muestras) "
            "deben ser positivos."
        )

    escala_entrada, cero_entrada = detalle_entrada["quantization"]
    escala_salida, cero_salida = detalle_salida["quantization"]
    if escala_entrada <= 0 or escala_salida <= 0:
        raise ValueError(
            "Las escalas de cuantizacion de entrada y salida deben ser mayores que cero."
        )

    techo_entrada_real = (127 - cero_entrada) * escala_entrada
    umbral_salida_int8 = int(
        np.clip(np.rint(argumentos.umbral / escala_salida + cero_salida), -128, 127)
    )
    umbral_reconstruido = (umbral_salida_int8 - cero_salida) * escala_salida

    directorio = argumentos.directorio_salida or ruta_modelo.parent
    directorio.mkdir(parents=True, exist_ok=True)
    origen = ruta_modelo.name
    arreglo = f"{nombre_base}_model"
    lineas_modelo = [
        "/* alignas es C11/C++; en C puro <stdint.h> no la define. */",
        "#include <stdalign.h>",
        "",
        f"alignas(16) static const unsigned char {arreglo}[] = {{",
        *[
            "    "
            + ", ".join(f"0x{byte:02x}" for byte in modelo[inicio : inicio + BYTES_POR_LINEA])
            + ","
            for inicio in range(0, len(modelo), BYTES_POR_LINEA)
        ],
        "};",
        f"static const unsigned int {arreglo}_len =",
        f"    (unsigned int)sizeof({arreglo});",
    ]
    lineas_config = [
        "/* Ventana de analisis, leida de la forma de entrada del .tflite. */",
        f"#define FRECUENCIA_HZ {argumentos.frecuencia_hz}",
        f"#define TAMANO_VENTANA {forma_entrada[1]}",
        f"#define PASO_MUESTRAS {paso_muestras}",
        f"#define NUM_CANALES {forma_entrada[2]}",
        f"#define FORMA_ENTRADA {{1, {forma_entrada[1]}, {forma_entrada[2]}}}",
        "",
        "/* Cuantizacion de entrada: q = clip(rint(x / ESCALAF + CERO), -128, 127). */",
        f"#define ENTRADA_ESCALAF {numero(float(escala_entrada))}",
        f"#define ENTRADA_CERO {int(cero_entrada)}",
        "",
        "/* Valor real maximo representable en la entrada cuantizada. */",
        f"#define TECHO_ENTRADA_REAL {numero(techo_entrada_real)}",
        "",
        "/* Cuantizacion de salida: p = (q - SALIDA_CERO) * SALIDA_ESCALAF. */",
        f"#define SALIDA_ESCALAF {numero(float(escala_salida))}",
        f"#define SALIDA_CERO {int(cero_salida)}",
        "",
        f"#define UMBRAL {numero(argumentos.umbral)}",
        f"#define UMBRAL_SALIDA_INT8 {umbral_salida_int8}",
        f"#define UMBRAL_RECONSTRUIDO {numero(umbral_reconstruido)}",
    ]

    ruta_header_modelo = escribir_header(
        directorio / f"{nombre_base}_model.h",
        f"{nombre_base.upper()}_MODEL_H",
        origen,
        lineas_modelo,
    )
    ruta_header_config = escribir_header(
        directorio / f"{nombre_base}_config.h",
        f"{nombre_base.upper()}_CONFIG_H",
        origen,
        lineas_config,
    )

    print(f"Modelo:       {ruta_modelo}")
    print(f"Tamano:       {len(modelo)} bytes")
    print(f"sha256:       {hashlib.sha256(modelo).hexdigest()}")
    print(f"Header modelo: {ruta_header_modelo}")
    print(f"Header config: {ruta_header_config}")
    print(
        f"Entrada INT8:  forma {forma_entrada}, escala {numero(float(escala_entrada))}, "
        f"cero {int(cero_entrada)}"
    )
    print(
        f"Salida INT8:   forma {forma_salida}, escala {numero(float(escala_salida))}, "
        f"cero {int(cero_salida)}"
    )
    print(
        f"Ventana:       {argumentos.frecuencia_hz} Hz, paso {paso_muestras} muestras, "
        f"{forma_entrada[2]} canal(es), {forma_entrada[1]} muestras"
    )
    print(f"Techo entrada: {numero(techo_entrada_real)} (valor real)")
    print(
        f"Umbral:        {numero(argumentos.umbral)} -> int8 {umbral_salida_int8} "
        f"-> {numero(umbral_reconstruido)}"
    )


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        sys.exit(f"ERROR: {error}")
