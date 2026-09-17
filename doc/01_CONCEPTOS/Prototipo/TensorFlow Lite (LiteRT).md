---
tags:
  - ML
---
## **TensorFlow Lite (LiteRT)**

>[!info] Fase del Plan de Trabajo
>[FASE 2 - CONVERSIÓN LiteRT](../../00_PLAN/FASE%202%20-%20CONVERSIÓN%20LiteRT.md)

TensorFlow Lite, en la actualidad evolucionado y renombrado como LiteRT, es el entorno de ejecución oficial de Google diseñado para el despliegue optimizado de modelos de aprendizaje automático e inteligencia artificial generativa de manera local (On-Device). Su tecnología resulta indispensable para portar modelos creados en ordenadores hacia [arquitecturas perimetrales (Edge)](Computación%20en%20el%20Borde%20%28Edge%20Computing%29.md) severamente restringidas, como plataformas IoT o microcontroladores, posibilitando inferencias de baja latencia sin sacrificar la privacidad.

En el desarrollo, esta herramienta toma los modelos previamente entrenados (archivos .h5) y los somete a un proceso de compresión algorítmica post-entrenamiento denominado cuantización (como la cuantización a formato _float16_). Este paso es fundamental para confirmar que la suma de los modelos de arritmias, oximetría y caídas ocupe colectivamente menos de 1 MB de almacenamiento, logrando tiempos de inferencia combinados menores a 300 milisegundos para operar fluida y localmente en equipos como la Raspberry Pi.