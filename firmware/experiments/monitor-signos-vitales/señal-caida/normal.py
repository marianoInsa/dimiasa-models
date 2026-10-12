import serial
import time
import math


# ============================================================
# CONFIGURACION
# ============================================================

PORT = "COM3"
BAUDRATE = 115200

FS = 100

DURATION = 5


# ============================================================
# CONEXION
# ============================================================

print("=" * 60)
print("AGENT2 — PRUEBA 2 — MOVIMIENTO NORMAL")
print("=" * 60)

print()
print(f"Puerto: {PORT}")
print(f"Frecuencia: {FS} Hz")
print(f"Duracion: {DURATION} segundos")
print()

ser = serial.Serial(
    PORT,
    BAUDRATE,
    timeout=1
)

time.sleep(2)

ser.reset_input_buffer()


# ============================================================
# GENERAR MOVIMIENTO NORMAL
# ============================================================

total_samples = FS * DURATION

period = 1.0 / FS

start_time = time.perf_counter()


print(
    f"Enviando {total_samples} muestras..."
)

print()


for i in range(total_samples):

    t = i / FS


    # --------------------------------------------------------
    # ACELERACION
    # --------------------------------------------------------
    #
    # Movimiento suave alrededor de 1 g.
    #
    # No hay impacto brusco.
    #

    ax = 0.08 * math.sin(
        2.0 * math.pi * 1.0 * t
    )

    ay = 0.05 * math.sin(
        2.0 * math.pi * 0.7 * t
    )

    az = (
        1.0
        + 0.10 * math.sin(
            2.0 * math.pi * 1.2 * t
        )
    )


    # --------------------------------------------------------
    # GIROSCOPIO
    # --------------------------------------------------------
    #
    # Movimiento normal moderado.
    #

    gx = 15.0 * math.sin(
        2.0 * math.pi * 0.8 * t
    )

    gy = 20.0 * math.sin(
        2.0 * math.pi * 0.6 * t
    )

    gz = 10.0 * math.sin(
        2.0 * math.pi * 1.0 * t
    )


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
    # CONTROL DE FRECUENCIA
    # --------------------------------------------------------

    target_time = (
        start_time
        +
        (i + 1) * period
    )

    while time.perf_counter() < target_time:
        pass


print()
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