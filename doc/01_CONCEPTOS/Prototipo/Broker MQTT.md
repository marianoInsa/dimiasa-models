---
tags:
  - IoT
---
## **Broker MQTT**

>[!info] Fase del Plan de Trabajo
>[[FASE 4 - SISTEMA MULTIAGENTE]]

El protocolo [[MQTT (Message Queuing Telemetry Transport)]] es un estándar de mensajería altamente eficiente, de bajo consumo de ancho de banda y energía, ideal para conectar dispositivos con recursos de hardware limitados. En la arquitectura del proyecto, se utiliza Mosquitto como una herramienta ligera de código abierto para implementar un Broker MQTT local directamente en el dispositivo principal (como una Raspberry Pi), sirviendo como el puente de comunicación interno.

![[mqtt broker.png]]

Este broker es fundamental para orquestar la comunicación del [[Sistemas Multiagente (MAS)]]. Permite que los múltiples procesos o agentes sensores (SpO2, ECG, Ambiente, Caídas) publiquen de forma continua e independiente sus estados y anomalías médicas en diferentes "tópicos". Simultáneamente, el Agente de Triaje coordinador se suscribe a dichos tópicos a través de la red local para recibir las sospechas en tiempo real, lo que posibilita el razonamiento cooperativo del sistema.

![[MQTT (Message Queuing Telemetry Transport)]]
