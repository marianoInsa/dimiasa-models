- **Objetivo: Integrar el sistema multiagente.** El corazón del paper - coordinación entre agentes. Esta es la fase donde el trabajo se convierte en el paper en sí. Cada sensor tiene su propio proceso corriendo de forma independiente, y los tres le reportan a un coordinador central que toma la decisión final aplicando la lógica de la Tabla 1 del paper.

- **Tareas:**
    - **Comunicación entre agentes:** Instalar y configurar el broker Mosquitto (MQTT local) en el dispositivo principal. Es liviano, open source, y, *en caso de que se consiga*, funciona perfectamente dentro de una sola Raspberry Pi con múltiples procesos.
    - Programar a cada agente sensor (ECG, SpO2, Ambiente, Caídas) para que publique sus anomalías/estado ("sospechas") en tópicos MQTT independientes.
    - Implementar el Agente de Triaje suscribiéndolo a los tópicos de todos los agentes periféricos.
    - **Lógica de decisión a implementar (Tabla 1 del paper):** Codificar la lógica de decisión cruzada (Rojo, Amarillo, Verde) según el soporte clínico de cada alerta.
    - **Fusión bayesiana (Ecuación 2 del paper):** Implementar la fusión bayesiana utilizando diccionarios de probabilidades condicionales (scipy.stats) o probabilidades simples definidas manualmente para recalcular el riesgo clínico post-evento. El objetivo es que si el estado hemodinámico es estable post-impacto, la probabilidad P(E_real) disminuya y el evento se clasifique como falso positivo técnico.

- **Duración:** 50 hs (2-3 semanas).

- **Resultados Esperados (Entregable):** Prototipo integrado con los tres agentes sensor comunicándose con el Agente de Triaje, generando alertas clínicas (Rojo/Amarillo/Verde) en tiempo real.

**Tabla 1 del paper:**

| **Sospecha (Agente emisor)** | **Soporte (Agente referencia)** | **Estado**           | **Significado clínico**        |
| ---------------------------- | ------------------------------- | -------------------- | ------------------------------ |
| Impacto (Caída)              | Taquicardia                     | 🔴🔴🔴<br>(ROJO)     | Trauma confirmado              |
| Hipotensión                  | Mareo/Ambiente                  | 🔴🔴🔴<br>(ROJO)     | Síncope detectado              |
| Impacto (Caída)              | Ritmo estable                   | 🟡🟡🟡<br>(AMARILLO) | Posible caída del dispositivo  |
| Taquicardia                  | Temp. alta                      | 🟡🟡🟡<br>(AMARILLO) | Posible estrés térmico         |
| Desaturación                 | Sin respuesta                   | 🟡🟡🟡<br>(AMARILLO) | Fallo de sensor / duda técnica |
| Pulso alto                   | Actividad alta                  | 🟢🟢🟢<br>(VERDE)    | Ejercicio normal               |

**Ecuación 2 del paper:**
$$P(E_{real}|E_{CAI}=1)=\frac{P(E_{CAI}=1|E_{real})\cdot P(E_{real})}{P(E_{CAI}=1)}$$
