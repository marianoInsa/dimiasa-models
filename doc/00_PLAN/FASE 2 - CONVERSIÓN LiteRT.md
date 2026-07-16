- **Condiciones:** Aún sin hardware adicional, proceso de cuantización y benchmarking.

- **Objetivo: Convertir y optimizar para edge.** En esta fase se convierte cada modelo a TensorFlow Lite, que es el formato que corre eficientemente en dispositivos pequeños. Este paso es importante hacerlo antes de comprar hardware porque determina exactamente qué tan pesados son los modelos.

- **Tareas:**
    - Proceso de conversión (igual para los 3 modelos): Convertir los tres modelos entrenados (.h5) utilizando la herramienta LiteRT Converter / TFLiteConverter desde el modelo Keras guardado.
    - Ejecutar los modelos convertidos sin cuantización para corroborar que mantienen la eficacia original y confirmar que el modelo funciona igual que el original.
    - Aplicar cuantización float16 a cada archivo para optimizarlos y encontrar el punto dulce entre velocidad y precisión para señales biomédicas.
    - Medir el peso final (tamaño final) de los modelos y el tiempo de inferencia en CPU para asegurar que el conjunto ocupe menos de 1 MB (ej. ~90 KB para ECG, ~600 KB para caídas) y verificando que el tiempo combinado sea menor a 300 ms.

- **Objetivos por módulo:**

| **Módulo**        | **Tamaño objetivo** | **Inferencia objetivo** | **Referencia bibliográfica** |
| ----------------- | ------------------- | ----------------------- | ---------------------------- |
| **ECG/Arritmias** | ~90 KB              | <10 ms                  | Tiny MF-CNN (PMC 2023)       |
| **Caídas (IMU)**  | ~600 KB             | <100 ms                 | LiteFallNet (2025)           |
| **SpO2/PPG**      | ~412 KB             | <200 ms                 | Q-PPG TCN (ETH)              |

- **Duración:** 20 hs (1-2 semanas).

- **Resultados Esperados (Entregable):** Tres archivos convertidos (.tflite) menores a 1 MB en total, con tiempos de inferencia combinados menores a 300 ms.