- **Objetivo: Resiliencia y validación experimental.** Lo que diferencia un prototipo de un sistema. Validación de las afirmaciones del paper. Esta última fase valida las afirmaciones más importantes del paper y genera los datos experimentales que la versión actual del paper presenta como proyecciones teóricas.

- **Pruebas a realizar (Tareas):**
    - **Medición de latencia real:** Medir la latencia de respuesta ejecutando el procesamiento a nivel local (edge) y compararla contra los tiempos de un envío directo a un servidor en la nube. El paper proyecta una reducción del 70%.
    - **Resiliencia ante caída de red:** Simular una pérdida de conectividad externa (desconectar el WiFi) para verificar el correcto funcionamiento offline, que el sistema sigue detectando eventos, y el almacenamiento local de las alertas generadas correctamente.
    - **Tasa de falsos positivos:** Cuantificar y registrar cuántas alarmas genera el sistema sin razonamiento cooperativo (sensor aislado) versus el sistema con razonamiento cooperativo entre agentes.
    - **Prueba en condiciones ambientales locales:** Replicar variables ambientales locales extremas para validar el ejemplo concreto del paper (ej. exposición a 38°C común en el NEA) con taquicardia leve de 110 bpm, para comprobar la supresión de falsos positivos en las lecturas de ritmo cardíaco (clasificada correctamente como Verde).
    - Documentar todas las métricas experimentales resultantes para redactar la actualización del apartado de resultados (actualizan la Sección 5 del paper).

- **Duración:** 50 hs (2-3 semanas).

- **Resultados Esperados (Entregable):** Métricas experimentales reales obtenidas de latencia, tasa de falsos positivos y resiliencia ante desconexión para la actualización de la Sección 5 del paper.