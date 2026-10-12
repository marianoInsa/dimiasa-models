
import serial
import time
import math


# ============================================================
# AGENT2 — PRUEBA 4
# FALSO POSITIVO
# ============================================================
#
# Objetivo:
#
# Simular un movimiento MUY fuerte que NO termina en caída.
#
# El objetivo es comprobar que:
#
#     impacto/movimiento fuerte
#
# NO sea suficiente por sí solo para declarar una caída.
#
#
# Fases:
#
# 0.0 - 2.0 s
#     Movimiento normal
#
# 2.0 - 2.5 s
#     Movimiento muy fuerte
#     Alta aceleración
#     Alta rotación
#
# 2.5 - 5.0 s
#     La persona continúa moviéndose
#
# ============================================================


# ============================================================
# CONFIGURACION
# ============================================================

PORT = "COM3"

BAUDRATE = 115200

FS = 100

DURATION = 5.0


# ============================================================
# CONEXION
# ============================================================

print()
print("=" * 60)
print("AGENT2 — PRUEBA 4 — FALSO POSITIVO")
print("=" * 60)

print()

print(f"Puerto: {PORT}")
print(f"Baudrate: {BAUDRATE}")
print(f"Frecuencia: {FS} Hz")
print(f"Duracion: {DURATION} segundos")

print()

print("FASES:")
print("0.0 - 2.0 s : MOVIMIENTO NORMAL")
print("2.0 - 2.5 s : MOVIMIENTO MUY FUERTE")
print("2.5 - 5.0 s : CONTINUA MOVIENDOSE")

print()

print("IMPORTANTE:")
print("NO se simula una caida.")
print("NO se simula inmovilidad posterior.")

print()


# ============================================================
# ABRIR PUERTO
# ============================================================

ser = serial.Serial(
    PORT,
    BAUDRATE,
    timeout=1
)

time.sleep(2)

ser.reset_input_buffer()

print("ESP32 conectado.")
print()


# ============================================================
# CONFIGURACION TEMPORAL
# ============================================================

TOTAL_SAMPLES = int(
    FS * DURATION
)

PERIOD = 1.0 / FS


# ============================================================
# ENVIO
# ============================================================

print(
    f"Enviando {TOTAL_SAMPLES} muestras..."
)

print()


start_time = time.perf_counter()


for i in range(TOTAL_SAMPLES):

    t = i / FS


    # ========================================================
    # FASE 1
    # MOVIMIENTO NORMAL
    #
    # 0 - 2 segundos
    # ========================================================

    if t < 2.0:

        ax = (
            0.05
            *
            math.sin(
                2.0
                *
                math.pi
                *
                1.0
                *
                t
            )
        )


        ay = (
            0.04
            *
            math.sin(
                2.0
                *
                math.pi
                *
                0.7
                *
                t
            )
        )


        az = (
            1.0
            +
            0.08
            *
            math.sin(
                2.0
                *
                math.pi
                *
                1.2
                *
                t
            )
        )


        gx = (
            10.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                0.8
                *
                t
            )
        )


        gy = (
            15.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                0.6
                *
                t
            )
        )


        gz = (
            8.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                1.0
                *
                t
            )
        )


    # ========================================================
    # FASE 2
    # MOVIMIENTO MUY FUERTE
    #
    # 2.0 - 2.5 segundos
    # ========================================================

    elif t < 2.5:

        phase_t = t - 2.0


        # ----------------------------------------------------
        # Oscilacion fuerte
        # ----------------------------------------------------

        ax = (
            2.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                8.0
                *
                phase_t
            )
        )


        ay = (
            1.5
            *
            math.sin(
                2.0
                *
                math.pi
                *
                6.0
                *
                phase_t
            )
        )


        az = (
            1.0
            +
            2.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                10.0
                *
                phase_t
            )
        )


        # ----------------------------------------------------
        # Rotacion muy fuerte
        # ----------------------------------------------------

        gx = (
            180.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                5.0
                *
                phase_t
            )
        )


        gy = (
            220.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                4.0
                *
                phase_t
            )
        )


        gz = (
            140.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                6.0
                *
                phase_t
            )
        )


    # ========================================================
    # FASE 3
    # CONTINUA MOVIENDOSE
    #
    # 2.5 - 5 segundos
    # ========================================================

    else:

        phase_t = t - 2.5


        # ----------------------------------------------------
        # Movimiento moderado/rápido
        #
        # IMPORTANTE:
        # No volvemos a cero.
        #
        # Esto representa que la persona continúa caminando
        # o moviéndose después del evento fuerte.
        # ----------------------------------------------------

        ax = (
            0.20
            *
            math.sin(
                2.0
                *
                math.pi
                *
                1.5
                *
                phase_t
            )
        )


        ay = (
            0.15
            *
            math.sin(
                2.0
                *
                math.pi
                *
                1.1
                *
                phase_t
            )
        )


        az = (
            1.0
            +
            0.25
            *
            math.sin(
                2.0
                *
                math.pi
                *
                1.8
                *
                phase_t
            )
        )


        gx = (
            40.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                1.2
                *
                phase_t
            )
        )


        gy = (
            55.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                0.9
                *
                phase_t
            )
        )


        gz = (
            30.0
            *
            math.sin(
                2.0
                *
                math.pi
                *
                1.5
                *
                phase_t
            )
        )


    # ========================================================
    # ENVIAR MUESTRA
    # ========================================================

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


    # ========================================================
    # CONTROL DE 100 Hz
    # ========================================================

    target_time = (
        start_time
        +
        (i + 1)
        *
        PERIOD
    )


    while time.perf_counter() < target_time:
        pass


# ============================================================
# FINAL DEL ENVIO
# ============================================================

print()

print("Movimiento fuerte enviado.")

print()

print("=" * 60)
print("ESPERANDO RESPUESTA DEL ESP32")
print("=" * 60)

print()


# ============================================================
# LEER RESPUESTA
# ============================================================

time.sleep(3)

last_data_time = time.time()


while True:

    if ser.in_waiting:

        line = (
            ser.readline()
            .decode(
                "utf-8",
                errors="ignore"
            )
            .strip()
        )

        if line:

            print(line)

            last_data_time = time.time()

    else:

        if (
            time.time()
            -
            last_data_time
            >
            2.0
        ):
            break


# ============================================================
# CERRAR PUERTO
# ============================================================

ser.close()


print()

print("=" * 60)
print("FIN DE LA PRUEBA")
print("=" * 60)
