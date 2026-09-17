---
tags:
  - ML
  - DL
---
## **Redes 1D-CNN**

>[!info] Fase del Plan de Trabajo
>[FASE 1 - MODELOS EN PC](../../00_PLAN/FASE%201%20-%20MODELOS%20EN%20PC.md) y [FASE 2 - CONVERSIÓN LiteRT](../../00_PLAN/FASE%202%20-%20CONVERSIÓN%20LiteRT.md)

Las Redes Neuronales Convolucionales Unidimensionales (1D-CNN) son arquitecturas de Deep Learning que extraen características espaciales y temporales diseñadas específicamente para el procesamiento secuencial de señales continuas. En este proyecto, se desarrolla un modelo de red 1D-CNN ligero enfocado en el "Módulo B", cuya tarea es analizar las señales analógicas de biopotenciales cardíacos filtradas desde el sensor de [ECG y Arritmias (AD8232)](ECG%20y%20Arritmias%20%28AD8232%29.md) para la clasificación y detección automática de arritmias.

El algoritmo original se entrena en un entorno informático convencional utilizando conjuntos de datos biomédicos públicos validados, como la base de datos de arritmias 'MIT-BIH' proporcionada por PhysioNet. Dado que debe operar en el [borde (Edge)](Computación%20en%20el%20Borde%20%28Edge%20Computing%29.md), la red neuronal se diseña bajo estrictas restricciones para que, una vez finalizada y optimizada, logre un peso final objetivo en memoria cercano a los 90 KB y un tiempo de inferencia ultrarrápido menor a 10 milisegundos.