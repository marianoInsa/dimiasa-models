- **Condiciones:** Sin hardware adicional - todo en Python puro.

- **Objetivo: Validar los modelos en la computadora.** El objetivo de esta fase es que, antes de tocar un sensor físico, ya tengas los tres modelos funcionando y entendidos. Se trabaja con datasets públicos que simulan exactamente los datos que después van a venir de los sensores reales.

- **Tareas:**
    - **Módulo A - [[Detección de Caídas (MPU6050)]]:**
        - Descargar el dataset ‘SisFall’ (38 participantes, 19 actividades diarias + 15 tipos de caída, acelerómetro a 200 Hz) para Detección de Caídas.
        - Desarrollar un pipeline de ETL, y aplicar técnicas de escalado y segmentación para preparar las señales de acelerometría.
        - Entrenar una red CNN-LSTM simple en Keras para detectar caídas usando los datos de aceleración en los ejes X, Y y Z.
        - Evaluar los modelos utilizando métricas de precisión, recall y F1-score.
        - Punto de partida: Repositorio de referencia 1saifj/Fall-Detection-System-SisFall-Dataset-Raspberry-Pi (>96% precisión con TFLite).
    - **Módulo B - [[ECG y Arritmias (AD8232)]]:**
        - Descargar el dataset ‘MIT-BIH Arrhythmia Database’ para ECG y Arritmias desde PhysioNet.
        - Desarrollar un pipeline de ETL, y aplicar técnicas de escalado y segmentación para preparar las señales de ECG.
        - Aplicar filtros pasa-banda (0.5-40 Hz) y segmentación en ventanas a las señales de ECG.
        - Entrenar un modelo 1D-CNN liviano para la clasificación de arritmias.
        - Usar el repositorio awni/ecg de Stanford como referencia de arquitectura.
        - Meta: Objetivo de tamaño de modelo menor a 1 MB con inferencia menor a 200 ms.
    - **Módulo C - [[SpO2 y Oximetría (MAX30102)]]:**
        - Instalar las dependencias pyPPG y NeuroKit2 en el entorno de desarrollo.
        - Cargar el dataset ‘BIDMC’ para SpO2 y Oximetría desde PhysioNet (53 grabaciones ICU con etiquetas SpO2).
        - Procesar las señales PPG existentes para validar el flujo de oximetría y entender qué genera el MAX30102 en código real.
        - Nota: En esta fase no se entrena un modelo propio, se valida el pipeline de procesamiento de señal.
> [!NOTE]
> ***Para citar el software:***
> ***pyPPG:*** Goda, M. A., Charlton, P. H., & Behar, J. A. (2023). pyPPG: A Python toolbox for comprehensive photoplethysmography signal analysis. DOI 10.1088/1361-6579/ad33a2, https://iopscience.iop.org/article/10.1088/1361-6579/ad33a2
> ***NeuroKit2:*** Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lespinasse, F., Pham, H., Schölzel, C., & Chen, S. A. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. Behavior Research Methods, 53(4), 1689–1696. https://doi.org/10.3758/s13428-020-01516-y
> ***WFDB:*** Xie, C., McCullum, L., Johnson, A., Pollard, T., Gow, B., & Moody, B. (2023). Waveform Database Software Package (WFDB) for Python (version 4.1.0). _PhysioNet_. RRID:SCR_007345. [https://doi.org/10.13026/9njx-6322](https://doi.org/10.13026/9njx-6322)


- **Duración:** 40 hs (2-3 semanas).

- **Resultados Esperados (Entregable):** Tres modelos entrenados y guardados en formato keras o .h5, listos para conversión.