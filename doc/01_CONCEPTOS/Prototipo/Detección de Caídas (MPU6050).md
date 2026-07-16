---
tags:
  - IoMT
---
## **Detección de Caídas (MPU6050)**

>[!info] Fase del Plan de Trabajo
>[[FASE 1 - MODELOS EN PC]], [[FASE 3 - SENSORES FÍSICOS]] y [[FASE 4 - SISTEMA MULTIAGENTE]]

El sensor MPU6050 es una unidad de medición inercial (IMU) de seis ejes que integra un acelerómetro y un giroscopio, encargado de capturar la cinemática del paciente, como los impactos y la pérdida de verticalidad (postura). A nivel de hardware, se conecta a la placa principal mediante el [[Protocolo I2C]], permitiendo obtener lecturas continuas de aceleración en los ejes X, Y y Z.

Primero tenemos que saber los rangos con los que está configurado nuestro MPU6050, dichos rangos pueden ser 2g/4g/8g/16g para el acelerómetro y 250/500/1000/2000(°/s) para el giroscopio.

![[sensor-caidas.png]]

En el contexto del proyecto (Módulo A), estas lecturas alimentan una red neuronal profunda (CNN-LSTM) entrenada con el dataset biomédico "SisFall" para identificar caídas de manera automática. Dentro del sistema multiagente, el Agente de Caídas reporta cualquier impacto detectado al Agente de Triaje, quien correlaciona esta cinemática con otros signos vitales; si el impacto se acompaña de taquicardia, se confirma un trauma real (Alerta Roja), pero si el ritmo cardíaco se mantiene estable, se cataloga lógicamente como una posible caída del dispositivo (Alerta Amarilla), evitando así [[Falsos positivos]].
#### Links
- **SisFall:** La base estándar y más robusta para empezar. Cuenta con registros de acelerometría y giroscopio capturando actividades diarias y tipos de caídas. Es el dataset perfecto para luego cuantizar el modelo final a formato TFLite sin perder exactitud (F1-score).
	- https://pmc.ncbi.nlm.nih.gov/articles/PMC5298771/
	- https://www.kaggle.com/datasets/nvnikhil0001/sis-fall-original-dataset

- **UP-Fall Detection Dataset:** Un dataset multimodal muy útil si el prototipo escala a futuro. Además de señales inerciales en muñeca, incluye métricas de otros sensores que enriquecen los escenarios de caídas frente a falsas alarmas (como tropezones o movimientos bruscos cotidianos).
	- https://www.mdpi.com/1424-8220/19/9/1988
	- https://www.kaggle.com/datasets/pragyachandak/upfalldataset

---