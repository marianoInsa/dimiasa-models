---
tags:
  - MAS
---
## Sistemas Multiagente (MAS)

>[!info] Fase del Plan de Trabajo
>[FASE 4 - SISTEMA MULTIAGENTE](../../00_PLAN/FASE%204%20-%20SISTEMA%20MULTIAGENTE.md)

Un Sistema Multiagente (MAS) es una arquitectura de software distribuida que reemplaza la lógica monolítica de un programa tradicional por una "sociedad" de agentes autónomos especializados (como el Agente de ECG, el Agente de Caídas o el Agente Ambiental). Cada sensor opera como un proceso independiente, recolectando datos e identificando sospechas clínicas de forma aislada para luego reportarlas a un "Agente de [Triaje](../Medicina/Triaje%20médico.md)" coordinador.

![diagrama multi agent framework](../../img/diagrama%20multi%20agent%20framework.png)

Para que estos agentes colaboren bajo estrictas limitaciones de hardware, se requieren protocolos de mensajería altamente eficientes. El proyecto plantea el uso de un [broker local MQTT](Broker%20MQTT.md) (Mosquitto) para orquestar la publicación y suscripción a tópicos. Alternativamente, se proyecta la implementación del **[Micro Agent Communication Protocol (µACP)](Micro%20Agent%20Communication%20Protocol%20%28µACP%29.md)**, un estándar emergente que garantiza la interoperabilidad y el consenso médico utilizando comandos mínimos de comunicación.

![sistema multiagente](../../img/sistema%20multiagente.png)