---
tags:
  - arquitectura
---
## **Capa de Aplicación**

>[!info] Fase del Plan de Trabajo
>[[FASE 3 - SENSORES FÍSICOS]], [[FASE 4 - SISTEMA MULTIAGENTE]] y [[FASE 5 - VALIDACIÓN EXPERIMENTAL]]

La Capa de Aplicación es el nivel superior de la arquitectura del sistema, alojada habitualmente en la nube, que funciona como el núcleo inteligente para el almacenamiento de datos a largo plazo y la analítica histórica. Al delegar el procesamiento en tiempo real y el [[Triaje médico]] crítico a las capas inferiores ([[Computación en el Borde (Edge Computing)]]), esta capa se libera de la carga de respuestas inmediatas y asume el rol de facilitador de analítica avanzada y de registro histórico seguro.

En esta capa se despliegan bases de datos seguras (como PostgreSQL o InfluxDB para el manejo de series temporales) y se desarrollan las interfaces de usuario, tales como aplicaciones móviles o cuadros de mando (Dashboards en herramientas como Grafana). Esto permite que los profesionales de la salud puedan visualizar de manera centralizada las tendencias de los signos vitales, recibir notificaciones de alertas validadas y tomar decisiones clínicas informadas bajo estrictos controles de privacidad.