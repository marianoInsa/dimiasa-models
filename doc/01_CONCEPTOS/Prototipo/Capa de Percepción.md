---
tags:
  - arquitectura
---
## **Redes de Sensores Físicos (Capa de Percepción)**

>[!info] Fase del Plan de Trabajo
>[FASE 3 - SENSORES FÍSICOS](../../00_PLAN/FASE%203%20-%20SENSORES%20FÍSICOS.md)


La **Capa de Percepción** representa el soporte físico principal del sistema, encargada de la captura continua de datos en bruto ("raw data") del estado biológico del paciente y su entorno ambiental. Depende de electrónica de precisión interconectada al hardware principal mediante protocolos físicos como I2C, incluyendo componentes fundamentales como el **[ECG y Arritmias (AD8232)](ECG%20y%20Arritmias%20%28AD8232%29.md) para biopotenciales analógicos (ECG), el [MAX30102](SpO2%20y%20Oximetría%20%28MAX30102%29.md) para fotopletismografía y oximetría (SpO2), y el [MPU6050](Detección%20de%20Caídas%20%28MPU6050%29.md) para acelerometría y postura**.

La función esencial de esta capa no es solo percibir, sino también realizar la conversión analógico-digital (ADC) inmediata y aplicar los primeros filtros básicos en los microcontroladores locales. Esto garantiza que los eventos biológicos del mundo real sean digitalizados eficientemente, reduciendo el ruido e iniciando una pre-compresión que optimiza las señales antes de que alimenten a los modelos matemáticos y algoritmos de inteligencia artificial descritos.

- **Aplicación en el Plan de Trabajo:** Corresponde a la **Fase 3 (Sensores Físicos)**, momento en el cual se requiere del hardware real para conectar cada sensor a la Raspberry Pi o el microcontrolador ESP32 de forma escalonada (desde el acelerómetro al sensor de ECG), con el objetivo de generar datos biomédicos verídicos en tiempo real que puedan ser procesados por la IA.