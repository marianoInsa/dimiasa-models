
---

# Remuestreo (Resampling)

El **remuestreo** (resampling) es una ==técnica que modifica la frecuencia de muestreo de una señal o la cantidad de datos en un conjunto de información==. Es el proceso de **cambiar la tasa o frecuencia de muestreo original** de una señal digital para unificarla a una nueva frecuencia.

Sus dos operaciones principales son el **upsampling** (sobremuestreo o aumento de escala) y el **downsampling** (submuestreo o reducción de escala).

## Upsampling

La **interpolación** (como la interpolación lineal) se usa para aumentar frecuencias bajas (ej. UMAFall de 20 Hz a 50 Hz) calculando matemáticamente los valores de las muestras faltantes.

## Downsampling

El **diezmado (down-sampling)** se usa para reducir frecuencias altas (ej. pasar SisFall de 200 Hz a 50 Hz descartando muestras) para unificar la cantidad de datos que entran a una red neuronal.

---

# Filtros

## Filtro Pasa-bajos (Low-pass)

Es un filtro que **permite el paso de señales con una frecuencia menor** a un límite establecido (frecuencia de corte) y atenúa o bloquea las frecuencias más altas.

**Contexto:** En la literatura de detección de caídas, se utiliza para limpiar las señales de los acelerómetros y giroscopios, eliminando el "ruido" de alta frecuencia y conservando únicamente el movimiento humano real. Es común configurarlos con frecuencias de corte bajas, como 5 Hz u 8 Hz.

---

## Filtro Antialiasing

Es un filtro pasa-bajos que se aplica **estrictamente antes** de realizar un submuestreo (_down-sampling_) a una señal.

**Contexto:** Si reduces la frecuencia de una señal sin filtrarla antes, todas las frecuencias originales que queden por encima de tu nueva **Frecuencia de Nyquist** se "disfrazarán" de frecuencias bajas (un efecto de distorsión llamado _aliasing_). El filtro antialiasing "corta" esas frecuencias altas antes de descartar las muestras, asegurando que tu modelo no aprenda de ruido distorsionado.

---

## Filtro Butterworth

Es un tipo específico de diseño matemático para filtros (como el pasa-bajos) cuya característica principal es tener una **respuesta de frecuencia lo más plana y constante posible** en la banda de paso, evitando crear ondulaciones artificiales en la señal.

**Contexto:** Los investigadores lo usan con frecuencia (por ejemplo, el filtro Butterworth de 4to orden) para suavizar los datos inerciales crudos y minimizar el ruido del sensor provocado por vibraciones mecánicas de los dispositivos.

---

# Frecuencia de Nyquist

Es un límite matemático fundamental que establece que la frecuencia máxima útil que puede capturarse y representarse de forma precisa en una señal digital es **exactamente la mitad de la frecuencia de muestreo**.

**Contexto:** Si vas a establecer la frecuencia de muestreo de tu ESP32 en 50 Hz, tu Frecuencia de Nyquist es de 25 Hz. Esto significa que cualquier fenómeno físico (como una vibración) que ocurra a más de 25 Hz no podrá ser capturado correctamente por tu modelo.

---

# Artefactos de Borde (Efecto Gibbs)

Son **distorsiones u oscilaciones matemáticas** (como un efecto de "timbre" o "eco") que ocurren al aplicar ciertos filtros a una señal que tiene cambios muy bruscos, violentos o discontinuos.

**Contexto:** Durante una caída, el impacto contra el suelo genera un pico de aceleración enorme en una fracción de segundo. Si aplicas un filtro matemático muy agresivo a esa señal, el Efecto Gibbs puede generar "picos fantasma" de aceleración justo antes o después del impacto real, alterando la forma original de la caída y confundiendo potencialmente a tu red neuronal.

---

# Densidad Espectral de Potencia (PSD)

La Densidad Espectral de Potencia es una función matemática que describe cómo se distribuye la potencia (la fuerza o energía) de una señal a lo largo de las diferentes frecuencias que la componen.

**Contexto:** Si transformas tu señal de aceleración temporal a la frecuencia (usando, por ejemplo, una FFT), la PSD te dirá exactamente en qué frecuencias se concentra la mayor cantidad de energía del movimiento. Durante un impacto por caída, la PSD mostrará una distribución de energía drásticamente diferente a la que mostraría la señal de alguien caminando, lo que le da a tu red neuronal un patrón muy claro y diferenciable para aprender.

