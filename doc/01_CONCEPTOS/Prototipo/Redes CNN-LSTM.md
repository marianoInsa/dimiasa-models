---
tags:
  - ML
  - DL
---
## **Redes CNN-LSTM**

>[!info] Fase del Plan de Trabajo
>[[FASE 1 - MODELOS EN PC]] y [[FASE 2 - CONVERSIÓN LiteRT]]

Las redes CNN-LSTM representan un poderoso marco de aprendizaje profundo multimodal que fusiona la extracción de características espaciales de las Redes Neuronales Convolucionales (CNN) con la capacidad de retención y análisis de dependencias a lo largo del tiempo de las redes de Memoria a Corto y Largo Plazo (LSTM). Esta integración algorítmica es utilizada para evaluar tanto las dinámicas de aceleración inercial como los signos vitales complejos en una única y precisa inferencia.

Dentro del marco de trabajo del proyecto, la arquitectura CNN-LSTM conforma la lógica del "Módulo A" orientado a la detección de caídas, procesando en tiempo real las aceleraciones continuas en los ejes X, Y y Z capturadas mediante el sensor de [[Detección de Caídas (MPU6050)]]. Para su construcción, el modelo se entrena en lenguaje Python puro a través de Keras, usando las múltiples simulaciones de caídas y de actividades diarias que provee el conjunto de datos abierto 'SisFall'.