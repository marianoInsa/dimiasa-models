---
tags:
  - medicina
---

---

# Concepto
> La **fotopletismografía (PPG)** es una técnica de medición óptica utilizada para evaluar los cambios en el volumen de sangre en los tejidos, lo cual permite monitorear signos vitales como la frecuencia cardíaca, la saturación de oxígeno y estimar la presión arterial.

La señal PPG capturada es una onda compleja superpuesta que se divide en dos componentes principales:

- **Componente continuo (DC):** Representa la absorción constante de luz que generan los tejidos estructurales fijos (como la piel, los huesos y los músculos) y la capacitancia de la sangre venosa estática.
- **Componente fluctuante (AC):** Es la variación dinámica que es directamente proporcional a la onda del pulso arterial generada por cada latido o gasto cardíaco sistólico.

## Cómo se mide
La medición se realiza de forma no invasiva mediante biosensores ópticos que constan de fuentes emisoras de luz y receptores ([[SpO2 y Oximetría (MAX30102)]]), usualmente colocados en áreas con buena irrigación superficial como la yema del dedo, la frente o el lóbulo de la oreja. El proceso es el siguiente:

- **Emisión de luz específica:** El dispositivo utiliza Diodos Emisores de Luz (LED) para inyectar fotones en la piel. La longitud de onda depende del objetivo clínico:
    - Para medir el ritmo cardíaco (muy común en _wearables_ o relojes inteligentes), se suele utilizar un **LED de luz verde**, ya que esta longitud de onda es **menos susceptible a sufrir distorsiones (artefactos) por los movimientos** del usuario.
    - Para medir la saturación de oxígeno (SpO2), se alternan pulsos de **luz roja** (absorbida por sangre sin oxígeno) y **luz infrarroja** (absorbida por sangre oxigenada).
- **Detección fotométrica:** Un fotodetector (o fotodiodo) captura la intensidad y cantidad de luz que logra atravesar el tejido o que rebota en él (retro-dispersión).
- **Procesamiento y filtrado:** La señal analógica original captada por el fotodiodo pasa por un pre-procesamiento mediante **filtros pasa-bajos activos y amplificadores**. Posteriormente, un microcontrolador digitaliza la información y aplica algoritmos de **sustracción adaptativa de ruido**; esto es un paso indispensable, ya que la señal PPG (especialmente su onda AC) es sumamente sensible a los artefactos de movimiento que pueden generar alarmas clínicas falsas.

---
