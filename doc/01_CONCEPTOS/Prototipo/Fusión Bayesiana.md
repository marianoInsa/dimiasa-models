---
tags:
  - MAS
---
## Fusión Bayesiana y Razonamiento Cooperativo

>[!info] Fase del Plan de Trabajo
>[[FASE 4 - SISTEMA MULTIAGENTE]]

La Fusión Bayesiana es el motor matemático detrás del razonamiento cooperativo del sistema, diseñado específicamente para combatir el exceso de [[Falsos positivos|falsas alarmas ("fatiga de alarmas")]]. Cuando un agente periférico detecta una anomalía (por ejemplo, un impacto que sugiere una caída), el Agente de Triaje utiliza probabilidades condicionales para recalcular el riesgo real consultando los signos vitales obtenidos por otros agentes en ese mismo instante.

El razonamiento emula el juicio clínico médico correlacionando evidencia. Por ejemplo, si se [[Detección de Caídas (MPU6050)|detecta una caída]] pero el paciente mantiene una frecuencia cardíaca y presión arterial estables en los instantes posteriores, la probabilidad bayesiana del evento disminuye drásticamente, catalogándolo como un falso positivo técnico (un dispositivo que se cayó, por ejemplo) y catalogando la alerta como "Amarilla" o "Verde" según la lógica de [[Triaje médico|triaje]] implementada.