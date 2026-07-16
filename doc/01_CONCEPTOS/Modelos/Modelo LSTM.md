
---

* En detalle cómo funciona una red LSTM: https://codificandobits.com/blog/redes-lstm/
* Introducción y ejemplos con MATLAB: https://la.mathworks.com/discovery/lstm.html
* Tutorial de preparación de los datos: https://www.youtube.com/watch?v=R8MEPGn9sFI

---

Un modelo **LSTM** (_Long Short-Term Memory_ o Memoria a Corto y Largo Plazo) es una *red neuronal recurrente (RNN)* avanzada diseñada para aprender patrones secuenciales. Destaca por resolver el problema de la pérdida de gradiente, permitiendo retener información a lo largo de grandes períodos de tiempo.

## ¿Cómo funciona?

A diferencia de las redes neuronales tradicionales o las recurrentes básicas, la estructura central de una LSTM es su **celda de estado** ($C_{t}$), que actúa como una cinta transportadora por donde viaja la información. Esta celda es manipulada por tres componentes clave llamados **compuertas** (_gates_), que deciden qué información se almacena o se elimina:

- **Compuerta del olvido (_Forget Gate_):** Analiza la entrada actual ($x_{t}$) y la salida anterior ($h_{t-1}$), utilizando una función sigmoide para decidir qué información descartar del estado de la celda ($C_{t-1}$).
- **Compuerta de entrada (_Input Gate_):** Determina qué nueva información proveniente del entorno es relevante para ser añadida y almacenada en el estado de la celda.
- **Compuerta de salida (_Output Gate_):** Regula qué partes del estado de la celda se enviarán como salida o predicción en ese paso de tiempo específico.

---

## Aplicación en Detección de Caídas

Aplicar un modelo LSTM para la detección de caídas en adultos mayores es ideal ==porque las caídas no son eventos aislados, sino **secuencias de movimientos en el tiempo**==.

1. Captura la evolución del movimiento

- Una caída tiene fases claras: pérdida de equilibrio, descenso rápido e impacto.
- Las redes tradicionales solo ven fotos fijas (un instante).
- La LSTM analiza el **historial inmediato de aceleración y ángulo** para entender la transición del cuerpo.

2. Evita las falsas alarmas

- Movimientos cotidianos como sentarse rápido o agacharse a buscar algo pueden confundir a un sensor.
- La LSTM diferencia estos gestos porque evalúa la **velocidad y trayectoria previa y posterior** al movimiento brusco.
- Distingue la quietud normal (estar sentado) de la quietud post-impacto (quedar inconsciente en el suelo).

3. Memoria de largo y corto plazo

- Su arquitectura olvida datos irrelevantes (como caminar normal por el pasillo).
- Retiene los cambios drásticos de los últimos segundos críticos para activar la alerta.

4. Flexibilidad de datos de entrada

- Funciona de manera excelente con datos provenientes de **sensores usables** (wearables) como acelerómetros y giroscopios de relojes inteligentes.
- También se adapta al análisis de **secuencias de video** paso a paso (frames) de cámaras de seguridad hogareñas.