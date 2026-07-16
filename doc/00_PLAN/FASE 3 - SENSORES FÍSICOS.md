- **Condiciones:** Acá sí se necesita hardware - ESP32 + sensores.

- **Objetivo: Conectar los sensores físicos.** Con los modelos ya validados en las fases anteriores, llega el momento de conectar los sensores reales. En esta fase el objetivo no es que todo funcione perfecto, sino que cada sensor genere datos que el modelo pueda procesar.

> [!WARNING]
> **Justificación de Hardware:** La recomendación es usar una Raspberry Pi 4 o 5 porque tiene amplia documentación, corre Python nativo, y los tres sensores tienen librerías probadas para ella. 
> **¿Por qué Raspberry Pi y no Jetson Nano?** El Jetson Nano original está en end-of-life y es difícil de conseguir. La Raspberry Pi 4/5 es suficiente para los tres modelos de señales biomédicas. 
> Si en la Fase 2 los modelos resultaron más pesados de lo esperado, la mejor opción actual es el Jetson Orin Nano Super (~USD 249, 67 TOPS) o agregar un Hailo-8L AI HAT a la Raspberry Pi 5.

- **Tareas (de menor a mayor complejidad):**
    1. **MPU6050 (acelerómetro/giroscopio):** El más simple. Se conecta mediante protocolo I2C a la placa base. Escribir el script de lectura en Python utilizando la librería smbus2 para obtener los valores de aceleración en X/Y/Z y ya se puede ver si el modelo de caídas reacciona a movimientos reales.
    2. **MAX30102 (SpO2):** También usa I2C. Tiene drivers Python probados en los repositorios doug-burrell/max30102 y vrano714/max30102-tutorial-raspberrypi. Conectar el sensor vía I2C, leer el sensor y procesar sus lecturas utilizando la librería pyPPG.
    3. **AD8232 (ECG):** Se deja para el final porque las señales analógicas de ECG son más delicadas y sensibles al ruido eléctrico del entorno. Integrar el sensor analógico utilizando el ADC del microcontrolador ESP32 o un conversor MCP3008 externo en la Raspberry Pi.
    - Verificar que cada sensor transmita de forma independiente sus datos en tiempo real hacia el procesamiento de los modelos.

>[!IMPORTANT]
>El orden de conexión no es aleatorio, se conectan de menor a mayor complejidad de señal.

- **Duración:** 40 hs (2-3 semanas).
    
- **Resultados Esperados (Entregable):** Sensores generando datos biomédicos y de movimiento en tiempo real que alimentan los modelos TFLite con inferencia funcionando en la ESP32.