---
tags:
  - ML
  - DL
---
## Optimización de Modelos (Cuantización LiteRT)

>[!info] Fase del Plan de Trabajo
>[FASE 1 - MODELOS EN PC](../../00_PLAN/FASE%201%20-%20MODELOS%20EN%20PC.md) y [FASE 2 - CONVERSIÓN LiteRT](../../00_PLAN/FASE%202%20-%20CONVERSIÓN%20LiteRT.md)

El proyecto emplea arquitecturas de Deep Learning, como [Redes 1D-CNN](Redes%201D-CNN.md) para la clasificación de arritmias y [Redes CNN-LSTM](Redes%20CNN-LSTM.md) para procesar tanto dinámicas inerciales como signos vitales. En una primera instancia, estos modelos se entrenan en la computadora utilizando datasets biomédicos públicos (como SisFall o MIT-BIH) empleando un entorno de Python puro y bibliotecas como Keras.

Dado que los [dispositivos Edge](Computación%20en%20el%20Borde%20%28Edge%20Computing%29.md) tienen severas restricciones de memoria, energía y capacidad computacional, los modelos deben pasar por un proceso de compresión algorítmica llamado cuantización. A través de herramientas como [TensorFlow Lite (LiteRT)](TensorFlow%20Lite%20%28LiteRT%29.md), los modelos se convierten y cuantizan (por ejemplo, a formato _float16_) para reducir su peso final a menos de 1 MB, encontrando un equilibrio entre una alta precisión clínica y tiempos de inferencia sumamente bajos.