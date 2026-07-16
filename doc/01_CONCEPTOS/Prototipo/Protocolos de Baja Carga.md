---
tags:
  - arquitectura
---
## **Conectividad Híbrida y Protocolos de Baja Carga (MQTT / µACP)**

>[!info] Fase del Plan de Trabajo
>[[FASE 4 - SISTEMA MULTIAGENTE]] y [[FASE 5 - VALIDACIÓN EXPERIMENTAL]]

La resiliencia en un [[Triaje médico]] remoto exige **conectividad híbrida**, utilizando canales redundantes para garantizar que las alertas críticas siempre lleguen a los profesionales. El sistema prioriza el uso de Wi-Fi o banda ancha móvil (4G) para transferencias rápidas y pesadas, pero incorpora arquitecturas **[[LoRaWAN (Long Range Wide Area Network)]]** como vía de respaldo; una modulación de largo alcance y bajo consumo de energía que transmite alarmas incluso con baja penetración de señal o cuando falla la infraestructura doméstica.

Para que esta transmisión y la comunicación interna entre agentes funcionen de manera eficiente sin agotar los recursos de la placa, se emplean protocolos ultra ligeros orientados a la telemetría. El protocolo **[[MQTT (Message Queuing Telemetry Transport)]]**, gestionado localmente por un intermediario (broker como Mosquitto), permite que los agentes se suscriban y publiquen alertas clínicas en tópicos independientes con mínimo consumo de ancho de banda. Sumado a ello, propuestas modernas como el **[[Micro Agent Communication Protocol (µACP)]]** garantizan el consenso semántico entre agentes bajo estrictas limitaciones de memoria.

- **Aplicación en el Plan de Trabajo:** El protocolo MQTT se configura transversalmente en la **Fase 4 (Sistema Multiagente)** para lograr la comunicación entre los agentes locales en el dispositivo. Asimismo, la resiliencia de esta estrategia de red se pone a prueba en la **Fase 5 (Validación Experimental)**, que requiere simular cortes intencionales en la conectividad primaria para evaluar el desempeño offline y la correcta tolerancia del sistema ante fallos externos.
