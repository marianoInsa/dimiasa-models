Fecha: 01-12-2025

- Paper: https://www.sciencedirect.com/science/article/pii/S1877050917312899?via%3Dihub
- Paper (por si el otro no carga): https://www.researchgate.net/publication/318385531_UMAFall_A_Multisensor_Dataset_for_the_Research_on_Automatic_Fall_Detection
- Dataset: https://figshare.com/articles/dataset/UMA_ADL_FALL_Dataset_zip/4214283

---

##### Descartado

| Dataset     | Motivo                                                                                                                                                                                                    |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **UMAFall** | Solo 3 tipos de caída (todos desde posición de pie), 180 trials, único caso de upsampling (20→50 Hz, 60% muestras interpoladas). No aporta diversidad que no cubran los otros datasets con mayor calidad. |

---

# Data 

* 184,100 filas
	* Caídas: 56,428
	* Trials: 180
* Frecuencia: 20 Hz
	* Factores de upsampling: up=5, down=2 
	* → 20 × 5/2 = 50.0 Hz
# Rendimiento

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

---

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