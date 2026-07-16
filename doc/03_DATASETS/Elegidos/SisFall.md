
- Referencia general: https://github.com/1saifj/Fall-Detection-System-SisFall-Dataset-Raspberry-Pi
* Paper online: https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/
* [[SisFall - A Fall and Movement Dataset|Paper local]]
* Descarga oficial (no anda): http://sistemic.udea.edu.co/investigacion/proyectos/english-falls/?lang=en
* Descarga en Kaggle: https://www.kaggle.com/datasets/nvnikhil0001/sis-fall-original-dataset

---

# Data

* 15,858,929 filas
	* Caídas: 5,393,714
	* Trials: 1798
* Frecuencia: 200 Hz

# Rendimiento

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

---

# Resumen

Consta de **19 actividades de la vida diaria (AVD)** y **15 tipos de caídas**
- 23 adultos jóvenes (19-30 años) realizaron todas las AVD y caídas
- 14 adultos mayores (60-75 años) realizaron 15 tipos de AVD (sin contar las siguientes: D06, D13, D18 y D19) y no realizaron caídas.
- 1 adulto mayor (60 años) realizó todas las AVD y caídas

Cantidad de registros:
* **1798 caídas**
* **2706 AVD**
* **==Total: 4504==**

Este dataset consta de 4504 archivos, ***cada uno de los cuales contiene una sola actividad***.

El paper valida el dataset utilizando detectores clásicos basados en características y umbrales, alcanzando hasta 96.1% de precisión en la detección de caídas.

*La mayoría de los errores se concentran en un número reducido de actividades.*

> [!Warning] Limitaciones
> Todas las caídas están simuladas, esto quiere decir que las caídas no son reales y están amortiguadas, por lo tanto las señales obtenidas son menos violentas que una caída accidental.
> Y el único adulto mayor (*SE06*) que realizó caídas, era experto en Judo. Por lo que no es representativo de la población de adultos mayores.
> Las personas mayores no realizaron las actividades *D06, D13, D18 y D19* por recomendación de un médico especialista en medicina deportiva.
> Además, algunas personas mayores no realizaron ciertas actividades debido a limitaciones personales (o por recomendación médica).

le tira beef a:
- MobiFall*
- tFall*
- DLR
- Project Gravity
\*estos estan en las investigaciones
Comparados con esos, SisFall ofrece mayor cantidad de participantes, actividades y registros.


## Tipos de Caídas Contempladas

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

## Actividades de la Vida Diaria Contempladas (AVD o ADL)
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

## Participantes

**38 voluntarios:** 
* 15 adultos mayores (8 hombres y 7 mujeres)
* 23 adultos jóvenes (11 hombres y 12 mujeres)

|         | Sex    | Age   | Height (m) | Weight (kg) |
| ------- | ------ | ----- | ---------- | ----------- |
| Elderly | Female | 62–75 | 1.50–1.69  | 50–72       |
| Elderly | Male   | 60–71 | 1.63–1.71  | 56–102      |
| Adult   | Female | 19–30 | 1.49–1.69  | 42–63       |
| Adult   | Male   | 19–30 | 1.65–1.83  | 58–81       |
> [!Note] Nota
> > [!Check] Adultos Jóvenes
> > * Realizaron todas las caídas y ADLs
> 
> >[!Danger] Adultos Mayores
> > * No realizaron las caídas, ni tampoco las actividades D06, D13, D18 y D19
> > * Un sólo participante (***SE06***) (*experto en Judo*), realizó todas las caídas y ADLs

## Set-Up del Experimento

Los datos se registraron con **tres sensores (2 acelerómetros y 1 giroscopio)** a una **frecuencia de muestreo de 200 Hz**. Desarrollaron un dispositivo ellos mismos:
* Microcontrolador (Kinets MKL25Z128VLK4)
* Acelerómetro (ADXL345) configurado para ±16 g y convertidor ADC de 13 bits
* Acelerómetro (MMA8451Q) configurado para ±8 g y convertidor ADC de 14 bits
* Giroscopio (ITG3200) configurado para ±2000∘/s y convertidor ADC de 16 bits.

El dispositivo se fijó en la **cintura** de los participantes:
* Justificación: Esta ubicación proporciona alta distinción entre actividades para un sistema de acelerómetro único.

![[sisfall-ubicacion-dispositivo.jpg]]

*Para su estudio, sólo usaron los datos obtenidos recibidos por el sensor **Acelerómetro (ADXL345)**, pero los datos de este y de los otros dos sensores estan disponibles en el dataset*.

*La orientación del sensor:*
* **eje z positivo** en dirección hacia delante
* **eje y positivo** en la dirección de la gravedad
* **eje x positivo** en dirección hacia el lado derecho del participante

*Frecuencia de muestreo: **200 Hz***
*  Demostraron que un filtro de cuarto orden a 5 Hz conserva información suficiente para detectar caídas en personas mayores autónomas.
> [!Important] Para el caso: MPU6050 y ESP32
> * Normalmente se usa 25 Hz, 50 Hz o hasta 100 Hz
> * Será necesario realizar *downsampling* para aproximar el comportamiento real

> [!Warning] A tener en cuenta
> * Las señales de los adultos mayores tienen menor amplitud que las de los adultos jóvenes.
> * Los adultos mayores generan aceleraciones menores en ADLs y caídas respecto a los jóvenes.
> * Si se entrena sólo con jóvenes:
> 	* los umbrales quedan altos
> 	* disminuye la sensibilidad

## Datos del Dataset

Cada archivo contiene nueve columnas y un número variable de filas, dependiendo de la duración de la prueba.

**Acelerómetro 1 (ADXL345):**
- 1ra columna contiene los datos de aceleración en el eje X.
- 2da columna contiene los datos de aceleración en el eje Y.
- 3ra columna contiene los datos de aceleración en el eje Z.

**Giroscopio (ITG3200):**
- 4ta columna contiene los datos de rotación en el eje X.
- 5ta columna contiene los datos de rotación en el eje Y.
- 6ta columna contiene los datos de rotación en el eje Z.

**Acelerómetro 2 (MMA8451Q):**
* 7ma columna contiene los datos de aceleración en el eje X.
* 8va columna contiene los datos de aceleración en el eje Y.
* 9na columna contiene los datos de aceleración en el eje Z.

==**Total: 9 canales**==

Los datos se expresan en bits y presentan las siguientes características:

ADXL345:
* Resolución: 13 bits
* Rango: ±16 g

ITG3200:
* Resolución: 16 bits
* Rango: ±2000 º/s

MMA8451Q:
* Resolución: 14 bits
* Rango: ±8 g

> [!Tip]
> Para convertir los datos de aceleración (AD), expresados en bits, en gravedad, utilice esta ecuación:
> * Aceleración (g) = [(2*{Rango}) / (2^{Resolución})] * Aceleración (bits)
> 
> Para convertir los datos de rotación (RD), expresados en bits, en velocidad angular, utilice esta ecuación:
> * Velocidad angular (º/s) = [(2*Rango) / (2^Resolución)] * Velocidad angular (bits)

> [!Warning] FORMATO DE LOS ARCHIVOS
> File name format:
> `<ADL OR FALL_CODE>_<SUBJECT_ID>_<TRIAL_NO>.txt`

Participantes:
* El `SUBJECT_ID` depende de la edad de los participantes. 
* ***SA***: Participantes adultos de entre 19 y 30 años
* ***SE***: Personas mayores de entre 60 y 75 años

| **Subject** | **Age** | **Height** | **Weight** | **Gender** |
| ----------- | ------- | ---------- | ---------- | ---------- |
| SA01        | 26      | 165        | 53         | F          |
| SA02        | 23      | 176        | 58.5       | M          |
| SA03        | 19      | 156        | 48         | F          |
| SA04        | 23      | 170        | 72         | M          |
| SA05        | 22      | 172        | 69.5       | M          |
| SA06        | 21      | 169        | 58         | M          |
| SA07        | 21      | 156        | 63         | F          |
| SA08        | 21      | 149        | 41.5       | F          |
| SA09        | 24      | 165        | 64         | M          |
| SA10        | 21      | 177        | 67         | M          |
| SA11        | 19      | 170        | 80.5       | M          |
| SA12        | 25      | 153        | 47         | F          |
| SA13        | 22      | 157        | 55         | F          |
| SA14        | 27      | 160        | 46         | F          |
| SA15        | 25      | 160        | 52         | F          |
| SA16        | 20      | 169        | 61         | F          |
| SA17        | 23      | 182        | 75         | M          |
| SA18        | 23      | 181        | 73         | M          |
| SA19        | 30      | 170        | 76         | M          |
| SA20        | 30      | 150        | 42         | F          |
| SA21        | 30      | 183        | 68         | M          |
| SA22        | 19      | 158        | 50.5       | F          |
| SA23        | 24      | 156        | 48         | F          |
| SE01        | 71      | 171        | 102        | M          |
| SE02        | 75      | 150        | 57         | F          |
| SE03        | 62      | 150        | 51         | F          |
| SE04        | 63      | 160        | 59         | F          |
| SE05        | 63      | 165        | 72         | M          |
| SE06        | 60      | 163        | 79         | M          |
| SE07        | 65      | 168        | 76         | M          |
| SE08        | 68      | 163        | 72         | F          |
| SE09        | 66      | 167        | 65         | M          |
| SE10        | 64      | 156        | 66         | F          |
| SE11        | 66      | 169        | 63         | F          |
| SE12        | 69      | 164        | 56.5       | M          |
| SE13        | 65      | 171        | 72.5       | M          |
| SE14        | 67      | 163        | 58         | M          |
| SE15        | 64      | 150        | 50         | F          |
* Height en *cm* and Weight en *kg*.

**Ejemplos:**

`F05_SA01_R04.txt`
* **F05**: Caída (Caída hacia delante mientras se trota, causada por un tropezón)
* **SA01**: Sujeto adulto 01.
* **R04**: Prueba 04

`D17_SE04_R02.txt`
* **D17**: AVD (Ponerse de pie, subir al coche, permanecer sentado y salir del coche)
* **SE04**: Persona mayor 04
* **R02**: Prueba 02
