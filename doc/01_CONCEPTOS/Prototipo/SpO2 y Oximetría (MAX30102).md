---
tags:
  - IoMT
---
## **SpO2 y Oximetría (MAX30102)**

>[!info] Fase del Plan de Trabajo
>[[FASE 1 - MODELOS EN PC]], [[FASE 3 - SENSORES FÍSICOS]] y [[FASE 4 - SISTEMA MULTIAGENTE]]

El MAX30102 es un módulo de oximetría de pulso que emplea tecnología de [[Fotopletismografía (PPG)]] para medir la [[Oximetría de Pulso (SpO2)]] y la perfusión tisular del paciente. Al igual que el acelerómetro, este componente se comunica con la unidad de procesamiento central a través del [[Protocolo I2C]], y sus lecturas en bruto son procesadas y validadas mediante bibliotecas especializadas de Python como pyPPG y NeuroKit2.

![[sensor-oximetria.png]]

Este flujo de trabajo constituye el "Módulo C", el cual se valida inicialmemente empleando el dataset de pacientes "BIDMC". Durante el monitoreo distribuido en tiempo real, el Agente de SpO2 es responsable de vigilar los niveles de oxigenación frente a umbrales clínicos de riesgo (como desaturaciones por debajo del 94% o del 85%). Su integración en el razonamiento del sistema es vital: si el agente reporta una desaturación crítica pero el paciente registra movimientos bruscos simultáneos según el MPU6050, el sistema deduce de manera autónoma que podría tratarse de un fallo o desprendimiento del sensor, catalogando el evento con precaución y mitigando el riesgo de la [[Falsos positivos|"fatiga de alarmas"]].

#### Links
* **BIDMC PPG and Respiration Dataset (PhysioNet):** Contiene registros continuos de pacientes en cuidados intensivos, incluyendo fotopletismografía (PPG), frecuencia respiratoria y niveles de SpO2. Es vital para entender la forma de onda original que luego replicará tu hardware en código real.
	* https://physionet.org/content/bidmc/1.0.0/
	* https://www.kaggle.com/datasets/anhtua/bidmc-ppg-dataset

* **High-Altitude Pilot Physiological Monitoring Dataset (2025):** Un conjunto muy novedoso que expone variaciones continuas de saturación de oxígeno y frecuencia cardíaca en ambientes de hipoxia simulada. Brinda series temporales limpias sobre cómo se deterioran los parámetros orgánicos en tiempo real.
	* https://www.nature.com/articles/s41597-025-06508-1
	* https://figshare.com/articles/dataset/High-Altitude_Pilot_Physiological_Monitoring_Dataset_Respiratory_Performance_and_SpO_Analysis/29947679

---
