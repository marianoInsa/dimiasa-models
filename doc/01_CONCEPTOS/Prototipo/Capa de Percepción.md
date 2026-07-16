---
tags:
  - arquitectura
---
## **Redes de Sensores Físicos (Capa de Percepción)**

>[!info] Fase del Plan de Trabajo
>[[FASE 3 - SENSORES FÍSICOS]]


La **Capa de Percepción** representa el soporte físico principal del sistema, encargada de la captura continua de datos en bruto ("raw data") del estado biológico del paciente y su entorno ambiental. Depende de electrónica de precisión interconectada al hardware principal mediante protocolos físicos como I2C, incluyendo componentes fundamentales como el **[[ECG y Arritmias (AD8232)]] para biopotenciales analógicos (ECG), el [[SpO2 y Oximetría (MAX30102)|MAX30102]] para fotopletismografía y oximetría (SpO2), y el [[Detección de Caídas (MPU6050)|MPU6050]] para acelerometría y postura**.

La función esencial de esta capa no es solo percibir, sino también realizar la conversión analógico-digital (ADC) inmediata y aplicar los primeros filtros básicos en los microcontroladores locales. Esto garantiza que los eventos biológicos del mundo real sean digitalizados eficientemente, reduciendo el ruido e iniciando una pre-compresión que optimiza las señales antes de que alimenten a los modelos matemáticos y algoritmos de inteligencia artificial descritos.

- **Aplicación en el Plan de Trabajo:** Corresponde a la **Fase 3 (Sensores Físicos)**, momento en el cual se requiere del hardware real para conectar cada sensor a la Raspberry Pi o el microcontrolador ESP32 de forma escalonada (desde el acelerómetro al sensor de ECG), con el objetivo de generar datos biomédicos verídicos en tiempo real que puedan ser procesados por la IA.