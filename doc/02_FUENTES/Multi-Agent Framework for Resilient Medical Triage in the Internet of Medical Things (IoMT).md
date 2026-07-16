---
tags: paper
autores: Sergio Gramajo, Reinaldo Scappini, Carlos Torres, Jorge Roa, Salvador Nuñez y Raul Montiel
año: "2026"
link: https://drive.google.com/drive/u/0/folders/1WjBnrufaQlYkNmVexaNJQdWAgXjnPRa4
---
---

# Multi-Agent Framework for Resilient Medical Triage in the Internet of Medical Things (IoMT)

---

## Resumen

### **Objetivo principal**

> El objetivo es **desarrollar un marco de trabajo multiagente distribuido, ejecutado en el borde (*Edge*) mediante hardware ESP32 y MicroPython**, para reemplazar la lógica monolítica y centralizada de la nube. Este sistema busca mitigar la vulnerabilidad a fallos de conexión y reducir la "fatiga de alarmas" (exceso de falsos positivos) simulando el juicio clínico médico mediante el razonamiento cooperativo entre sensores.

### **Metodología**
> El sistema descentraliza el proceso de triaje trasladando la inteligencia al dispositivo local del paciente. Emplea una sociedad de agentes autónomos que se comunican de forma ultraeficiente mediante el protocolo **Micro Agent Communication Protocol (µACP)**.
> El proceso está regido por un **Algoritmo de Validación Cooperativa** estructurado mediante un modelo BDI (Creencias-Deseos-Intenciones): cuando un sensor detecta una anomalía, no dispara una alerta de inmediato, sino que informa su "sospecha" al Agente de Triaje. 
> Este coordinador establece una ventana temporal (2000 ms) para consultar por cuórum el estado fisiológico a los demás sensores, validando o descartando la emergencia basándose en la convergencia de la evidencia (clasificando el evento en triaje Rojo, Amarillo o Verde).

### **Arquitectura**

Propone un modelo distribuido con un enfoque de conectividad híbrida:

1. **Capa de Percepción:** Compuesta por los sensores físicos que recolectan de forma activa los signos vitales y datos del entorno.
2. **Capa Edge/Fog (Borde):** Utiliza un microcontrolador ESP32 de doble núcleo. Mientras un núcleo gestiona la recolección física de los datos, el otro procesa concurrentemente la lógica del sistema multiagente (fusión local de datos).
3. **Capa de Red:** Implementa una **estrategia híbrida** para resiliencia; usa redes WiFi o 4G/5G para transmisión continua de datos (canal principal) y reserva **LoRaWAN** para emitir alertas críticas a largas distancias si falla la conexión a internet.
4. **Capa de Aplicación (Nube):** Al liberar a la nube de la respuesta en tiempo real, esta actúa como **facilitadora de analítica avanzada** y registro histórico seguro usando bases de datos (PostgreSQL, InfluxDB) y paneles visuales interactivos como Grafana para el personal médico.

### **Sensores utilizados**

- **AD8232:** Módulo analógico para capturar biopotenciales cardíacos (ECG - derivación II) y evaluar arritmias.
- **MAX30102:** Oxímetro de pulso basado en fotopletismografía (PPG) para medir la saturación de oxígeno (SpO2) y perfusión.
- **MPU6050:** Sensor inercial de 6 ejes (acelerómetro y giroscopio) para la cinemática del paciente y detección de caídas.
- **MPX5050:** Transductor de presión para vigilar de forma no invasiva la presión arterial del paciente.
- **MG-811:** Sensor ambiental responsable de medir la calidad del aire.

![[modelo anterior de la arqui centralizada en la nube.png]]

### **Agentes**

La "sociedad" está orquestada por distintos especialistas lógicos que se comunican en tiempo real:

- **Agente de Triaje ($A_{TRJ}$):** Es el coordinador principal de todo el sistema. Aplica reglas lógicas para deducir y sintetizar el nivel de emergencia global del paciente.
- **Agentes locales/periféricos:** Un agente por cada sensor o dimensión a estudiar
	- _Agente de ECG_
	- _Agente de SpO2_
	- _Agente de Presión_
	- _Agente de Caídas_
	- _Agente Ambiental_

![[diagrama multi agent framework.png]]

### **Fusión Bayesiana**

> Es el **motor matemático detrás del razonamiento cooperativo** que correlaciona las dimensiones fisiológicas y ambientales para frenar las falsas alarmas.
> Si un agente periférico detecta un evento (como un impacto indicativo de caída), el sistema no genera una alerta ciega; en su lugar, el Agente de Triaje recalcula la probabilidad de que el trauma sea real basándose en el Teorema de Bayes. 
> Si, luego de un impacto repentino, los demás agentes reportan que la hemodinámica del paciente (pulso y presión) permanece estable, **la probabilidad real de la caída decrece**, confirmando de manera autónoma que podría tratarse de un impacto técnico (por ejemplo, el paciente dejó caer accidentalmente el dispositivo).

**Fórmula:**
$$P(E_{real}|E_{CAI}=1)=\frac{P(E_{CAI}=1|E_{real})\cdot P(E_{real})}{P(E_{CAI}=1)}$$
Donde:
- **$P(E_{real}|E_{CAI}=1)$**: Es la probabilidad de que el evento sea **real** dado que el sensor ha detectado una caída ($E_{CAI}=1$).
- **$P(E_{CAI}=1|E_{real})$**: Representa la probabilidad de que el sensor detecte una caída cuando el evento es efectivamente **real**.
- **$P(E_{real})$**: Es la probabilidad a priori de que ocurra un evento **real**.
- **$P(E_{CAI}=1)$**: Es la probabilidad total de que el sensor emita una detección de caída.

### **Resultados**

- **Obtenidos:** Los resultados proyectan **una precisión cercana al 100% en la discriminación de actividades de la vida diaria** frente a caídas reales, reduciendo casi por completo el ruido (falsos positivos). Adicionalmente, el modelo local logró llevar la **latencia de reacción por debajo de los 100 milisegundos**, permitiendo respuestas instantáneas al eliminar la dependencia de los servidores alojados en la nube (RTT).

- **Trabajo Futuro:** Como trabajos futuros, los autores plantean expandir este marco incorporando Aprendizaje Federado (_Federated Learning_) entre dispositivos de distintas casas, con el fin de optimizar el modelo central de manera colaborativa sin compartir en la red los datos biológicos crudos.

---
