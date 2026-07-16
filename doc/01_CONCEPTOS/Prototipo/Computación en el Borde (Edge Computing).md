---
tags:
  - arquitectura
---
## Computación en el Borde (Edge / Fog Computing)

>[!info] Fase del Plan de Trabajo
>[[FASE 2 - CONVERSIÓN LiteRT]] y [[FASE 5 - VALIDACIÓN EXPERIMENTAL]]

La Computación en el Borde (Edge Computing) consiste en desplazar la capacidad de procesamiento y toma de decisiones lo más cerca posible de la fuente de los datos (el paciente y sus sensores), en lugar de depender exclusivamente de servidores centralizados. En la arquitectura del proyecto, esto se materializa ejecutando algoritmos directamente sobre microcontroladores como el ESP32 o placas como la Raspberry Pi 4/5.

![[edge computing.png]]

Esta descentralización es crítica para resolver vulnerabilidades graves de los sistemas de monitoreo clásicos: la latencia y la dependencia a la conectividad. Al procesar los datos de manera local, el sistema garantiza un tiempo de respuesta inmediato en caso de emergencias médicas y logra mantener el funcionamiento (resiliencia) de las alarmas clínicas incluso en operaciones fuera de línea o ante la pérdida de señal de red.