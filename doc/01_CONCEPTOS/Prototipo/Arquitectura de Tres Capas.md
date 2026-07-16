---
tags:
  - arquitectura
---
## **Arquitectura de Tres Capas**

>[!info] Fase del Plan de Trabajo
>[[FASE 3 - SENSORES FÍSICOS]] y [[FASE 4 - SISTEMA MULTIAGENTE]], materializándose como el modelo estructural transversal de todo el prototipo.

La **arquitectura de tres capas** es un modelo estructurado empleado para diseñar sistemas escalables de Internet de las Cosas Médicas (IoMT), el cual proporciona un flujo claro y organizado de la información desde su origen en el paciente hasta su análisis remoto. Este diseño se divide en la **[[Capa de Percepción]]**, encargada de la adquisición física de datos a través de los sensores y de la conversión analógico-digital (ADC); la **[[Capa de Red]]**, que actúa como columna vertebral transmitiendo la información mediante conectividad híbrida (WiFi o LoRaWAN) y protocolos eficientes como MQTT; y la **[[Capa de Aplicación]]**, alojada en la nube, que maneja el almacenamiento seguro, la analítica a largo plazo y las interfaces de usuario (como un _dashboard_) para los profesionales de la salud.

En el contexto del proyecto, este modelo resulta indispensable para articular la recolección de múltiples señales biológicas y ambientales. Sin embargo, para combatir la "fatiga de alarmas" y la vulnerabilidad a fallos de conexión propios de un enfoque centralizado en la nube, el sistema propone adaptar esta arquitectura aplicando [[Computación en el Borde (Edge Computing)]]. De esta manera, **el procesamiento crítico y la clasificación de anomalías se delegan a las capas inferiores** (dentro del microcontrolador local), dejando a la Capa de Aplicación la función de actuar como facilitador de analítica avanzada e historial clínico, garantizando así un monitoreo ágil y resiliente.