---
tags:
  - arquitectura
---
## **Arquitectura de Tres Capas**

>[!info] Fase del Plan de Trabajo
>[FASE 3 - SENSORES FÍSICOS](../../00_PLAN/FASE%203%20-%20SENSORES%20FÍSICOS.md) y [FASE 4 - SISTEMA MULTIAGENTE](../../00_PLAN/FASE%204%20-%20SISTEMA%20MULTIAGENTE.md), materializándose como el modelo estructural transversal de todo el prototipo.

La **arquitectura de tres capas** es un modelo estructurado empleado para diseñar sistemas escalables de Internet de las Cosas Médicas (IoMT), el cual proporciona un flujo claro y organizado de la información desde su origen en el paciente hasta su análisis remoto. Este diseño se divide en la **[Capa de Percepción](Capa%20de%20Percepción.md)**, encargada de la adquisición física de datos a través de los sensores y de la conversión analógico-digital (ADC); la **[Capa de Red](Capa%20de%20Red.md)**, que actúa como columna vertebral transmitiendo la información mediante conectividad híbrida (WiFi o LoRaWAN) y protocolos eficientes como MQTT; y la **[Capa de Aplicación](Capa%20de%20Aplicación.md)**, alojada en la nube, que maneja el almacenamiento seguro, la analítica a largo plazo y las interfaces de usuario (como un _dashboard_) para los profesionales de la salud.

En el contexto del proyecto, este modelo resulta indispensable para articular la recolección de múltiples señales biológicas y ambientales. Sin embargo, para combatir la "fatiga de alarmas" y la vulnerabilidad a fallos de conexión propios de un enfoque centralizado en la nube, el sistema propone adaptar esta arquitectura aplicando [Computación en el Borde (Edge Computing)](Computación%20en%20el%20Borde%20%28Edge%20Computing%29.md). De esta manera, **el procesamiento crítico y la clasificación de anomalías se delegan a las capas inferiores** (dentro del microcontrolador local), dejando a la Capa de Aplicación la función de actuar como facilitador de analítica avanzada e historial clínico, garantizando así un monitoreo ágil y resiliente.