# Pipeline de Preprocesamiento de Datasets de Caídas

**Nota de estado:** Las referencias con DOI fueron verificadas contra su registro editorial (septiembre de 2026) y las afirmaciones sin respaldo directo se marcan explícitamente como decisiones propias. Las fuentes primarias del proyecto —los trabajos originales usados para diseñar cada etapa— se citan por su publicación oficial y tienen prioridad interpretativa sobre el resto de la bibliografía; la sección 13 mapea decisión por decisión. El notebook `notebooks/fase_1/00_Preprocesamiento.ipynb` es la verdad del pipeline: constantes, umbrales y conteos provienen de su ejecución del 17 de septiembre de 2026 (re-ejecución con UP-Fall a 18.4 Hz).

Documentos relacionados: [Fundamentación bibliográfica](fundamentacion-literatura.md) · [Taxonomía unificada](taxonomía-unificada.md) · [Señales](../01_CONCEPTOS/Señales.md) · [Estrategia de datasets](../03_DATASETS/Elegidos/Estrategia.md) · [README del proyecto](../../README.md).

---

## 1. Introducción: qué hace el pipeline y cómo se organiza

`00_Preprocesamiento.ipynb` es un pipeline ETL que convierte los CSV inmutables de la capa **bronce** en dos Parquet listos para entrenamiento en la capa **oro**, todos a 50 Hz y con un esquema común de 14 columnas. El recorrido es: ingesta de cinco datasets, auditoría de calidad cruda, validación de etiquetas, métricas de fidelidad del resampleo por trial (capa **plata**), descarte de trials que no superan umbrales, y resampleo definitivo con exportación. El propósito clínico es la alerta temprana de caídas en adultos mayores: las caídas son la segunda causa mundial de muerte por lesión no intencional —684 000 muertes al año y 172 millones de personas con discapacidad temporal o permanente— (WHO, 2021), y los sistemas vestibles todavía rinden muy por debajo de sus números de laboratorio cuando se los evalúa con caídas reales (Silva et al., 2024); el repositorio FARSEEING documentó la escasez de esos datos al verificar solo 208 caídas reales (Klenk et al., 2016). En la arquitectura del proyecto, esa alerta alimenta un triage multiagente en el borde (Gramajo et al., 2026; Baker et al., 2017).

La organización sigue la **arquitectura medallion**, un patrón de industria (no una taxonomía académica formal): bronce conserva la copia cruda sin modificar, plata contiene datos validados y conformados, oro contiene agregados listos para consumo (Databricks, s.f.; Microsoft, s.f.). Cada capa puede reprocesarse desde la anterior: corregir una regla de limpieza reconstruye plata y oro sin reingestar ni editar bronce. El pipeline lo materializa con `clear_oro()` (celda `165f4fb1`), que borra los Parquet antes de cada exportación, y con la ausencia total de escrituras sobre `bronce/falls`. El versionado transaccional es lo que sostiene la reproducibilidad capa a capa (Armbrust et al., 2020), y la trazabilidad se apoya en la clave de trial `(Subject, Activity_Code, Trial)`, que sobrevive en todas las capas y queda en el JSON de validez y en el CSV de métricas.

| Capa   | Ruta                           | Contenido                                                                         | Artefactos                                                                                 |
| ------ | ------------------------------ | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Bronce | `notebooks/data/bronce/falls/` | CSV crudos e inmutables, ya reducidos a la IMU de cintura y a columnas homogéneas | `{Dataset}-Reduced.csv`                                                                    |
| Plata  | `notebooks/data/plata/falls/`  | Validación y métricas por trial                                                   | `bronze_sanity.json`, `resampling_metrics_per_trial_50hz.csv`, `trial_quality_config.json` |
| Oro    | `notebooks/data/oro/falls/`    | Señal resampleada y consolidada                                                   | `set_a.parquet`, `set_b.parquet`                                                           |

La lógica se reparte en seis celdas de funciones (`165f4fb1`, `2c0acf3c`, `90c5129c`, `3bdb4091`, `cell-fns-metrics`, `cell-fns-validation`) y siete celdas de ejecución (`cell-bronze-load`, `30dfa980`, `cell-validate-labels`, `cell-metrics-run`, `cell-filtering`, `cell-gold-export`, `cell-evidence`). El diseño separa _validar_ de _limpiar_: no hay imputación en ningún punto; un trial que no supera los controles se excluye con su motivo registrado (Wang & Strong, 1996; Batini et al., 2009). El contrato se declara explícito y se verifica al final con comparación exacta de columnas y orden (Data Contract Specification, s.f.; pandera developers, s.f.).

---

## 2. Contratos y constantes

La celda `52c27302` (líneas 62–119 del `.ipynb`) fija el contrato del pipeline.

### 2.1 Esquema de salida (14 columnas)

`Dataset`, `Subject`, `Activity_Label`, `Activity_Code`, `Trial`, `Sample_Index`, `Ax`, `Ay`, `Az`, `Gx`, `Gy`, `Gz`, `AVM`, `GVM`.

Las cuatro primeras identifican el trial; `Sample_Index` enumera las muestras (`np.arange`, celda `90c5129c`); las seis siguientes son los canales inerciales y las dos últimas las magnitudes vectoriales. `validate_schema` (celda `cell-fns-validation`) exige coincidencia exacta con `SCHEMA_COLS`, orden incluido: cualquier desviación aborta la exportación con `ValueError` (celda `cell-gold-export`), y ese _fail-fast_ es lo que garantiza que ambos Parquet compartan contrato (Data Contract Specification, s.f.).

### 2.2 Unidades

Aceleración en $g$ ($1g \approx 9.81\ \text{m/s}^2$) y giroscopio en °/s. No hay reescalado: se asume que los cinco CSV ya vienen en esas unidades (Sucerquia et al., 2017; Yu et al., 2021; Saleh et al., 2021; Martínez-Villaseñor et al., 2019; Casilari et al., 2017), y la auditoría de la sección 4 verifica la suposición.

### 2.3 Full-scales por dataset

| Dataset  | `ACC_FS` (g) | `GYRO_FS` (°/s) | Origen                                                                                                                                |
| -------- | ------------ | --------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| SisFall  | 16           | 2000            | ADXL345 ±16 g, ITG3200 ±2000 °/s (Sucerquia et al., 2017)                                                                             |
| KFall    | 16           | 2000            | LPMS-B2 ±16 g / ±2000 °/s (Yu et al., 2021)                                                                                           |
| FallAllD | 16           | 2000            | El dataset declara ±8 g / ±2000 °/s (Saleh et al., 2021); ver nota                                                                    |
| UPFall   | 16           | 2000            | El paper no declara rangos (Martínez-Villaseñor et al., 2019): decisión propia                                                        |
| UMAFall  | 8            | 256             | ±8 g / ±256 °/s (Casilari et al., 2017, Table 3); verificado contra el paper primario en la revisión de fuentes de septiembre de 2026 |

**Nota (FallAllD):** el acelerómetro satura a ±8 g (Saleh et al., 2021); auditar con 16 g vuelve imposible detectar recorte de aceleración en ese dataset ($0.99 \times 16 = 15.84$ g jamás se alcanza). La fracción de 0.0 reportada es un piso del código, no evidencia de ausencia de clipping. El valor de giroscopio sí coincide con la ficha.

### 2.4 Frecuencias y frecuencia objetivo

| Dataset      | $f_s$ nativa             | Intervalo | Factor a 50 Hz               |
| ------------ | ------------------------ | --------- | ---------------------------- |
| FallAllD     | 238 Hz                   | 4.2 ms    | 25/119                       |
| SisFall      | 200 Hz                   | 5 ms      | 1/4                          |
| KFall        | 100 Hz                   | 10 ms     | 1/2                          |
| UPFall | ≈18.4 Hz (consolidado) | ~54 ms | 125/46 |
| UMAFall      | 20 Hz                    | 50 ms     | 5/2                          |
| **Objetivo** | **50 Hz**                | **20 ms** | —                            |

`FS_TARGET = 50` Hz vale para todo el corpus. Su respaldo es que el contenido útil del movimiento humano, caídas incluidas, se concentra por debajo de 20 Hz y una Nyquist de 25 Hz lo preserva con margen (Tsinganos & Skodras, 2018; ampliado en [Fundamentación bibliográfica](fundamentacion-literatura.md)); la exactitud de las características de aceleración en HAR se estabiliza ya a 15–20 Hz (Maurer et al., 2006) y 50 Hz es la tasa de trabajo del detector de referencia por ingeniería de características (Guo & Nakayama, 2025). Los factores surgen de reducir la razón por el máximo común divisor (`get_poly_factors`, celda `90c5129c`); corrección respecto de descripciones previas: SisFall (200 → 50 Hz) usa $1/4$, no $4/1$.

**UP-Fall: corrección aplicada (17-sep-2026).** El paper describe los IMU crudos a 100 Hz, pero el archivo consolidado que distribuye —y que coincide con el bronce de este proyecto— está remuestreado a ≈18.4 Hz a partir de los timestamps de cámara (Martínez-Villaseñor et al., 2019). La corrección: `UPFall: 18.4` en `DATASETS_META` y factor racional **125/46** (`Fraction`). El pipeline se re-ejecutó y las caídas de UP-Fall pasan de ~90 a ~490–500 muestras (mediana 498), por lo que vuelven a generar ventanas de entrenamiento; su banda efectiva llega a ~9.2 Hz. Conteos nuevos: 238 trials válidos (antes 252) y 792 665 filas en oro (antes 147 208). Efecto de lectura a declarar: con Nyquist de 9.2 Hz, la guarda `cutoff >= 0.99·Nyq` omite el prefiltrado de la referencia en las métricas de fidelidad, de modo que el Pearson de UP-Fall (0.790 AVM / 0.874 GVM) compara la señal original sin filtrar contra la resampleada y mezcla fidelidad con cambio de banda.

### 2.5 Filtrado

`BUTTER_ORDER = 4` y `BUTTER_CUTOFF = 8.0` Hz. El filtro se aplica antes del resampleo en la ruta de exportación (celda `90c5129c`) y se justifica en la sección 7. La combinación orden 4 + 8 Hz es habitual para limpiar ruido de vibración preservando la dinámica del movimiento (Fridolfsson et al., 2019; Sucerquia et al., 2017 —cuyo propio preprocesamiento usó un Butterworth de cuarto orden a 5 Hz—; Villa & Casilari, 2026); los valores concretos son decisión propia.

---

## 3. Datos de entrada y capa bronce

La ingesta (`cell-bronze-load`) lee cada CSV desde `../data/bronce/falls/` con `pd.read_csv`. La lectura está protegida con `try/except` por dataset; las etapas siguientes filtran por presencia en `raw_datasets` y la consolidación de `set_a` presupone los cinco archivos, de modo que un archivo faltante detiene el pipeline.

| Dataset  | Origen                     | Sujetos                          | ADL / Caídas | $f_s$                                                             | Sensor de cintura                                                    | Fuente                            |
| -------- | -------------------------- | -------------------------------- | ------------ | ----------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------- |
| SisFall  | U. de Antioquia (Colombia) | 38 (23 jóvenes, 15 mayores)      | 19 / 15      | 200 Hz                                                            | ADXL345 ±16 g + ITG3200 ±2000 °/s                                    | Sucerquia et al. (2017)           |
| KFall    | KAIST (Corea)              | 32                               | 21 / 15      | 100 Hz                                                            | LPMS-B2 en espalda baja, ±16 g / ±2000 °/s                           | Yu et al. (2021)                  |
| FallAllD | dataloggers RF-Track       | 15                               | ~44 / ~35    | 238 Hz                                                            | ±8 g / ±2000 °/s                                                     | Saleh et al. (2021)               |
| UP-Fall  | U. Panamericana (México)   | 17 (18–24 años)                  | 6 / 5 tipos  | ≈18.4 Hz (consolidado; el paper describe los IMU crudos a 100 Hz) | IMU de cintura, rangos no declarados                                 | Martínez-Villaseñor et al. (2019) |
| UMAFall  | U. de Málaga (España)      | 18 en el bronce (17 en el paper) | 12 / 3 tipos | ~20 Hz                                                            | nodos inalámbricos, ±8 g / ±256 °/s (Casilari et al., 2017, Table 3) | Casilari et al. (2017)            |

Los CSV de bronce ya están reducidos a la IMU de cintura y a las columnas homogéneas `Subject, Activity_Label, Activity_Code, Trial, Sample_Index, Ax…Gz`; la reducción y el mapeo a etiquetas binarias ocurrieron antes del pipeline. Filas cargadas:

| Dataset   | Filas          |
| --------- | -------------- |
| SisFall   | 15,858,929     |
| FallAllD  | 8,558,480      |
| UMAFall   | 164,392        |
| KFall     | 3,995,100      |
| UPFall    | 294,678        |
| **Total** | **28,871,579** |

**Conteos: bronce vs paper.** Cuando el archivo reducido difiere del paper se documenta el bronce y se anota la diferencia: SisFall tiene 4 500 trials (2 702 ADL / 1 798 caídas) frente a los 2 706 ADL del texto de Sucerquia et al. (2017); UMAFall tiene 553 trials de 18 sujetos frente a los 531 de 17 sujetos del paper (versión del repositorio v8); UP-Fall coincide con el paper en 559 trials (304 ADL / 255 caídas).

La inmutabilidad de bronce implica que el pipeline nunca corrige, reescala ni completa valores: solo los lee y deriva artefactos nuevos. No imputar es deliberado y consistente con la literatura de calidad de datos: mejor un dataset más chico y trazable que uno completo y sintético (Wang & Strong, 1996; Batini et al., 2009).

---

## 4. Auditoría de calidad cruda

### 4.1 Fundamento físico

Un acelerómetro MEMS capacitivo mide fuerza específica, no aceleración cinemática pura: en reposo reporta la reacción al peso y su módulo vale $\approx 1g$ en cualquier orientación, mientras que en caída libre tiende a $0g$ (Bosch Sensortec, s.f.-a, s.f.-b; Analog Devices, s.f.). De ahí el control de unidades más simple y potente sobre datos inerciales: si la mediana de $|\vec{a}|$ de un dataset está cerca de 1 g, los datos están en g y los ejes bien escalados. El rango aceptado, $[0.75, 1.35]$ g, es decisión propia; la referencia física es 1 g.

Cuando la señal supera el fondo de escala, el ADC recorta el pico (_clipping_): la señal se trunca al rango de medición (Bagalà et al., 2012). Ese aplanado distorsiona RMS, varianza y descriptores espectrales, y sesga el instante de impacto; el encadenamiento es razonamiento de ingeniería propio. El recorte es irreversible, por eso los datasets de caídas eligen rangos amplios y el pipeline lo audita en lugar de corregirlo: FallAllD cuantificó que truncar su señal reduce la exactitud de los clasificadores (de 95.13 % con ±8 g a 92.95 % con ±4 g y 92.63 % con ±2 g, en cintura; Saleh et al., 2021). Un canal muerto (desviación estándar exactamente nula) señala eje no habilitado, sensor no inicializado o buffer congelado. Los NaN provienen de desconexiones y errores de sincronización; KFall documenta la eliminación de registros incompletos por fallas de Bluetooth (Yu et al., 2021). Los controles concretos ($\sigma = 0$, fracción $\ge 0.99$ del fondo de escala, mediana de AVM) son una síntesis de ingeniería del pipeline: decisión propia.

### 4.2 Implementación y guardas

La celda `2c0acf3c` define `_sat` (fracción de muestras con $|x| \ge 0.99 \cdot FS$ por canal), `saturation_report` (aplica `_sat` a aceleración con `ACC_FS` y a giroscopio con `GYRO_FS`) y `check_sanity` (total de NaN en los seis canales, mediana de AVM, canales con `std() == 0`). La auditoría corre una vez por dataset completo (celda `30dfa980`), persiste en `bronze_sanity.json` y aplica dos guardas duras: mediana de AVM fuera de $[0.75, 1.35]$ g o cualquier NaN lanzan `ValueError`. Canales muertos y saturación se reportan pero no abortan: no existe en el notebook una regla que descarte trials por esas causas.

### 4.3 Resultados

| Dataset  | Mediana AVM (g) | NaN | Canales muertos | Saturación máxima          |
| -------- | --------------- | --- | --------------- | -------------------------- |
| UMAFall  | 1.0099          | 0   | —               | 0.0073 (Gy)                |
| UPFall   | 1.0114          | 0   | —               | 0.0001 (Gy)                |
| SisFall  | 0.9991          | 0   | —               | 0.0                        |
| KFall    | 1.0081          | 0   | —               | 0.0                        |
| FallAllD | 0.9958          | 0   | —               | 0.0 (ver nota de `ACC_FS`) |

Las cinco medianas quedan a menos de dos centésimas de 1 g: las señales están en unidades de gravedad. No hay NaN ni canales muertos. Las saturaciones no nulas son marginales y se concentran en UMAFall (Gy 0.73 %, Gz 0.07 %, Ax 0.02 % y Az 0.01 %) y en UPFall (0.01 % en un eje); ninguna invalida un trial. La guarda dura se cumplió en todos los casos.

---

## 5. Integridad de etiquetas

`VALID_LABELS = {"Fall", "ADL"}` (celda `cell-fns-validation`). La celda `cell-validate-labels` verifica dos cosas por dataset: que `Activity_Label` no tenga valores fuera del conjunto y que ningún trial `(Subject, Activity_Code, Trial)` mezcle etiquetas, condición crítica porque un trial mixto propagaría etiquetas contradictorias a la misma señal en el ventaneo posterior. La detección usa `nunique()` por grupo: un conteo mayor que uno es la señal de alarma. Los cinco datasets pasaron ambas comprobaciones. La proveniencia de las etiquetas también difiere: KFall las genera de forma semiautomática con video sincronizado a 90 Hz, y UP-Fall anota las caídas por inspección de cámara y las ADL por timestamp (Yu et al., 2021; Martínez-Villaseñor et al., 2019). Distribución inicial de trials, antes del gate de calidad:

| Dataset   | ADL       | Fall      | Total      |
| --------- | --------- | --------- | ---------- |
| UPFall    | 304       | 255       | 559        |
| KFall     | 2,729     | 2,346     | 5,075      |
| FallAllD  | 1,332     | 466       | 1,798      |
| SisFall   | 2,702     | 1,798     | 4,500      |
| UMAFall   | 373       | 180       | 553        |
| **Total** | **7,440** | **5,045** | **12,485** |

El desbalance a nivel de archivo es moderado (≈54/46 ADL-caídas en UPFall y KFall; 60/40 en el total), pero será mucho mayor a nivel de muestra y de ventana porque las caídas duran ~1 s y las ADL hasta minutos (He & Garcia, 2009; Johnson & Khoshgoftaar, 2019). La taxonomía F1–F10 / A1–A13 se construye sobre estos códigos en [Taxonomía unificada](taxonomía-unificada.md), fuera de este pipeline.

---

## 6. Magnitudes vectoriales: AVM y GVM

$$
\text{AVM}[n] = \sqrt{A_x[n]^2 + A_y[n]^2 + A_z[n]^2}, \qquad
\text{GVM}[n] = \sqrt{G_x[n]^2 + G_y[n]^2 + G_z[n]^2}
$$

**Invariancia.** La norma euclídea no cambia con rotaciones ni reflexiones ($\|R\vec{a}\| = \|\vec{a}\|$ para toda matriz ortogonal $R$). El montaje en cintura no controla la orientación exacta del encapsulado y los cinco datasets usan convenciones de ejes distintas: comparar ejes entre sujetos o sesiones es inválido sin alineación, pero comparar módulos no requiere alineación alguna (Analog Devices, s.f.; Yu et al., 2021; Ponce et al., 2020, que documenta que la orientación del dispositivo no es fija en uso real y que asumirla constante degrada el rendimiento).

**AVM.** En reposo vale $\approx 1g$ en cualquier postura, en caída libre tiende a $0g$ y en el impacto captura el pico vectorial completo sin importar qué eje lo recibe; es la señal canónica de la detección de caídas (Bagalà et al., 2012; Sucerquia et al., 2017; Yu et al., 2021). Límite a declarar: no separa gravedad de movimiento, así que un salto o un sentarse brusco elevan la AVM sin ser caídas (van Hees et al., 2013). Por eso el proyecto no la usa como detector de umbral aislado, sino como entrada de un modelo supervisado.

**GVM.** Es la rapidez angular total en 3D. Chen et al. (2023) la formalizan como «la tasa de cambio direccional entre marcos sucesivos» y muestran con captura óptica que es más completa que las componentes por separado; KFall la combina con la magnitud de aceleración y el ángulo vertical en su algoritmo de pre-impacto (Yu et al., 2021). Al ser instantánea, no acumula la deriva del bias que sí aparece al integrar velocidad angular para estimar orientación: el bias existe (±0.5 °/s típicos, con deriva térmica; valores de ficha técnica, no reverificados en esta revisión), pero no crece con el tiempo en una magnitud instantánea (Bosch Sensortec, s.f.-a; STMicroelectronics, s.f.). Advertencia de alcance: Chen et al. (2023) provienen de ergonomía ocupacional; su fórmula y validación como norma 3D son transferibles, sus percentiles no. Extender la GVM a caídas es decisión propia, ya declarada en [Fundamentación bibliográfica](fundamentacion-literatura.md).

**Dónde se derivan.** En la ruta de exportación (`resample_trial_df`, celda `90c5129c`) se filtran los seis canales, se resamplean y **recién entonces** se calculan AVM y GVM sobre los ejes resampleados: así la magnitud exportada es exactamente la norma de los ejes exportados. En la ruta de métricas (`analyze_trial`, celda `cell-fns-metrics`) el orden es el inverso —magnitudes sobre ejes crudos y luego resampleo— porque ahí se mide la fidelidad del resampleo, no el efecto del filtro.

---

## 7. Filtrado: Butterworth de orden 4 a 8 Hz

### 7.1 Diseño

`butter_lowpass_filter` (celda `90c5129c`) implementa un Butterworth pasa-bajos de orden 4, corte 8 Hz, en forma SOS y con fase cero. Su respuesta de magnitud es

$$
|H(j\Omega)|^2 = \frac{1}{1 + \left(\Omega/\Omega_c\right)^{2N}},
$$

con $\Omega_c$ a −3 dB. La **planitud máxima** —las primeras $2N-1$ derivadas de $|H|$ se anulan en $\Omega = 0$— elimina el rizado en la banda de paso a costa de una transición más suave que Chebyshev o elíptico del mismo orden (Smith, 1997). Con $N = 4$ la asíntota es $20N = 80$ dB/década (24 dB/octava), suficiente para el ruido de vibración del sensor. Los diseños con rizado ganan pendiente pero pagan peor retardo de grupo y mayor _ringing_, intercambio desfavorable con un transitorio de impacto presente (Smith, 1997). SciPy recomienda `output='sos'` desde orden 4: la forma $b, a$ sufre cancelación de raíces y es frágil; un Butterworth de orden 4 son exactamente dos biquads en cascada (SciPy Developers, 2025).

### 7.2 Fase cero

Un IIR causal tiene fase no lineal y retardo de grupo $\tau_g(\omega) = -d\varphi/d\omega$ dependiente de la frecuencia: las componentes de un impacto llegan desfasadas y el pico se emborrona y desplaza. `sosfiltfilt` filtra hacia adelante y hacia atrás, con fase cero y magnitud $|H(\omega)|^2$: equivalente en amplitud a un Butterworth de orden 8 (SciPy Developers, 2025; Gustafsson, 1996). El costo es que no es causal —usa muestras futuras— y solo vale _offline_; en tiempo real haría falta un `sosfilt` causal compensado o un FIR de fase lineal. Las muestras extremas de cada trial dependen de la extensión de bordes (`padlen` de 15 muestras para dos biquads; en UMAFall, 750 ms a 20 Hz), un detalle a tener en cuenta si se recortan bordes.

### 7.3 Guarda, rol anti-ruido y rol anti-aliasing

El filtro se omite si `cutoff >= 0.99 * fs/2`. A 20 Hz (Nyquist 10 Hz, $0.99 \times 10 = 9.9 > 8$) el filtro **sí** se aplica; se omitiría recién a $f_s \le 16.2$ Hz. Su papel es **anti-ruido**: quita la vibración de alta frecuencia del MEMS y define la banda de interés cinemático. No es el anti-aliasing del remuestreo, aunque lo preceda: con corte en 8 Hz, muy por debajo de la Nyquist de salida (25 Hz), las componentes entre 8 y 25 Hz que sobreviven atenuadas podrían plegarse al decimar si no hubiera una segunda barrera. Esa barrera es el FIR polifásico de `resample_poly`, con corte en 25 Hz (sección 8). El anti-aliasing real debe actuar antes del diezmado y cortar en la Nyquist de salida: eso es lo que hace el FIR (Crochiere & Rabiner, 1981; Nyquist, 1928; Shannon, 1949).

Beneficio lateral: los seis canales pasan por el mismo filtro y el mismo FIR, así que la alineación relativa entre acelerómetro y giroscopio se conserva; un IIR causal por canal la rompería (Keresnyei et al., 2015).

### 7.4 Por qué 8 Hz

La dinámica discriminante de marcha y caídas se concentra en frecuencias bajas: el paso tiene su fundamental por debajo de 4 Hz, la contribución relevante de aceleración llega hasta ~10 Hz y ahí Fridolfsson et al. (2019) ubican el corte óptimo (Antonsson & Mann, 1985; van Hees et al., 2013). SisFall reportó que hasta 11 Hz podría bastar para detectar caídas en sus datos (Sucerquia et al., 2017), Villa y Casilari (2026) muestran que la información útil se concentra aún más abajo, y en HAR las características de aceleración se estabilizan a 15–20 Hz (Maurer et al., 2006). El corte de 8 Hz conserva esa banda con planitud y atenúa el ruido; el valor concreto es decisión propia, anclada en la literatura pero no prescrita por ella.

---

## 8. Remuestreo a 50 Hz

### 8.1 Teoría de muestreo y aliasing

Una señal limitada en banda $B$ se reconstruye sin ambigüedad si $f_s > 2B$ (Nyquist, 1928; Shannon, 1949). Si no, una componente $f > f_s/2$ se pliega a $|f - k f_s|$ para el entero $k$ que la lleva a $[0, f_s/2]$: al decimar de 238 a 50 Hz, un tono de 40 Hz aparecería como uno de 10 Hz y uno de 119 Hz como uno de 19 Hz. Todo submuestreo exige un pasa-bajos previo (Crochiere & Rabiner, 1981). Los impactos son transitorios de banda ancha y KFall subraya que el instante de impacto «incluye la información más discriminativa (pico de aceleración y de velocidad angular)» (Yu et al., 2021); pasar de 238 a 50 Hz descarta la banda 25–119 Hz, que sin filtrar plegaría dentro de $[0, 25]$ Hz y contaminaría forma y amplitud de los picos.

### 8.2 Remuestreo racional polifásico

La conversión por un factor $L/M$ combina interpolación por $L$ (inserción de ceros y pasa-bajos a $\pi/L$) con decimación por $M$ (pasa-bajos a $\pi/M$ y descarte), en un único FIR con corte en $\pi/\max(L, M)$; la descomposición polifásica baja el costo por muestra de $O(N \cdot Q)$ a $O(N/P)$ (Crochiere & Rabiner, 1981). `resample_poly` hace exactamente eso: reduce la razón por el máximo común divisor, diseña un FIR simétrico de $2 \cdot \text{half\_len} + 1$ coeficientes con `half_len = 10 · max(up, down)`, lo escala por `up` y usa `upfirdn` (SciPy Developers, 2025). Su ventana es Kaiser con $\beta = 5$ (`KAISER_BETA`, celda `90c5129c`) y `padtype="line"`:

$$
w(n) = \frac{I_0\left(\beta\sqrt{1 - \left(\frac{2n}{M-1}\right)^2}\right)}{I_0(\beta)}
$$

$\beta$ regula el compromiso lóbulo principal / lóbulos laterales: más $\beta$, más atenuación y transición más ancha (Kaiser, 1974). Con la regla de Harris (1978), $\beta = 0.1102\,(A - 8.7)$ para $A > 50$ dB, se estima que $\beta = 5$ entrega unos 54 dB de atenuación de banda atenuada (cálculo propio). `padtype="line"` extiende la señal siguiendo la tendencia lineal de los extremos, lo que reduce el transitorio frente al relleno con ceros; aun así las primeras y últimas muestras dependen de extrapolación (SciPy Developers, 2025). Frente a una interpolación lineal o cúbica —dos a cuatro coeficientes, con _droop_ y réplicas espectrales— el FIR polifásico windowed-sinc ofrece rizado controlado y conversión de tasa exacta. Ninguna interpolación crea información: reconstruye bajo el supuesto de banda limitada que impone su propio corte.

### 8.3 Los cinco casos

| Dataset  | Conversión  | $(up, down)$ | Dirección | Corte del FIR | Coeficientes | Transición estimada |
| -------- | ----------- | ------------ | --------- | ------------- | ------------ | ------------------- |
| FallAllD | 238 → 50 Hz | 25 / 119     | baja      | 25 Hz         | 2,381        | ≈21–29 Hz           |
| SisFall  | 200 → 50 Hz | 1 / 4        | baja      | 25 Hz         | 81           | ≈21–29 Hz           |
| KFall    | 100 → 50 Hz | 1 / 2        | baja      | 25 Hz         | 41           | ≈21–29 Hz           |
| UPFall | 18.4 → 50 Hz | 125 / 46 | sube | 9.2 Hz | 2,501 | ≈3 Hz |
| UMAFall  | 20 → 50 Hz  | 5 / 2        | sube      | 10 Hz         | 101          | ≈8.4–11.6 Hz        |

Cortes y cantidades de coeficientes se derivan de la lógica de `resample_poly`; las transiciones son estimaciones propias con la fórmula de ventana Kaiser–Harris (Harris, 1978; Oppenheim & Schafer, 2010), no mediciones. En los cuatro _downsampling_ el FIR corta en la Nyquist de salida (25 Hz): es el anti-aliasing efectivo. En el _upsampling_ de UMAFall corta en la Nyquist de entrada (10 Hz), porque no hay información por encima de esa frecuencia que reconstruir.

En UP-Fall (18.4 → 50 Hz) el FIR corta en la Nyquist de entrada (9.2 Hz), como en el upsampling de UMAFall; la transición ≈3 Hz es una estimación propia con la fórmula Kaiser–Harris (Harris, 1978; Oppenheim & Schafer, 2010).

### 8.4 Qué se gana y qué se pierde

**Bajar la tasa.** Se descarta banda: los impactos son transitorios anchos y parte de su energía supera los 25 Hz, así que los picos quedan suavizados y de menor amplitud. El intercambio es aceptado: mantener 100–238 Hz multiplicaría el tamaño y rompería la homogeneidad, y la evidencia indica que la dinámica se conserva bien a tasas bajas. Liu et al. (2018) reportan al menos 97 % de exactitud con 22 Hz; Villa y Casilari (2026) logran 98.9 % de exactitud, 96.7 % de sensibilidad y 99.6 % de especificidad con CNN-LSTM a 20 Hz, con degradación mínima a 10 Hz; Santoyo-Ramón et al. (2022b) concluyen que 20 Hz bastan para maximizar la efectividad de un detector vestible, lo que refuerza que bajar a 50 Hz no sacrifica la dinámica relevante; Silva et al. (2024) llevan esa lógica más lejos y remuestrean todo su banco de evaluación a 25 Hz con un FIR anti-aliasing.

**Subir la tasa.** No se crea información: UMAFall ya está limitada a 10 Hz y el FIR reconstruye el mismo contenido en una rejilla más fina. Se gana compatibilidad de formato —mismas muestras por segundo, ventanas y contrato— y se arriesga la interpretación, porque la rejilla de 20 ms sugiere una resolución temporal que la señal de 20 Hz no tiene (entre muestra y muestra hay 50 ms). Guo y Nakayama (2025) resuelven ese caso con interpolación lineal; acá se usa el FIR polifásico, que controla la banda en vez de suponerla. Ese riesgo es de lectura, no de señal: la tasa nativa queda documentada y el original permanece en bronce.

**Heterogeneidad remanente.** Con la tasa unificada, la banda efectiva sigue difiriendo: UMAFall conserva hasta 10 Hz, los demás hasta ~25 Hz. Mezclar bandas introduce un sesgo de corpus que afecta comparaciones y evaluación cruzada (Casilari & Silva, 2022). Por eso existen `set_a` (cinco datasets) y `set_b` (sin UMAFall), y por eso las métricas deben reportarse también por dataset de origen.

---

## 9. Validación de fidelidad del resampleo (capa plata)

### 9.1 Qué se mide

La celda `cell-fns-metrics` calcula, para cada trial `Fall` (los ADL no se evalúan: no contienen el transitorio que el gate protege), cinco familias de métricas sobre AVM y GVM: SNR en banda $[0, 24.5]$ Hz; Pearson $r$ entre original filtrada y resampleada; desfase de pico (ms); atenuación de pico (%); y estadísticos pre/post (media, desviación estándar, mediana, P05, P95). Las cuatro primeras se calculan en una ventana de $\pm 1$ s alrededor del pico de AVM (`EVAL_WINDOW_SEC = 2.0`), decisión propia del pipeline; otras referencias trabajan con segmentos alrededor del pico, pero sin una ventana de ±1 s prescrita: el segmento óptimo de Tsinganos y Skodras (2018) es asimétrico (≈ −2170/+1155 ms). Los estadísticos se calculan sobre el trial completo. La ventana concentra la evaluación en el impacto y evita diluir el error en reposo. La referencia original se pasa antes por un Butterworth de orden 8 con corte en 24.5 Hz, para comparar anchos de banda equivalentes: la banda de la SNR queda por debajo de la zona de rechazo del FIR (que arranca cerca de 29 Hz) y separada de la Nyquist de salida. En UMAFall (20 Hz) y en UP-Fall (≈18.4 Hz) el corte excede la Nyquist y la guarda hace que la referencia no se filtre: la señal ya está limitada a 10/9.2 Hz, y por eso su Pearson baja frente al de los datasets con referencia prefiltrada (sección 12).

### 9.2 Fórmulas

$$\text{SNR}_{dB} = 10 \log_{10}\left(\frac{P_s}{P_e}\right), \qquad P_s = \frac{1}{N}\sum_n x_{\text{ref}}[n]^2, \quad P_e = \frac{1}{N}\sum_n \left(x_{\text{ref}}[n] - x_{\text{res}}[n]\right)^2$$

$$r = \frac{\sum_n (x_n - \bar{x})(y_n - \bar{y})}{\sqrt{\sum_n (x_n - \bar{x})^2}\sqrt{\sum_n (y_n - \bar{y})^2}}, \qquad \Delta t = \left| \frac{\arg\max_n x_{\text{ref}}[n]}{f_s^{\text{orig}}} - \frac{\arg\max_n x_{\text{res}}[n]}{f_s^{\text{obj}}} \right| \cdot 1000, \qquad A\% = \frac{\left| \max_n x_{\text{ref}} - \max_n x_{\text{res}} \right|}{\max_n x_{\text{ref}}} \cdot 100$$

La SNR se lee como siempre: 20 dB equivalen a un error de potencia del 1 % y 30 dB al 0.1 % (Smith, 1997). Pearson mide forma, invariante a escala y offset ($r = 0.99 \Rightarrow r^2 = 0.98$, 98 % de varianza compartida), pero es ciego al retardo global; por eso se complementa con desfase y atenuación. La atenuación de pico es directamente relevante para detectores de umbral fijo en g o °/s (Bagalà et al., 2012; Casilari & Silva, 2022), y que los filtros anti-aliasing introduzcan retardos de milisegundos comparables al desfase entre señales está documentado por Keresnyei et al. (2015).

### 9.3 Alineación temporal

Original y resampleada viven en rejillas distintas, así que se alinean con `np.interp` sobre rejillas normalizadas $\text{linspace}(0, 1, N)$: la ventana resampleada se interpola sobre la grilla normalizada de la ventana original. Es una interpolación lineal auxiliar que forma parte del error medido (la SNR y el $r$ reportados la incluyen). Si alguna ventana queda recortada en un borde del trial, las longitudes difieren de la nominal y la normalización reparte el desajuste sobre toda la ventana: otra razón para mirar desfase y atenuación con cautela en esos casos.

### 9.4 Límites del `argmax`

El desfase se estima con la diferencia de índices del máximo, y esa estimación tiene tres límites, ninguno corregido en el pipeline:

- **Cuantización:** $\pm 1$ muestra; 20 ms a 50 Hz y 50 ms en la rejilla original de UMAFall. Las medianas reportadas (0, 10, 20 ms) son múltiplos de esa cuantización (los P95 de la tabla interpolan entre muestras).
- **Meseta del máximo:** el filtrado y la interpolación aplanan la cresta, varios índices empatan y `np.argmax` devuelve el primero, con sesgo direccional.
- **Ventanas centradas:** cada ventana está centrada en el pico de su propia señal (AVM original y AVM resampleada), de modo que para la AVM el desfase queda acotado por construcción y cercano a cero salvo recortes de borde. Para la GVM la ventana se centra en el pico de AVM, así que el desfase reportado mide el corrimiento relativo del pico de giroscopio respecto del de aceleración: es la lectura informativa.

La mitigación estándar (interpolación parabólica sobre los tres puntos vecinos, correlación cruzada con refinamiento sub-muestra, o agregación del desfase en múltiples ventanas) no está implementada y queda como mejora natural. Ningún post-proceso devuelve precisión que la señal no contiene.

### 9.5 Persistencia

`cell-metrics-run` itera los datasets (omite el cálculo si $f_s^{\text{orig}} = 50$ Hz, caso ausente en este corpus) y concatena todo en `resampling_metrics_per_trial_50hz.csv`: 10,090 filas (5,045 trials de caída × 2 sensores) y 2,786,604 bytes. Cada fila identifica el trial por `(Subject, Activity_Code, Trial)`, indica el sensor (`AVM` o `GVM`) y trae las cuatro métricas más los diez estadísticos pre/post. Es el insumo del gate y la evidencia de la sección 12.

---

## 10. Gate de calidad: qué se descarta y por qué

### 10.1 Umbrales y lógica

| Criterio           | Umbral       | Significado                                          | Respaldo                                                                                        |
| ------------------ | ------------ | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Pearson $r$        | $\ge 0.85$   | La forma se preserva en la banda útil                | Decisión propia                                                                                 |
| Desfase de pico    | $\le 100$ ms | El impacto no se corre más de cinco muestras a 50 Hz | Análogo: orden de magnitud de los retardos anti-aliasing (Keresnyei et al., 2015); valor propio |
| Atenuación de pico | $\le 25$ %   | La amplitud del impacto se conserva                  | Decisión propia                                                                                 |

`filter_valid_trials` (celda `3bdb4091`) combina los umbrales así:

1. **Falla por métrica con OR entre sensores:** una métrica falla si no cumple el umbral en AVM **o** en GVM.
2. **Descarte con ≥ 2 de 3 fallas.** Una sola métrica mala no alcanza; la política tolera una medición ruidosa pero no dos.
3. **NaN = descarte.** Un trial de menos de 1 s (`len(avm) < fs_orig`) no genera métricas, queda NaN en el cruce y se descarta por falta de evidencia.
4. **Solo Fall.** Los ADL no se filtran ni se descartan: el gate protege el transitorio de impacto, que solo existe en las caídas, y las métricas ni siquiera se calcularon para los ADL.

Todo queda en `trial_quality_config.json`, con `criteria` (`pearson_r_min`, `phase_shift_ms_max`, `peak_atten_pct_max`, `sensors: ["AVM", "GVM"]`, `combine: "or"`), `valid_ids` por dataset y marca temporal UTC. Umbrales y política OR ≥ 2 son decisión propia, como se declara en [Fundamentación bibliográfica](fundamentacion-literatura.md).

### 10.2 Resultados

| Dataset   | Trials Fall | Válidos   | Descartados | % descarte |
| --------- | ----------- | --------- | ----------- | ---------- |
| UPFall | 255 | 238 | 17 | 6.7 % |
| KFall     | 2,346       | 2,295     | 51          | 2.2 %      |
| FallAllD  | 466         | 415       | 51          | 10.9 %     |
| SisFall   | 1,798       | 1,742     | 56          | 3.1 %      |
| UMAFall   | 180         | 163       | 17          | 9.4 %      |
| **Total** | **5,045** | **4,853** | **192** | **3.8 %** |

El patrón es informativo: los mayores descartes son FallAllD (10.9 %), el cambio de tasa más agresivo (25/119); UMAFall (9.4 %) y UP-Fall (6.7 %), los dos upsamplings (20→50 y 18.4→50 Hz) con picos suavizados; SisFall 3.1 % y KFall 2.2 %. El porcentaje escala con la severidad de la conversión, que es exactamente lo que el gate busca detectar. El JSON se regenera en cada corrida (≈350 KB, casi todo por las listas de IDs válidos).

---

## 11. Exportación a la capa oro

### 11.1 Reconstrucción y escritura

`cell-gold-export` recorre los datasets en el orden de `DATASETS_META` y, por cada uno: reconstruye `valid_ids` como tuplas y las cruza con un `MultiIndex` de `(Subject, Activity_Code, Trial)`; conserva las caídas válidas y **todos** los ADL; itera por grupos de trial, castea los seis canales a `float32` y aplica `resample_trial_df` (Butterworth → resampleo Kaiser → AVM/GVM sobre los ejes resampleados → metadatos → `Sample_Index` → esquema de 14 columnas); verifica el esquema y aborta con `ValueError` si no coincide con `SCHEMA_COLS`; y acumula por dataset liberando memoria. Al final, `clear_oro()` borra los Parquet previos y se escriben `set_a.parquet` (cinco datasets: UPFall, KFall, FallAllD, SisFall, UMAFall) y `set_b.parquet` (los cuatro sin UMAFall), ambos con `index=False`. La ablación `set_a`/`set_b` responde a la evidencia cross-dataset: los clasificadores entrenados con varios corpus se degradan al transferir a uno nuevo (Santoyo-Ramón et al., 2022a; Silva et al., 2024) y los repositorios difieren en sensor, tasa y banda efectiva (Casilari et al., 2020; Fula & Moreno, 2024).

El `float32` se justifica con el estándar IEEE 754-2019: 24 bits de mantisa (~7 dígitos decimales) sobran para un ADC de 12–16 bits, que no aporta información bajo $2^{-11}$–$2^{-15}$ del fondo de escala; usar `float32` en lugar de `float64` reduce el archivo a la mitad (IEEE, 2019). Las acumulaciones largas conviene hacerlas en doble precisión, y el pipeline lo respeta: las métricas se calculan en `float64` y el cast se aplica recién en la exportación.

### 11.2 Por qué Parquet

Parquet es columnar: agrupa los datos por columnas dentro de _row groups_, guarda estadísticas por página (mínimo, máximo, nulos) que permiten descartar bloques sin leerlos, comprime por columna y evoluciona esquema vía metadatos (Apache Software Foundation, s.f.-a). Para este corpus eso significa poder leer solo `Ax…Gz` sin tocar `Subject` o `Activity_Code`, comprimir `Activity_Label` por diccionario y `Sample_Index` por codificación delta. Zeng et al. (2023) documentan que codificación y compresión dominan el rendimiento de lectura, y PyArrow expone lectura selectiva y control de compresión (Apache Software Foundation, s.f.-b). El pipeline usa los valores por defecto de compresión: una decisión a medir si el corpus crece.

### 11.3 Resultado

| Dataset                 | Filas Fall    | Filas ADL     | Total         |
| ----------------------- | ------------- | ------------- | ------------- |
| UPFall | 116,629 | 676,036 | 792,665 |
| KFall                   | 844,349       | 1,135,503     | 1,979,852     |
| FallAllD                | 415,000       | 1,332,000     | 1,747,000     |
| SisFall                 | 1,306,463     | 2,616,399     | 3,922,862     |
| UMAFall                 | 121,449       | 277,188       | 398,637       |
| **set_a (5)** | **2,803,890** | **6,037,126** | **8,841,016** |
| **set_b (sin UMAFall)** | **2,682,441** | **5,759,938** | **8,442,379** |

`set_a.parquet` pesa 563.74 MB y `set_b.parquet` 537.70 MB (corrida del 17-sep-2026, con UP-Fall a 18.4 Hz). Los ADL pasan del 60 % de los trials al 68 % de las filas: la duración desigual (caídas de ~1 s, ADL de decenas de segundos) es la primera fuente real de desbalance, mucho antes que el conteo de archivos (He & Garcia, 2009; Johnson & Khoshgoftaar, 2019).

---

## 12. Evidencia, conclusiones y limitaciones

### 12.1 Evidencia agregada

| Dataset  | Sensor | $r$ mediana | $r$ P05 | Desfase P95 (ms) | Atenuación P95 (%) |
| -------- | ------ | ----------- | ------- | ---------------- | ------------------ |
| FallAllD | AVM    | 0.903       | 0.278   | 0.0              | 16.1               |
| FallAllD | GVM    | 0.959       | 0.275   | 397.9            | 16.3               |
| KFall    | AVM    | 0.986       | 0.788   | 0.0              | 9.5                |
| KFall    | GVM    | 0.991       | 0.824   | 80.0             | 16.9               |
| SisFall  | AVM    | 0.952       | 0.631   | 0.0              | 14.7               |
| SisFall  | GVM    | 0.986       | 0.823   | 90.0             | 12.2               |
| UMAFall  | AVM    | 0.921       | 0.579   | 0.0              | 21.2               |
| UMAFall  | GVM    | 0.974       | 0.734   | 230.5            | 14.4               |
| UPFall | AVM | 0.790 | 0.515 | 21.7 | 18.4 |
| UPFall | GVM | 0.874 | 0.479 | 92.5 | 14.4 |

La comparación pre/post (mediana por trial) muestra que el resampleo no introduce sesgo apreciable: la variación de la media es menor al 0.4 %, la de la desviación estándar menor al 9 % y la de P05/P95 menor al 10 %. Se conserva la distribución; lo que cambia, y poco, son las colas.

### 12.2 Conclusiones

La celda `cell-conclusion` afirma, con esta evidencia: (1) la forma de onda se preserva (mediana de Pearson $\ge 0.79$: AVM 0.790–0.986, GVM 0.874–0.991; el mínimo es UP-Fall, cuya referencia no se prefiltra —sección 9— y cuyo Pearson mezcla fidelidad con cambio de banda); (2) la amplitud se controla (atenuación P95 bajo 25 % en todos los casos, máximo 21.2 % en AVM de UMAFall); (3) los estadísticos son invariantes (variación mínima en media, desviación y percentiles); y (4) la sincronía del impacto se mantiene, con desfase de pico de AVM $\le 21.7$ ms (P95; máximo en UP-Fall, el resto $\le 20$ ms). En GVM la mediana es de una muestra (10–20 ms) pero el P95 llega a 92.5–397.9 ms (UP-Fall, FallAllD y UMAFall): el notebook lo atribuye al 5 % de trials con peor desfase y lo interpreta como limitación de la métrica por `argmax` —picos secundarios ambiguos del giroscopio—, no como pérdida real de fidelidad, porque forma y amplitud siguen siendo buenas ($r$ mediana $\ge 0.96$).

### 12.3 Limitaciones

- **Desfase de GVM.** Además de la ambigüedad del `argmax`, hay una causa estructural: las ventanas se centran en el pico de AVM, así que el desfase de GVM mide el corrimiento relativo del pico de giroscopio, cuantizado a 20 ms y, en la señal original de UMAFall, a 50 ms. El umbral de 100 ms deja pasar trials con dos o más muestras de corrimiento: es conservador por cobertura, no por exigencia.
- **Atenuación de picos.** El gate mide la atenuación del resampleo con referencia limitada a 24.5 Hz; no mide el efecto del Butterworth de 8 Hz, que también recorta picos. La atenuación total de la cadena exportada es mayor que la reportada: a cuantificar si un detector de umbral fijo pierde sensibilidad.
- **Ventanas de borde.** Los trials con pico a menos de 1 s del inicio o del final tienen ventanas recortadas y comparaciones distorsionadas por la normalización; la proporción no se reporta.
- **Heterogeneidad de banda.** A 50 Hz, UMAFall conserva hasta 10 Hz y los demás hasta ~25 Hz. Mezclarlos sesga el corpus y puede amplificarse en evaluación cruzada (Casilari & Silva, 2022; Santoyo-Ramón et al., 2022a). `set_b` existe para medir ese efecto.
- **Pearson de UP-Fall no comparable.** Al estar a ≈18.4 Hz, la referencia de sus métricas no se prefiltra (sección 9.1) y su Pearson (0.790/0.874) mide, además de fidelidad, una diferencia de banda respecto de los demás datasets. Es la única métrica del corpus cuya lectura no es homogénea entre datasets.
- **Brecha laboratorio–realidad.** El corpus es enteramente de laboratorio y con caídas simuladas. En caídas reales, los algoritmos clásicos rinden ~57 % de sensibilidad con falsas alarmas diarias (Bagalà et al., 2012) y los modelos evaluados no superan el 50 % de sensibilidad (Silva et al., 2024); en despliegue inter-paciente, un sistema de un solo IMU cae a 69.8 % de sensibilidad (Ponce et al., 2020). La especificidad de laboratorio no se traduce en tasas de falsas alarmas por hora aceptables (Silva et al., 2024).
- **Saturación ciega de FallAllD.** La auditoría de su acelerómetro usa `ACC_FS = 16` cuando el fondo real es ±8 g: la fracción 0.0 no debe leerse como ausencia de clipping.
- **Decisiones propias.** Los umbrales $r \ge 0.85$, desfase $\le 100$ ms y atenuación $\le 25$ %, la política OR ≥ 2, el rango $[0.75, 1.35]$ g, la regla `std = 0`, la fracción 0.99 y las cuatro métricas de resampleo como control de calidad son aportes del pipeline sin respaldo directo, consistentes con lo declarado en [Fundamentación bibliográfica](fundamentacion-literatura.md).

En síntesis: el corpus resultante es homogéneo, trazable y validado, con pérdida de fidelidad baja y acotada. Las limitaciones son de medición y de metadatos, no de corrupción de datos, y las que afectan la interpretación (banda efectiva, saturación ciega) quedan visibles para quien entrene sobre el corpus.

---

## 13. Fuentes primarias por decisión

Las fuentes primarias del proyecto —los trabajos originales y las revisiones usados para diseñar cada etapa— se citan por su publicación oficial y tienen prioridad interpretativa sobre el resto de la bibliografía. Este mapa resume el respaldo principal de cada decisión; las referencias no listadas acá se conservan como respaldo complementario.

| Decisión del pipeline                                         | Fuente primaria                                                                                                                | Tipo                         |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| Unidades y fondo de escala por dataset                        | Sucerquia et al. (2017); Yu et al. (2021); Saleh et al. (2021); Casilari et al. (2017); Martínez-Villaseñor et al. (2019)      | Directo                      |
| Frecuencias nativas (200/238/100/20 Hz y ≈18.4 Hz de UP-Fall, ya corregida en el código) | Ídem | Directo |
| Objetivo 50 Hz                                                | Tsinganos & Skodras (2018); Maurer et al. (2006); Santoyo-Ramón et al. (2022b); Villa & Casilari (2026); Guo & Nakayama (2025) | Directo y análogo            |
| Filtro Butterworth de baja frecuencia antes del resampleo     | Sucerquia et al. (2017, 4.º orden a 5 Hz); Fridolfsson et al. (2019); Villa & Casilari (2026)                                  | Directo y análogo            |
| Remuestreo FIR polifásico con anti-aliasing                   | Crochiere & Rabiner (1981); Villa & Casilari (2026); Silva et al. (2024)                                                       | Directo y análogo            |
| AVM como señal invariante a la orientación                    | Sucerquia et al. (2017); Yu et al. (2021); Ponce et al. (2020)                                                                 | Directo                      |
| GVM (magnitud angular 3D)                                     | Chen et al. (2023); Yu et al. (2021)                                                                                           | Análogo (alcance ergonómico) |
| Etiquetado de eventos por video                               | Yu et al. (2021); Martínez-Villaseñor et al. (2019)                                                                            | Directo                      |
| Ablación `set_a`/`set_b` por heterogeneidad de corpus         | Santoyo-Ramón et al. (2022a); Silva et al. (2024); Casilari et al. (2020); Fula & Moreno (2024)                                | Directo                      |
| Población objetivo y contexto clínico                         | WHO (2021); Klenk et al. (2016)                                                                                                | Directo                      |
| Contexto de sistema (IoT médico, triage en el borde)          | Baker et al. (2017); Gramajo et al. (2025, 2026)                                                                               | Contexto                     |
| Métricas de fidelidad, umbrales del gate y política OR ≥ 2    | —                                                                                                                              | Propio                       |

---

## 14. Referencias

Analog Devices. (s.f.). _ADXL345 data sheet_ (Rev. G). https://www.analog.com/media/en/technical-documentation/data-sheets/adxl345.pdf

Antonsson, E. K., & Mann, R. W. (1985). The frequency content of gait. _Journal of Biomechanics, 18_(1), 39–47. https://doi.org/10.1016/0021-9290(85)90043-0

Apache Software Foundation. (s.f.-a). _File format_. Apache Parquet. https://parquet.apache.org/docs/file-format/

Apache Software Foundation. (s.f.-b). _Reading and writing the Apache Parquet format_. Apache Arrow. https://arrow.apache.org/docs/python/parquet.html

Armbrust, M., Das, T., Sun, L., Yavuz, B., Zhu, S., Murthy, M., Torres, J., van Hovell, H., Ionescu, A., Łuszczak, A., Świtakowski, M., Szafrański, M., Li, X., Ueshin, T., Mokhtar, M., Boncz, P., Ghodsi, A., Paranjpye, S., Senster, P., ... Zaharia, M. (2020). Delta Lake: High-performance ACID table storage over cloud object stores. _Proceedings of the VLDB Endowment, 13_(12), 3411–3424. https://doi.org/10.14778/3415478.3415560

Bagalà, F., Becker, C., Cappello, A., Chiari, L., Aminian, K., Hausdorff, J. M., Zijlstra, W., & Klenk, J. (2012). Evaluation of accelerometer-based fall detection algorithms on real-world falls. _PLoS ONE, 7_(5), e37062. https://doi.org/10.1371/journal.pone.0037062

Baker, S., Xiang, W., & Atkinson, I. (2017). Internet of Things for smart healthcare: Technologies, challenges, and opportunities. _IEEE Access, 5_, 26521–26544. https://doi.org/10.1109/ACCESS.2017.2775180

Batini, C., Cappiello, C., Francalanci, C., & Maurino, A. (2009). Methodologies for data quality assessment and improvement. _ACM Computing Surveys, 41_(3), 1–52. https://doi.org/10.1145/1541880.1541883

Bosch Sensortec. (s.f.-a). _BMI270 data sheet_. https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmi270-ds000.pdf

Bosch Sensortec. (s.f.-b). _Accelerometers overview_. https://www.bosch-sensortec.com/en/products/motion-sensors/accelerometers

Casilari, E., Santoyo-Ramón, J. A., & Cano-García, J. M. (2017). UMAFall: A multisensor dataset for the research on automatic fall detection. _Procedia Computer Science, 110_, 32–39. https://doi.org/10.1016/j.procs.2017.06.110

Casilari, E., Santoyo-Ramón, J. A., & Cano-García, J. M. (2020). On the heterogeneity of existing repositories of movements intended for the evaluation of fall detection systems. _Journal of Healthcare Engineering, 2020_, 6622285. https://doi.org/10.1155/2020/6622285

Casilari, E., & Silva, C. A. (2022). An analytical comparison of datasets of real-world and simulated falls intended for the evaluation of wearable fall alerting systems. _Measurement, 202_, 111843. https://doi.org/10.1016/j.measurement.2022.111843

Chen, H., Schall, M. C., & Fethke, N. B. (2023). Gyroscope vector magnitude: A proposed method for measuring angular velocities. _Applied Ergonomics, 109_, 103981. https://doi.org/10.1016/j.apergo.2023.103981

Crochiere, R. E., & Rabiner, L. R. (1981). Interpolation and decimation of digital signals—A tutorial review. _Proceedings of the IEEE, 69_(3), 300–331. https://doi.org/10.1109/PROC.1981.11969

Data Contract Specification. (s.f.). _Data contracts: The complete guide to data contract standards, tools & best practices_. https://datacontract.com/

Databricks. (s.f.). _What is the medallion lakehouse architecture?_ https://docs.databricks.com/aws/en/lakehouse/medallion

Fridolfsson, J., Börjesson, M., Buck, C., Ekblom, Ö., Ekblom-Bak, E., Hunsberger, M., Lissner, L., & Arvidsson, D. (2019). Effects of frequency filtering on intensity and noise in accelerometer-based physical activity measurements. _Sensors, 19_(9), 2186. https://doi.org/10.3390/s19092186

Fula, V., & Moreno, P. (2024). Wrist-based fall detection: Towards generalization across datasets. _Sensors, 24_(5), Article 1679. https://doi.org/10.3390/s24051679

Gramajo, S., Torres, C., Nuñez, S., Scappini, R., Roa, J., & Montiel, R. (2025). Integrated IoT system for remote health monitoring in home hospitalization. En _Anais do XXII Congresso Latino-Americano de Software Livre e Tecnologias Abertas (Latinoware 2025)_ (pp. 598–602). Sociedade Brasileira de Computação. https://doi.org/10.5753/latinoware.2025.16539

Gramajo, S. D., Scappini, R. J. R., Nuñez, S., Torres, C., Montiel, R., & Roa, J. (2026). Multi-agent framework for resilient medical triage in the Internet of Medical Things (IoMT). En _Actas de las 14th Conference on Cloud Computing, Big Data & Emerging Topics (JCC-BD&ET 2026)_ (pp. 88–101). Universidad Nacional de La Plata, Facultad de Informática. https://sedici.unlp.edu.ar/handle/10915/197628

Guo, P., & Nakayama, M. (2025). A feature engineering method for smartphone-based fall detection. _Sensors, 25_(20), Article 6500. https://doi.org/10.3390/s25206500

Gustafsson, F. (1996). Determining the initial states in forward-backward filtering. _IEEE Transactions on Signal Processing, 44_(4), 988–992. https://doi.org/10.1109/78.492552

Harris, F. J. (1978). On the use of windows for harmonic analysis with the discrete Fourier transform. _Proceedings of the IEEE, 66_(1), 51–83. https://doi.org/10.1109/PROC.1978.10837

He, H., & Garcia, E. A. (2009). Learning from imbalanced data. _IEEE Transactions on Knowledge and Data Engineering, 21_(9), 1263–1284. https://doi.org/10.1109/TKDE.2008.239

IEEE. (2019). _IEEE standard for floating-point arithmetic_ (IEEE Std 754-2019). Institute of Electrical and Electronics Engineers. https://doi.org/10.1109/IEEESTD.2019.8766229

Johnson, J. M., & Khoshgoftaar, T. M. (2019). Survey on deep learning with class imbalance. _Journal of Big Data, 6_(1), Article 27. https://doi.org/10.1186/s40537-019-0192-5

Kaiser, J. F. (1974). Nonrecursive digital filter design using the I0-sinh window function. _Proceedings of the 1974 IEEE International Symposium on Circuits and Systems (ISCAS)_, 20–23.

Keresnyei, R., Megyeri, P., Zidarics, Z., & Hejjel, L. (2015). Selecting the optimal anti-aliasing filter for multichannel biosignal acquisition intended for inter-signal phase shift analysis. _Physiological Measurement, 36_(1), N23–N34. https://doi.org/10.1088/0967-3334/36/1/N23

Klenk, J., Schwickert, L., Palmerini, L., Mellone, S., Bourke, A., Ihlen, E. A. F., Kerse, N., Hauer, K., Pijnappels, M., Synofzik, M., Srulijes, K., Maetzler, W., Helbostad, J. L., Zijlstra, W., Aminian, K., Todd, C., Chiari, L., & Becker, C. (2016). The FARSEEING real-world fall repository: A large-scale collaborative database to collect and share sensor signals from real-world falls. _European Review of Aging and Physical Activity, 13_(1), Article 8. https://doi.org/10.1186/s11556-016-0168-9

Liu, K.-C., Hsieh, C.-Y., Hsu, S. J.-P., & Chan, C.-T. (2018). Impact of sampling rate on wearable-based fall detection systems based on machine learning models. _IEEE Sensors Journal, 18_(23), 9882–9890. https://doi.org/10.1109/JSEN.2018.2872835

Martínez-Villaseñor, L., Ponce, H., Brieva, J., Moya-Albor, E., Núñez-Martínez, J., & Peñafort-Asturiano, C. (2019). UP-Fall detection dataset: A multimodal approach. _Sensors, 19_(9), 1988. https://doi.org/10.3390/s19091988

Maurer, U., Smailagic, A., Siewiorek, D. P., & Deisher, M. (2006). Activity recognition and monitoring using multiple sensors on different body positions. En _International Workshop on Wearable and Implantable Body Sensor Networks (BSN'06)_ (pp. 113–116). IEEE. https://doi.org/10.1109/BSN.2006.6

Microsoft. (s.f.). _Implement medallion lakehouse architecture in Fabric_. Microsoft Learn. https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture

Nyquist, H. (1928). Certain topics in telegraph transmission theory. _Transactions of the American Institute of Electrical Engineers, 47_(2), 617–644. https://doi.org/10.1109/T-AIEE.1928.5055024

Oppenheim, A. V., & Schafer, R. W. (2010). _Discrete-time signal processing_ (3rd ed.). Pearson.

pandera developers. (s.f.). _pandera documentation_. https://pandera.readthedocs.io/en/stable/

Ponce, H., Martínez-Villaseñor, L., & Nuñez-Martínez, J. (2020). Sensor location analysis and minimal deployment for fall detection system. _IEEE Access, 8_, 166678–166691. https://doi.org/10.1109/ACCESS.2020.3022971

Saleh, M., Abbas, M., & Le Jeannès, R. B. (2021). FallAllD: An open dataset of human falls and activities of daily living for classical and deep learning applications. _IEEE Sensors Journal, 21_(2), 1849–1858. https://doi.org/10.1109/JSEN.2020.3018335

Santoyo-Ramón, J. A., Casilari, E., & Cano-García, J. M. (2022a). A cross-dataset evaluation of wearable fall detection systems. _Proceedings of the 15th International Conference on PErvasive Technologies Related to Assistive Environments (PETRA '22)_, 1–6. https://doi.org/10.1145/3529190.3529191

Santoyo-Ramón, J. A., Casilari, E., & Cano-García, J. M. (2022b). A study of the influence of the sensor sampling frequency on the performance of wearable fall detectors. _Measurement, 193_, 110945. https://doi.org/10.1016/j.measurement.2022.110945

SciPy Developers. (2025). _Signal processing (scipy.signal)_ [Documentación]. https://docs.scipy.org/doc/scipy/reference/signal.html

Shannon, C. E. (1949). Communication in the presence of noise. _Proceedings of the IRE, 37_(1), 10–21. https://doi.org/10.1109/JRPROC.1949.232969

Silva, C. A., Casilari, E., & García-Bermúdez, R. (2024). Cross-dataset evaluation of wearable fall detection systems using data from real falls and long-term monitoring of daily life. _Measurement, 235_, Article 114992. https://doi.org/10.1016/j.measurement.2024.114992

Smith, S. W. (1997). _The scientist and engineer's guide to digital signal processing_. California Technical Publishing. https://www.dspguide.com/

STMicroelectronics. (s.f.). _Gyroscopes – MEMS and sensors_. https://www.st.com/en/mems-and-sensors/gyroscopes.html

Sucerquia, A., López, J. D., & Vargas-Bonilla, J. F. (2017). SisFall: A fall and movement dataset. _Sensors, 17_(1), 198. https://doi.org/10.3390/s17010198

Tsinganos, P., & Skodras, A. (2018). On the comparison of wearable sensor data fusion to a single sensor machine learning technique in fall detection. _Sensors, 18_(2), 592. https://doi.org/10.3390/s18020592

van Hees, V. T., Gorzelniak, L., Dean León, E. C., Eder, M., Pias, M., Taherian, S., Ekelund, U., Renström, F., Franks, P. W., Horsch, A., & Brage, S. (2013). Separating movement and gravity components in an acceleration signal and implications for the assessment of human daily physical activity. _PLoS ONE, 8_(4), e61691. https://doi.org/10.1371/journal.pone.0061691

Villa, M., & Casilari, E. (2026). The impact of the accelerometer sampling rate on the performance of machine and deep learning models in wearable fall-detection systems. _Sensors, 26_(1), 162. https://doi.org/10.3390/s26010162

Wang, R. Y., & Strong, D. M. (1996). Beyond accuracy: What data quality means to data consumers. _Journal of Management Information Systems, 12_(4), 5–33. https://doi.org/10.1080/07421222.1996.11518099

World Health Organization. (2021). _Step safely: Strategies for preventing and managing falls across the life-course_. https://www.who.int/publications/i/item/978924002191-4

Yu, X., Jang, J., & Xiong, S. (2021). A large-scale open motion dataset (KFall) and benchmark algorithms for detecting pre-impact fall of the elderly using wearable inertial sensors. _Frontiers in Aging Neuroscience, 13_, 692865. https://doi.org/10.3389/fnagi.2021.692865

Zeng, X., Hui, Y., Shen, J., Pavlo, A., McKinney, W., & Zhang, H. (2023). An empirical evaluation of columnar storage formats. _Proceedings of the VLDB Endowment, 17_(2), 148–161. https://doi.org/10.14778/3626292.3626298
