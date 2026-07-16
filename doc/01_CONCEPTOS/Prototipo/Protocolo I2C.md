---
tags:
  - arquitectura
  - IoT
---
# **Protocolo I2C**

>[!info] Fase del Plan de Trabajo
>[[FASE 3 - SENSORES FÍSICOS]], [[FASE 4 - SISTEMA MULTIAGENTE]] y [[FASE 5 - VALIDACIÓN EXPERIMENTAL]]

El protocolo I2C (Inter-Integrated Circuit) es un estándar de comunicación en serie altamente utilizado en sistemas integrados para conectar y transferir datos entre microcontroladores y sensores periféricos digitales. Este protocolo resulta ideal para plataformas de Internet de las Cosas (IoT) y dispositivos portátiles debido a que permite interconectar múltiples módulos con la unidad de procesamiento central utilizando una interfaz mínima de cables, facilitando el intercambio constante y estructurado de información biomédica o ambiental.

![[protocolo i2c.png]]

Dentro del desarrollo técnico de este proyecto, el I2C constituye el mecanismo de comunicación física fundamental entre la placa base (como una Raspberry Pi o un ESP32) y los sensores digitales críticos. Específicamente, componentes biomédicos e inerciales como la unidad MPU6050 (empleada para acelerometría y detección de caídas) y el oxímetro MAX30102 se comunican a través de este bus de datos, requiriendo el uso de bibliotecas de software especializadas como _smbus2_ para extraer las lecturas en tiempo real y alimentar a los modelos de inteligencia artificial.