
---

- Video con explicación rápida: https://www.youtube.com/watch?v=rtemoj2T208
- Clase magistral de 3Blue1Brown: https://www.youtube.com/watch?v=aircAruvnKk

---

Una **Red Neuronal Convolucional** (CNN) ==es un modelo de inteligencia artificial de aprendizaje profundo, diseñado específicamente para procesar datos visuales y espaciales==. Aprende a "ver" descomponiendo imágenes y extrayendo automáticamente características, como bordes, texturas y formas, para realizar tareas como reconocimiento de objetos y clasificación.

---

## Arquitectura principal

Un modelo CNN estándar está compuesto por tres tipos de capas fundamentales apiladas secuencialmente:

1. **Capa de Convolución:** Aplica filtros (matrices matemáticas) que escanean la imagen para extraer características básicas (líneas, sombras, bordes).
2. **Capa de Activación (ReLU):** Convierte los valores negativos en cero para acelerar y simplificar el proceso de aprendizaje.
3. **Capa de Agrupación (Pooling):** Reduce el tamaño espacial de la imagen (simplifica la resolución) conservando solo la información más importante para evitar el exceso de cálculos.
4. **Capa Conectada (Fully Connected):** Toma toda la información extraída y "agrupada" para emitir una predicción o decisión final (por ejemplo, "esta imagen es un perro").

