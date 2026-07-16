
---

# Configuración de Split por Sujeto

La variable `SPLIT_RATIOS` define la partición del dataset para el ciclo de vida del aprendizaje automático. En este notebook, se utiliza una **estrategia de validación cruzada por sujetos** con la siguiente distribución:

1. **`train` (0.70):** El 70% de los sujetos se utiliza para ajustar los pesos del modelo. Es el conjunto donde la red neuronal busca patrones para distinguir entre una caída y una actividad normal.

2. **`val` (0.10):** El 10% de los sujetos sirve como "examen de práctica". Se usa durante el entrenamiento para monitorizar el *overfitting* (sobreajuste) y ajustar hiperparámetros sin contaminar los resultados finales.

3. **`test` (0.20):** El 20% de los sujetos se reserva para la evaluación final. Representa el desempeño en el mundo real ante usuarios desconocidos para el sistema.

**Fundamentación:**
Al realizar el split **por sujeto** (y no por ventanas aleatorias), garantizamos que ninguna característica biomecánica específica de una persona (como su forma de caminar o su peso) se filtre del entrenamiento a la evaluación. Esto asegura que el modelo aprenda a detectar el *evento* de caída de forma generalizable y no a reconocer a la *persona*.

---

# Configuración del Ventaneo (100 Hz)

Para la segmentación de señales en este experimento, se utilizan tres variables críticas que definen cómo el modelo "ve" los datos:

1. **`WINDOW_SAMPLES` (200):** Define el tamaño de la ventana de entrada.
	* **Significado:** Representa **2 segundos** de datos continuos (200 muestras / 100 Hz).
	* **Por qué este valor:** 2 segundos es el tiempo estándar suficiente para capturar la dinámica completa de una caída (fase de descenso e impacto) según la literatura técnica.

2. **`OVERLAP_STEP` (100):** Controla el desplazamiento de la ventana deslizante.
	* **Significado:** Indica que la ventana avanza 100 muestras (1 segundo) cada vez, creando un **solapamiento del 50%**.
	* **Por qué este valor:** El solapamiento asegura que los eventos de impacto no queden divididos drásticamente entre dos ventanas, aumentando la probabilidad de que al menos una ventana capture el pico de la caída de forma centrada.

3. **`FALL_LABEL_THR` (0.30):** Es el umbral de decisión para el etiquetado de la ventana.
	* **Significado:** Si al menos el **30%** de las muestras dentro de una ventana de 200 están etiquetadas como "Fall", la ventana completa se clasifica como positiva (1), en caso contrario, se considera "ADL" y se etiqueta como (0).
	* **Por qué este valor:** Dado que el impacto es un evento breve, un umbral del 30% permite detectar la caída incluso si el movimiento de 'descenso' o 'recuperación' ocupa gran parte de la ventana, evitando falsos negativos por exigencia excesiva de muestras de caída.

---

# 🛡️Umbrales de Descarte (Métricas)

Para garantizar la integridad del entrenamiento, se aplican tres filtros de exclusión basados en métricas de fidelidad de señal. Estos umbrales se fundamentan en la preservación de la **morfología del impacto**, crítica para la detección de caídas:

1. **`THR_PEARSON_MIN` (<0.85) - Similitud Morfológica:**
	* **Fundamento:** El coeficiente de correlación de Pearson mide la linealidad entre la señal original (filtrada) y la resampleada.
	* **Justificación:** En la literatura de procesamiento de señales biomédicas, un $r < 0.85$ indica que la distorsión introducida ha alterado la firma característica del movimiento. Si la forma de la onda cambia significativamente, el modelo podría aprender artefactos del resampleo en lugar de patrones reales de caída.

2. **`THR_PHASE_MS_MAX` (>100ms) - Coherencia Temporal:**
	* **Fundamento:** Mide el desplazamiento del pico de aceleración máxima (el impacto).
	* **Justificación:** Las caídas son eventos transitorios rápidos. Un desfase superior a 100 ms (el equivalente a un ciclo completo a 10 Hz o 10 muestras a 100 Hz) puede causar que el impacto quede fuera de la ventana focal o que se pierda la sincronía entre sensores (ACC vs GYRO). Mantener el desfase $< 100$ ms garantiza que la etiqueta temporal siga siendo válida para el evento físico.

3. **`THR_ATTEN_PCT_MAX` (>25%) - Preservación de Energía:**
	* **Fundamento:** Evalúa cuánta amplitud del pico de impacto se pierde tras el filtrado y resampleo.
	* **Justificación:** El impacto es la característica más discriminativa de una caída. Una atenuación $> 25\%$ subestima severamente la magnitud del evento, pudiendo causar que el modelo clasifique erróneamente una caída real como una actividad de baja intensidad (ADL) debido a una reducción artificial de la magnitud de los vectores de aceleración.

---
