
- Paper online: https://www.frontiersin.org/journals/aging-neuroscience/articles/10.3389/fnagi.2021.692865/full
- [[KFall - A Large-Scale Open Motion Dataset (KFall) and Benchmark Algorithms for Detecting Pre-impact Fall of the Elderly Using Wearable Inertial Sensors|Paper local]]
- Descarga de Dataset: https://sites.google.com/view/kfalldataset (por petición)

---

# Data 

* 3,995,100 filas
	* Caídas: 1,725,407
	* Trials: 2346
* Frecuencia: 100 Hz

# Rendimiento

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

---

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