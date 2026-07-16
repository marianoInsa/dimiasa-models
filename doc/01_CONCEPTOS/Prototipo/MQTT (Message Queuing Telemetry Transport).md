---
tags:
  - arquitectura
  - IoT
---
# **MQTT (Message Queuing Telemetry Transport)**

>[!info] Fase del Plan de Trabajo
>[[FASE 4 - SISTEMA MULTIAGENTE]]

El protocolo MQTT es un estándar de mensajería extremadamente ligero que opera bajo un modelo de publicación y suscripción (_publish-subscribe_), siendo ideal para entornos IoT con restricciones severas de ancho de banda y energía. Su arquitectura funciona a través de un intermediario central llamado "broker", el cual recibe los datos que los clientes publican clasificados en diferentes "tópicos" y se encarga de distribuirlos instantáneamente a otros clientes que estén suscritos a esos mismos tópicos.

Dentro del plan de trabajo de este sistema, MQTT cumple un doble rol comunicacional que es fundamental. A nivel de [[Computación en el Borde (Edge Computing)|procesamiento local (Edge)]], se instala un broker ligero (Mosquitto) directamente en el hardware principal para permitir que cada agente sensor (ECG, SpO2, caídas) publique sus anomalías en tópicos independientes, a los cuales el [[Sistemas Multiagente (MAS)|Agente de Triaje]] se suscribe para realizar su razonamiento cruzado. Simultáneamente, el protocolo se utiliza para empaquetar y transferir las alertas definitivas a la [[Capa de Aplicación]] en la nube, garantizando un flujo ágil que minimiza tanto el consumo de batería como el gasto de datos.