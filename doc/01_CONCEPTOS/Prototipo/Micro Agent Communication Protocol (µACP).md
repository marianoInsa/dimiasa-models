---
tags:
  - MAS
---
## **Micro Agent Communication Protocol (µACP)**

>[!info] Fase del Plan de Trabajo
>[[FASE 4 - SISTEMA MULTIAGENTE]]

El **Micro Agent Communication Protocol (µACP)** es un estándar emergente de interoperabilidad distribuida diseñado específicamente para orquestar ecosistemas que operan bajo condiciones extremas y restricciones de hardware, como limitaciones de memoria, energía y ancho de banda. A diferencia de los protocolos de comunicación semántica tradicionales (como FIPA-ACL), los cuales resultan prohibitivamente pesados para ejecutarse en microcontroladores, el µACP se basa en un cálculo formal que emplea una base mínima de verbos (**PING, TELL, ASK, OBSERVE**), demostrando ser semánticamente completo para establecer consensos.

![[agent communication protocol (ACP).png]]

La aplicación de este protocolo es el pilar central del marco de trabajo descentralizado que se plantea en el proyecto. Gracias a su extrema eficiencia, permite que **los distintos [[Sistemas Multiagente (MAS)|agentes autónomos]] (ECG, ambiental, oximetría, caídas) se comuniquen y "debatan" directamente [[Computación en el Borde (Edge Computing)|en el borde de la red]]**. Esta interacción constante, regida por el µACP, hace posible el razonamiento cooperativo del sistema, logrando que los agentes crucen sus datos para confirmar una emergencia o descartar un evento (como un falso positivo técnico) de forma autónoma, sin depender de la nube para el análisis inmediato.

#### Link

* https://medium.com/@harshit.sinha0910/understanding-the-agent-communication-protocol-acp-816713deea21
* https://datatracker.ietf.org/doc/html/draft-mallick-muacp

---