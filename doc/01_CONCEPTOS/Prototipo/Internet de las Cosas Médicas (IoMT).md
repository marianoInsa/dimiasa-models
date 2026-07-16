---
tags:
  - IoMT
---
## Internet de las Cosas Médicas (IoMT) y Arquitecturas de Tres Capas

>[!info] Fase del Plan de Trabajo
>[[FASE 1 - MODELOS EN PC]], [[FASE 2 - CONVERSIÓN LiteRT]], [[FASE 3 - SENSORES FÍSICOS]], [[FASE 4 - SISTEMA MULTIAGENTE]] y [[FASE 5 - VALIDACIÓN EXPERIMENTAL]]

El Internet de las Cosas Médicas (IoMT) es un ecosistema compuesto por dispositivos, sensores y aplicaciones interconectadas que tienen la capacidad de generar, analizar y transmitir datos biológicos en tiempo real. A nivel técnico, este proyecto estructura el IoMT mediante una arquitectura de tres capas: la [[Capa de Percepción]] (adquisición de datos mediante sensores como el AD8232 o el MAX30102), la [[Capa de Red]] (transmisión híbrida vía WiFi y LoRaWAN) y la [[Capa de Aplicación]] (almacenamiento y analítica avanzada en la nube).

![[diagrama de arquitectura iomt.png]]

A diferencia de los modelos centralizados tradicionales que envían un flujo continuo de datos crudos a la nube, la evolución del IoMT requiere procesar la información de forma local para evitar cuellos de botella. Esto permite el monitoreo continuo de parámetros críticos como la oxigenación en sangre, la presión arterial y la actividad cardíaca, posibilitando que el sistema sea escalable y reduzca la carga sobre las infraestructuras hospitalarias mediante la internación domiciliaria.

![[diagrama de flujo iot.png]]