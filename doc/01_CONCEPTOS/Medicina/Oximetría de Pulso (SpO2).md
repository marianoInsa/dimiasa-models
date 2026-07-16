---
tags:
  - medicina
---
## Oximetría de Pulso (SpO2)
> La **oximetría de pulso (SpO2)**, o saturación de oxígeno periférico, es una métrica que indica la proporción de hemoglobina oxigenada frente a la hemoglobina desoxigenada en la sangre del cuerpo, es decir, **la cantidad de oxígeno que llega a los tejidos**.
> En una persona sana, este nivel normal oscila entre el **96% y el 100%**. Si los valores están fuera de este rango y son persistentes, es recomendable consultar a un médico, ya que podría ser un caso de **hipoxemia** (bajo nivel) o **hiperoxemia** (alto nivel).

---

![[sp02-oximetro.png]]

---

## Cómo se mide
Se realiza de forma no invasiva utilizando un dispositivo llamado **oxímetro de pulso**, el cual suele sujetarse como un clip en la **yema del dedo, el lóbulo de la oreja o la frente**. Su funcionamiento se basa en principios ópticos y espectrofotométricos:

- **Emisión de luz:** El sensor emite fotones alternando entre un **diodo de luz roja** (la cual es fuertemente absorbida por la sangre sin oxígeno) y un **diodo de luz infrarroja** (absorbida por la sangre rica en oxígeno).
- **Detección:** Un fotodetector mide la cantidad e intensidad de luz que logra atravesar o rebotar en los tejidos de la piel.
- **Procesamiento de la señal:** Esta medición genera una onda óptica (señal fotopletismográfica o PPG) que es procesada por un microcontrolador (como el Módulo MAX30100 o el [[SpO2 y Oximetría (MAX30102)]] utilizados frecuentemente en dispositivos [[Internet de las Cosas Médicas (IoMT)|IoMT]]).
- **Cálculo final:** El algoritmo aísla las pulsaciones de la sangre arterial del ruido generado por huesos y músculos, y calcula un índice matemático ("Ratio of Ratios") para proyectar el **porcentaje exacto de oxígeno en tiempo real**.

---

#### Links relevantes

* https://www.clikisalud.net/salud-general-oximetria-pulso-que-es-para-que-utiliza/
* https://gwinnettlung.com/decoding-pulse-oximetry-readings-what-each-number-means/
* https://www.omron-healthcare.es/salud-y-estilo-de-vida/nivel-de-oxigeno-en-sangre-que-es-y-como-aumentarlo
* https://www.somatechnology.com/spanish/2025/04/08/que-es-spo2/

---
