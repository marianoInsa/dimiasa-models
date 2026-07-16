
- Paper online: https://ieeexplore.ieee.org/document/9171857
- Descarga: https://ieee-dataport.org/open-access/fallalld-comprehensive-dataset-human-falls-and-activities-daily-living
- Descarga en kaggle: https://www.kaggle.com/datasets/sankalpsinghvishen/derived-fallalld-dataset

---

## Data 

* 8,558,480 filas
	* Caídas: 2,218,160
	* Trials: 2346
* Frecuencia: 238 Hz
	* Factores polifásicos: up=25, down=119 
	* →  238 × 25/119 = 50.0000 Hz

## Rendimiento

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

---
# Resumen

Este dataset esta diseñado para superar las limitaciones de los datasets anteriores en cuanto a frecuencia de muestreo, rango de medición y variedad de posiciones de los sensores.

Consta de **26.420 archivos** correspondientes a **35 tipos de caídas** y **44 Actividades de la Vida Diaria (AVD)** realizadas por **15 participantes**:
- 8 hombres
- 7 mujeres

**Validación:** Validado en el paper original obteniendo diferencias significativas de rendimiento frente a otros datasets debido a su alta frecuencia de muestreo y amplio rango dinámico, lo cual previene el recorte (clipping) de la señal durante impactos fuertes.

> [!Warning] Limitaciones
> - **Simulación en población sana:** A pesar de ser muy completo, los datos fueron recolectados en 15 adultos jóvenes y sanos (edad promedio: 32 años) que _simularon_ caídas. Las caídas reales en adultos mayores pueden presentar una dinámica de aceleración y posturas previas distintas a la de los simulacros.
> - **Entorno simulado (Outdoors):** Se indica que las caídas fueron simuladas al aire libre (sobre pasto/césped suave en lugar de colchonetas de laboratorio), lo cual le da un toque de realismo, pero la anticipación natural a la caída por parte del usuario sigue presente.
> - **Representatividad de anomalías patológicas:** No incluye datos de pacientes con marcha inestable, trastornos neurológicos (ej. Parkinson) o caídas por síncopes/desmayos reales.

> [! Danger] Si usas KAGGLE
> - La versión de Kaggle (`FallAllD_40SamplesPerSec_ActivityIdsFiltered.pkl`) elimina los datos del magnetómetro, del barómetro y del sensor ubicado en el cuello, limitando el análisis a solo dos posiciones (cintura y muñeca).
> - La técnica SMOTE fue aplicada en la versión de Kaggle para balancear las clases, lo que introduce datos sintéticos que no corresponden a capturas físicas reales.

## Tipos de Caídas Contempladas

- Incluye **35 tipos de caídas** (considerando dirección, causa —resbalón, tropiezo, síncope—, y recuperación post-caída).
- Caídas hacia adelante, hacia atrás, hacia los lados (lateral derecha/izquierda) y caídas al sentarse.
- **Fases de movimiento:** Incluye caídas con y sin fase de recuperación posterior, lo que ayuda a entrenar modelos clínicos más robustos.

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

## Actividades de la Vida Diaria Contempladas (AVD o ADL)
*Activities of Daily Living

* Inician desde distintas posturas como estar caminando, corriendo, de pie o sentado, y son registradas por tres sensores inerciales ubicados en **cintura, cuello y muñeca**.
* Incluye 12 actividades solo de mano para la muñeca
* Las 44 ADL incluyen actividades transicionales (sentarse, levantarse, acostarse) que generan falsos positivos

**Actividades de la Vida Diaria - ADL (44 tipos):**
* *Actividades cíclicas:* Caminar (lento/rápido), trotar (lento/rápido), subir o bajar escaleras (lento/rápido), aplaudir, agitar las manos, darse la mano.

* *Fases transitorias (inicios y paradas):* Empezar/detenerse al caminar, trotar, aplaudir, agitar las manos, subir y bajar escaleras.

* *Actividades transitorias:* Sentarse (silla alta/baja), levantarse (silla alta/baja), fallar al intentar levantarse de una silla/sofá, acostarse en la cama, cambiar de posición en la cama, levantarse de la cama, tropezar sin caer, saltar (leve/fuerte), agacharse para recoger algo del suelo y levantarse, aplaudir una vez, levantar la mano, bajar la mano, subir y bajar la mano de inmediato, golpear una mesa con la mano.

* *Otras ADL:* Usar el ascensor (empezar/detenerse al subir o bajar), y usar transporte público (estar de pie o sentado en un autobús/metro en movimiento).

> [!Note] Nota
> - El archivo `activity_info.pkl` de Kaggle funciona como un diccionario clave para mapear directamente los IDs de actividad con sus descripciones de texto.
> - En la versión de Kaggle, algunas actividades originales que no se consideraron relevantes para la detección multiclase de caídas fueron filtradas y eliminadas del dataset final.

## Participantes

- **Total de sujetos:** 15 participantes.
- La demografía de la cohorte está compuesta enteramente por individuos sanos (jóvenes y adultos jóvenes) debido a la naturaleza física requerida para simular caídas de forma segura.

|         | **Sexo** | **Edad**     |
| ------- | -------- | ------------ |
| Jóvenes | 8M, 7F   | 21 - 53 años |

## Set-Up del Experimento

- **Hardware:** Tres registradores de datos idénticos desarrollados por la empresa RF-Track.

- **Sensores incluidos:**
	- LSM9DS1: Acelerómetro de 3 ejes, Giroscopio de 3 ejes y Magnetómetro de 3 ejes.
	- MS5607-02BA03: Barómetro.

- **Ubicación de los dispositivos:** Cintura, muñeca y cuello de los sujetos.
> [!Note]
> - La versión reducida de Kaggle eliminó los datos del cuello.

- **Configuraciones de frecuencia y rango (Dataset Original):**
	- Acelerómetro: 238 Hz, rango de +-8 g.
	- Giroscopio: 238 Hz, tasa angular de +-2000 dps.
	- Magnetómetro: 80 Hz, escala completa de +-4 Gauss.
	- Barómetro: 10 Hz.

> [!Danger] Si usas Kaggle
> - La frecuencia de muestreo del acelerómetro y giroscopio fue reducida (downsampling) de 238 Hz a 40 Hz para disminuir el costo computacional.

![[fallalld-ubicacion-dispositivos.jpg]]


> [!Warning] A tener en cuenta
> - El uso de la técnica SMOTE en el dataset derivado de Kaggle resuelve problemas de desbalanceo de clases para el entrenamiento, pero debes tener cuidado al evaluar (testing) el modelo con datos sintéticos; la validación final siempre debe hacerse con muestras físicas reales.
> - Las señales provenientes de la muñeca suelen contener muchísimo más ruido provocado por gestos cotidianos no relacionados con el centro de masa del cuerpo, en contraste con las mediciones más estables de la cintura.

## Datos del Dataset

- **Formato lógico original:** MATLAB struct (.mat) o Pandas dataframe (.h5 o .pkl) conteniendo los campos: `{SubjectID, ActivityID, TrialNo, Device, Acc, Gyr, Mag, Bar}`.

- **Formato derivado (Kaggle):** Pandas dataframe (.pkl) conteniendo únicamente `{SubjectID, ActivityID, TrialNo, Device, Acc, Gyr}`.

- **Conversión de Aceleración:** Para transformar los bits brutos de un acelerómetro estándar de 16 bits (considerando el rango de $\pm 8\text{g}$) a unidades de gravedad $g$, la ecuación general aplicada es:
$$A_{g} = \text{Valor\_Crudo} \times \left( \frac{16}{2^{16}} \right)$$

> [!Warning] FORMATO DE LOS ARCHIVOS
> La nomenclatura y estructura de datos varía según el entorno, pero la convención interna organizativa se basa en los identificadores clave de la estructura de MATLAB/Python.

- **Identificadores principales:**
	- `SubjectID`: Número único del 1 al 15 correspondiente al voluntario.
	- `ActivityID`: Código único que define la actividad (mapeado en `activity_info.pkl`).
	- `TrialNo`: Número del intento de esa misma actividad por el mismo sujeto.
	- `Device`: Posición del sensor (Waist, Wrist, Neck).

**Ejemplo (Kaggle):** 
Al cargar `FallAllD_40SamplesPerSec_ActivityIdsFiltered.pkl`, cada fila representa una serie temporal etiquetada. 
Si filtras por `SubjectID == 5` y `Device == 'Waist'`, obtendrás todos los vectores de tiempo (Acc y Gyr) capturados en la cintura de ese participante específico.
