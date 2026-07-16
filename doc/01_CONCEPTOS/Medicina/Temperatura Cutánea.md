---
tags:
  - medicina
---
# Concepto
> La **temperatura cutánea ($T_{skin}$)** es la temperatura superficial del cuerpo. En el ámbito clínico y de dispositivos wearables, se mide típicamente de forma no invasiva a través de **termistores o sensores en contacto con la piel**.

## Diferencia con la Temperatura Corporal Central ($T_{core}$)
Existe una **desconexión fisiológica crítica** entre ambas temperaturas debido al sistema de termorregulación del hipotálamo del cuerpo:

- **Frente al calor o esfuerzo físico:** El cuerpo se defiende con vasodilatación periférica y sudor. Esto hace que la **temperatura de la piel baje** abruptamente para disipar el calor, mientras que la **temperatura central se mantiene estable o aumenta**.
- **Frente al frío o al inicio de fiebre:** Ocurre una vasoconstricción periférica severa que **desploma la temperatura cutánea** para proteger y retener el calor en el núcleo del cuerpo. Esto puede generar una lectura engañosa de piel fría frente a una fiebre interna real.
- En resumen, las respuestas involuntarias del cuerpo (como tiritar o sudar) están dictaminadas casi en exclusiva por la temperatura central, no por la cutánea.

## Cómo se mide
La medición primaria se realiza con sensores flexibles pegados a la piel o termómetros de contacto (como el modelo LM35). Sin embargo, como tomar esta lectura de forma aislada puede llevar a diagnósticos erróneos, los ecosistemas de monitoreo avanzado (IoMT) gestionan la medición mediante algoritmos de [[Computación en el Borde (Edge Computing)]] de la siguiente manera:

- **Modelos de Regresión Múltiple:** Se integra la medición de la temperatura de la piel con datos de **sensores ambientales**, cruzando variables como la temperatura del cuarto, la humedad relativa, el flujo de calor local y la tasa metabólica del paciente (estimada por acelerómetros).
- **Análisis de Componentes Principales (PCA):** Debido a que muchas variables ambientales y dérmicas se influyen entre sí, se aplica PCA para extraer componentes matemáticos limpios y evitar que el modelo se distorsione por datos solapados (multicolinealidad).
- Al procesar estos datos combinados, el sistema logra **predecir en tiempo real la verdadera temperatura central** del paciente con una precisión tan alta que es comparable a los estándares de medición invasivos, como las sondas rectales o las píldoras telemétricas ingeribles.

---
