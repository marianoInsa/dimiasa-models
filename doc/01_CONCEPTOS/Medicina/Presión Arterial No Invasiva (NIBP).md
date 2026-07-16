---
tags:
  - medicina
---
# Concepto
> La **Presión Arterial No Invasiva (NIBP, por sus siglas en inglés)** es una de las métricas de signos vitales fundamentales que evalúa la presión ejercida por la sangre contra las paredes arteriales sin necesidad de insertar catéteres o líneas arteriales dentro del cuerpo. Se mide en milímetros de mercurio (mmHg) y proporciona dos lecturas específicas: la presión sistólica y la diastólica.

## Qué se mide
La **presión sistólica** y la **presión diastólica** son las dos lecturas específicas que componen la medición de la presión arterial, la cual es uno de los signos vitales fundamentales del cuerpo humano. Ambas presiones se miden en milímetros de mercurio (mmHg) y sus lecturas pueden verse afectadas por diversos factores fisiológicos, como la edad, el nivel de actividad, la medicación y el estado del sistema nervioso autónomo.

## Cómo se mide
Tradicionalmente, la NIBP se medía mediante el *método auscultatorio*, el cual depende de un profesional que escucha los sonidos arteriales (sonidos de Korotkoff) utilizando un estetoscopio y un manguito manual. Sin embargo, en la telemedicina moderna y los ecosistemas de [[Internet de las Cosas Médicas (IoMT)]], el estándar es el **método oscilométrico**. La oscilometría es preferida porque puede ser totalmente automatizada por microcontroladores y sigue siendo precisa en estados críticos donde los sonidos arteriales son inaudibles, como en vasoconstricciones severas.

El método oscilométrico automatizado funciona de la siguiente manera:

- **Captura física (Sensores y Actuadores):** Se utiliza un manguito oclusivo que se infla y desinfla automáticamente mediante una electroválvula y un microcompresor. Un sensor de presión integrado (como el MPX5050) monitorea los cambios.
- **Generación del Oscilograma:** A medida que la presión del manguito desciende gradualmente, las pulsaciones de la sangre en la arteria subyacente provocan **micro-oscilaciones en la presión del aire dentro del manguito**. Estas oscilaciones crecen hasta alcanzar un pico máximo (que representa la Presión Arterial Media o MAP) y luego disminuyen, formando una curva conocida como envolvente de oscilación u oscilograma.
- **Procesamiento Algorítmico Clásico (MAA):** El sistema utiliza el Algoritmo de Amplitud Máxima (MAA), el cual aplica proporciones matemáticas sobre la curva ascendente y descendente del oscilograma para deducir los valores exactos de la presión sistólica y diastólica.
- **Modelado Matemático Avanzado:** Debido a que el MAA tradicional asume relaciones fijas que pueden causar errores en ciertas poblaciones, los dispositivos IoMT de vanguardia aplican modelados deterministas avanzados directamente en el Borde (Edge Computing). Estos algoritmos calculan la **curva de distensibilidad arterial** de manera dinámica, compensando factores como la rigidez de las arterias en pacientes ancianos y logrando márgenes de error inferiores a 1.5 mmHg.

De manera alternativa, algunos relojes inteligentes comerciales (smartwatches) están comenzando a estimar la presión arterial utilizando **sensores ópticos (fotopletismografía o PPG)** que detectan variaciones en el volumen de sangre en los tejidos.

> [!WARNING]
> Sin embargo, aunque son útiles para el seguimiento diario, estas estimaciones ópticas no están diseñadas actualmente para reemplazar a los dispositivos médicos oscilométricos tradicionales.

---

#### Antes
![[presion arterial no invasiva (antes).png]]

#### Ahora (IoMT)
![[presion arterial no invasiva (despues).png]]

---
### Enlaces de Interés

* https://www.nature.com/articles/s41598-022-24264-9
* https://www.ahajournals.org/doi/10.1161/SVIN.122.000711

---
