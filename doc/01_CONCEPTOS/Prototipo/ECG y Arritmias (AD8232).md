---
tags:
  - IoMT
---
## **ECG y Arritmias (AD8232)**

>[!info] Fase del Plan de Trabajo
>[[FASE 1 - MODELOS EN PC]], [[FASE 3 - SENSORES FÍSICOS]] y [[FASE 4 - SISTEMA MULTIAGENTE]]

El módulo AD8232 es un sensor analógico diseñado para medir la actividad eléctrica del corazón y capturar biopotenciales cardíacos, centrándose en este prototipo en la derivación II (Lead II) del [[Electrocardiograma (ECG o EKG)|electrocardiograma (ECG]]). Al generar señales analógicas muy delicadas y sensibles al ruido eléctrico del entorno, requiere el uso de un conversor analógico a digital (ADC), como el integrado en el microcontrolador ESP32 o un conversor externo (MCP3008), para poder procesar la información correctamente.

![[sensor-ecg.png]]

Los datos obtenidos por este sensor son analizados por el "Módulo B", el cual emplea una red neuronal unidimensional ([[Redes 1D-CNN|1D-CNN]]) ultraligera entrenada con la base de datos "MIT-BIH" para clasificar la estabilidad cardíaca y detectar arritmias. En la lógica de triaje cooperativo, el Agente de ECG provee un contexto hemodinámico crucial; su información permite validar emergencias graves al combinarse con otros agentes (como confirmar un síncope si hay hipotensión asociada), o descartar anomalías si un pulso elevado corresponde simplemente a un estado de actividad física normal verificado por el acelerómetro.

#### Links
* **MIT-BIH Arrhythmia Database (PhysioNet):** El patrón oro indiscutido. Contiene registros de ECG ambulatorios. Es ideal para aplicar segmentación en ventanas, programar los filtros pasa-banda y alimentar arquitecturas convolucionales 1D.
	* https://physionet.org/content/mitdb/1.0.0/
	* https://www.kaggle.com/datasets/taejoongyoon/mitbit-arrhythmia-database

* **PTB-XL:** Una base de datos masiva de electrocardiografía clínica con más de 21,000 registros de pacientes reales. Aporta una diversidad morfológica enorme que ayuda a las redes neuronales a generalizar la "línea base" fisiológica y disparar alarmas ante la anomalía con mayor precisión.
	* https://physionet.org/content/ptb-xl/1.0.3/
	* https://www.kaggle.com/datasets/khyeh0719/ptb-xl-dataset/code

---
