---
tags:
  - arquitectura
---
## **Capa de Red**

>[!info] Fase del Plan de Trabajo
>[[FASE 3 - SENSORES FÍSICOS]] y [[FASE 4 - SISTEMA MULTIAGENTE]]

La Capa de Red actúa como la columna vertebral de comunicaciones dentro de la arquitectura de [[Internet de las Cosas Médicas (IoMT)]], garantizando la transferencia segura y confiable de los datos desde la capa de percepción hacia el procesamiento local o la nube. Para asegurar la resiliencia en situaciones críticas, el proyecto implementa una estrategia de conectividad híbrida que utiliza redes de alta velocidad y ancho de banda, como WiFi o redes celulares (4G/5G), como canal principal para el flujo constante de datos pesados.

Como mecanismo de respaldo ante la pérdida de conectividad tradicional, esta capa incorpora tecnología [[LoRaWAN (Long Range Wide Area Network)]]. Esta alternativa de largo alcance y bajo consumo energético permite transmitir alertas críticas a largas distancias, en topologías descentralizadas o sin puertas de enlace (gateway-free), asegurando que el monitoreo de los pacientes no se interrumpa en entornos urbanos o rurales con intermitencias en el servicio. Durante esta transmisión, los datos son empaquetados utilizando protocolos eficientes como [[MQTT (Message Queuing Telemetry Transport)]] para minimizar el consumo de ancho de banda y batería.