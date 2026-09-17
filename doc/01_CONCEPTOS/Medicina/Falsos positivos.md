---
tags:
  - IoMT
---

---

# Concepto
> Los **falsos positivos** son **falsas alarmas en las que un dispositivo notifica de manera urgente sobre una emergencia biológica que empíricamente nunca ha ocurrido**. Un ejemplo común se da en los sistemas de detección de caídas, donde el sistema puede confundir erróneamente actividades de la vida diaria (ADL) de alta aceleración, como sentarse rápidamente o agacharse a recoger algo del suelo, con una caída real.

## Implicancias
La principal consecuencia de una abrumadora generación de falsos positivos es la inducción de un fenómeno clínico y psicológico denominado ***"Fatiga por Alarmas" (Alarm Fatigue)***. Las implicancias de este fenómeno son graves:

- **Desensibilización médica:** La sobrecarga de notificaciones erróneas desensibiliza subrepticiamente a los profesionales de la salud.
- **Retraso letal en la atención:** Al ignorar o restar urgencia a las alertas, **se prolonga peligrosamente el tiempo de respuesta humana cuando ocurre un evento adverso genuino**.
- **Pánico innecesario:** En entornos de hospitalización domiciliaria, la alta tasa de alarmas por artefactos técnicos o movimientos espásticos puede generar un pánico irracional en los operadores remotos o en los familiares

## Procedimiento
Para mitigar los falsos positivos, la ingeniería biomédica moderna ha dejado atrás el razonamiento determinista simple (reglas de "Si/Entonces") para implementar arquitecturas más sofisticadas:

- **[Sistemas Multiagente (MAS)](../Prototipo/Sistemas%20Multiagente%20%28MAS%29.md) y [Fusión Bayesiana](../Prototipo/Fusión%20Bayesiana.md):** Esta es la solución de vanguardia. En lugar de depender de un solo sensor, se utiliza la estadística Bayesiana para actualizar dinámicamente la probabilidad de una emergencia cruzando datos de múltiples sensores independientes. Por ejemplo, si un agente biocinético detecta un impacto compatible con una caída, pero simultáneamente el agente electrocardiográfico y oximétrico reportan que el ritmo cardíaco y la saturación de oxígeno del paciente están perfectamente estables, **el sistema reduce drásticamente la probabilidad de que sea una emergencia médica real y descarta la anomalía como un falso positivo** (ej. el dispositivo se cayó sobre la mesa). En uso real, los detectores de caídas muestran sensibilidades desde ~57% con 3-85 falsos positivos/día (Bagalà et al., PLoS ONE 7(5):e37017, 2012) y PPV domiciliario de 0,02 (Chaudhuri et al., PMC4662041); cerrar esa brecha es exactamente el objetivo de la fusión multisensor (DETECT-2: 2 falsos positivos en 179 caídas combinando PPG y acelerometría, DOI 10.1093/ehjdh/ztag043).
- **Machine Learning Personalizado:** Los sistemas recopilan datos personalizados del usuario individual para entrenar modelos de aprendizaje profundo, lo cual optimiza la precisión del modelo y ayuda a distinguir mejor entre un accidente y las actividades normales del paciente. Además, el uso de validaciones con Machine Learning sobre los detectores iniciales reduce significativamente las tasas de falsas alarmas.
- **Análisis de Inactividad Post-evento:** Para evitar falsas alarmas inerciales, los algoritmos avanzados añaden puntos de control adicionales, como **monitorear el nivel de inactividad de la persona inmediatamente después de un supuesto impacto**, lo cual es clave para confirmar si realmente ocurrió una caída incapacitante.

---
