

/*
============================================================
AGENT2 — FALL DETECTION V2
============================================================

SENSOR:
    Pecho

DATOS:
    Accelerometer:
        Ax
        Ay
        Az

    Gyroscope:
        Gx
        Gy
        Gz

FRECUENCIA:
    100 Hz

VENTANA:
    1 segundo

MUESTRAS:
    100 por ventana


============================================================
LOGICA
============================================================

                    NORMAL
                      |
                      | impacto fuerte
                      v
                   IMPACTO
                      |
                      | observar durante
                      | un tiempo limitado
                      v
              POST-IMPACTO
                /         \
               /           \
        movimiento       inmovilidad
           |                 |
           v                 v
        CANCELAR        POSIBLE CAIDA
                              |
                              | 2 ventanas
                              | inmoviles
                              v
                       CAIDA CONFIRMADA


IMPORTANTE:

Un impacto solo NO confirma una caída.

Para confirmar:

    IMPACTO
       +
    INMOVILIDAD POSTERIOR
       +
    2 VENTANAS INMOVILES


TIMEOUT:

Después del impacto tenemos un número limitado
de ventanas para encontrar la inmovilidad.

Si no aparece:

    CAIDA CANCELADA

y el sistema vuelve a:

    NORMAL


============================================================
*/


// ============================================================
// CONFIGURACION
// ============================================================

const float FS = 100.0;

const int WINDOW_SAMPLES = 100;


// ============================================================
// UMBRALES
// ============================================================

// Movimiento fuerte
const float ACC_STRONG_THRESHOLD = 0.40;

const float GYRO_STRONG_THRESHOLD = 60.0;


// Impacto fuerte
const float ACC_IMPACT_THRESHOLD = 2.0;

const float GYRO_IMPACT_THRESHOLD = 150.0;


// Inmovilidad
const float ACC_STILL_THRESHOLD = 0.40;

const float GYRO_STILL_THRESHOLD = 30.0;


// ============================================================
// CONFIRMACION
// ============================================================

// Ventanas inmoviles necesarias
const int STILL_WINDOWS_REQUIRED = 2;


// ============================================================
// TIMEOUT POST-IMPACTO
// ============================================================
//
// El impacto ocurre en una ventana.
//
// Después observamos hasta 3 ventanas.
//
// Si durante esas ventanas no aparece inmovilidad,
// se cancela la sospecha.
//
// 3 ventanas = aproximadamente 3 segundos.
//
// ============================================================

const int POST_IMPACT_MAX_WINDOWS = 3;


// ============================================================
// BUFFERS
// ============================================================

float ax_buffer[WINDOW_SAMPLES];

float ay_buffer[WINDOW_SAMPLES];

float az_buffer[WINDOW_SAMPLES];

float gx_buffer[WINDOW_SAMPLES];

float gy_buffer[WINDOW_SAMPLES];

float gz_buffer[WINDOW_SAMPLES];


// ============================================================
// CONTADOR DE MUESTRAS
// ============================================================

int sample_count = 0;


// ============================================================
// MAQUINA DE ESTADOS
// ============================================================

enum FallState
{
    STATE_NORMAL,

    STATE_IMPACT,

    STATE_POSSIBLE_FALL,

    STATE_CONFIRMED
};


FallState fall_state = STATE_NORMAL;


// ============================================================
// CONTADORES
// ============================================================

int still_windows = 0;

int post_impact_windows = 0;


// ============================================================
// MAGNITUD
// ============================================================

float calculateMagnitude(
    float x,
    float y,
    float z
)
{
    return sqrt(
        x * x
        +
        y * y
        +
        z * z
    );
}


// ============================================================
// REINICIAR EVENTO
// ============================================================

void resetFallDetection()
{

    fall_state =
        STATE_NORMAL;

    still_windows =
        0;

    post_impact_windows =
        0;
}


// ============================================================
// PROCESAR VENTANA
// ============================================================

void processWindow()
{

    // ========================================================
    // VARIABLES
    // ========================================================

    float acc_min = 999999.0;

    float acc_max = -999999.0;

    float gyro_min = 999999.0;

    float gyro_max = -999999.0;


    // ========================================================
    // ACELEROMETRO
    // ========================================================

    for (
        int i = 0;
        i < WINDOW_SAMPLES;
        i++
    )
    {

        float acc =
            calculateMagnitude(
                ax_buffer[i],
                ay_buffer[i],
                az_buffer[i]
            );


        if (
            acc < acc_min
        )
        {
            acc_min = acc;
        }


        if (
            acc > acc_max
        )
        {
            acc_max = acc;
        }
    }


    // ========================================================
    // GIROSCOPIO
    // ========================================================

    for (
        int i = 0;
        i < WINDOW_SAMPLES;
        i++
    )
    {

        float gyro =
            calculateMagnitude(
                gx_buffer[i],
                gy_buffer[i],
                gz_buffer[i]
            );


        if (
            gyro < gyro_min
        )
        {
            gyro_min = gyro;
        }


        if (
            gyro > gyro_max
        )
        {
            gyro_max = gyro;
        }
    }


    // ========================================================
    // RANGOS
    // ========================================================

    float acc_range =
        acc_max - acc_min;


    float gyro_range =
        gyro_max - gyro_min;


    // ========================================================
    // MOSTRAR DATOS
    // ========================================================

    Serial.println();

    Serial.println(
        "========================================"
    );

    Serial.println(
        "AGENT2 — VENTANA 1 s"
    );

    Serial.println(
        "========================================"
    );


    Serial.print(
        "ACC min: "
    );

    Serial.println(
        acc_min,
        4
    );


    Serial.print(
        "ACC max: "
    );

    Serial.println(
        acc_max,
        4
    );


    Serial.print(
        "ACC range: "
    );

    Serial.println(
        acc_range,
        4
    );


    Serial.print(
        "GYRO min: "
    );

    Serial.println(
        gyro_min,
        4
    );


    Serial.print(
        "GYRO max: "
    );

    Serial.println(
        gyro_max,
        4
    );


    Serial.print(
        "GYRO range: "
    );

    Serial.println(
        gyro_range,
        4
    );


    // ========================================================
    // CONDICIONES
    // ========================================================

    bool strong_acc =
        acc_range >=
        ACC_STRONG_THRESHOLD;


    bool strong_gyro =
        gyro_range >=
        GYRO_STRONG_THRESHOLD;


    bool impact_acc =
        acc_range >=
        ACC_IMPACT_THRESHOLD;


    bool impact_gyro =
        gyro_range >=
        GYRO_IMPACT_THRESHOLD;


    bool still =
        (
            acc_range <
            ACC_STILL_THRESHOLD

            &&

            gyro_range <
            GYRO_STILL_THRESHOLD
        );


    // ========================================================
    // MAQUINA DE ESTADOS
    // ========================================================

    switch (
        fall_state
    )
    {

        // ====================================================
        // NORMAL
        // ====================================================

        case STATE_NORMAL:

            still_windows = 0;

            post_impact_windows = 0;


            // ------------------------------------------------
            // IMPACTO
            // ------------------------------------------------

            if (
                impact_acc
                &&
                impact_gyro
            )
            {

                fall_state =
                    STATE_IMPACT;


                post_impact_windows =
                    0;


                still_windows =
                    0;


                Serial.println(
                    "ESTADO: IMPACTO"
                );


                Serial.println(
                    "EVENTO: IMPACTO FUERTE"
                );


                Serial.println(
                    "OBSERVANDO TRANSICION"
                );
            }


            // ------------------------------------------------
            // MOVIMIENTO FUERTE SIN IMPACTO
            // ------------------------------------------------

            else if (
                strong_acc
                ||
                strong_gyro
            )
            {

                Serial.println(
                    "ESTADO: DINAMICO"
                );


                Serial.println(
                    "EVENTO: MOVIMIENTO FUERTE"
                );


                Serial.println(
                    "REQUIERE ANALISIS DE TRANSICION"
                );
            }


            // ------------------------------------------------
            // NORMAL
            // ------------------------------------------------

            else
            {

                Serial.println(
                    "ESTADO: ESTATICO"
                );


                Serial.println(
                    "EVENTO: SIN CAIDA CONFIRMADA"
                );
            }


            break;


        // ====================================================
        // IMPACTO
        // ====================================================

        case STATE_IMPACT:

            post_impact_windows++;


            Serial.println(
                "ESTADO: POST-IMPACTO"
            );


            Serial.print(
                "VENTANA POST-IMPACTO: "
            );


            Serial.print(
                post_impact_windows
            );


            Serial.print(
                " / "
            );


            Serial.println(
                POST_IMPACT_MAX_WINDOWS
            );


            // ------------------------------------------------
            // INMOVILIDAD
            // ------------------------------------------------

            if (
                still
            )
            {

                still_windows = 1;


                fall_state =
                    STATE_POSSIBLE_FALL;


                Serial.println(
                    "POST-IMPACTO: INMOVILIDAD"
                );


                Serial.println(
                    "EVENTO: POSIBLE CAIDA"
                );


                Serial.println(
                    "ESPERANDO SEGUNDA CONFIRMACION"
                );
            }


            // ------------------------------------------------
            // SIGUE MOVIENDOSE
            // ------------------------------------------------

            else
            {

                Serial.println(
                    "POST-IMPACTO: MOVIMIENTO"
                );


                // --------------------------------------------
                // TIMEOUT
                // --------------------------------------------

                if (
                    post_impact_windows
                    >=
                    POST_IMPACT_MAX_WINDOWS
                )
                {

                    Serial.println(
                        "TIMEOUT POST-IMPACTO"
                    );


                    Serial.println(
                        "CAIDA NO CONFIRMADA"
                    );


                    resetFallDetection();
                }


                else
                {

                    Serial.println(
                        "EVENTO SOSPECHOSO"
                    );


                    Serial.println(
                        "CONTINUANDO OBSERVACION"
                    );
                }
            }


            break;


        // ====================================================
        // POSIBLE CAIDA
        // ====================================================

        case STATE_POSSIBLE_FALL:

            Serial.println(
                "ESTADO: POSIBLE CAIDA"
            );


            // ------------------------------------------------
            // SIGUE INMOVIL
            // ------------------------------------------------

            if (
                still
            )
            {

                still_windows++;


                Serial.print(
                    "VENTANAS INMOVILES: "
                );


                Serial.println(
                    still_windows
                );


                // --------------------------------------------
                // CONFIRMACION
                // --------------------------------------------

                if (
                    still_windows
                    >=
                    STILL_WINDOWS_REQUIRED
                )
                {

                    fall_state =
                        STATE_CONFIRMED;


                    Serial.println(
                        "========================================"
                    );


                    Serial.println(
                        "CAIDA CONFIRMADA"
                    );


                    Serial.println(
                        "========================================"
                    );
                }


                else
                {

                    Serial.println(
                        "POSIBLE CAIDA"
                    );


                    Serial.println(
                        "ESPERANDO CONFIRMACION"
                    );
                }
            }


            // ------------------------------------------------
            // VUELVE A MOVERSE
            // ------------------------------------------------

            else
            {

                Serial.println(
                    "MOVIMIENTO DETECTADO"
                );


                Serial.println(
                    "CAIDA CANCELADA"
                );


                resetFallDetection();
            }


            break;


        // ====================================================
        // CONFIRMADA
        // ====================================================

        case STATE_CONFIRMED:

            Serial.println(
                "ESTADO: CAIDA CONFIRMADA"
            );


            Serial.println(
                "EVENTO: CAIDA"
            );


            Serial.println(
                "ESPERANDO NUEVO EVENTO"
            );


            resetFallDetection();


            break;
    }


    Serial.println(
        "========================================"
    );
}


// ============================================================
// SETUP
// ============================================================

void setup()
{

    Serial.begin(
        115200
    );


    delay(1000);


    Serial.println();

    Serial.println(
        "========================================"
    );

    Serial.println(
        "AGENT2 — FALL DETECTION V2"
    );

    Serial.println(
        "MAQUINA DE ESTADOS + TIMEOUT"
    );

    Serial.println(
        "========================================"
    );


    Serial.println();

    Serial.println(
        "Sensor: PECHO"
    );

    Serial.println(
        "Acelerometro: 3 ejes"
    );

    Serial.println(
        "Giroscopio: 3 ejes"
    );

    Serial.println(
        "Frecuencia: 100 Hz"
    );

    Serial.println(
        "Ventana: 1 segundo"
    );

    Serial.println(
        "Muestras/ventana: 100"
    );


    Serial.println();

    Serial.println(
        "----------------------------------------"
    );

    Serial.println(
        "PARAMETROS"
    );

    Serial.println(
        "----------------------------------------"
    );


    Serial.print(
        "ACC fuerte: "
    );

    Serial.println(
        ACC_STRONG_THRESHOLD,
        2
    );


    Serial.print(
        "GYRO fuerte: "
    );

    Serial.println(
        GYRO_STRONG_THRESHOLD,
        2
    );


    Serial.print(
        "ACC impacto: "
    );

    Serial.println(
        ACC_IMPACT_THRESHOLD,
        2
    );


    Serial.print(
        "GYRO impacto: "
    );

    Serial.println(
        GYRO_IMPACT_THRESHOLD,
        2
    );


    Serial.print(
        "ACC inmovilidad: "
    );

    Serial.println(
        ACC_STILL_THRESHOLD,
        2
    );


    Serial.print(
        "GYRO inmovilidad: "
    );

    Serial.println(
        GYRO_STILL_THRESHOLD,
        2
    );


    Serial.print(
        "Ventanas inmoviles: "
    );

    Serial.println(
        STILL_WINDOWS_REQUIRED
    );


    Serial.print(
        "Timeout post-impacto: "
    );

    Serial.print(
        POST_IMPACT_MAX_WINDOWS
    );

    Serial.println(
        " segundos"
    );


    Serial.println();

    Serial.println(
        "========================================"
    );

    Serial.println(
        "AGENT2 LISTO"
    );

    Serial.println(
        "========================================"
    );
}


// ============================================================
// LOOP
// ============================================================

void loop()
{

    if (
        Serial.available()
    )
    {

        String line =
            Serial.readStringUntil(
                '\n'
            );


        line.trim();


        if (
            line.length() == 0
        )
        {
            return;
        }


        // ====================================================
        // DATOS
        //
        // Ax,Ay,Az,Gx,Gy,Gz
        // ====================================================

        float ax;
        float ay;
        float az;

        float gx;
        float gy;
        float gz;


        int values =
            sscanf(
                line.c_str(),
                "%f,%f,%f,%f,%f,%f",
                &ax,
                &ay,
                &az,
                &gx,
                &gy,
                &gz
            );


        if (
            values != 6
        )
        {

            Serial.println(
                "ERROR: FORMATO DE DATOS"
            );


            return;
        }


        // ====================================================
        // GUARDAR
        // ====================================================

        ax_buffer[
            sample_count
        ] = ax;


        ay_buffer[
            sample_count
        ] = ay;


        az_buffer[
            sample_count
        ] = az;


        gx_buffer[
            sample_count
        ] = gx;


        gy_buffer[
            sample_count
        ] = gy;


        gz_buffer[
            sample_count
        ] = gz;


        sample_count++;


        // ====================================================
        // VENTANA COMPLETA
        // ====================================================

        if (
            sample_count >=
            WINDOW_SAMPLES
        )
        {

            processWindow();


            sample_count = 0;
        }
    }
}

