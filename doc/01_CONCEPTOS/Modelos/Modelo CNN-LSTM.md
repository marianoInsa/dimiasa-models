
---

- Clase magistral: https://www.youtube.com/watch?v=f6PaCo-NfJA

---

Un modelo **CNN-LSTM** es una ==red neuronal híbrida que combina Redes Convolucionales (CNN) y Redes de Memoria a Corto y Largo Plazo (LSTM)==. Está diseñado para procesar datos que tienen componentes tanto **espaciales** (como imágenes o características en una matriz) como **temporales** (secuencias o datos a lo largo del tiempo).

## ¿Cómo funciona?

El modelo se divide en dos etapas principales:

1. **Extracción Espacial (CNN):** Las capas convolucionales y de agrupación (_pooling_) analizan los datos de entrada para extraer características o patrones locales relevantes.
2. **Interpretación Temporal (LSTM):** Los patrones extraídos por la CNN se organizan en secuencias y son procesados por la red LSTM, la cual evalúa cómo evolucionan estas características en el tiempo para generar una predicción final.

## Ventajas de su arquitectura

- **Automatización:** Elimina la necesidad de extraer características manualmente antes de alimentar a la red neuronal.
- **Memoria:** El componente LSTM resuelve el problema de retener información a largo plazo (evitando la pérdida del gradiente) que ocurre en las Redes Neuronales Recurrentes tradicionales.
- **Reconocimiento local y secuencial:** Permite identificar "qué" hay en los datos y "cuándo" sucede.

**Es la arquitectura estándar de la industria para el Reconocimiento de Actividad Humana (HAR).**

- **Cómo funciona:** Una red convolucional (CNN 1D) actúa como extractor de características en ventanas de tiempo cortas (ej. 2-3 segundos de aceleración). La salida de la CNN se pasa a la LSTM para que analice la secuencia temporal de esas características.
- **Ventaja:** La CNN reduce el ruido de los sensores y la LSTM identifica la secuencia exacta del impacto.
- **Extensión:** Muy fácil de escalar si añades nuevos sensores (ej. magnetómetro o ritmo cardíaco); solo incrementas los canales de entrada de la CNN.