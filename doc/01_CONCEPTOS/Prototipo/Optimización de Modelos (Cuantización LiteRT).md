---
tags:
  - ML
  - DL
---
## Optimización de Modelos (Cuantización LiteRT)

>[!info] Fase del Plan de Trabajo
>[[FASE 1 - MODELOS EN PC]] y [[FASE 2 - CONVERSIÓN LiteRT]]

El proyecto emplea arquitecturas de Deep Learning, como [[Redes 1D-CNN]] para la clasificación de arritmias y [[Redes CNN-LSTM]] para procesar tanto dinámicas inerciales como signos vitales. En una primera instancia, estos modelos se entrenan en la computadora utilizando datasets biomédicos públicos (como SisFall o MIT-BIH) empleando un entorno de Python puro y bibliotecas como Keras.

Dado que los [[Computación en el Borde (Edge Computing)|dispositivos Edge]] tienen severas restricciones de memoria, energía y capacidad computacional, los modelos deben pasar por un proceso de compresión algorítmica llamado cuantización. A través de herramientas como [[TensorFlow Lite (LiteRT)]], los modelos se convierten y cuantizan (por ejemplo, a formato _float16_) para reducir su peso final a menos de 1 MB, encontrando un equilibrio entre una alta precisión clínica y tiempos de inferencia sumamente bajos.