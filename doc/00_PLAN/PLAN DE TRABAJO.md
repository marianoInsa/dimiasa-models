---
tags: plan
---

---

## **LUGAR DE REALIZACIÓN**

- **Identificación:** Universidad Tecnológica Nacional, Facultad Regional Resistencia, Departamento de Ingeniería en Sistemas de Información.
- **Actividad Principal:** Desarrollo e Investigación Tecnológica.
- **Grupo de Investigación:** Centro de Investigación Aplicada en Tecnologías de la Información y la Comunicación (CInApTIC).
- **Domicilio:** French 414 – Resistencia (3500) Chaco - Argentina.
- **Director del Proyecto:** Dr. Gramajo, Sergio Daniel.
- **Tutor:** Ing. Montiel, Raul.

---

## **TÍTULO DEL PROYECTO**

- **Título Principal:** “Diseño de Modelos Inteligentes de IoT Aplicados a Salud y Ambiente (DiMIASA)”.
- **Foco del Prototipo:** Implementación de un Prototipo Funcional "Framework Multiagente para Triaje Médico Resiliente en IoMT".
- **Código SCyT:** CCTCRE0008613TC.

### **ANTECEDENTES DEL PROYECTO**

* El desarrollo del proyecto tiene sus raíces en la necesidad crítica de transformar el monitoreo remoto de pacientes, una demanda que se intensificó significativamente durante la pandemia de COVID-19.
* El desbordamiento de las instituciones sanitarias impulsó la internación domiciliaria como medida paliativa, evidenciando una brecha tecnológica en la gestión eficaz y en tiempo real de la salud de personas fuera de las instalaciones hospitalarias.
* En este contexto, se identificó que uno de los principales obstáculos era la identificación ineficaz de eventos de salud por parte de personas sin formación médica (como familiares), lo que derivaba en avisos tardíos o diagnósticos erróneos.
* Como respuesta inicial, surgió el proyecto *DIMIASA ("Diseño de modelos inteligentes de IoT aplicados a salud y ambiente")*, el cual se centró en el desarrollo de prototipos robustos capaces de monitorear 9 variables críticas de manera simultánea.
	* Estas variables se dividieron en 5 fisiológicas (ECG en derivación II, oximetría SpO2, presión arterial, temperatura de piel y detección de caídas mediante acelerometría) y 4 ambientales (niveles de CO2, temperatura ambiente, humedad y presión atmosférica), reconociendo que el entorno del paciente influye directamente en su estado clínico.
* La arquitectura se estructuró en un modelo de tres capas (Percepción, Red y Aplicación), utilizando microcontroladores ESP32 y una estrategia de conectividad híbrida mediante WiFi, LoRaWAN y MQTT para garantizar la resiliencia en la transmisión de datos.
* En sus fases previas, se aplicaron técnicas de Ciencia de Datos y Aprendizaje Automático (como Support Vector Machines y Random Forest) para la clasificación de señales y detección de anomalías.
* Asimismo, se exploró el uso de Edge/Fog Computing para procesar información en el borde de la red, asegurando una baja latencia en la detección de eventos críticos sin depender exclusivamente de la nube.
* Actualmente, el proyecto evoluciona hacia la Idea de un "Framework LLM Multiagente para IoMT".

### **DESCRIPCIÓN DEL PROYECTO**

* Impulsado por la demanda global post-pandemia de soluciones tecnológicas, este proyecto propone integrar las TICs, el Internet de las Cosas (IoT) y la Ciencia de Datos para abordar problemáticas en salud y medio ambiente.
* El núcleo de la propuesta radica en aprovechar la capacidad del IoT para conectar dispositivos con mínima intervención humana, facilitando el monitoreo de variables críticas y la toma de decisiones basadas en análisis de datos.
* Finalmente, el objetivo principal es diseñar modelos técnicos validados que puedan transferirse al entorno local, resolviendo así la falta de estudios regionales y permitiendo que estas innovaciones se implementen con éxito y respaldo académico.
* En este sentido, el proyecto correspondiente a la PS se enfoca fundamentalmente en tratar este problema en un entorno de aplicaciones sobre un framework multiagente distribuido, y el estudio de datasets y modelos de IA para tratar este campo de conocimiento.

### **LÓGICA DEL PLAN**

- Este plan de trabajo tiene como objetivo guiar la implementación progresiva del sistema multiagente para triaje médico resiliente descripto en el paper 'Framework Multiagente para un Triaje Médico Resiliente en Internet de las Cosas Médicas (IoMT)' del CInApTIC - UTN FRRe.
- La lógica del plan es simple: primero dominás cada pieza por separado, después las unís.
- No tiene sentido pelear con la IA si los sensores no andan, y no tiene sentido comprar hardware nuevo si no validaste los modelos antes.
- Cada fase tiene un entregable concreto que sirve de base para la siguiente.

---

## **OBJETIVOS**

### **OBJETIVOS DEL PROYECTO**

* Desarrollar modelos inteligentes de Internet de las Cosas en base a estudios e identificación de atributos sobre telecomunicaciones y componentes tecnológicos que puedan aplicarse en áreas de Salud y Ambiente en la región.

### **OBJETIVOS DEL ALUMNO**

* Analizar las arquitecturas y protocolos usados en Telecomunicaciones para IoT en Salud y Ambiente.  
* Analizar los modelos inteligentes y ciencia de datos para usar en los modelos de IoT.  
* Identificar y desarrollar escenarios de prueba y generación de aplicaciones orientados a Salud y Ambiente.  
* Generar transferencias al medio local y/o proponer modelos de estudio para las investigaciones del grupo.  
* Desarrollar prototipos de IoT en base a estándares y adaptarlos al medio regional.

---

## **ACTIVIDADES DEL ALUMNO**

### **TIEMPO ESTIMADO DE DURACIÓN (en horas)**  

- **Horario de trabajo que deberá cumplir el alumno:** Matutino.
- **Semana laboral:** 6 hs.
- **Duración Total:** 200 (en horas).
- El plan está diseñado para ser trabajado a ritmo de investigación (no a tiempo completo), con una estimación total de 3 a 4 meses.

| **Parámetro Inicial**           | **Detalle**         |
| ------------------------------- | ------------------- |
| **Hardware de partida**         | ESP32               |
| **Nivel ML**                    | Intermedio          |
| **Objetivo**                    | Prototipo funcional |
| **Duración estimada**           | 3 a 4 meses         |
| **Hardware adicional sugerido** | Raspberry Pi 4 o 5  |
> [!NOTE]
> El HW adicional sugerido es una posibilidad a futuro. La idea es realizar la totalidad del proyecto sobre el HW de partida (ESP32).

### **DESCRIPCIÓN DE LAS ACTIVIDADES**

#### **RESUMEN POR FASES**

| **Fase**                                                                  | **Duración** | **Hardware**     | **Resultado**            |
| ------------------------------------------------------------------------- | ------------ | ---------------- | ------------------------ |
| **[[FASE 1 - MODELOS EN PC\|FASE 1: MODELOS EN PC]]**                     | 2-3 semanas  | Solo laptop      | 3 modelos entrenados     |
| **[[FASE 2 - CONVERSIÓN LiteRT\|FASE 2: CONVERSIÓN LiteRT]]**             | 1-2 semanas  | Solo laptop      | 3 modelos <1 MB          |
| **[[FASE 3 - SENSORES FÍSICOS\|FASE 3: SENSORES FÍSICOS]]**               | 2-3 semanas  | ESP32 + sensores | Datos reales funcionando |
| **[[FASE 4 - SISTEMA MULTIAGENTE\|FASE 4: SISTEMA MULTIAGENTE]]**         | 2-3 semanas  | ESP32            | Prototipo integrado      |
| **[[FASE 5 - VALIDACIÓN EXPERIMENTAL\|FASE 5: VALIDACIÓN EXPERIMENTAL]]** | 2-3 semanas  | Todo lo anterior | Métricas del paper       |

---

## **HARDWARE Y HERRAMIENTAS NECESARIAS**

### **Hardware**

|**Componente**|**Necesario en**|**Costo aprox.**|**Notas**|
|---|---|---|---|
|**Laptop/PC (ya tenés)**|Fases 1-2|USD 0|Para entrenar y convertir modelos|
|**ESP32 (ya tenés)**|Fase 3 (ECG)|USD 0|Como ADC para el AD8232|
|**Raspberry Pi 4 o 5**|Fases 3-5|USD 60-80|Hardware central del prototipo|
|**Sensor MPU6050**|Fase 3|USD 3-5|Acelerómetro/giroscopio I2C|
|**Sensor MAX30102**|Fase 3|USD 5-8|SpO2 y frecuencia cardiaca I2C|
|**Sensor AD8232**|Fase 3|USD 8-12|Módulo ECG analógico|
|**Cables, protoboard**|Fase 3|USD 5-10|Para conexiones de sensores|

### **Software y Librerías**

| **Herramienta**        | **Usado en Fase** | **Función**                           |
| ---------------------- | ----------------- | ------------------------------------- |
| **TensorFlow / Keras** | 1-2               | Entrenamiento de modelos              |
| **TensorFlow Lite**    | 2-5               | Inferencia optimizada en Raspberry Pi |
| **pyPPG/NeuroKit2**    | 1, 3-5            | Procesamiento de señales PPG/ECG      |
| **smbus2/RPi.GPIO**    | 3-5               | Drivers I2C para sensores en RPi      |
| **Mosquitto (MQTT)**   | 4-5               | Comunicación local entre agentes      |
| **scipy.stats**        | 4-5               | Implementación de fusión bayesiana    |
| **PhysioNet datasets** | 1                 | MIT-BIH (ECG), BIDMC (PPG/SpO2)       |
| **SisFall dataset**    | 1                 | Caídas con acelerómetro               |

---

## **APORTES QUE SE ESPERA REALIZAR CON ESTE TRABAJO**  

- **Aportes a la Formación Profesional:** Este trabajo pondrá en práctica competencias fundamentales del diseño curricular vinculadas a ciencia de datos, arquitectura de sistemas y el despliegue de inteligencia artificial en hardware embebido.
- **Aportes al Grupo de Investigación (CInApTIC):** Se entregará un prototipo funcional que valide, mediante mediciones empíricas, las hipótesis teóricas de latencia, resiliencia y falsos positivos de su paper, habilitando su posterior publicación indexada. Los resultados de la Fase 5 serían la contribución experimental que fortalecería significativamente el paper para una publicación en conferencia o revista indexada al reemplazar las proyecciones teóricas de la Sección 5.
- **Aportes a la Comunidad:** Se espera aportar al desarrollo de tecnologías biomédicas eficientes y de bajo costo (IoMT), garantizando mayor autonomía y precisión en los sistemas de alerta temprana de salud.

- **¿Por dónde empezar hoy mismo?** La Fase 1 no requiere comprar nada. Con Python, TensorFlow y los datasets gratuitos de PhysioNet y SisFall se puede arrancar esta semana. El primer objetivo concreto es entrenar un modelo CNN-LSTM de detección de caídas con SisFall y lograr un F1-score mayor a 0.90.

---