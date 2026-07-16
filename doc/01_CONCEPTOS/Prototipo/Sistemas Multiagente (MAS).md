---
tags:
  - MAS
---
## Sistemas Multiagente (MAS)

>[!info] Fase del Plan de Trabajo
>[[FASE 4 - SISTEMA MULTIAGENTE]]

Un Sistema Multiagente (MAS) es una arquitectura de software distribuida que reemplaza la lógica monolítica de un programa tradicional por una "sociedad" de agentes autónomos especializados (como el Agente de ECG, el Agente de Caídas o el Agente Ambiental). Cada sensor opera como un proceso independiente, recolectando datos e identificando sospechas clínicas de forma aislada para luego reportarlas a un "Agente de [[Triaje médico|Triaje]]" coordinador.

![[diagrama multi agent framework.png]]

Para que estos agentes colaboren bajo estrictas limitaciones de hardware, se requieren protocolos de mensajería altamente eficientes. El proyecto plantea el uso de un [[Broker MQTT|broker local MQTT]] (Mosquitto) para orquestar la publicación y suscripción a tópicos. Alternativamente, se proyecta la implementación del **[[Micro Agent Communication Protocol (µACP)]]**, un estándar emergente que garantiza la interoperabilidad y el consenso médico utilizando comandos mínimos de comunicación.

![[sistema multiagente.png]]