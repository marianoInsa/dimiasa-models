# Entrenamiento del clasificador de caídas CNN-BiLSTM

> **Estado de verificación:** Cada referencia fue contrastada contra su registro editorial (septiembre de 2026); las afirmaciones sin respaldo directo en la literatura se marcan como decisiones propias del pipeline. Las fuentes primarias del proyecto se citan por su publicación oficial y tienen prioridad interpretativa sobre el resto de la bibliografía; la sección 15 mapea decisión por decisión.

Este documento describe, paso a paso y con su fundamento teórico, el pipeline de entrenamiento implementado en [01_Entrenamiento.ipynb](../../notebooks/pipeline/01_Entrenamiento.ipynb) (variante CPU, cuyos artefactos se describen en este documento: `comparison_results.json`, `set_{a,b}_final.keras` y `set_{a,b}_scaler.joblib`). El código del notebook es la fuente de verdad: cada vez que el texto descriptivo del propio notebook discrepa del código ejecutable, acá se documenta el código y la discrepancia se señala de forma explícita.

## 1. Introducción: de la capa oro al clasificador de ventanas

El punto de partida es la capa `oro/falls/` (`../../notebooks/data/oro/falls/`), generada por `00_Preprocesamiento.ipynb`: dos archivos Parquet con esquema estandarizado de 14 columnas (`Dataset, Subject, Activity_Label, Activity_Code, Trial, Sample_Index, Ax, Ay, Az, Gx, Gy, Gz, AVM, GVM`), ya remuestreados a 50 Hz y filtrados con un Butterworth de cuarto orden a 8 Hz (filtrado y resampleo en `00_Preprocesamiento.ipynb`, celda `90c5129c`). `set_a` agrega cinco datasets (SisFall, KFall, FallAllD, UP-Fall y UMAFall) con 8 841 016 filas (563.74 MB); `set_b` agrega los mismos cuatro datasets sin UMAFall, con 8 442 379 filas (537.70 MB) (salida de `cell-gold-export` en `00_Preprocesamiento.ipynb`). La fundamentación del preprocesamiento —remuestreo polifásico, umbrales de calidad, derivación de AVM y GVM— está documentada en [Fundamentación científica del pipeline de preprocesamiento](fundamentacion-literatura.md) y no se repite acá.

El modelo no clasifica caídas: clasifica **ventanas** de señal inercial. Cada ejemplo de entrenamiento es una matriz de 150 pasos temporales por 2 canales (`AVM`, `GVM`), es decir, 3.0 segundos de magnitud vectorial de aceleración y de giroscopio, con una etiqueta binaria `Fall`/`ADL`. Esta unidad de análisis es la habitual en reconocimiento de actividad humana (HAR) con sensores vestibles: un clasificador recibe vectores de longitud fija y decide sobre ellos (Bulling et al., 2014). La consecuencia operativa —y la limitación más importante de todo el pipeline— es que una caída real genera varias ventanas contiguas, de modo que el desempeño medido por ventana no equivale al desempeño por evento (Villa & Casilari, 2026). La sección 14 retoma este punto. El objetivo clínico del sistema completo es la alerta temprana en adultos mayores —las caídas son la segunda causa mundial de muerte por lesión no intencional (WHO, 2021)— con un triage multiagente en el borde (Gramajo et al., 2025, 2026; Baker et al., 2017); este documento cubre solo el clasificador.

La salida del modelo es una probabilidad por ventana, producida por una única neurona con activación sigmoide; la decisión final se toma comparando esa probabilidad contra un umbral fijo de 0.5 (celda `376edc2f`). Todo el flujo —ventaneo, etiquetado, submuestreo, escalado, partición, entrenamiento y métricas— se ejecuta dos veces, una por configuración (`set_a` y `set_b`), dentro del bucle de la celda `d96eb2d9`.

## 2. Configuración experimental

Las constantes que gobiernan el experimento se fijan en la celda `87a57b4c`. La tabla siguiente las reproduce tal como están en el código, con su significado:

| Constante | Valor | Significado |
| --- | ---: | --- |
| `FS` | 50 | Frecuencia de muestreo común de la capa oro (Hz). |
| `WINDOW_SEC` / `WINDOW_SIZE` | 3.0 s / 150 | Longitud de ventana (pasos temporales). |
| `WINDOW_STEP` | 75 | Paso de la ventana deslizante (solape del 50 %). |
| `PEAK_MARGIN_SEC` / `PEAK_MARGIN_SAMPLES` | 1.5 s / 75 | Margen alrededor del pico de AVM para etiquetar caída. |
| `N_FOLDS` | 5 | Folds de la validación cruzada. |
| `CHANNEL_COLS` / `N_CHANNELS` | `["AVM", "GVM"]` / 2 | Canales de entrada del modelo. |
| `MAX_TRAIN_WINDOWS_PER_CLASS` | 15 000 | Tope de ventanas por clase en el entrenamiento interno de cada fold. |
| `MAX_TEST_WINDOWS_PER_CLASS` | 5 000 | Tope de ventanas por clase en el test de cada fold. |
| `MAX_EPOCHS` | 200 | Épocas máximas de `fit`. |
| `PATIENCE` | 10 | Paciencia de `EarlyStopping` sobre `val_loss`. |
| `BATCH_SIZE` | 64 | Tamaño de lote. |
| `LEARNING_RATE` | 1e-3 | Tasa de aprendizaje de Adam. |

El tope de validación, en cambio, no es una constante: la celda `376edc2f` usa `max(500, MAX_TRAIN_WINDOWS_PER_CLASS // 15)`, es decir, 1000 ventanas por clase. La elección de topes (15k/1k/5k) responde a un presupuesto de cómputo en CPU y es una **decisión propia** del pipeline; el comentario del código lo declara ("subsampleo leve para acotar tiempo en CPU"). Ninguno de esos valores proviene de la literatura: son parámetros de viabilidad, y la sección 6 analiza su efecto estadístico.

**Prosa del notebook corregida (sep-2026).** Los markdown del notebook describían otra corrida (`lr=5e-4`, `batch=128`, `epochs=15`, `patience=5`); en la revisión de septiembre de 2026 se alinearon con el código ejecutable (`lr=1e-3`, `batch=64`, tope de 200 épocas con `EarlyStopping(patience=10)`), que es el que se documenta acá.

## 3. Taxonomía unificada: F1–F10 como herramienta de diagnóstico

Antes de ventanear, la celda `d96eb2d9` aplica `map_to_unified_taxonomy()` (celda `f338e58c`), que agrega la columna `Fall_Type_Unified` con los grupos F1–F10 definidos en la [Taxonomía unificada](taxonomía-unificada.md). El mapeo se construye con un diccionario `(Dataset, Activity_Code) → grupo` que preserva los códigos originales de cada corpus:

| Grupo | SisFall | KFall | FallAllD (códigos enteros) | UP-Fall | UMAFall |
| --- | --- | --- | --- | --- | --- |
| F1 · Resbalón caminando | F01–F03 | F13–F15 | 103–110, 123–126 | — | — |
| F2 · Tropiezo caminando | F04 | F11 | 101, 102, 121, 122 | — | — |
| F3 · Tropiezo trotando | F05 | F12 | — | — | — |
| F4 · Síncope caminando/de pie | F06, F07 | F09, F10 | 111–114, 132–135 | — | — |
| F5 · Caída al intentar sentarse | F10–F12 | F01–F03 | 115–120 | 5 | — |
| F6 · Caída al intentar levantarse | F08, F09 | F04, F05 | — | — | — |
| F7 · Síncope estando sentado | F13–F15 | F06–F08 | 129–131 | — | — |
| F8 · Caída desde la cama | — | — | 127, 128 | — | — |
| F9 · Solo dirección | — | — | — | 3, 4 | forwardFall, backwardFall, lateralFall |
| F10 · Solo mecanismo de impacto | — | — | — | 1, 2 | — |

La taxonomía agrupa por mecanismo biomecánico y no reinterpreta las etiquetas de los datasets que aportan menos detalle (Noury et al., 2008; Kellogg International Work Group on the Prevention of Falls by the Elderly, 1987): UP-Fall y UMAFall solo informan dirección o forma de impacto, y por eso quedan en F9/F10 sin forzar equivalencias (Sucerquia et al., 2017; Yu et al., 2021; Saleh et al., 2021; Martínez-Villaseñor et al., 2019; Casilari et al., 2017). Un detalle del mapeo: los códigos A123–A126 de FallAllD, cuya descripción oficial dice *slipping*, se asignan a F1 (resbalón) y no a F2, corrigiendo una versión anterior de la agrupación (comentario del docstring en `f338e58c`).

Dos puntos de rigor importantes:

1. **La taxonomía no es el target del modelo.** El modelo se entrena con `Activity_Label` binario (`Fall`/`ADL`), no con F1–F10. Los grupos se usan **solo con fines diagnósticos**: se arrastran por fold (`ft_test` en la celda `376edc2f`) y se muestran como "top-3 grupos por cuadrante" en la matriz de confusión agregada (celda `a195351f`). Es un instrumento de lectura de errores, no una salida del clasificador.
2. **Queda ruido de etiquetas residual.** Si un código de caída no está en el diccionario, `Fall_Type_Unified` recibe el valor `UNMAPPED`; la celda `d96eb2d9` cuenta esas filas y las imprime con sus códigos de origen. Para las actividades cotidianas se asigna `ADL`. Las abreviaturas de dos letras usadas en los gráficos (`TAXONOMY_ABBR`: `RC`, `TC`, `TT`, `SC`, `CS`, `CL`, `SS`, `CC`, `SD`, `SM`, `ADL`) se definen también en `f338e58c`.

Vale la pena recordar una asimetría documentada en la taxonomía: la clase A11 (cuasi-caída, "tropiezo sin caer") está presente en SisFall, KFall y FallAllD, pero ausente en UP-Fall y UMAFall. Como es el tipo de movimiento que más se confunde con una caída real, la especificidad medida depende de la composición del corpus (taxonomía unificada, "Consideraciones"). La dirección de la caída tampoco es una salida del modelo: clasificarla mejora significativamente al combinar 2–3 sensores (Teng et al., 2024), y acá el corpus la aporta solo de forma parcial para el diagnóstico F9.

## 4. Ventaneo: ventana deslizante dentro de cada trial

El ventaneo ocurre en `create_windows()` (celda `c5c956fc`). El dataframe se recorre agrupando por `["Dataset", "Subject", "Activity_Code", "Trial"]` y cada grupo se ordena por `Sample_Index`; las ventanas se extraen **dentro de cada trial** y nunca lo cruzan. Esta decisión evita que una ventana mezcle el final de un movimiento con el comienzo de otro, lo que produciría etiquetas ambiguas, y mantiene consistente la unidad de agrupación usada después en la partición.

Para un trial de $L$ muestras, con ventana $W=150$ y paso $S=75$, la cantidad de ventanas es:

$$
N = \left\lfloor \frac{L - W}{S} \right\rfloor + 1
$$

Por ejemplo, un trial de 500 muestras (10 s) produce $\lfloor 350/75 \rfloor + 1 = 5$ ventanas; uno de exactamente 150 muestras produce 1. Los trials con $L < W$ se descartan (`if n < window_size: continue`), lo que elimina ventanas incompletas pero sesga el corpus hacia los trials largos.

El solape del 50 % (paso igual a media ventana) es la convención más difundida en HAR y duplica el número de ventanas, pero **no agrega información independiente**: ventanas consecutivas comparten la mitad de las muestras y sus errores están correlacionados, por lo que funcionan como pseudo-réplicas. Esa correlación es la razón por la que la partición debe agrupar por sujeto y no por ventana, como se explica en la sección 10.

La longitud de 3.0 s es un compromiso entre contexto y latencia. Banos et al. (2014), barriendo ventanas de 0.25 a 7 s con varios clasificadores clásicos, encontraron el mejor compromiso en 1–2 s; Gu et al. (2011) usaron cortes de hasta 15 s para actividades compuestas; Ordóñez y Roggen (2016) emplearon ventanas de 500 ms en su DeepConvLSTM. La ventana elegida acá es más larga que el óptimo clásico de HAR: gana contexto (permite ver pre-impacto, impacto y post-impacto dentro de la misma ventana) pero, con paso 75, la decisión se refresca cada 1.5 s, mientras que la detección pre-impacto de la literatura necesita adelantos del orden de 0.3–0.4 s (Yu et al., 2021). Se trata de una **decisión propia con respaldo convergente**: Guo y Nakayama (2025) optimizan una ventana de 3 s con dos sub-ventanas al 50 % de solape y reportan caídas de 3–10 % de F1 al pasar a 1–2 s; Ponce et al. (2020) eligen 2–3 s para caídas de ~2 s; Santoyo-Ramón et al. (2022b) segmentan 3 s centradas en el pico de SMV; Villa y Casilari (2026) usan 4 s. La tasa de 50 Hz excede lo necesario para la dinámica: en HAR la exactitud de las características de aceleración se estabiliza a 15–20 Hz (Maurer et al., 2006). Aun así está orientada a un clasificador *offline* por ventana, no a un detector causal de baja latencia.

Finalmente, `build_group_id()` (misma celda) construye `Group_ID = Dataset + "_" + Subject`, la unidad que usarán todos los separadores de la validación cruzada. Agrupar por sujeto y dataset es lo que evita que la misma persona (y su sensor, su complexión, su forma de caminar) aparezca a la vez en entrenamiento y test.

## 5. Etiquetado por pico de AVM

La caída es un evento con inicio e impacto, no una clase estacionaria; etiquetar ventanas exige un criterio de vecindad temporal. El pipeline implementa un **etiquetado débil por proximidad al pico** (celda `c5c956fc`):

- Para cada trial de caída se calcula `peak_idx = argmax(AVM)`, el índice de la muestra con mayor magnitud de aceleración.
- La ventana se etiqueta positiva ($y=1$) si su **centro** $c$ cumple $|c - p| \le 75$ muestras con $p$ el índice del pico, es decir, dentro de ±1.5 s.
- Todas las ventanas de trials `ADL` son negativas. Las ventanas de un trial de caída fuera del margen del pico también son negativas: el comentario del código las describe como "caminar pre/post impacto, reposo".

Sobre la rejilla de centros (paso 75) una caída puede marcar hasta tres ventanas positivas (desfasajes de −75, 0 y +75 muestras) y típicamente una o dos; en trials cortos, una sola. La elección de ±1.5 s es una **decisión propia**, dentro del rango de márgenes alrededor del pico que la literatura ha explorado: Casilari et al. (2020) evaluaron márgenes de ±0.5, ±1, ±1.5 y ±2.5 s alrededor del pico de AVM.

El pico de AVM es un ancla razonable porque la magnitud vectorial de aceleración es invariante a la orientación del sensor y es la señal estándar de la detección de caídas (Sucerquia et al., 2017; Tsinganos & Skodras, 2018). Aun así, el etiquetado es **débil** y arrastra ruido:

- El margen tolera desalineaciones de anotación (la verdad temporal del evento es difusa), pero vuelve positivas ventanas que quizá no contienen el impacto, y deja como negativas ventanas de un trial de caída que sí contienen dinámica de caída. En la taxonomía de Frénay y Verleysen (2014), son etiquetas incorrectas o ambiguas; su survey señala que el ruido de etiquetas degrada el rendimiento de los clasificadores y exige más datos para compensarlo.
- KFall es el único corpus del set con etiquetas temporales semiautomáticas de inicio e impacto validadas por video (Yu et al., 2021); para el resto, el pico de AVM es la mejor aproximación disponible. La anotación de caídas reales de FARSEEING usó doble evaluador ciego con certeza graduada (Klenk et al., 2016), y la alternativa supervisada de tres clases —no caída, pre-impacto y caída— fue desarrollada sobre señales vestibles por Yu, Qiu y Xiong (2020).
- Como los positivos son ventanas **solapadas** alrededor del mismo pico, la clase positiva queda sobrerrepresentada en ventanas correlacionadas. Cuando la caída dura poco y la ventana es de 3 s, casi todas las ventanas del trial se vuelven positivas y la tarea se aproxima más a "trial de caída vs. ADL" que a "instante de caída vs. resto". Es una simplificación deliberada, y conviene declararla al interpretar las métricas.

Una alternativa teóricamente más fiel sería etiquetar por fracción del evento (positiva si al menos el 50 % de la ventana cae dentro del intervalo de caída), pero exige fronteras precisas que solo KFall provee de forma completa.

## 6. Submuestreo por clase

Con el ventaneo, el desbalance aparece aunque los corpus estén "balanceados" en cantidad de archivos: las caídas duran aproximadamente un segundo y las actividades cotidianas minutos, de modo que las ventanas de caída suelen quedar en torno al 10 % o menos del total. El código imprime ese ratio al ventanear (`ratio Fall` en `c5c956fc`). Con desbalance severo, la exactitud es engañosa: un detector que siempre responde "no caída" alcanza la prevalencia de ADL como exactitud con sensibilidad nula —la paradoja de la exactitud (He & Garcia, 2009; Johnson & Khoshgoftaar, 2019).

La estrategia elegida es **submuestreo aleatorio por clase** (`subsample()`, celda `c5c956fc`): para cada clase se conservan todas las ventanas si no superan el tope, o se eligen `max_per_class` índices sin reemplazo con un generador `np.random.default_rng(seed)`. Los topes son 15 000 (train interno), 1000 (validación) y 5000 (test) por clase. Las semillas son explícitas: `seed=fold_idx` para train, `fold_idx + 100` para validación y `fold_idx + 200` para test dentro de la CV; `seed=42` en el entrenamiento final (celdas `376edc2f` y `1436bd9b`). Frente a la generación sintética (SMOTE; Chawla et al., 2002), el submuestreo no inventa señales fisiológicamente imposibles ni interpola ventanas de sujetos distintos; frente a los pesos de clase, descarta información, que es justamente lo que la ponderación de la pérdida evita (sección 9). Zhang et al. (2021) proponen y comparan técnicas de desbalance (pesos de clase, SMOTE, focal loss y ajuste de umbral) sobre señales vestibles; el efecto depende del grado de desbalance y del modelo (Johnson & Khoshgoftaar, 2019). Sobre estos corpus hay precedentes de cada alternativa: SMOTE en entrenamiento (Guo & Nakayama, 2025), pesos inversos a la frecuencia de clase (Fula & Moreno, 2024) y focal loss (Yu, Qiu & Xiong, 2020); Fula y Moreno (2024) reportan un 4.46 % de muestras (ventanas) de caída en su corpus combinado, un orden de magnitud coherente con el ~10 % de este pipeline.

Dos efectos que conviene tener presentes:

1. **El orden importa.** En `run_experiment()` primero se particiona (por grupos) y después se submuestrea dentro de cada partición. Así, el submuestreo nunca mezcla sujetos entre train y test: solo selecciona ventanas ya asignadas.
2. **El prior del test cambia.** El test conserva todas las ventanas Fall disponibles (1 812–1 992 por fold) y aplica un tope de 5 000 ventanas ADL, es decir, queda con una prevalencia de ≈27 % Fall en lugar del ~10 % natural. Esto no invalida la sensibilidad ni la especificidad, que son invariantes al prior, pero sí la precisión (PPV) y la exactitud, que dependen de él. La sección 11 desarrolla esta distinción, que es la clave para no sobreinterpretar los resultados.

## 7. Escalado z-score por canal

Las redes neuronales optimizan mejor cuando las entradas están centradas y escaladas. `fit_scaler()` (celda `c5c956fc`) ajusta un `StandardScaler` de scikit-learn sobre los datos de entrenamiento reordenados como `(n·t, c)`; `apply_scaler()` aplica la transformación y devuelve la forma `(n, t, c)`. Por canal, la transformación es:

$$
z = \frac{x - \mu_{\text{train}}}{\sigma_{\text{train}}}
$$

`StandardScaler` usa la desviación estándar poblacional (ddof = 0) y guarda `mean_` y `scale_` para reutilizarlos en `transform` (scikit-learn developers, s.f.-c). El punto crítico es el alcance del ajuste: en la validación cruzada, `fit_scaler()` se llama **solo con el train interno de cada fold** (`inner_train`, ya separado del test y de la validación interna), y luego se aplica a train, validación y test con esas estadísticas congeladas (celda `376edc2f`). Ajustar el escalador con todo el dataset filtraría media y desviación del test hacia el train y produciría estimaciones optimistas: es la fuga de preprocesamiento clásica, que scikit-learn documenta como "nunca llamar a `fit` sobre el test" (scikit-learn developers, s.f.-b; Kaufman et al., 2012).

¿Por qué importa en una red y no solo en modelos lineales? Centrar y escalar homogeneíza la curvatura de la superficie de pérdida en cada eje y mejora el condicionamiento del problema de optimización, evitando que un canal con amplitudes grandes domine el gradiente por el solo hecho de tener otra unidad (Goodfellow et al., 2016). En este pipeline `AVM` está en g y `GVM` en °/s: órdenes de magnitud distintos que, sin escalado, entrarían en la primera convolución con escalas incomparables. Dos matices de la literatura: Fula y Moreno (2024) hallaron que normalizar su señal a [−1, 1] degradó el F1 de su red (69.9 % → 48.7 %), y Santoyo-Ramón et al. (2022a) observaron que el z-score no siempre ayuda porque atenúa picos; el escalado no es una mejora universal, sino una decisión que debe verificarse en cada pipeline.

En inferencia, la transformación debe ser exactamente la misma que en entrenamiento. Por eso el escalador no se descarta: se persiste junto al modelo con `joblib` (sección 12) y se aplica antes de predecir. El formato `.keras` no incluye preprocesamiento, así que el par `modelo + scaler` es la unidad desplegable (Keras team, 2023).

## 8. Arquitectura CNN-BiLSTM

### 8.1 Capas y fundamento

`build_cnn_bilstm()` (celda `80d503d9`) construye un `Sequential` con la siguiente pila. Los conceptos de cada bloque están desarrollados en [Modelo CNN](../01_CONCEPTOS/Modelos/Modelo%20CNN.md), [Modelo LSTM](../01_CONCEPTOS/Modelos/Modelo%20LSTM.md) y [Modelo CNN-LSTM](../01_CONCEPTOS/Modelos/Modelo%20CNN-LSTM.md):

| # | Capa | Configuración | Rol |
| --- | --- | --- | --- |
| 0 | `Input` | (150, 2) | Ventana de AVM y GVM. |
| 1 | `Conv1D` | 32 filtros, kernel 7, `same`, `use_bias=False` | Patrones locales de ~140 ms. |
| 2 | `BatchNormalization` | — | Estabiliza la escala de activaciones. |
| 3 | `ReLU` | — | No linealidad. |
| 4 | `Conv1D` | 64 filtros, kernel 5, `same`, `use_bias=False` | Patrones de ~100 ms. |
| 5 | `BatchNormalization` | — | — |
| 6 | `ReLU` | — | — |
| 7 | `MaxPooling1D` | pool 2 | Reduce la longitud a 75; invariancia local. |
| 8 | `Conv1D` | 64 filtros, kernel 3, `same`, `use_bias=False` | Patrones de ~60 ms. |
| 9 | `BatchNormalization` | — | — |
| 10 | `ReLU` | — | — |
| 11 | `MaxPooling1D` | pool 2 | Reduce la longitud a 37. |
| 12 | `Bidirectional(LSTM(64))` | — | Dinámica temporal en ambos sentidos; salida de 128 dimensiones. |
| 13 | `Dropout` | 0.4 | Regularización. |
| 14 | `Dense(1, sigmoid)` | — | Probabilidad de caída. |

**Convoluciones 1D.** Una `Conv1D` desliza un kernel de pesos compartidos sobre el eje temporal: $y[i] = \phi\left(\sum_c \sum_{k=0}^{K-1} W[k,c]\, x[i \cdot s + k, c] + b\right)$. El peso compartido impone **invariancia a la traslación**: un pico de impacto se detecta igual al principio o al final de la ventana, algo deseable porque la caída no ocurre en una posición fija. `padding="same"` conserva la longitud de salida ($L_{out} = \lceil L/s \rceil$) rellenando con ceros los bordes, a costa de contexto artificial en los extremos (Keras team, s.f.-a). Las capas convolucionales aprenden representaciones jerárquicas directamente de aceleración y giroscopio, superando a las características heurísticas en HAR (Ordóñez & Roggen, 2016; Yang et al., 2015). En el panorama agregado, Gorce y Jacquier-Bret (2025) hallan en su revisión PRISMA que el aprendizaje profundo obtiene los mejores resultados globales en las cinco métricas que comparan, aunque sin superioridad clara sobre los umbrales en exactitud y especificidad y sin efecto significativo en sensibilidad.

**`use_bias=False` y Batch Normalization.** En cada convolución se omite el sesgo porque la capa de normalización que sigue incluye un parámetro $\beta$ que lo subsume: la BN original ya señala que el sesgo puede ignorarse cuando precede una normalización (Ioffe & Szegedy, 2015). BN normaliza cada activación por mini-lote ($\hat{x} = (x-\mu_B)/\sqrt{\sigma_B^2+\varepsilon}$, luego $y = \gamma \hat{x} + \beta$) y, en inferencia, usa medias y varianzas móviles. Su beneficio real no es tanto el "internal covariate shift" original como el suavizado del paisaje de optimización, con gradientes más predecibles (Santurkar et al., 2018).

**ReLU.** $f(x) = \max(0, x)$ tiene gradiente 1 en la región positiva, no satura y produce representaciones dispersas, lo que permite apilar capas profundas sin el desvanecimiento del gradiente de las sigmoides (Nair & Hinton, 2010; Glorot et al., 2011).

**Max pooling.** `MaxPooling1D(pool_size=2)` toma el máximo en ventanas contiguas de dos posiciones: reduce la dimensión temporal (150 → 75 → 37), introduce invariancia local a pequeñas traslaciones y amplifica el campo receptivo. Para caídas, retener la activación dominante tiene sentido: los picos de impacto y de velocidad angular son la firma discriminativa.

**BiLSTM.** La LSTM resuelve el desvanecimiento del gradiente de las RNN simples con un estado de celda de flujo casi constante y compuertas multiplicativas (Hochreiter & Schmidhuber, 1997; Gers et al., 2000): $f_t = \sigma(W_f[h_{t-1}, x_t] + b_f)$, $i_t = \sigma(W_i[\cdot] + b_i)$, $o_t = \sigma(W_o[\cdot] + b_o)$, $c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t$, $h_t = o_t \odot \tanh(c_t)$. La variante bidireccional procesa la secuencia en los dos sentidos y concatena ambas salidas, $h_t = [\overrightarrow{h_t}; \overleftarrow{h_t}]$ (Graves & Schmidhuber, 2005). Como este pipeline es *offline* —clasifica una ventana completa ya grabada—, el contexto futuro está disponible y ayuda a desambiguar las fases de la caída (pre-impacto, impacto, inactividad). En un detector causal en tiempo real la rama backward no sería computable y correspondería una LSTM unidireccional o una TCN causal. La combinación CNN + recursiva es la arquitectura de referencia del HAR vestible (Ordóñez & Roggen, 2016); en la detección de marcha anormal asociada a riesgo de caída —no de caídas—, Kiprijanovska et al. (2020) reportan que CNN+BiLSTM supera a cada componente por separado. Sobre datos vestibles, Yu, Qiu y Xiong (2020) combinan bloques convolucionales con LSTM para pre-impacto, y Gaud et al. (2025) reportan una BiLSTM sobre SisFall; este último se cita solo como precedente arquitectónico, porque sus resultados son internamente inconsistentes (99.68 % de exactitud en el abstract y la Tabla V frente a 98.78 % en la conclusión en prosa del mismo trabajo).

**Dropout.** Con probabilidad 0.4 se apagan unidades en cada paso de entrenamiento, lo que impide la co-adaptación de características y aproxima un ensamble exponencial de subredes; en inferencia se usa la red completa con el escalado correspondiente (Srivastava et al., 2014). Su ubicación —una sola vez, después del BiLSTM y antes de la capa densa— es la práctica habitual: el dropout recurrente degrada la memoria temporal y el dropout sobre la misma activación que BN introduce varianza inconsistente entre train e inferencia.

**Capa de salida.** Una neurona con sigmoide, $p = \sigma(z) = 1/(1+e^{-z})$, parametriza un Bernoulli condicional. Para clasificación binaria, `sigmoid` más entropía cruzada binaria es la parametrización estándar y algebraicamente equivalente a un softmax de dos clases con un parámetro redundante (Goodfellow et al., 2016). La probabilidad resultante requiere calibración para leerse como posterior; en este pipeline se usa directamente contra un umbral (sección 9).

### 8.2 Campo receptivo

El campo receptivo se calcula con la fórmula recursiva; con $r_0 = 1$ y $j_0 = 1$:

$$
r_{out} = r_{in} + (k-1)\cdot j_{in}, \qquad j_{out} = j_{in} \cdot s
$$

| Capa | $k$ | $s$ | $r_{in}$ | $r_{out}$ | $j_{out}$ |
| --- | ---: | ---: | ---: | ---: | ---: |
| Conv1D 32 | 7 | 1 | 1 | 7 | 1 |
| Conv1D 64 | 5 | 1 | 7 | 11 | 1 |
| MaxPooling1D | 2 | 2 | 11 | 12 | 2 |
| Conv1D 64 | 3 | 1 | 12 | 16 | 2 |
| MaxPooling1D | 2 | 2 | 16 | **18** | **4** |

El campo receptivo teórico de cada paso temporal a la entrada del BiLSTM es de **18 muestras** (0.36 s). La longitud de la señal evoluciona 150 → 150 → 150 → 75 → 75 → 37, de modo que el BiLSTM recibe 37 pasos y cada paso "ve" 18 muestras de entrada; el salto acumulado es $j = 4$, así que la secuencia completa cubre $37 \times 4 = 148$ muestras, prácticamente toda la ventana de 150. Para una caída, esa combinación es adecuada: la CNN aporta la morfología local del impacto (0.36 s por paso) y la BiLSTM integra la secuencia completa. (El docstring del notebook se corrigió en septiembre de 2026: antes declaraba ~52 muestras por una heurística que sumaba los kernels y multiplicaba por el submuestreo.)

## 9. Entrenamiento: pérdida, optimizador y callbacks

**Pérdida.** `model.compile()` usa `loss="binary_crossentropy"`, que con los pesos de clase $w_{y_i}$ que inyecta Keras toma la forma:

$$
\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N} w_{y_i}\left[ y_i \log p_i + (1-y_i)\log(1-p_i) \right]
$$

Minimizar la BCE equivale a maximizar la verosimilitud de un modelo Bernoulli condicional, es decir, es el criterio de máxima verosimilitud para esta tarea (Goodfellow et al., 2016).

**`class_weight={0: 2.0, 1: 1.0}`.** El comentario del código (celda `376edc2f`) declara su motivo: "compensa subsampleo 50/50 hacia la distribución natural (~10% Fall): ADL pesa 2x". La corrida documentada no quedó 50/50: el train contiene 15 000 ventanas ADL (tope) y todas las Fall disponibles (6 553–7 100 por fold; 6 553 en el fold 1 de `set_a`), una prevalencia de ≈30–32 % Fall sobre la que el peso 2:1 se suma. En la práctica, cada error en la clase 0 pesa el doble que uno en la clase 1: con el train real (~30 % Fall), la contribución efectiva a la pérdida queda en ≈4.4:1 ADL:Fall (2 × 15 000 frente a ~6 800), lo que aproxima el prior efectivo a ≈18 %, más cerca del ~10 % natural que del ~30 % del set, aunque sin restaurarlo exactamente. En la regla de decisión sensible al costo, ponderar la clase mayoritaria endurece el umbral para declarar caída: la clase 1 se predice cuando la probabilidad supera $p^* = w_0/(w_0+w_1) = 2/3$ en lugar de 0.5, es decir, el peso vuelve al detector más conservador para la clase minoritaria que un entrenamiento sin ponderar. El valor 2.0 es una **decisión propia**, no una restitución exacta del prior natural. La documentación de Keras indica que `class_weight` pondera la pérdida *during training only*; la advertencia literal sobre métricas sin ponderar (`weighted_metrics`) corresponde a `sample_weight`, no a `class_weight`, por lo que la `accuracy` de `fit` que se ve en consola no está ponderada (Keras team, s.f.-c).

**Optimizador.** `Adam(learning_rate=1e-3)` con el resto de parámetros en sus valores por defecto. Adam mantiene medias exponenciales del gradiente y de su cuadrado, corrige el sesgo de inicialización y actualiza:

$$
m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t, \qquad
v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2
$$

$$
\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \qquad
\hat{v}_t = \frac{v_t}{1-\beta_2^t}, \qquad
\theta_t = \theta_{t-1} - \alpha \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \varepsilon}
$$

con $\beta_1 = 0.9$, $\beta_2 = 0.999$ y $\varepsilon$ en su valor por defecto de Keras (Kingma & Ba, 2015; Keras team, s.f.-c). Su ventaja práctica en un pipeline pequeño es la convergencia rápida y robusta al escalado de gradientes sin *schedule* manual. Un paralelo útil: Yu, Qiu y Xiong (2020) entrenan con batch 64 y 200 épocas —igual que acá— pero con focal loss y tasa 5e-4.

**Bucle de `fit`.** Hasta 200 épocas, `batch_size=64`, con el barajado por defecto de Keras (`shuffle=True`), que reordena las muestras cada época y evita sesgos por orden (Keras team, s.f.-c). Un lote más grande da un gradiente más estable a costa de menos actualizaciones por época; 64 es un compromiso habitual.

**Callbacks.**

- `EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)`: detiene el entrenamiento cuando la pérdida de validación deja de mejorar durante 10 épocas y restituye los pesos de la mejor época (Keras team, s.f.-b). Sin `restore_best_weights`, Keras conserva los pesos de la última época, que no son los mejores. Prechelt (1998) estudia el compromiso de los criterios de parada: detener el entrenamiento antes ahorra cómputo, pero puede costar generalización promedio.
- `ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, min_lr=1e-6)`: tras 4 épocas sin mejora, multiplica la tasa de aprendizaje por 0.5, hasta un piso de $10^{-6}$. La lógica es explorar pasos grandes al principio y refinar después (Keras team, s.f.-d).



**Umbral.** La predicción se obtiene con `(model.predict(...) >= 0.5)`, un umbral fijo. El umbral 0.5 solo es óptimo cuando los costos de ambos errores y las prevalencias son simétricos (Saito & Rehmsmeier, 2015); acá no lo son: no detectar una caída (FN) puede dejar a una persona lesionada sin auxilio, mientras que una falsa alarma (FP) es una molestia. A eso se suma la interacción con `class_weight`: el peso endurece el umbral efectivo para declarar caída (sección 9, $p^* = 2/3$ sobre la probabilidad no ponderada), de modo que el 0.5 aplicado a la salida ponderada es coherente con el objetivo usado al entrenar —donde el falso positivo pesa el doble— pero no con la prioridad operativa de maximizar la sensibilidad. El umbral no se optimiza en este pipeline: es un valor operativo por defecto, y ajustarlo es una de las mejoras pendientes que scikit-learn documenta como parte del ciclo de vida del clasificador (scikit-learn developers, 2026b).

## 10. Validación cruzada y control de fugas de información

La evaluación se organiza con `run_experiment()` (celda `376edc2f`):

1. `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` reparte los grupos (`Group_ID`) en 5 folds. La estratificación preserva, en la medida de lo posible, la proporción de clases de cada fold, y la restricción de grupos evita que un mismo sujeto aparezca en train y test a la vez (scikit-learn developers, s.f.-a, s.f.-d). La implementación es greedy —asigna grupos de mayor a menor varianza de frecuencias de clase— y exige al menos tantos grupos como folds; con más de cien pares dataset-sujeto, esa condición se cumple con holgura.
2. Dentro de cada fold, un `GroupShuffleSplit(n_splits=1, test_size=0.1, random_state=fold_idx)` separa un 10 % de los grupos de entrenamiento como validación interna para los callbacks. El resto es el `inner_train`.
3. Salvaguarda de mezcla: el fold registra e imprime los datasets y las etiquetas presentes en el train interno, y advierte si falta alguno ("Data mixing"). Es un chequeo de sanidad del experimento, no un cambio automático de la partición.
4. Recién entonces se submuestrea cada partición (sección 6), se ajusta el escalador con `inner_train` (sección 7), se construye un modelo nuevo, se entrena y se predice el test.
5. Tras cada fold se liberan las referencias (`del model, Xtr, Xva, Xte`) y se llama a `tf.keras.backend.clear_session()`, que reinicia el estado global de Keras (nombres de capas, grafos) y libera memoria, evitando fugas de estado entre folds (TensorFlow, s.f.-a).

**Semillas.** Son explícitas para las particiones y el submuestreo: `random_state=42` en `StratifiedGroupKFold`, `random_state=fold_idx` en el `GroupShuffleSplit` interno, semillas `fold_idx`, `fold_idx + 100` y `fold_idx + 200` en los submuestreos de train, validación y test, y `seed=42` en el submuestreo del modelo final. El notebook fija la semilla global con `tf.keras.utils.set_random_seed(42)` (celda `87a57b4c`): inicialización de pesos, barajado y dropout quedan determinados para una misma secuencia de ejecución (Keras team, s.f.-e; TensorFlow, s.f.-b). La reproducibilidad es alta dentro de una corrida; entre notebooks con distinto orden de creación de modelos los pesos pueden diferir aunque la semilla sea la misma.

**¿Qué fugas evita este protocolo y por qué importa?** Kaufman et al. (2012) definen la fuga como la introducción de información sobre el objetivo que no debería estar legítimamente disponible y que rompe el supuesto de independencia entre train y test. En este problema hay cuatro fuentes potenciales:

- **Por sujeto:** rasgos personales (marcha, complexión, colocación del sensor) hacen que un mismo sujeto en train y test infle las métricas. El estándar de generalización a usuarios nuevos es el protocolo *subject-wise* —y su extremo, dejar un sujeto afuera (*LOSO*)—; acá se implementa con `Group_ID = Dataset + Subject`.
- **Por ventana solapada:** ventanas con 50 % de solape son casi duplicados. Un split aleatorio por ventana repartiría muestras hermanas entre train y test; el ventaneo intra-trial más la agrupación por sujeto lo impiden.
- **Por preprocesamiento:** ajustar el escalador con todo el dataset (sección 7).
- **Temporal:** con `shuffle` el "futuro" entrena el "pasado". Para un despliegue realista sobre series continuas haría falta un corte temporal; acá se evalúa por ventanas y con mezcla aleatoria de grupos, lo cual es una limitación que se declara.

Un contraste instructivo: UP-Fall evalúa con validación cruzada de 10 folds **por muestra** (Martínez-Villaseñor et al., 2019), partición que reparte ventanas del mismo sujeto y del mismo trial entre train y test —exactamente la fuga que el `Group_ID` evita—, mientras que Fula y Moreno (2024) usan k = 10 agrupada por sujeto. La lección metodológica es doble: la partición por muestra infla las métricas aunque el dataset sea de laboratorio (Martínez-Villaseñor et al., 2019) y el sobreaprendizaje al testbed se confirma al evaluar cross-dataset (Santoyo-Ramón et al., 2022a).

Con `Group_ID = Dataset + Subject`, los folds separan conjuntos de pares dataset-sujeto, pero **no garantizan evaluación cross-dataset**: si un dataset aporta sujetos a varios folds, el modelo ve ese corpus en train y en test. La única salvaguarda es la advertencia de "Data mixing" cuando un dataset desaparece por completo del train de un fold. La evaluación cross-dataset es el escenario más exigente y muestra degradaciones severas en la literatura: Santoyo-Ramón et al. (2022a) documentan que los clasificadores sobreaprenden las condiciones del dataset de entrenamiento, y Silva et al. (2024) reportan sensibilidad menor a 0.5 frente a caídas reales en la mayoría de los clasificadores entrenados con datos de laboratorio. El notebook principal no la implementa; el experimento `01_Entrenamiento_2.ipynb` evalúa UMAFall como holdout externo (resultados en la sección 13).

La CV de 5 folds con agregación media ± desvío es estándar (Stone, 1974; Kohavi, 1995). Con solo 5 folds, la desviación estándar es una estimación ruidosa, por lo que conviene reportar también los valores por fold. Como los hiperparámetros son fijos y no se eligen mirando la validación, no hay sesgo de selección que exija validación cruzada anidada; si en el futuro se ajustaran umbral, arquitectura o tamaño de submuestreo contra la validación, correspondería anidar (Varma & Simon, 2006).

## 11. Métricas y lectura correcta

`compute_metrics()` (celda `027ecd76`) calcula a mano TP, FN, TN y FP y deriva tres métricas de la matriz de confusión (la lectura de métricas en detección de caídas está desarrollada en [Métricas](../01_CONCEPTOS/Modelos/Métricas.md)):

$$
\text{Sensibilidad} = \frac{TP}{TP + FN}, \qquad
\text{Especificidad} = \frac{TN}{TN + FP}, \qquad
\text{Precisión (PPV)} = \frac{TP}{TP + FP}
$$

El cálculo manual evita depender de implementaciones externas y deja explícito el conteo. La sensibilidad es la métrica prioritaria en detección de caídas porque el peor error es el falso negativo (He & Garcia, 2009); la especificidad controla las falsas alarmas y la fatiga de alarmas, y la precisión solo tiene sentido leída junto con la sensibilidad, ya que ambas compiten (Fawcett, 2006; Saito & Rehmsmeier, 2015). La exactitud no se reporta, lo cual es correcto con desbalance (He & Garcia, 2009). La literatura operativa recomienda además medir la tasa de falsas alarmas por hora (Silva et al., 2024), que este pipeline no calcula (sección 14).

**Agregación.** Por fold se computan las tres métricas y se guardan también `y_test`, `y_pred` y `ft_test`; al final, `run_experiment()` agrega media y desvío estándar entre folds para sensibilidad, especificidad y precisión. El resultado se imprime como tabla y se persiste en `comparison_results.json` (celda `6bda6f57`, con `json.dump(..., default=str)` para serializar los tipos no nativos).

**Matriz de confusión agregada.** La celda `a195351f` concatena las predicciones de todos los folds, construye la matriz 2×2 y anota cada cuadrante con los **tres grupos taxonómicos de mayor volumen** presentes ahí, con su porcentaje. Dos precisiones de lectura:

1. Las etiquetas son abreviaturas de dos letras (`RC`, `TC`, `TT`, `SC`, `CS`, `CL`, `SS`, `CC`, `SD`, `SM`) y una leyenda al pie las decodifica.
2. El porcentaje se calcula **sobre el subtotal de esos tres grupos**, no sobre el total del cuadrante: el código hace `pct = top / top.sum() * 100` (celda `a195351f`), aunque el markdown del notebook describa "porcentaje respecto al total del cuadrante". Es un indicador de composición relativa del top-3, útil para ver qué tipos dominan los errores, no una tasa de error por tipo.

**El punto crítico: prior del test y alcance de cada métrica.** El test de cada fold conserva todas las ventanas Fall disponibles (1 812–1 992) y aplica un tope de 5 000 ventanas ADL, de modo que la prevalencia resultante es de ≈27 % Fall, no el ~10 % natural. De ahí se siguen tres consecuencias:

- **Sensibilidad y especificidad son invariantes al prior.** Se calculan condicionadas a la clase verdadera ($P(\hat{y}=1 \mid y=1)$ y $P(\hat{y}=0 \mid y=0)$), por lo que no cambian si se submuestrea una clase. Son las métricas comparables entre configuraciones y con la literatura.
- **Precisión (PPV) y exactitud no lo son.** Dependen de la prevalencia. Con la prevalencia del test (≈27 % Fall), el PPV medido (~0.98) se mantiene alto y es coherente con la sensibilidad y la especificidad observadas; el ejemplo didáctico del 1 % muestra el límite de esa lectura: con sensibilidad y especificidad de 0.95 y una prevalencia real del 1 %, el PPV cae a $\frac{0.95 \times 0.01}{0.95 \times 0.01 + 0.05 \times 0.99} \approx 0.16$: apenas 16 % de las alarmas serían caídas reales, y el PPV del test no se traslada directamente al despliegue.
- **La tasa de falsas alarmas sí importa en tiempo real.** Con decisiones cada 1.5 s hay 57 600 ventanas por día; una especificidad de 0.95 implicaría unas 2880 falsas alarmas diarias, 0.99 unas 576 y 0.999 unas 58. Son valores que deben juzgarse contra el costo asistencial, no contra la exactitud.

**Umbral.** El umbral de operación es fijo (0.5) y no se optimizó; su valor solo sería óptimo con costos y prevalencias simétricos (Saito & Rehmsmeier, 2015). El pipeline reporta probabilidades de ventana y decide con 0.5 sobre la salida ya ponderada por `class_weight` (sección 9), sin un barrido de umbral orientado a la prioridad operativa (maximizar sensibilidad). Es una decisión por defecto, no una elección óptima.

**Sin métricas a nivel evento.** Todas las métricas son a nivel ventana. Una caída genera varias ventanas positivas contiguas, de modo que el desempeño operativo por evento requiere post-procesamiento (agregación o votación temporal, umbral ajustado al costo) que este pipeline no implementa. La brecha entre ambos niveles está documentada: Villa y Casilari (2026) reportan ~98.9 % de exactitud por ventana pero ~82 % de sensibilidad sobre caídas reales externas, y Kiprijanovska et al. (2020) reportan que la agregación a nivel de trial (umbral 0.8) eleva la especificidad de 82.5 % a 86.2 %, con una sensibilidad que pasa de 92.3 % a 90.0 %. No hay métricas de eventos, ni de pre-impacto, ni de latencia de detección en este pipeline.

## 12. Modelos finales y persistencia

Tras la validación cruzada, la celda `1436bd9b` entrena un modelo final por configuración sobre **todo el set** (no por folds):

1. Carga el Parquet, mapea la taxonomía, ventanea y submuestrea con `MAX_TRAIN_WINDOWS_PER_CLASS` (15 000) y `seed=42`.
2. `GroupShuffleSplit(n_splits=1, test_size=0.05, random_state=42)` reserva un 5 % de los grupos como validación para `EarlyStopping` y `ReduceLROnPlateau`. La partición sigue siendo por grupos, de modo que la validación no comparte sujetos con el entrenamiento.
3. Ajusta el escalador **solo con el split de entrenamiento** (`fit_scaler(Xtr[tr_idx])`) y aplica la transformación a todo el conjunto; el modelo se entrena con `tr_idx` y valida con `va_idx`.
4. Guarda el modelo y el escalador:

```python
model.save(MODELS_DIR / f"{config_name}_final.keras")
joblib.dump(scaler, MODELS_DIR / f"{config_name}_scaler.joblib")
```

Los artefactos quedan en `notebooks/data/modelos/falls/`: `set_a_final.keras`, `set_b_final.keras`, `set_a_scaler.joblib`, `set_b_scaler.joblib`, `comparison_results.json` y, del experimento cross-dataset (`01_Entrenamiento_2.ipynb`), `cross_final.keras`, `cross_scaler.joblib` y `cross_results.json`.

**Por qué se serializa todo el estado.** El formato `.keras` es un archivo zip con la configuración de la arquitectura (`config.json`), los pesos (HDF5) y metadatos de versión; como el modelo fue compilado, también incluye el estado del optimizador, lo que permite reanudar un entrenamiento de forma idéntica. Por eso se guarda el modelo completo y no solo los pesos (Keras team, 2023). El preprocesamiento no forma parte del `.keras`: el `StandardScaler` se persiste aparte con `joblib.dump`, la opción que scikit-learn recomienda para objetos con arrays NumPy grandes, con serialización eficiente y carga mapeada en memoria (Joblib developers, 2025; scikit-learn developers, 2026a). Para inferir hay que aplicar `scaler.transform` antes de `model.predict`; omitir el escalado produce predicciones inválidas aunque el `.keras` cargue sin errores. Nota de seguridad: `joblib` usa pickle, por lo que solo deben cargarse archivos generados por el propio pipeline.

**Reproducibilidad.** Además de las semillas de partición y submuestreo ya enumeradas, cada iteración cierra con `clear_session()`, que reinicia el estado global de Keras entre modelos y libera memoria (TensorFlow, s.f.-a). El notebook fija además la semilla global (`tf.keras.utils.set_random_seed(42)`): la reproducibilidad es alta dentro de una misma corrida, aunque entre notebooks con distinto orden de creación de modelos los pesos pueden diferir. En inferencia, el resultado es determinista dado el par modelo-scaler.

**Ajuste del escalador (corregido).** Hasta septiembre de 2026 el escalador se ajustaba antes de separar el 5 % de validación, incluyendo esas ventanas en las estadísticas. La revisión movió el ajuste a `fit_scaler(Xtr[tr_idx])`, de modo que la validación de los callbacks queda fuera; la fuga documentada en versiones anteriores ya no existe.

## 13. Resultados observados (referencia)

Los números que siguen provienen de [comparison_results.json](../../notebooks/data/modelos/falls/comparison_results.json) y se incluyen solo como referencia de la corrida registrada; no se interpretan más allá de lo que dicen.

| Config | Sensibilidad (media ± DE) | Especificidad (media ± DE) | Precisión (media ± DE) |
| --- | --- | --- | --- |
| `set_a` (5 datasets) | 0.9772 ± 0.0096 | 0.9922 ± 0.0032 | 0.9799 ± 0.0082 |
| `set_b` (4 datasets, sin UMAFall) | 0.9742 ± 0.0132 | 0.9934 ± 0.0025 | 0.9823 ± 0.0063 |

Por fold, `set_a` obtiene sensibilidades entre 0.9668 y 0.9916, y `set_b` entre 0.9478 y 0.9831; en ambos casos el test de cada fold tiene 5 000 ventanas ADL (tope) y todas las Fall disponibles (1 812–1 992 según el fold), con una prevalencia de ≈27 % Fall. Los valores corresponden a la implementación documentada en este archivo (topes de submuestreo, umbral 0.5, `class_weight` 2:1, semilla global fija).

**Evaluación cross-dataset con UMAFall (`01_Entrenamiento_2.ipynb`).** El notebook entrenó una única configuración con los cuatro datasets de `set_b` y evaluó UMAFall como holdout externo (4 315 ventanas, 324 Fall, prevalencia 7.5 %) usando el escalador del entrenamiento. Con los cinco modelos de fold: natural Sens 0.9846 ± 0.0020, Spec 0.9917 ± 0.0012, Prec 0.9064 ± 0.0120; balanceado 50/50: Sens 0.9846, Spec 0.9920, Prec 0.9920. Con el modelo final: natural Sens 0.9938, Spec 0.9922, Prec 0.9122 (322/324 caídas); balanceado 0.9938 / 0.9969 / 0.9969. La brecha con la CV interna es pequeña en este corpus, con tres cautelas: UMAFall es un dominio limitado (tres direcciones de caída, taxonomía F9), su resampleo 20→50 Hz es sintético y el holdout tiene 324 caídas de 18 sujetos, sin caídas reales. Resultados completos en `cross_results.json`.

## 14. Limitaciones metodológicas

Las siguientes limitaciones se desprenden del propio código y de las decisiones documentadas; no se atribuyen a fuentes externas salvo donde se cita:

- **Aprendizaje y métricas a nivel ventana.** No hay evaluación a nivel evento ni post-procesamiento temporal (sección 11); la brecha ventana-evento está documentada por Villa y Casilari (2026) y Kiprijanovska et al. (2020).
- **Prevalencia del test distinta de la real.** El test aplica un tope de 5 000 ADL y conserva todas las Fall (≈27 % Fall); PPV y exactitud no se trasladan a una prevalencia real del orden del 1 % (sección 11).
- **Umbral no optimizado.** Se usa 0.5 sin barrerlo ni corregirlo por el `class_weight` (secciones 9 y 11).
- **Evaluación cross-dataset limitada.** El notebook `01_Entrenamiento_2.ipynb` evalúa UMAFall como holdout externo (sección 13), pero no cubre LODO completo, otros corpus externos ni caídas reales, el escenario más exigente (Klenk et al., 2016; Silva et al., 2024).
- **Ruido de etiquetas.** El etiquetado por pico de AVM es débil: positivos por proximidad, negativos pre/post impacto en trials de caída, y ventanas solapadas que generan múltiples positivos correlacionados (sección 5; Frénay & Verleysen, 2014).
- **Sesgo de los trials largos.** Se descartan los trials con menos de 150 muestras y el submuestreo elimina ventanas de la clase mayoritaria por presupuesto de CPU (secciones 4 y 6); ambos efectos son **decisiones propias** de viabilidad, no elecciones estadísticas óptimas.
- **Cobertura desigual de cuasi-caídas.** UP-Fall y UMAFall no incluyen la clase A11; la especificidad frente a "tropiezos sin caer" está menos probada de lo que sugiere el número agregado (taxonomía unificada, "Consideraciones").
- **Datos de laboratorio.** Todo el corpus es de laboratorio y con caídas simuladas; el desempeño real es menor y los corpus con resampleo sintético (UMAFall en `set_a`) introducen diferencias de dominio que el pipeline no controla (Casilari & Silva, 2022). Las evaluaciones con caídas reales y monitoreo prolongado cuantifican la brecha: sensibilidad < 0.5 y falsas alarmas por hora insostenibles en la mayoría de los modelos (Silva et al., 2024), y 69.8 % de sensibilidad en despliegue inter-paciente con un solo IMU (Ponce et al., 2020). Las revisiones del campo coinciden: la mayoría de los estudios se evalúa con datos controlados y pocas caídas reales (Rastogi & Singh, 2021; Gorce & Jacquier-Bret, 2025).
- **Referencia con fuga de sujeto.** La evaluación publicada de UP-Fall usa 10-fold por muestra (Martínez-Villaseñor et al., 2019): un recordatorio de cuánto infla la fuga de sujeto los números de laboratorio, y de por qué acá se agrupa por `Group_ID`.
- **Sin pre-impacto ni temporalidad operativa.** El modelo no predice pre-impacto ni latencia (Yu, Qiu & Xiong, 2020) y su refresco de decisión es de 1.5 s, lejos de los adelantos de 0.3–0.4 s de la literatura (Yu et al., 2021); el triage y la alerta pertenecen a otra capa del sistema (Gramajo et al., 2026).

## 15. Fuentes primarias por decisión

Las fuentes primarias del proyecto se citan por su publicación oficial y tienen prioridad interpretativa sobre el resto de la bibliografía. Mapa de respaldo principal:

| Decisión del pipeline | Fuente primaria | Tipo |
| --- | --- | --- |
| Ventana de 3 s con solape del 50 % | Guo & Nakayama (2025); Ponce et al. (2020); Santoyo-Ramón et al. (2022b); Villa & Casilari (2026) | Directo y análogo |
| Etiquetado débil por pico de AVM | Yu et al. (2021); Martínez-Villaseñor et al. (2019); Casilari et al. (2020) | Análogo (márgenes estudiados) |
| Alternativas de etiquetado (video, tres clases, caídas reales) | Yu et al. (2021); Yu, Qiu & Xiong (2020); Klenk et al. (2016) | Directo |
| Desbalance: submuestreo y pesos de clase | Fula & Moreno (2024); Guo & Nakayama (2025); Yu, Qiu & Xiong (2020) | Análogo (alternativas comparadas) |
| Escalado z-score ajustado solo en train | scikit-learn developers (s.f.-c); Kaufman et al. (2012) | Directo (protocolo) |
| Arquitectura CNN-BiLSTM | Ordóñez & Roggen (2016); Yu, Qiu & Xiong (2020); Gaud et al. (2025); Kiprijanovska et al. (2020) | Directo y análogo |
| Optimización: BCE, Adam y callbacks | Kingma & Ba (2015); Prechelt (1998); Keras team (s.f.-b, s.f.-d); Yu, Qiu & Xiong (2020) | Directo y análogo |
| Validación agrupada por sujeto (`Group_ID`) | Kaufman et al. (2012); scikit-learn developers (s.f.-a, s.f.-d); Fula & Moreno (2024) | Directo |
| Contraste de partición con fuga (UP-Fall) | Martínez-Villaseñor et al. (2019); Santoyo-Ramón et al. (2022a) | Directo (contraejemplo) |
| Evaluación cross-dataset con UMAFall (`01_Entrenamiento_2`) | Martínez-Villaseñor et al. (2019); Santoyo-Ramón et al. (2022a); Silva et al. (2024) | Contraejemplo y protocolo propio |
| Métricas y su lectura (sensibilidad, prior) | Villa & Casilari (2026); Silva et al. (2024); Klenk et al. (2016); Saito & Rehmsmeier (2015) | Directo |
| Contexto clínico y de sistema (triage en el borde) | WHO (2021); Gramajo et al. (2025, 2026); Baker et al. (2017) | Contexto |
| Topes 15k/1k/5k, umbral 0.5, `class_weight` 2:1, dropout 0.4, `ReduceLROnPlateau` | — | Propio |

---

## 16. Referencias

Baker, S., Xiang, W., & Atkinson, I. (2017). Internet of Things for smart healthcare: Technologies, challenges, and opportunities. *IEEE Access, 5*, 26521–26544. https://doi.org/10.1109/ACCESS.2017.2775180

Banos, O., Galvez, J.-M., Damas, M., Pomares, H., & Rojas, I. (2014). Window size impact in human activity recognition. *Sensors, 14*(4), 6474–6499. https://doi.org/10.3390/s140406474

Bulling, A., Blanke, U., & Schiele, B. (2014). A tutorial on human activity recognition using body-worn inertial sensors. *ACM Computing Surveys, 46*(3), Article 33. https://doi.org/10.1145/2499621

Casilari, E., Lora-Rivera, R., & García-Lagos, F. (2020). A study on the application of convolutional neural networks to fall detection evaluated with multiple public datasets. *Sensors, 20*(5), 1466. https://doi.org/10.3390/s20051466

Casilari, E., Santoyo-Ramón, J. A., & Cano-García, J. M. (2017). UMAFall: A multisensor dataset for the research on automatic fall detection. *Procedia Computer Science, 110*, 32–39. https://doi.org/10.1016/j.procs.2017.06.110

Casilari, E., & Silva, C. A. (2022). An analytical comparison of datasets of real-world and simulated falls intended for the evaluation of wearable fall alerting systems. *Measurement, 202*, 111843. https://doi.org/10.1016/j.measurement.2022.111843

Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. *Journal of Artificial Intelligence Research, 16*, 321–357. https://doi.org/10.1613/jair.953

Fawcett, T. (2006). An introduction to ROC analysis. *Pattern Recognition Letters, 27*(8), 861–874. https://doi.org/10.1016/j.patrec.2005.10.010

Frénay, B., & Verleysen, M. (2014). Classification in the presence of label noise: A survey. *IEEE Transactions on Neural Networks and Learning Systems, 25*(5), 845–869. https://doi.org/10.1109/TNNLS.2013.2292894

Fula, V., & Moreno, P. (2024). Wrist-based fall detection: Towards generalization across datasets. *Sensors, 24*(5), Article 1679. https://doi.org/10.3390/s24051679

Gaud, N., Rathore, M., Suman, U., & Semwal, V. B. (2025). FIBiLS: Fall detection of healthy elderly using IMU sensor and BiLSTM model. *IEEE Sensors Journal, 25*(19), 37124–37131. https://doi.org/10.1109/JSEN.2025.3602945

Gers, F. A., Schmidhuber, J., & Cummins, F. (2000). Learning to forget: Continual prediction with LSTM. *Neural Computation, 12*(10), 2451–2471. https://doi.org/10.1162/089976600300015015

Glorot, X., Bordes, A., & Bengio, Y. (2011). Deep sparse rectifier neural networks. *Proceedings of the 14th International Conference on Artificial Intelligence and Statistics* (PMLR 15, pp. 315–323). https://proceedings.mlr.press/v15/glorot11a.html

Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep learning*. MIT Press. https://www.deeplearningbook.org/

Gorce, P., & Jacquier-Bret, J. (2025). Fall detection in elderly people: A systematic review of ambient assisted living and smart home-related technology performance. *Sensors, 25*(21), Article 6540. https://doi.org/10.3390/s25216540

Gramajo, S., Torres, C., Nuñez, S., Scappini, R., Roa, J., & Montiel, R. (2025). Integrated IoT system for remote health monitoring in home hospitalization. En *Anais do XXII Congresso Latino-Americano de Software Livre e Tecnologias Abertas (Latinoware 2025)* (pp. 598–602). Sociedade Brasileira de Computação. https://doi.org/10.5753/latinoware.2025.16539

Gramajo, S. D., Scappini, R. J. R., Nuñez, S., Torres, C., Montiel, R., & Roa, J. (2026). Multi-agent framework for resilient medical triage in the Internet of Medical Things (IoMT). En *Actas de las 14th Conference on Cloud Computing, Big Data & Emerging Topics (JCC-BD&ET 2026)* (pp. 88–101). Universidad Nacional de La Plata, Facultad de Informática. https://sedici.unlp.edu.ar/handle/10915/197628

Graves, A., & Schmidhuber, J. (2005). Framewise phoneme classification with bidirectional LSTM and other neural network architectures. *Neural Networks, 18*(5–6), 602–610. https://doi.org/10.1016/j.neunet.2005.06.042

Gu, T., Wang, L., Wu, Z., Tao, X., & Lü, J. (2011). A pattern mining approach to sensor-based human activity recognition. *IEEE Transactions on Knowledge and Data Engineering, 23*(9), 1359–1372. https://doi.org/10.1109/TKDE.2010.184

Guo, P., & Nakayama, M. (2025). A feature engineering method for smartphone-based fall detection. *Sensors, 25*(20), Article 6500. https://doi.org/10.3390/s25206500

He, H., & Garcia, E. A. (2009). Learning from imbalanced data. *IEEE Transactions on Knowledge and Data Engineering, 21*(9), 1263–1284. https://doi.org/10.1109/TKDE.2008.239

Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation, 9*(8), 1735–1780. https://doi.org/10.1162/neco.1997.9.8.1735

Ioffe, S., & Szegedy, C. (2015). Batch normalization: Accelerating deep network training by reducing internal covariate shift. *Proceedings of the 32nd International Conference on Machine Learning* (PMLR 37, pp. 448–456). https://proceedings.mlr.press/v37/ioffe15.html

Joblib developers. (2025). *Serialization and memory-mapped loading*. Joblib documentation (v1.6.0). https://joblib.readthedocs.io/en/stable/user_guide/persistence.html

Johnson, J. M., & Khoshgoftaar, T. M. (2019). Survey on deep learning with class imbalance. *Journal of Big Data, 6*(1), Article 27. https://doi.org/10.1186/s40537-019-0192-5

Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: Formulation, detection, and avoidance. *ACM Transactions on Knowledge Discovery from Data, 6*(4), Article 15. https://doi.org/10.1145/2382577.2382579

Kellogg International Work Group on the Prevention of Falls by the Elderly. (1987). The prevention of falls in later life. *Danish Medical Bulletin, 34*(Suppl 4), 1–24.

Keras team. (s.f.-a). *Conv1D layer*. Keras 3 API documentation. https://keras.io/api/layers/convolution_layers/convolution1d/

Keras team. (s.f.-b). *EarlyStopping*. Keras 3 API documentation. https://keras.io/api/callbacks/early_stopping/

Keras team. (s.f.-c). *Model training APIs*. Keras API documentation. https://keras.io/api/models/model_training_apis/

Keras team. (s.f.-d). *ReduceLROnPlateau*. Keras 3 API documentation. https://keras.io/api/callbacks/reduce_lr_on_plateau/

Keras team. (s.f.-e). *Reproducibility in Keras models*. Keras examples. https://keras.io/examples/keras_recipes/reproducibility_recipes/

Keras team. (2023). *Save, serialize, and export models*. Keras developer guides. https://keras.io/guides/serialization_and_saving/

Kingma, D. P., & Ba, J. (2015). Adam: A method for stochastic optimization. *Proceedings of the 3rd International Conference on Learning Representations (ICLR)*. https://arxiv.org/abs/1412.6980

Kiprijanovska, I., Gjoreski, H., & Gams, M. (2020). Detection of gait abnormalities for fall risk assessment using wrist-worn inertial sensors and deep learning. *Sensors, 20*(18), 5373. https://doi.org/10.3390/s20185373

Klenk, J., Schwickert, L., Palmerini, L., Mellone, S., Bourke, A., Ihlen, E. A. F., Kerse, N., Hauer, K., Pijnappels, M., Synofzik, M., Srulijes, K., Maetzler, W., Helbostad, J. L., Zijlstra, W., Aminian, K., Todd, C., Chiari, L., & Becker, C. (2016). The FARSEEING real-world fall repository: A large-scale collaborative database to collect and share sensor signals from real-world falls. *European Review of Aging and Physical Activity, 13*(1), Article 8. https://doi.org/10.1186/s11556-016-0168-9

Kohavi, R. (1995). A study of cross-validation and bootstrap for accuracy estimation and model selection. En *Proceedings of the 14th International Joint Conference on Artificial Intelligence* (Vol. 2, pp. 1137–1143). Morgan Kaufmann. https://www.ijcai.org/Proceedings/95-2/Papers/016.pdf

Martínez-Villaseñor, L., Ponce, H., Brieva, J., Moya-Albor, E., Núñez-Martínez, J., & Peñafort-Asturiano, C. (2019). UP-Fall detection dataset: A multimodal approach. *Sensors, 19*(9), 1988. https://doi.org/10.3390/s19091988

Maurer, U., Smailagic, A., Siewiorek, D. P., & Deisher, M. (2006). Activity recognition and monitoring using multiple sensors on different body positions. En *International Workshop on Wearable and Implantable Body Sensor Networks (BSN'06)* (pp. 113–116). IEEE. https://doi.org/10.1109/BSN.2006.6

Nair, V., & Hinton, G. E. (2010). Rectified linear units improve restricted Boltzmann machines. *Proceedings of the 27th International Conference on Machine Learning* (pp. 807–814). https://dl.acm.org/doi/10.5555/3104322.3104425

Noury, N., Rumeau, P., Bourke, A. K., Ó Laighin, G., & Lundy, J. E. (2008). A proposal for the classification and evaluation of fall detectors. *IRBM, 29*(6), 340–349. https://doi.org/10.1016/j.irbm.2008.08.002

Ordóñez, F. J., & Roggen, D. (2016). Deep convolutional and LSTM recurrent neural networks for multimodal wearable activity recognition. *Sensors, 16*(1), 115. https://doi.org/10.3390/s16010115

Ponce, H., Martínez-Villaseñor, L., & Nuñez-Martínez, J. (2020). Sensor location analysis and minimal deployment for fall detection system. *IEEE Access, 8*, 166678–166691. https://doi.org/10.1109/ACCESS.2020.3022971

Prechelt, L. (1998). Early stopping — But when? En G. B. Orr & K.-R. Müller (Eds.), *Neural networks: Tricks of the trade* (LNCS 1524, pp. 55–69). Springer. https://doi.org/10.1007/3-540-49430-8_3

Rastogi, S., & Singh, J. (2021). A systematic review on machine learning for fall detection system. *Computational Intelligence, 37*(2), 951–974. https://doi.org/10.1111/coin.12441

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLOS ONE, 10*(3), e0118432. https://doi.org/10.1371/journal.pone.0118432

Saleh, M., Abbas, M., & Le Bouquin Jeannès, R. (2021). FallAllD: An open dataset of human falls and activities of daily living for classical and deep learning applications. *IEEE Sensors Journal, 21*(2), 1849–1858. https://doi.org/10.1109/JSEN.2020.3018335

Santurkar, S., Tsipras, D., Ilyas, A., & Madry, A. (2018). How does batch normalization help optimization? *Advances in Neural Information Processing Systems 31*. https://proceedings.neurips.cc/paper/2018/hash/905056c1ac1dad141560467e0a99e1cf-Abstract.html

Santoyo-Ramón, J. A., Casilari, E., & Cano-García, J. M. (2022a). A cross-dataset evaluation of wearable fall detection systems. En *PETRA '22: Proceedings of the 15th International Conference on PErvasive Technologies Related to Assistive Environments* (pp. 1–6). Association for Computing Machinery. https://doi.org/10.1145/3529190.3529191

Santoyo-Ramón, J. A., Casilari, E., & Cano-García, J. M. (2022b). A study of the influence of the sensor sampling frequency on the performance of wearable fall detectors. *Measurement, 193*, Article 110945. https://doi.org/10.1016/j.measurement.2022.110945

scikit-learn developers. (s.f.-a). *3.1. Cross-validation: Evaluating estimator performance*. https://scikit-learn.org/stable/modules/cross_validation.html

scikit-learn developers. (s.f.-b). *12. Common pitfalls and recommended practices*. https://scikit-learn.org/stable/common_pitfalls.html

scikit-learn developers. (s.f.-c). *StandardScaler*. https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html

scikit-learn developers. (s.f.-d). *StratifiedGroupKFold*. https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html

scikit-learn developers. (2026a). *Model persistence*. https://scikit-learn.org/stable/model_persistence.html

scikit-learn developers. (2026b). *Tuning the decision threshold for class prediction*. https://scikit-learn.org/stable/modules/classification_threshold.html

Silva, C. A., Casilari, E., & García-Bermúdez, R. (2024). Cross-dataset evaluation of wearable fall detection systems using data from real falls and long-term monitoring of daily life. *Measurement, 235*, 114992. https://doi.org/10.1016/j.measurement.2024.114992

Srivastava, N., Hinton, G., Krizhevsky, A., Sutskever, I., & Salakhutdinov, R. (2014). Dropout: A simple way to prevent neural networks from overfitting. *Journal of Machine Learning Research, 15*(56), 1929–1958. https://jmlr.org/papers/v15/srivastava14a.html

Stone, M. (1974). Cross-validatory choice and assessment of statistical predictions. *Journal of the Royal Statistical Society: Series B (Methodological), 36*(2), 111–147. https://doi.org/10.1111/j.2517-6161.1974.tb00994.x

Sucerquia, A., López, J. D., & Vargas-Bonilla, J. F. (2017). SisFall: A fall and movement dataset. *Sensors, 17*(1), 198. https://doi.org/10.3390/s17010198

Teng, S., Kim, J.-Y., Jeon, S., Gil, H.-W., Lyu, J., Chung, E. H., Kim, K. S., & Nam, Y. (2024). Analyzing optimal wearable motion sensor placement for accurate classification of fall directions. *Sensors, 24*(19), Article 6432. https://doi.org/10.3390/s24196432

TensorFlow. (s.f.-a). *tf.keras.backend.clear_session*. TensorFlow API documentation. https://www.tensorflow.org/api_docs/python/tf/keras/backend/clear_session

TensorFlow. (s.f.-b). *tf.keras.utils.set_random_seed*. TensorFlow API documentation. https://www.tensorflow.org/api_docs/python/tf/keras/utils/set_random_seed

Tsinganos, P., & Skodras, A. (2018). On the comparison of wearable sensor data fusion to a single sensor machine learning technique in fall detection. *Sensors, 18*(2), 592. https://doi.org/10.3390/s18020592

Varma, S., & Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics, 7*, 91. https://doi.org/10.1186/1471-2105-7-91

Villa, M., & Casilari, E. (2026). The impact of the accelerometer sampling rate on the performance of machine and deep learning models in wearable fall-detection systems. *Sensors, 26*(1), 162. https://doi.org/10.3390/s26010162

World Health Organization. (2021). *Step safely: Strategies for preventing and managing falls across the life-course*. https://www.who.int/publications/i/item/978924002191-4

Yang, J. B., Nguyen, M. N., San, P. P., Li, X.-L., & Krishnaswamy, S. (2015). Deep convolutional neural networks on multichannel time series for human activity recognition. *Proceedings of the 24th International Joint Conference on Artificial Intelligence* (pp. 3995–4001). https://www.ijcai.org/Proceedings/15/Papers/561.pdf

Yu, X., Jang, J., & Xiong, S. (2021). A large-scale open motion dataset (KFall) and benchmark algorithms for detecting pre-impact fall of the elderly using wearable inertial sensors. *Frontiers in Aging Neuroscience, 13*, 692865. https://doi.org/10.3389/fnagi.2021.692865

Yu, X., Qiu, H., & Xiong, S. (2020). A novel hybrid deep neural network to predict pre-impact fall for older people based on wearable inertial sensors. *Frontiers in Bioengineering and Biotechnology, 8*, Article 63. https://doi.org/10.3389/fbioe.2020.00063

Zhang, J., Li, J., & Wang, W. (2021). A class-imbalanced deep learning fall detection algorithm using wearable sensors. *Sensors, 21*(19), 6511. https://doi.org/10.3390/s21196511
