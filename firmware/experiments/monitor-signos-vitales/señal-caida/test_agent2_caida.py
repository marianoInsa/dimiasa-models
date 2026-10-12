
import serial
import time
import math


# ============================================================
# AGENT2 — PRUEBA 3
# SIMULACION DE CAIDA
# ============================================================
#
# Flujo:
#
#   0.0 - 2.0 s
#       Movimiento normal
#
#   2.0 - 2.2 s
#       Perdida de estabilidad
#
#   2.2 - 2.4 s
#       Impacto
#
#   2.4 - 5.0 s
#       Inmovilidad posterior
#
# Datos enviados:
#
#   Ax, Ay, Az, Gx, Gy, Gz
#
# Frecuencia:
#
#   100 Hz
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
print("AGENT2 — PRUEBA 3 — CAIDA SIMULADA")
print("=" * 60)

print()
print(f"Puerto: {PORT}")
print(f"Baudrate: {BAUDRATE}")
print(f"Frecuencia: {FS} Hz")
print(f"Duracion: {DURATION} segundos")

print()

print("FASES:")
print("0.0 - 2.0 s : MOVIMIENTO NORMAL")
print("2.0 - 2.2 s : PERDIDA DE ESTABILIDAD")
print("2.2 - 2.4 s : IMPACTO")
print("2.4 - 5.0 s : INMOVILIDAD")

print()


# ============================================================
# ABRIR PUERTO
# ============================================================

ser = serial.Serial(
    PORT,
    BAUDRATE,
    timeout=1
)


# Esperar reinicio/conexion del ESP32

time.sleep(2)


# Limpiar mensajes anteriores

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
# ENVIAR DATOS
# ============================================================

print(
    f"Enviando {TOTAL_SAMPLES} muestras..."
)

print()


start_time = time.perf_counter()


for i in range(TOTAL_SAMPLES):

    # Tiempo actual de la simulacion

    t = i / FS


    # ========================================================
    # FASE 1
    # MOVIMIENTO NORMAL
    #
    # 0.0 <= t < 2.0
    # ========================================================

    if t < 2.0:

        # Acelerometro:
        # pequeñas variaciones alrededor de 1 g

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


        # Giroscopio:
        # movimiento moderado

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
    # PERDIDA DE ESTABILIDAD
    #
    # 2.0 <= t < 2.2
    # ========================================================

    elif t < 2.2:

        phase_t = t - 2.0


        # Movimiento cada vez mayor

        factor = (
            phase_t
            /
            0.2
        )


        # Aceleracion irregular

        ax = (
            0.2
            *
            factor
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
            0.4
            *
            factor
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
            -
            0.5
            *
            factor
        )


        # Aumento fuerte de la rotacion

        gx = (
            80.0
            *
            factor
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


        gy = (
            120.0
            *
            factor
        )


        gz = (
            60.0
            *
            factor
            *
            math.sin(
                2.0
                *
                math.pi
                *
                3.0
                *
                phase_t
            )
        )


    # ========================================================
    # FASE 3
    # IMPACTO
    #
    # 2.2 <= t < 2.4
    # ========================================================

    elif t < 2.4:

        phase_t = t - 2.2


        # ----------------------------------------------------
        # IMPACTO
        #
        # Pico de aceleracion.
        #
        # Usamos una forma gaussiana para que exista un
        # pico fuerte aproximadamente en el centro.
        # ----------------------------------------------------

        impact = math.exp(
            -(
                (
                    phase_t
                    -
                    0.10
                )
                ** 2
            )
            /
            (
                2.0
                *
                0.025
                *
                0.025
            )
        )


        # Pico aproximado de varios g

        ax = (
            1.5
            *
            impact
        )


        ay = (
            2.0
            *
            impact
        )


        az = (
            1.0
            +
            2.5
            *
            impact
        )


        # ----------------------------------------------------
        # ROTACION FUERTE
        # ----------------------------------------------------

        gx = (
            150.0
            *
            impact
        )


        gy = (
            250.0
            *
            impact
        )


        gz = (
            100.0
            *
            impact
        )


    # ========================================================
    # FASE 4
    # INMOVILIDAD POSTERIOR
    #
    # 2.4 <= t <= 5.0
    # ========================================================

    else:

        # Simulamos una postura final diferente.
        #
        # El vector gravedad ya no esta principalmente
        # en Z como al comienzo.

        ax = 0.85

        ay = 0.05

        az = 0.52


        # Practicamente sin movimiento

        gx = 0.5

        gy = 0.5

        gz = 0.2


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
        line.encode(
            "utf-8"
        )
    )


    # ========================================================
    # MANTENER 100 Hz
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
# ENVIO TERMINADO
# ============================================================

print("Caida simulada enviada.")

print()

print("=" * 60)
print("ESPERANDO RESPUESTA DEL ESP32")
print("=" * 60)

print()


# ============================================================
# ESPERAR QUE EL ESP32 TERMINE
# ============================================================

time.sleep(3)


# ============================================================
# LEER TODAS LAS RESPUESTAS
# ============================================================

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

        # Si durante 2 segundos no llegan datos,
        # consideramos terminada la respuesta.

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
print("FIN DE LA PRUEBA — CAIDA SIMULADA")
print("=" * 60)

