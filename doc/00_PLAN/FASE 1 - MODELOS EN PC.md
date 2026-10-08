# FASE 1 - MODELOS EN PC

> **Estado:** ✅ Módulo A (caídas) completado; ✅ Módulo B (ECG) completado con pipeline oficial PTB-XL Lead II 250 Hz binario + TinyECGNet Sequential (Keras Acc 0.7894 / INT8 Acc 0.7960 en TEST n=2113); ⏸️ Módulo C (SpO2): **C1 ejecutado 18-sep-2026** (commit `5ee0d6b`) — pipeline PPG + FC/calidad sobre BIDMC, sin modelo SpO2; resultados en [preprocesamiento-ppg](../04_PIPELINE/preprocesamiento-ppg.md); **C2 bloqueado** sin Rojo/IR ni ground truth independiente. Ver [tablero de avance](../README.md#tablero-de-avance). Experimento opcional: corrida 500 Hz contra resultados 250 Hz.

- **Condiciones:** Sin hardware adicional - todo en Python puro.

- **Objetivo: Validar los modelos en la computadora.** El objetivo de esta fase es que, antes de tocar un sensor físico, ya tengas los tres modelos funcionando y entendidos. Se trabaja con datasets públicos que simulan exactamente los datos que después van a venir de los sensores reales.

- **Tareas:**
  - **Módulo A - [Detección de Caídas (MPU6050)](../01_CONCEPTOS/Prototipo/Detecci%C3%B3n%20de%20Ca%C3%ADdas%20%28MPU6050%29.md):**
    - Descargar el dataset ‘SisFall’ (38 participantes, 19 actividades diarias + 15 tipos de caída, acelerómetro a 200 Hz) para Detección de Caídas.
    - Desarrollar un pipeline de ETL, y aplicar técnicas de escalado y segmentación para preparar las señales de acelerometría.
    - Entrenar una red CNN-LSTM simple en Keras para detectar caídas usando los datos de aceleración en los ejes X, Y y Z.
    - Evaluar los modelos utilizando métricas de precisión, recall y F1-score.
    - Punto de partida: Repositorio de referencia 1saifj/Fall-Detection-System-SisFall-Dataset-Raspberry-Pi (>96% precisión con TFLite).
  - **Módulo B - [ECG y Arritmias (AD8232)](../01_CONCEPTOS/Prototipo/ECG%20y%20Arritmias%20%28AD8232%29.md):** ✅ pipeline oficial PTB-XL Lead II 250 Hz binario (ver [Plan_Implementacion_Módulo_B](Plan_Implementacion_Módulo_B.md))
    - Dataset PTB-XL 1.0.3 desde PhysioNet: 20 970 ECG (Lead II, 500 Hz → 250 Hz vía `resample`, 10 s / 2500 muestras), etiqueta NORMAL/ANORMAL, particiones TRAIN 16 761 / VAL 2 096 / TEST 2 113 sin solape de pacientes.
    - Preprocesamiento M2: pasa-banda 0.5-40 Hz + notch 50 Hz y z-score por ECG; augment de entrenamiento (ganancia, ruido, shift).
    - Modelo TinyECGNet Sequential (SeparableConv1D, 2 673 parámetros): Keras Acc 0.7894 / F1 0.7967; INT8 Acc 0.7960 / F1 0.8051 en TEST.
    - Entregables: `.keras` 115.76 KB, TFLite FP32 20.48 KB, TFLite INT8 18.15 KB + headers C verificados.
  - **Módulo C - [SpO2 y Oximetría (MAX30102)](../01_CONCEPTOS/Prototipo/SpO2%20y%20Oximetr%C3%ADa%20%28MAX30102%29.md):**
    - Instalar las dependencias pyPPG y NeuroKit2 en el entorno de desarrollo.
    - Cargar el dataset ‘BIDMC’ para SpO2 y Oximetría desde PhysioNet (53 grabaciones ICU con etiquetas SpO2).
    - Procesar las señales PPG existentes para validar el flujo de oximetría y entender qué genera el MAX30102 en código real.
    - Nota: En esta fase no se entrena un modelo propio, se valida el pipeline de procesamiento de señal.

  > [!NOTE]
  > **_Para citar el software:_**
  > **_pyPPG:_** Goda, M. A., Charlton, P. H., & Behar, J. A. (2023). pyPPG: A Python toolbox for comprehensive photoplethysmography signal analysis. DOI 10.1088/1361-6579/ad33a2, https://iopscience.iop.org/article/10.1088/1361-6579/ad33a2
  > **_NeuroKit2:_** Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lespinasse, F., Pham, H., Schölzel, C., & Chen, S. A. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. Behavior Research Methods, 53(4), 1689–1696. https://doi.org/10.3758/s13428-020-01516-y
  > **_WFDB:_** Xie, C., McCullum, L., Johnson, A., Pollard, T., Gow, B., & Moody, B. (2023). Waveform Database Software Package (WFDB) for Python (version 4.1.0). *PhysioNet*. RRID:SCR_007345. [https://doi.org/10.13026/9njx-6322](https://doi.org/10.13026/9njx-6322)

- **Duración:** 40 hs (2-3 semanas).

- **Resultados Esperados (Entregable):** Tres modelos entrenados y guardados en formato keras o .h5, listos para conversión.
