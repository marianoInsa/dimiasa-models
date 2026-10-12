
import serial
import time
import math


# ============================================================
# CONFIGURACION
# ============================================================

PORT = "COM3"

BAUDRATE = 115200

FS = 100

DURATION = 3


# ============================================================
# CONEXION
# ============================================================

print("=" * 60)
print("AGENT2 — PRUEBA ESP32")
print("=" * 60)

print()

print(f"Puerto: {PORT}")
print(f"Baudrate: {BAUDRATE}")
print(f"Frecuencia: {FS} Hz")

print()

ser = serial.Serial(
    PORT,
    BAUDRATE,
    timeout=1
)

time.sleep(2)


# ============================================================
# LIMPIAR BUFFER
# ============================================================

ser.reset_input_buffer()


# ============================================================
# ESPERAR AGENT2
# ============================================================

print("Esperando AGENT2...")

time.sleep(1)


# ============================================================
# GENERAR SEÑAL ESTATICA
# ============================================================
#
# Sensor quieto:
#
# aceleracion ≈ 1 g
# giroscopio ≈ 0 deg/s
#
# Suponemos que el eje Z apunta hacia arriba.
#

total_samples = FS * DURATION


print()
print(f"Enviando {total_samples} muestras...")
print()


period = 1.0 / FS


start_time = time.perf_counter()


for i in range(total_samples):

    # --------------------------------------------------------
    # ACELEROMETRO
    # --------------------------------------------------------

    ax = 0.0
    ay = 0.0
    az = 1.0


    # --------------------------------------------------------
    # GIROSCOPIO
    # --------------------------------------------------------

    gx = 0.0
    gy = 0.0
    gz = 0.0


    # --------------------------------------------------------
    # ENVIAR
    # --------------------------------------------------------

    line = (
        f"{ax:.6f},"
        f"{ay:.6f},"
        f"{az:.6f},"
        f"{gx:.6f},"
        f"{gy:.6f},"
        f"{gz:.6f}\n"
    )


    ser.write(
        line.encode("utf-8")
    )


    # --------------------------------------------------------
    # MANTENER 100 Hz
    # --------------------------------------------------------

    target_time = start_time + (i + 1) * period

    while time.perf_counter() < target_time:
        pass


# ============================================================
# FINAL
# ============================================================

print("Envío terminado.")

print()

print("=" * 60)
print("ESPERANDO RESPUESTA DEL ESP32")
print("=" * 60)

print()


# ============================================================
# LEER RESPUESTA
# ============================================================

time.sleep(2)


while ser.in_waiting:

    line = ser.readline().decode(
        "utf-8",
        errors="ignore"
    ).strip()

    if line:
        print(line)


# ============================================================
# CERRAR
# ============================================================

ser.close()

print()

print("=" * 60)
print("FIN DE LA PRUEBA")
print("=" * 60)

