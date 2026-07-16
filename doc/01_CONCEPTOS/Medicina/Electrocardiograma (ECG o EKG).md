---
tags:
  - medicina
---

---

El electrocardiograma (EKG, del alemán Elektrokardiogramm) es la representación gráfica de la actividad eléctrica del corazón. El electrocardiograma **permite determinar si el *corazón* funciona normalmente o sufre de anomalías**; muestra la condición física de un paciente durante un examen de esfuerzo y provee información sobre las condiciones físicas del corazón. Tiene la ventaja de ser un procedimiento médico no invasivo con resultados disponibles inmediatamente.

---

![[electrocardiograma-ejecucion.png]]

![[electrocardiograma-elementos-grafico.png]]

---

#### Links relevantes

* https://mesimedical.com/es/noticias/como-realizar-correctamente-un-ecg
* https://mesimedical.com/es/noticias/como-interpretar-el-ecg ⭐

---

# Electrocardiograma (ECG) de derivación única (Single-lead)

## Concepto
>El Electrocardiograma (ECG) es una prueba médica que registra la actividad eléctrica del corazón a lo largo del tiempo. Un ECG de **derivación única** (single-lead) es una versión simplificada de esta prueba, diseñada especialmente para dispositivos portátiles (wearables) e IoMT, en la cual la adquisición de la señal se limita a un solo canal o vector periférico analógico.

A pesar de esta restricción (frente a los ECG clínicos tradicionales de 12 derivaciones), esta configuración suele utilizar el equivalente a la **Derivación II** o MLII (Modified Limb Lead II), la cual proporciona una visibilidad excepcional de los vectores de despolarización ventricular. Esto permite identificar de forma clara los **complejos QRS y las ondas T**, siendo fundamental para detectar morfológicamente **[[Arritmia]]** y alteraciones cardíacas.

## Cómo se mide
La medición se realiza a través de una cadena de hardware y procesamiento inteligente de la siguiente manera:

- **Electrodos de contacto:** Se utilizan parches colocados en el pecho, brazos o piernas que captan los minúsculos cambios eléctricos cardíacos. Se pueden emplear tanto electrodos "húmedos" convencionales (de Ag/AgCl que usan un gel electrolítico como conductor) como electrodos "secos" (placas recubiertas de plata que no requieren gel).
- **Amplificación del biopotencial:** En los prototipos IoMT modernos, la señal captada por los electrodos pasa por un **amplificador de biopotencial analógico (típicamente el [[ECG y Arritmias (AD8232)|AD8232]])**, que limpia y amplifica la señal del corazón.
- **Conversión Digital:** Esta señal se envía a un **Convertidor Analógico-Digital (ADC)** integrado en un microcontrolador central (como el ESP32) para digitalizar la información.
- **Procesamiento Inteligente (Edge AI):** Para analizar el electrocardiograma en tiempo real directamente en el dispositivo, el estándar actual utiliza **Redes Neuronales Convolucionales Unidimensionales (1D-CNN)**. Estas redes procesan la morfología de la señal latido a latido desplazándose en el dominio temporal continuo, logrando clasificar arritmias con una precisión superior al 97% en fracciones de segundo y con muy bajo consumo de memoria.

---