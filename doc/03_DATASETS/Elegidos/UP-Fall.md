Fecha: 28 April 2019

- Paper online: https://www.mdpi.com/1424-8220/19/9/1988
- [[UP-Fall Detection Dataset A Multimodal Approach|Paper local]]
- Dataset: https://sites.google.com/up.edu.mx/har-up/
- Repo: https://github.com/jpnm561/HAR-UP


---

# Data 

* 294,678 filas
	* Caídas: 45,951
	* Trials: 255
* Frecuencia: 100 Hz

# Rendimiento

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

---

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