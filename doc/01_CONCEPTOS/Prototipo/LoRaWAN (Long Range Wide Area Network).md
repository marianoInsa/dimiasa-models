---
tags:
  - arquitectura
  - IoT
---
# **LoRaWAN (Long Range Wide Area Network)**

>[!info] Fase del Plan de Trabajo
>[[FASE 3 - SENSORES FÍSICOS]], [[FASE 4 - SISTEMA MULTIAGENTE]] y [[FASE 5 - VALIDACIÓN EXPERIMENTAL]]

LoRaWAN es un protocolo de red de área amplia y baja potencia (LPWAN) diseñado específicamente para la comunicación inalámbrica de dispositivos de Internet de las Cosas (IoT) a largas distancias. Utiliza una modulación de espectro ensanchado por chirp (CSS) que le permite alcanzar amplios rangos de transmisión, típicamente hasta 15 kilómetros en áreas rurales y 5 kilómetros en entornos urbanos, soportando una gran capacidad de red de forma simultánea y con un consumo energético mínimo.

En la arquitectura de este proyecto, LoRaWAN se implementa dentro de la [[Capa de Red]] como un canal de comunicaciones de respaldo estratégico (_Backup Channel_). Su propósito es garantizar la resiliencia total del sistema de [[Triaje médico]]; en caso de que la conexión principal de alta velocidad (como WiFi o 4G/5G) falle o se encuentre en un área con mala señal, LoRaWAN permite transmitir las alertas críticas a largas distancias a través de redes de malla sin depender de pasarelas centrales (_gateway-free_), asegurando que el monitoreo de emergencias de los pacientes no se interrumpa.