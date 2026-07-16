
---

# Datasets Seleccionados

## Sobre el Experimento

| Dataset      | Participantes | Demografía                                             | Caídas/AVD  | Datos     | Año      | Conseguido |
| ------------ | ------------- | ------------------------------------------------------ | ----------- | --------- | -------- | ---------- |
| ==SisFall==  | ==38==        | ==23 jóvenes (19-30 años)<br>15 mayores (60-75 años)== | ==15 / 19== | ==4504==  | ==2017== | ==✅==      |
| ==FallAllD== | ==15==        | ==21-53 años (media: 32)==                             | ==35 / 44== | ==26420== | ==2021== | ==✅==      |
| UMAFall      | 17            | 18-55 años (media: 26.9)                               | 3 / 8       | 531       | 2017     | ✅          |
| ==UP-Fall==  | ==17==        | ==18-24 años==                                         | ==5 / 6==   | ==561==   | ==2019== | ==✅==      |
| ==KFall==    | ==32==        | ==24.9 ± 3.7 años==                                    | ==15 / 21== | ==5075==  | ==2021== | ==✅==      |
| \*FARSEEING  | +2000         | > 65 años                                              | +300 reales | ☠         | 2016     | ☠          |
**\* Sobre FARSEEING**
* Es sólo con acceso restringido, difícil de conseguir, pero sería clave para marcar la diferencia y validar el modelo.
* El gran valor de FARSEEING es que contiene caídas reales de adultos mayores monitoreadas por sensores portátiles en el mundo real.

## Sobre el Sensor (del centro de masa)

| Dataset          | Posición  | Orientación                          | Acelerómetro                      | Giroscopio                     | Frecuencia |
| ---------------- | --------- | ------------------------------------ | --------------------------------- | ------------------------------ | ---------- |
| SisFall          | ✅ Cintura | X = right<br>Y = down<br>Z = forward | ±16 g (13 bits)<br>±8 g (14 bits) | ±2000 º/s<br>(16 bits)         | 200 Hz     |
| FallAllD (Waist) | ✅ Cintura | ⚠️                                   | ±8 g (no aclara bits)             | ±2000 º/s (no aclara bits)<br> | ⚠️ 238 Hz  |
| UMAFall (Waist)  | ✅ Cintura | ⚠️                                   | ±8 g (16 bits)                    | 256 º/s (16 bits)              | ☠ 20 Hz    |
| UP-Fall (Waist)  | ✅ Cintura | ⚠️                                   | ⚠️g (solo aclara unidades)        | ⚠️ º/s (solo aclara unidades)  | 100 Hz     |
| KFall            | ⚠️ Lumbar | X = right<br>Y = up<br>Z = backward  | ±16 g (no aclara bits)            | ±2000 º/s (no aclara bits)     | 100 Hz     |

> [!Warning] Sobre MPU6050
> El sensor que ocupamos en nuestro proyecto tiene una resolución de lectura de 16 bits y los rangos de lectura son los siguientes:
> * Acelerómetro: 2 g / 4 g / 8 g / 16 g
> * Giroscopio: 250 / 500 / 1000 / 2000 (°/s)

## Sobre la Orientación del Dispositivo

Cómo no todos los datasets documentan cuál es la convención que usaron para la orientación del los dispositivos, lo mejor es cambiar de estrategia: usaremos **SVM (Signal Vector Magnitude)**.

Usar la **Signal Vector Magnitude (SVM)** para unificar los 3 ejes es una práctica estándar en el análisis de actividad física y detección de caídas.

El **SVM** normaliza la fuerza que se distribuye en los ejes: $\text{SVM} = \sqrt{x^2 + y^2 + z^2}$
Da un solo valor que representa la "fuerza total", independientemente de cómo esté orientado el dispositivo. Esto hace que el modelo sea **generalizable** a múltiples datasets.
**Usamos magnitud vectorial para hacer los datasets agnósticos a la convención de ejes.**

**Para aceleración (*Acceleration Vector Magnitude*):**
$$
\text{AVM} = \sqrt{A_x^2 + A_y^2 + A_z^2}
$$
**Para giroscopio (*Gyroscope Vector Magnitude*):**
$$
\text{GVM} = \sqrt{G_x^2 + G_y^2 + G_z^2}
$$

> [!Danger] **Posición anatómica (lumbar vs. cintura)**
> SVM no lo resuelve; la zona lumbar está más cerca del centro de masa del cuerpo, lo que hace que el pico de impacto en una caída tenga menor amplitud y menos dispersión lateral que en la cintura.

- Incluir ***KFall*** en el entrenamiento, ya que introduce variabilidad posicional controlada.
- Hacer un experimento:
	1. Entrenar con SisFall+FallAllD y hacer test con UP-Fall
	2. Entrenar con SisFall+FallAllD+KFall y hacer test con UP-Fall
	* Demostrar si la fusión ayuda o perjudica.

---


# Data unificada sobre Datasets

## FallAllD

### Data 

* 8,558,480 filas
	* Caídas: 2,218,160
	* Trials: 2346
* Frecuencia: 238 Hz
	* Factores polifásicos: up=25, down=119 
	* →  238 × 25/119 = 50.0000 Hz

**Actividades de la Vida Diaria - ADL (44 tipos):**
* *Actividades cíclicas:* Caminar (lento/rápido), trotar (lento/rápido), subir o bajar escaleras (lento/rápido), aplaudir, agitar las manos, darse la mano.

* *Fases transitorias (inicios y paradas):* Empezar/detenerse al caminar, trotar, aplaudir, agitar las manos, subir y bajar escaleras.

* *Actividades transitorias:* Sentarse (silla alta/baja), levantarse (silla alta/baja), fallar al intentar levantarse de una silla/sofá, acostarse en la cama, cambiar de posición en la cama, levantarse de la cama, tropezar sin caer, saltar (leve/fuerte), agacharse para recoger algo del suelo y levantarse, aplaudir una vez, levantar la mano, bajar la mano, subir y bajar la mano de inmediato, golpear una mesa con la mano.

* *Otras ADL:* Usar el ascensor (empezar/detenerse al subir o bajar), y usar transporte público (estar de pie o sentado en un autobús/metro en movimiento).

**Tipos de Caídas (35 escenarios en total):** Este conjunto abarca múltiples combinaciones que varían según la postura inicial, motivo de la caída, dirección, si hay o no rotación y si hay o no recuperación (ponerse de pie tras caer). Las caídas incluyen:

* Caminar y tropezar hacia adelante (con/sin recuperación).

* Caminar y resbalar hacia adelante o hacia atrás (con/sin recuperación, con/sin rotación).

* Caminar y sufrir un síncope/desmayo hacia atrás, lateral, o hacia adelante (este último con el gesto de protección de poner las manos en una mesa).

* Intentar sentarse/acostarse y perder el equilibrio hacia adelante, atrás o lateral (con/sin recuperación).

* Trotar y tropezar hacia adelante (con/sin recuperación).

* Trotar y resbalar hacia adelante (con/sin recuperación, con/sin rotación).

* Estar acostado en la cama y cambiar de posición/rotar provocando una caída lateral (con/sin recuperación).

* Estar sentado en una silla y sufrir un síncope/desmayo hacia adelante, atrás o lateral.

* Estar de pie y sufrir un síncope/desmayo hacia adelante, atrás, lateral o de forma vertical (deslizándose lentamente por una pared como protección).

### Rendimiento

  Procesando 466 trials (Fall)…

============================================================
  FallAllD  |  238 Hz  →  50 Hz
============================================================

  Sensor: ACC
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       14.675   14.297   23.998   32.382
  Pearson r               0.824    0.903    0.988    0.997
  DTW normalizado         0.027    0.024    0.050    0.090
  Phase shift (ms)        3.621    0.000    0.000  900.000
  Aten. pico filtrado (%)    6.181    4.653   16.102   54.407

  Sensor: GYRO
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       14.945   15.207   25.271   31.059
  Pearson r               0.872    0.959    0.996    0.999
  DTW normalizado         0.019    0.016    0.045    0.095
  Phase shift (ms)       65.877   10.084  420.798  988.403
  Aten. pico filtrado (%)    5.745    3.399   16.344   73.956

## KFall

### Data 

* 3,995,100 filas
	* Caídas: 1,725,407
	* Trials: 2346
* Frecuencia: 100 Hz

**Tipos de Caídas (15 tipos):**

1. F01: Caída hacia adelante al intentar sentarse.

2. F02: Caída hacia atrás al intentar sentarse.

3. F03: Caída lateral al intentar sentarse.

4. F04: Caída hacia adelante al intentar levantarse.

5. F05: Caída lateral al intentar levantarse.

6. F06: Caída hacia adelante mientras se está sentado, causada por desmayo.

7. F07: Caída lateral mientras se está sentado, causada por desmayo.

8. F08: Caída hacia atrás mientras se está sentado, causada por desmayo.

9. F09: Caída vertical (hacia adelante) al caminar, causada por desmayo.

10. F10: Caída al caminar usando las manos para amortiguar, causada por desmayo.

11. F11: Caída hacia adelante al caminar provocada por un tropiezo.

12. F12: Caída hacia adelante al trotar provocada por un tropiezo.

13. F13: Caída hacia adelante al caminar provocada por un resbalón.

14. F14: Caída lateral al caminar provocada por un resbalón.

15. F15: Caída hacia atrás al caminar provocada por un resbalón.

**Actividades de la Vida Diaria - ADL (21 tipos):**

1. D01: Estar de pie durante 30 segundos.

2. D02: Estar de pie, doblar la espalda lentamente (con o sin doblar las rodillas), atarse el zapato y levantarse.

3. D03: Recoger un objeto del suelo.

4. D04: Saltar suavemente (intentando alcanzar un objeto).

5. D05: Estar de pie, sentarse en el suelo, esperar un momento y levantarse a velocidad normal.

6. D06: Caminar normalmente con un giro de 4 metros.

7. D07: Caminar rápido con un giro de 4 metros.

8. D08: Trotar normalmente con un giro de 4 metros.

9. D09: Trotar rápido con un giro de 4 metros.

10. D10: Tropezar mientras se camina.

11. D11: Sentarse en una silla durante 30 segundos.

12. D12: Sentarse en un sofá (con la espalda apoyada) durante 30 segundos.

13. D13: Sentarse en una silla y levantarse a velocidad normal.

14. D14: Sentarse en una silla y levantarse rápidamente.

15. D15: Sentarse un momento, intentar levantarse y colapsar de vuelta en la silla.

16. D16: Estar de pie, sentarse en el sofá (con la espalda apoyada) y levantarse normalmente.

17. D17: Acostarse en la cama durante 30 segundos.

18. D18: Sentarse un momento, acostarse en la cama normalmente y levantarse a velocidad normal.

19. D19: Sentarse un momento, acostarse en la cama rápidamente y levantarse rápidamente.

20. D20: Subir y bajar escaleras a velocidad normal (cinco escalones).

21. D21: Subir y bajar escaleras rápidamente (cinco escalones).

### Rendimiento

  Procesando 2346 trials (Fall)…

============================================================
  KFall  |  100 Hz  →  50 Hz
============================================================

  Sensor: ACC
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       19.052   20.855   25.394   31.328
  Pearson r               0.944    0.986    0.993    0.997
  DTW normalizado         0.016    0.008    0.034    0.051
  Phase shift (ms)        0.009    0.000    0.000   10.000
  Aten. pico filtrado (%)    4.617    4.216    9.484   18.456

  Sensor: GYRO
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       19.496   20.560   28.043   32.283
  Pearson r               0.958    0.991    0.998    0.999
  DTW normalizado         0.011    0.005    0.033    0.117
  Phase shift (ms)       22.903   10.000   80.000  720.000
  Aten. pico filtrado (%)    5.795    3.890   16.906   30.986

## SisFall

### Data

* 15,858,929 filas
	* Caídas: 5,393,714
	* Trials: 1798
* Frecuencia: 200 Hz

#### Tipos de Caídas Contempladas

| Code |                                                                                          Activity                                                                                           | Trials | Duration |
| :--: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :----: | :------: |
| F01  |                                        **Fall forward while walking caused by a slip**<br>(*Caída hacia delante al caminar causada por un resbalón*)                                        |   5    |   15 s   |
| F02  |                                        **Fall backward while walking caused by a slip**<br>(*Caída hacia atrás al caminar causada por un resbalón*)                                         |   5    |   15 s   |
| F03  |                                           **Lateral fall while walking caused by a slip**<br>(*Caída lateral al caminar causada por un resbalón*)                                           |   5    |   15 s   |
| F04  |                                        **Fall forward while walking caused by a trip**<br>(*Caída hacia delante al caminar causada por un tropezón*)                                        |   5    |   15 s   |
| F05  |                                        **Fall forward while jogging caused by a trip**<br>(*Caída hacia delante al trotar causada por un tropezón*)                                         |   5    |   15 s   |
| F06  |                                         **Vertical fall while walking caused by fainting**<br>(*Caída vertical al caminar causada por un desmayo*)                                          |   5    |   15 s   |
| F07  | **Fall while walking, with use of hands in a table to dampen fall, caused by fainting**<br>(*Caída al caminar, con apoyo de las manos en una mesa para amortiguar, causada por un desmayo*) |   5    |   15 s   |
| F08  |                                                  **Fall forward when trying to get up**<br>(*Caída hacia delante al intentar levantarse*)                                                   |   5    |   15 s   |
| F09  |                                                     **Lateral fall when trying to get up**<br>(*Caída lateral al intentar levantarse*)                                                      |   5    |   15 s   |
| F10  |                                                  **Fall forward when trying to sit down**<br>(*Caída hacia delante al intentar sentarse*)                                                   |   5    |   15 s   |
| F11  |                                                   **Fall backward when trying to sit down**<br>(*Caída hacia atrás al intentar sentarse*)                                                   |   5    |   15 s   |
| F12  |                                                     **Lateral fall when trying to sit down**<br>(*Caída lateral al intentar sentarse*)                                                      |   5    |   15 s   |
| F13  |               **Fall forward while sitting, caused by fainting or falling asleep**<br>(*Caída hacia delante estando sentado, causada por un desmayo o por quedarse dormido*)                |   5    |   15 s   |
| F14  |                **Fall backward while sitting, caused by fainting or falling asleep**<br>(*Caída hacia atrás estando sentado, causada por un desmayo o por quedarse dormido*)                |   5    |   15 s   |
| F15  |                  **Lateral fall while sitting, caused by fainting or falling asleep**<br>(*Caída lateral estando sentado, causada por un desmayo o por quedarse dormido*)                   |   5    |   15 s   |

> [!Tip] Un total de 1798 caídas registradas

#### Actividades de la Vida Diaria Contempladas (AVD o ADL)
*Activities of Daily Living

| Code |                                                                                                     Activity                                                                                                     | Trials | Duration |
| :--: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :----: | :------: |
| D01  |                                                                                    **Walking slowly**<br>(*Caminar despacio*)                                                                                    |   1    |  100 s   |
| D02  |                                                                                    **Walking quickly**<br>(*Caminar rápido*)                                                                                     |   1    |  100 s   |
| D03  |                                                                                    **Jogging slowly**<br>(*Trotar despacio*)                                                                                     |   1    |  100 s   |
| D04  |                                                                                     **Jogging quickly**<br>(*Trotar rápido*)                                                                                     |   1    |  100 s   |
| D05  |                                                                **Walking upstairs and downstairs slowly**<br>(*Subir y bajar escaleras despacio*)                                                                |   5    |   25 s   |
| D06  |                                                                **Walking upstairs and downstairs quickly**<br>(*Subir y bajar escaleras rápido*)                                                                 |   5    |   25 s   |
| D07  |                     **Slowly sit in a half height chair, wait a moment, and up slowly**<br>(*Sentarse lentamente en una silla de media altura, esperar un momento y levantarse lentamente*)                      |   5    |   12 s   |
| D08  |                   **Quickly sit in a half height chair, wait a moment, and up quickly**<br>(*Sentarse rápidamente en una silla de media altura, esperar un momento y levantarse rápidamente*)                    |   5    |   12 s   |
| D09  |                      **Slowly sit in a low height chair, wait a moment, and up slowly**<br>(*Sentarse lentamente en una silla de baja altura, esperar un momento y levantarse lentamente*)                       |   5    |   12 s   |
| D10  |                    **Quickly sit in a low height chair, wait a moment, and up quickly**<br>(*Sentarse rápidamente en una silla de baja altura, esperar un momento y levantarse rápidamente*)                     |   5    |   12 s   |
| D11  |                                 **Sitting a moment, trying to get up, and collapse into a chair**<br>(*Estar sentado un momento, intentar levantarse y desplomarse en la silla*)                                 |   5    |   12 s   |
| D12  |                         **Sitting a moment, lying slowly, wait a moment, and sit again**<br>(*Estar sentado un momento, recostarse lentamente, esperar un momento y volver a sentarse*)                          |   5    |   12 s   |
| D13  |                        **Sitting a moment, lying quickly, wait a moment, and sit again**<br>(*Estar sentado un momento, recostarse rápidamente, esperar un momento y volver a sentarse*)                         |   5    |   12 s   |
| D14  | **Being on one’s back change to lateral position, wait a moment, and change to one’s back**<br>(*Estar tumbado boca arriba, cambiar a una posición lateral, esperar un momento y volver a tumbarse boca arriba*) |   5    |   12 s   |
| D15  |                                         **Standing, slowly bending at knees, and getting up**<br>(*Estar parado, doblar lentamente las rodillas y volver a levantarse*)                                          |   5    |   12 s   |
| D16  |                           **Standing, slowly bending without bending knees, and getting up**<br>(*Estar parado, inclinarse lentamente sin doblar las rodillas y volver a levantarse*)                            |   5    |   12 s   |
| D17  |                                 **Standing, get into a car, remain seated and get out of the car**<br>(*Estar parado, subir a un auto, mantenerse sentado y bajarse del coche*)                                  |   5    |   25 s   |
| D18  |                                                                               **Stumble while walking**<br>(*Tropezón al caminar*)                                                                               |   5    |   12 s   |
| D19  |                                     **Gently jump without falling (trying to reach a high object)**<br>(*Saltar suavemente sin caerse (intentando alcanzar un objeto alto)*)                                     |   5    |   12 s   |

> [!Tip] Un total de 2706 ADL registradas

### Rendimiento

  Procesando 1798 trials (Fall)…

============================================================
  SisFall  |  200 Hz  →  50 Hz
============================================================

  Sensor: ACC
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       16.236   16.054   27.194   38.630
  Pearson r               0.901    0.952    0.995    0.998
  DTW normalizado         0.021    0.020    0.042    0.078
  Phase shift (ms)        0.150    0.000    0.000  270.000
  Aten. pico filtrado (%)    6.378    5.423   14.713  102.556

  Sensor: GYRO
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       19.262   19.228   29.804   36.159
  Pearson r               0.951    0.986    0.999    1.000
  DTW normalizado         0.012    0.010    0.027    0.122
  Phase shift (ms)       24.650   10.000   90.000  995.000
  Aten. pico filtrado (%)    4.397    3.032   12.186  353.333

## UMAFall

### Data 

* 184,100 filas
	* Caídas: 56,428
	* Trials: 180
* Frecuencia: 20 Hz
	* Factores de upsampling: up=5, down=2 
	* → 20 × 5/2 = 50.0 Hz

**Tipos de Caídas (3 tipos):** Todas las caídas parten de una postura inicial de pie (erguida) e incluyen:

1. Caída hacia atrás.

2. Caída hacia adelante.

3. Caída lateral.

**Actividades de la Vida Diaria - ADL (8 tipos):**

1. Doblar el cuerpo / Agacharse (hacer sentadillas).

2. Bajar escaleras.

3. Subir escaleras.

4. Saltar (hopping).

5. Trote ligero.

6. Acostarse (y levantarse) de una cama.

7. Sentarse (y levantarse) de una silla.

8. Caminar a un paso normal.

### Rendimiento

  Procesando 180 trials (Fall)…

============================================================
  UMAFall  |  20 Hz  →  50 Hz
============================================================

  Sensor: ACC
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       15.046   13.726   25.188   28.736
  Pearson r               0.881    0.921    0.994    0.997
  DTW normalizado         0.018    0.016    0.032    0.065
  Phase shift (ms)        0.000    0.000    0.000    0.000
  Aten. pico filtrado (%)    7.739    5.996   18.560   34.163

  Sensor: GYRO
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       17.043   16.745   26.627   32.031
  Pearson r               0.944    0.975    0.998    0.999
  DTW normalizado         0.009    0.007    0.021    0.120
  Phase shift (ms)       42.000   20.000  200.000 1030.000
  Aten. pico filtrado (%)    4.071    2.870   14.077   20.098

## UP-Fall

### Data 

* 294,678 filas
	* Caídas: 45,951
	* Trials: 255
* Frecuencia: 100 Hz

**Tipos de Caídas (5 tipos):**

1. Caída hacia adelante usando las manos para amortiguar.

2. Caída hacia adelante usando las rodillas.

3. Caída hacia atrás.

4. Caída lateral.

5. Caída al intentar sentarse en una silla vacía.

**Actividades de la Vida Diaria - ADL (6 tipos):**

1. Caminar.

2. Estar de pie.

3. Sentarse.

4. Recoger un objeto.

5. Saltar.

6. Estar acostado.

### Rendimiento

  Procesando 255 trials (Fall)…

============================================================
  UPFall  |  100 Hz  →  50 Hz
============================================================

  Sensor: ACC
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       20.880   20.789   25.437   29.650
  Pearson r               0.929    0.956    0.979    0.989
  DTW normalizado         0.009    0.008    0.018    0.063
  Phase shift (ms)        7.765   10.000   20.000  130.000
  Aten. pico filtrado (%)    9.441    8.938   19.550   25.169

  Sensor: GYRO
  Métrica                 Media      P50      P95      Máx
  --------------------------------------------------------
  SNR in-band (dB)       17.652   17.781   23.232   25.719
  Pearson r               0.983    0.989    0.997    0.998
  DTW normalizado         0.001    0.000    0.001    0.052
  Phase shift (ms)       12.745   10.000   50.000  230.000
  Aten. pico filtrado (%)    6.827    6.589   16.575   29.637
