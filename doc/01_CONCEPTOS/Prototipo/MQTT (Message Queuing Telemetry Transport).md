---
tags:
  - arquitectura
  - IoT
---
# **MQTT (Message Queuing Telemetry Transport)**

>[!info] Fase del Plan de Trabajo
>[FASE 4 - SISTEMA MULTIAGENTE](../../00_PLAN/FASE%204%20-%20SISTEMA%20MULTIAGENTE.md)

El protocolo MQTT es un estándar de mensajería extremadamente ligero que opera bajo un modelo de publicación y suscripción (_publish-subscribe_), siendo ideal para entornos IoT con restricciones severas de ancho de banda y energía. Su arquitectura funciona a través de un intermediario central llamado "broker", el cual recibe los datos que los clientes publican clasificados en diferentes "tópicos" y se encarga de distribuirlos instantáneamente a otros clientes que estén suscritos a esos mismos tópicos.

Dentro del plan de trabajo de este sistema, MQTT cumple un doble rol comunicacional que es fundamental. A nivel de [procesamiento local (Edge)](Computación%20en%20el%20Borde%20%28Edge%20Computing%29.md), se instala un broker ligero (Mosquitto) directamente en el hardware principal para permitir que cada agente sensor (ECG, SpO2, caídas) publique sus anomalías en tópicos independientes, a los cuales el [Agente de Triaje](Sistemas%20Multiagente%20%28MAS%29.md) se suscribe para realizar su razonamiento cruzado. Simultáneamente, el protocolo se utiliza para empaquetar y transferir las alertas definitivas a la [Capa de Aplicación](Capa%20de%20Aplicación.md) en la nube, garantizando un flujo ágil que minimiza tanto el consumo de batería como el gasto de datos.