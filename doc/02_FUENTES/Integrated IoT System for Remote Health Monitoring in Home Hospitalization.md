---
tags:
  - paper
autores: Sergio Gramajo, Reinaldo Scappini, Carlos Torres, Jorge Roa, Salvador Nuñez y Raul Montiel
año: "2025"
link: https://drive.google.com/drive/u/0/folders/1WjBnrufaQlYkNmVexaNJQdWAgXjnPRa4
---
---

# Integrated IoT System for Remote Health Monitoring in Home Hospitalization

---

## Resumen

### **Objetivo principal**

> El objetivo principal del proyecto es **desarrollar un sistema IoT escalable y validado para monitorear parámetros fisiológicos y ambientales en pacientes con hospitalización domiciliaria**. Con esto se busca reducir la carga sobre los recursos de los hospitales y mejorar la efectividad de las respuestas ante emergencias médicas en escenarios de atención en el hogar.

### **Metodología**
> El desarrollo se enfoca en el despliegue de dos prototipos complementarios: un dispositivo ponible (_wearable_) para variables fisiológicas y una unidad de monitoreo ambiental, ambos controlados por microcontroladores **ESP32**.
> La metodología se basa en realizar el procesamiento inicial de forma local en el dispositivo          (_Edge Computing_) para llevar a cabo la conversión analógico-digital (ADC), el filtrado de señales y los cálculos críticos para la detección de eventos, como caídas o umbrales anómalos de signos vitales. Posteriormente, los datos se empaquetan y se transmiten a la nube mediante protocolos ligeros como **MQTT/CoAP**, donde se almacenan y se envían alertas en tiempo real a través de APIs web.

### **Arquitectura**

El sistema emplea un **modelo IoT de tres capas**:

1. **Capa de Percepción:** Constituye la interfaz física. Se encarga de la recolección de los datos analógicos de los sensores, su conversión digital y el preprocesamiento inicial (filtrado, compresión y aprendizaje automático en el borde) para optimizar ancho de banda y batería.
2. **Capa de Red:** Es la columna vertebral de comunicaciones. Utiliza un enfoque híbrido de conectividad con **Wi-Fi** (para alta velocidad y monitoreo en tiempo real) y **LoRaWAN / redes celulares 4G** (como respaldo de largo alcance y bajo consumo ante caídas de internet), intercambiando los datos mediante el protocolo MQTT.
3. **Capa de Aplicación:** Aloja el núcleo inteligente en la nube, encargándose del almacenamiento seguro en bases de datos (PostgreSQL, InfluxDB), el análisis de datos mediante algoritmos y la interfaz de usuario (_dashboards_ como Grafana y aplicaciones móviles) para el personal de salud.

![[diagrama de arquitectura iomt.png]]

### **Sensores utilizados**

- **Prototipo** **Wearable** **(Fisiológico):** Emplea el sensor **AD8232** para electrocardiograma (ECG de una sola derivación), **MAX30102** para medir la oximetría de pulso (SpO2) y frecuencia cardíaca, un acelerómetro **MPU6050** para la detección de caídas, un sistema para presión arterial no invasiva (basado en un sensor de presión **MPX5050**, válvula y manguito inflable), y sensores para medir la temperatura cutánea.
- **Variables ambientales:** Utiliza sensores para medir la temperatura ambiente, la humedad relativa, la presión atmosférica, la intensidad de la luz y los niveles de CO2.

### **Resultados**

- **Obtenidos:** Se validó exitosamente la arquitectura del sistema propuesta, la integración rigurosa de los sensores médicos (como el AD8232 y MAX30102) y se desplegó una prueba de concepto funcional. Además, se logró visualizar correctamente las métricas y alarmas en un _dashboard_ centralizado en tiempo real.

- **Trabajo Futuro:** El proyecto espera avanzar hacia una validación más profunda de las ondas del ECG (específicamente el segmento ST para análisis de patologías), implementar estos algoritmos directamente en sistemas embebidos portátiles, e integrar Redes Neuronales Convolucionales (CNN) para conseguir una clasificación avanzada y autónoma de arritmias.

---
