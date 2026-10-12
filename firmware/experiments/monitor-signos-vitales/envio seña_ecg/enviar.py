
import time
from pathlib import Path

import numpy as np
import serial

# ============================================================
# CONFIGURACION
# ============================================================

PORT = "COM3"
BAUDRATE = 115200
TIMEOUT = 1
RESULT_TIMEOUT = 90

NUM_MUESTRAS = 5000

DATASET = Path(__file__).resolve().with_name("PTBXL_TEST_LEAD_II_500HZ.npz")


# ============================================================
# CARGAR BANCO PTB-XL
# ============================================================

print("=" * 60)
print("AGENT1 ECG - CLASIFICACION ESP32")
print("=" * 60)

print("\nCargando banco de prueba...")

try:
    data = np.load(DATASET)

    X = data["X"]
    y = data["y"]
    ecg_ids = data["ecg_ids"]

except Exception as e:
    print("ERROR al cargar el banco:")
    print(e)
    raise SystemExit


# ============================================================
# VALIDAR BANCO
# ============================================================

if X.ndim != 2 or X.shape[1] != NUM_MUESTRAS:
    raise RuntimeError(
        f"Se esperaban 5000 muestras por ECG. Forma encontrada: {X.shape}"
    )

if len(X) != len(y) or len(X) != len(ecg_ids):
    raise RuntimeError(
        "X, y y ecg_ids tienen diferente cantidad de registros."
    )

print("\nBanco cargado correctamente.")
print("Registros disponibles:", len(X))
print("Muestras por ECG:", NUM_MUESTRAS)
print("Frecuencia: 500 Hz")
print("Duracion: 10 segundos")


# ============================================================
# OBTENER ETIQUETA REAL
# ============================================================

def obtener_etiqueta_real(valor):

    valor = int(valor)

    if valor == 0:
        return "NORMAL"

    elif valor == 1:
        return "ANORMAL"

    else:
        raise ValueError(
            f"Etiqueta inesperada: {valor}. "
            "Se esperaba 0=NORMAL o 1=ANORMAL."
        )


# ============================================================
# ENVIAR ECG AL ESP32 CON PROGRESO
# ============================================================

def enviar_ecg(ser, ecg):

    if len(ecg) != NUM_MUESTRAS:
        raise ValueError(
            f"El ECG tiene {len(ecg)} muestras; "
            f"se esperaban {NUM_MUESTRAS}."
        )

    # Limpiar respuestas anteriores
    ser.reset_input_buffer()

    # Iniciar adquisicion
    ser.write(b"START\n")
    ser.flush()

    time.sleep(0.05)

    print("\nENVIANDO ECG AL ESP32")
    print("-" * 40)

    for i in range(NUM_MUESTRAS):

        valor = float(ecg[i])
        mensaje = f"{valor:.9f}\n"

        ser.write(mensaje.encode("ascii"))

        # Mostrar progreso cada 500 muestras
        if (i + 1) % 500 == 0:
            print(f"Enviadas: {i + 1}/{NUM_MUESTRAS}")

    ser.flush()

    print("\nEnvio de las 5000 muestras finalizado.")


# ============================================================
# LEER CLASIFICACION DEL ESP32
# ============================================================

def leer_clasificacion(ser):

    inicio = time.monotonic()

    while time.monotonic() - inicio < RESULT_TIMEOUT:

        raw = ser.readline()

        if not raw:
            continue

        linea = raw.decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if linea.startswith("RESULTADO:"):

            resultado = linea.split(
                ":",
                1
            )[1].strip().upper()

            if resultado == "NORMAL":
                return "NORMAL"

            elif resultado == "ANORMAL":
                return "ANORMAL"

    raise TimeoutError(
        "El ESP32 no devolvio una clasificacion "
        "dentro del tiempo limite."
    )


# ============================================================
# CONECTAR ESP32
# ============================================================

print("\nConectando con el ESP32 por", PORT)

try:

    ser = serial.Serial(
        PORT,
        BAUDRATE,
        timeout=TIMEOUT
    )

except serial.SerialException as e:

    print("\nERROR al abrir el puerto serial:")
    print(e)
    print("Verifica que el ESP32 este conectado.")
    print("Cierra el Monitor Serie de Arduino.")

    raise SystemExit


# ============================================================
# ESPERAR REINICIO DEL ESP32
# ============================================================

time.sleep(2)
ser.reset_input_buffer()

print("ESP32 conectado correctamente.")


# ============================================================
# SELECCION Y CLASIFICACION AUTOMATICA
# ============================================================

try:

    while True:

        print("\n" + "=" * 60)
        print("SELECCION DE ECG")
        print("=" * 60)

        print(f"Indices disponibles: 0 a {len(X) - 1}")
        print("Ingresa -1 para terminar.")

        # Al presionar Enter con el indice,
        # el programa comienza el envio automaticamente.
        entrada = input("\nIndice del ECG: ").strip()

        try:
            indice = int(entrada)

        except ValueError:
            print("ERROR: ingresa un numero entero.")
            continue

        if indice == -1:
            break

        if indice < 0 or indice >= len(X):
            print("ERROR: indice fuera de rango.")
            continue

        # Obtener el registro seleccionado
        ecg = X[indice]
        etiqueta_real = obtener_etiqueta_real(y[indice])
        ptbxl_id = int(ecg_ids[indice])

        print("\nREGISTRO SELECCIONADO")
        print("-" * 40)
        print("Indice seleccionado:", indice)
        print("PTB-XL ID real:", ptbxl_id)
        print("Etiqueta real:", etiqueta_real)
        print("Muestras:", len(ecg))
        print("Frecuencia: 500 Hz")
        print("Duracion: 10 segundos")

        # ENVIO AUTOMATICO: no se solicita confirmacion
        try:

            enviar_ecg(ser, ecg)

        except (serial.SerialException, ValueError) as e:

            print("\nERROR durante el envio:")
            print(e)
            continue

        # Esperar resultado
        print("\nEsperando clasificacion del ESP32...")

        try:

            prediccion = leer_clasificacion(ser)

        except (serial.SerialException, TimeoutError) as e:

            print("\nERROR al recibir resultado:")
            print(e)
            continue

        # Comparar con etiqueta real
        coincide = prediccion == etiqueta_real

        # Mostrar resultado final
        print("\n")
        print("=" * 60)
        print("RESULTADO DE LA CLASIFICACION")
        print("=" * 60)

        print("INDICE SELECCIONADO:", indice)
        print("PTB-XL ID REAL:", ptbxl_id)
        print("ETIQUETA REAL:", etiqueta_real)
        print("CLASIFICACION ESP32:", prediccion)

        if coincide:
            print("COINCIDE CON EL VALOR REAL: SI")
        else:
            print("COINCIDE CON EL VALOR REAL: NO")

        print("=" * 60)

finally:

    ser.close()

    print("\nPuerto COM3 cerrado.")
    print("FIN.")
