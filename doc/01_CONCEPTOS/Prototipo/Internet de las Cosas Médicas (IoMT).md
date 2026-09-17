---
tags:
  - IoMT
---
## Internet de las Cosas Médicas (IoMT) y Arquitecturas de Tres Capas

>[!info] Fase del Plan de Trabajo
>[FASE 1 - MODELOS EN PC](../../00_PLAN/FASE%201%20-%20MODELOS%20EN%20PC.md), [FASE 2 - CONVERSIÓN LiteRT](../../00_PLAN/FASE%202%20-%20CONVERSIÓN%20LiteRT.md), [FASE 3 - SENSORES FÍSICOS](../../00_PLAN/FASE%203%20-%20SENSORES%20FÍSICOS.md), [FASE 4 - SISTEMA MULTIAGENTE](../../00_PLAN/FASE%204%20-%20SISTEMA%20MULTIAGENTE.md) y [FASE 5 - VALIDACIÓN EXPERIMENTAL](../../00_PLAN/FASE%205%20-%20VALIDACIÓN%20EXPERIMENTAL.md)

El Internet de las Cosas Médicas (IoMT) es un ecosistema compuesto por dispositivos, sensores y aplicaciones interconectadas que tienen la capacidad de generar, analizar y transmitir datos biológicos en tiempo real. A nivel técnico, este proyecto estructura el IoMT mediante una arquitectura de tres capas: la [Capa de Percepción](Capa%20de%20Percepción.md) (adquisición de datos mediante sensores como el AD8232 o el MAX30102), la [Capa de Red](Capa%20de%20Red.md) (transmisión híbrida vía WiFi y LoRaWAN) y la [Capa de Aplicación](Capa%20de%20Aplicación.md) (almacenamiento y analítica avanzada en la nube).

![diagrama de arquitectura iomt](../../img/diagrama%20de%20arquitectura%20iomt.png)

A diferencia de los modelos centralizados tradicionales que envían un flujo continuo de datos crudos a la nube, la evolución del IoMT requiere procesar la información de forma local para evitar cuellos de botella. Esto permite el monitoreo continuo de parámetros críticos como la oxigenación en sangre, la presión arterial y la actividad cardíaca, posibilitando que el sistema sea escalable y reduzca la carga sobre las infraestructuras hospitalarias mediante la internación domiciliaria.

![diagrama de flujo iot](../../img/diagrama%20de%20flujo%20iot.png)