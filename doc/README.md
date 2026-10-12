# DiMIASA: modelos para salud y ambiente

DiMIASA es un proyecto de investigación del Centro de Investigación Aplicada en Tecnologías de la Información y la Comunicación (CInApTIC), de la Universidad Tecnológica Nacional, Facultad Regional Resistencia. Estudia cómo usar sensores y modelos de inteligencia artificial para apoyar el monitoreo de la salud y el ambiente.

Este repositorio reúne análisis de datos, modelos y una prueba técnica en una placa ESP32. **No es un producto médico y sus resultados no reemplazan una evaluación clínica.**

## Qué se desarrolló

- **Detección de caídas:** preparación de cinco conjuntos de datos públicos y entrenamiento de modelos que distinguen caídas de actividades cotidianas.
- **Electrocardiograma (ECG):** clasificación de señales como normales o anormales y ejecución de un modelo compacto en una ESP32.
- **Fotopletismografía (PPG):** revisión de calidad de señal y estimación de frecuencia cardíaca. No se entrenó un modelo de oxígeno en sangre porque el conjunto disponible no tiene las señales y mediciones de referencia necesarias.
- **Prueba integrada:** reproducción de señales guardadas desde una computadora hacia la ESP32 por USB. No se usaron sensores conectados a una persona.

## Por dónde empezar

1. [Cómo preparar y usar el proyecto](uso.md)
2. [Qué datos y modelos utiliza](metodologia.md)
3. [Qué se verificó y qué limitaciones tiene](validacion.md)
4. [Fuentes de investigación](referencias.md)

Los detalles exactos de cada análisis están en los notebooks y el firmware que ejecuta cada proceso.
