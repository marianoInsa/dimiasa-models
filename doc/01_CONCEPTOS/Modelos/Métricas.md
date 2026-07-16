
La literatura científica sobre detección de caídas evalúa las métricas basándose en dos factores críticos: **el riesgo vital que supone no detectar una caída** y el **desbalance natural de los datos** (las caídas son eventos muy raros en comparación con las actividades normales diarias). 

Dado que *Sensibility* (Sensibilidad) y *Recall* (Exhaustividad) son términos matemáticamente equivalentes en este contexto [1, 2], a continuación se presenta la lista ordenada de la métrica más crítica y robusta a la menos descriptiva por sí sola:

**1. Sensibilidad (Sensibility / Recall)**
*   **Interpretación:** Mide la proporción de caídas reales (positivos) que el modelo logra predecir y "descubrir" correctamente [1, 3]. 
*   **Por qué es la prioridad número uno:** Los sistemas de detección de caídas son dispositivos a los que los usuarios confían sus vidas [1]. La literatura prioriza la sensibilidad porque **el peor escenario posible es un falso negativo** (que ocurra una caída real y el sistema no alerte) [1, 4]. Un modelo debe asegurar que la mayor cantidad posible de caídas sean descubiertas [1].

**2. F1-Score**
*   **Interpretación:** Es la media armónica que combina la Precisión y la Sensibilidad (Recall) en un solo valor [1, 5].
*   **Por qué es excelente:** Es considerado el indicador individual más robusto del rendimiento predictivo del modelo [3]. A diferencia de la exactitud, el F1-Score detalla el rendimiento por clase y permite evaluar las compensaciones de rendimiento, lo cual es fundamental para **conjuntos de datos altamente desbalanceados**, que son muy comunes en tareas activadas por sensores [1, 5].

**3. Especificidad (Specificity)**
*   **Interpretación:** Mide la proporción de actividades normales de la vida diaria (negativos reales) que son correctamente identificadas por el modelo como "no caídas" [1].
*   **Por qué es crítica:** En el mundo real, una mayor especificidad significa **menos falsas alarmas** [1]. Si un sistema tiene baja especificidad, generará alertas por movimientos bruscos normales, lo que provocará la "fatiga de alarmas" y el abandono del dispositivo por parte del usuario o el personal médico.

**4. Precisión (Precision)**
*   **Interpretación:** Mide la proporción de verdaderos positivos sobre el total de predicciones positivas; es decir, de todas las veces que el modelo gritó "¡Caída!", cuántas fueron caídas reales [1, 3].
*   **Por qué está en esta posición:** Una mayor precisión también indica menos falsas alarmas, pero la literatura señala que **la Precisión y la Sensibilidad son métricas que compiten entre sí** [1]. Si se ajusta un modelo para ser extremadamente preciso, podría volverse conservador y perder sensibilidad (no detectar caídas reales). Por ello, es mejor analizarla en conjunto dentro del F1-Score [1, 3].

**5. Exactitud (Accuracy)**
*   **Interpretación:** Es la proporción de todas las muestras (tanto caídas como no caídas) que el modelo predijo correctamente sobre el total de muestras [1, 3]. 
*   **Por qué es la "peor" métrica por sí sola:** Aunque evalúa el rendimiento global, la literatura la considera engañosa para sistemas críticos porque **se centra en el rendimiento general sin discriminar las clases** [1]. En un dataset donde el 98% de los datos son actividades normales y solo el 2% son caídas, un modelo inútil que siempre prediga "No caída" tendrá un 98% de exactitud (Accuracy), enmascarando el hecho de que es incapaz de detectar el evento crítico real [1, 5].

*Nota adicional de la literatura:* Para compensar las deficiencias de la Exactitud tradicional, algunos autores recomiendan usar la **Macro Average Accuracy (MAA)**, que es el promedio aritmético de la exactitud de cada tipo de actividad, permitiendo que cada clase (sin importar su volumen de datos) contribuya equitativamente a la evaluación [1].

**References:**
- [1] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Decade of Progress in Wearable Sensors for Fall Detection (2015–2024): A Network-Based Visualization Review - MDPI**: "ad) y *Recall* (Exhaustividad) son términos matemáticamente equivalentes e"
- [2] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Feature Engineering Method for Smartphone-Based Fall Detection - PMC**: " / Recall)**
*   **Interpretación:** Mide la proporción de caídas reales (positivos) que el modelo l..."
- [3] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate**: " [1, 3]. 
*   **Por qué es la prioridad número uno:** Los sistemas de detección de caídas son"
- [4] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Large-Scale Open Motion Dataset (KFall) and Benchmark Algorithms for Detecting Pre-impact Fall of the Elderly Using Wearable Inertial Sensors - Frontiers**: "dad porque **el peor escenario posible es un falso"
- [5] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate**: " negativo** (que ocurra una caída real y el sistema no alerte) [1, 4]. Un modelo de"
- [6] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Study of One-Class Classification Algorithms for Wearable Fall Sensors - PMC**: "tidad posible de caídas sean descubiertas [1].

**2. F1-Score**
*   **Interpretación:** E"
- [7] **A Feature Engineering Method for Smartphone-Based Fall Detection - PMC**: " combina la Precisión y la Sensibilidad (Recall) en un solo valor [1, 5].
*   **Por qué "
- [8] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Study of One-Class Classification Algorithms for Wearable Fall Sensors - PMC**: "r las compensaciones de rendimiento, lo cual es fundam"
- [9] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate**: "lanceados**, que son muy comunes en tareas activadas por sensores [1, 5].

**3. Especificidad (Speci..."
- [10] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate**
- [11] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Feature Engineering Method for Smartphone-Based Fall Detection - PMC**: ", lo que provocará la "fatiga de alarmas" y el abandono del dispositivo por parte del usuario o el p..."
- [12] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate**
- [13] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Feature Engineering Method for Smartphone-Based Fall Detection - PMC**: "*Por qué está en esta posición:** Una mayor precisión también indica menos falsas alarmas, pero la l..."
- [14] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Feature Engineering Method for Smartphone-Based Fall Detection - PMC**: "ente preciso, podría volverse conservador y perder sensibilidad (no detectar caídas reales). Por ell..."
- [15] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate**
- [16] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate, A Study of One-Class Classification Algorithms for Wearable Fall Sensors - PMC**: "muestras [1, 3]. 
*   **Por qué es la "peor" métrica por sí sola:** Aunque evalúa el rendimiento glo..."
- [17] **(PDF) Securing IoT Using Lightweight TCN for Edge Deployment on Raspberry Pi 4 - ResearchGate**: "uracy), enmascarando el hecho de que es incapaz de detectar el evento crítico real [1, 5].
