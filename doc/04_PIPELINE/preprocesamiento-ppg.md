# Pipeline de Preprocesamiento PPG (Módulo C1 — BIDMC)

**Nota de estado:** Las referencias con DOI están verificadas contra su registro editorial (septiembre de 2026) y las decisiones sin respaldo directo se marcan explícitamente como **decisión propia**. El notebook `notebooks/fase_1/modulo_c_ppg/00_Preprocesamiento-PPG.ipynb` es la verdad del pipeline: constantes, umbrales y conteos provienen de su ejecución del 18 de septiembre de 2026 (commit `5ee0d6b`); los números se re-derivaron de los artefactos de `notebooks/data/plata/ppg/` y `notebooks/data/oro/ppg/`.

Documentos relacionados: [Preprocesamiento de caídas (Módulo A)](preprocesamiento.md) · [Ficha BIDMC](../03_DATASETS/Elegidos/BIDMC.md) · [Plan de Implementación del Módulo C](../00_PLAN/Plan_Implementacion_Módulo_C.md) · [Fundamentación bibliográfica](fundamentacion-literatura.md) · [Fuentes](../02_FUENTES/Fuentes.md) · [README de la wiki](../README.md).

---

## 1. Introducción: qué hace el pipeline y cómo se organiza

`00_Preprocesamiento-PPG.ipynb` es un pipeline ETL que convierte el CSV inmutable de la capa **bronce** (`BIDMC-Reduced.csv`) en un Parquet listo para consumo en la capa **oro** —`set_a.parquet`, nueve columnas a 125 Hz— y en un conjunto de artefactos de validación en la capa **plata** (auditoría física, SQI por ventana, umbrales de calidad y validación de frecuencia cardíaca). El alcance es **C1: pipeline PPG + FC/calidad, sin modelo SpO2**. BIDMC aporta un canal PLETH monocanal procesado por el monitor, sin canales Rojo/IR ni ground truth independiente de SpO2, de modo que un modelo `PPG → SpO2` no es evaluable; C2 queda bloqueado hasta contar con OpenOximetry o una cohorte propia (Sjoding et al., 2020; Cabanas et al., 2024; Fong et al., 2025). La meta de C1 es dejar validado el flujo de señal que después alimentará al MAX30102 en FASE 3 y caracterizar la calidad de la señal antes de entrenar nada; en el roadmap PPG vestible la calidad y la validación de la señal son el cuello de botella reconocido (Charlton et al., 2023), y la transferencia de estimadores de SpO2 a PPG vestible de baja tasa sigue siendo un problema abierto (Liang et al., 2025).

La organización sigue la **arquitectura medallion**: bronce conserva la copia cruda sin modificar, plata contiene datos validados y conformados, oro contiene agregados listos para consumo. No hay reingesta ni edición de bronce; el pipeline solo lee y deriva artefactos nuevos. A diferencia del Módulo A de caídas, acá no hay resampleo: **la tasa nativa de BIDMC es 125 Hz** y se conserva.

| Capa   | Ruta                          | Contenido                                                                                  | Artefactos                                                                                                     |
| ------ | ----------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| Bronce | `notebooks/data/bronce/ppg/`  | CSV crudo e inmutable (`BIDMC-Reduced.csv`)                                                | —                                                                                                              |
| Plata  | `notebooks/data/plata/ppg/`   | Auditoría física, calidad por ventana, umbrales, validación de FC y figuras                | `bidmc_audit.json`, `ppg_quality_config.json`, `ppg_quality_per_window_125hz.csv`, `hr_validation_summary.json`, `fig_*.png` |
| Oro    | `notebooks/data/oro/ppg/`     | Señal a 125 Hz con esquema común                                                           | `set_a.parquet`                                                                                                |

La lógica se reparte en once celdas. La separación de responsabilidades es la misma del Módulo A: **validar** (auditar, medir, marcar calidad) no es **limpiar** (imputar, corregir). El pipeline no imputa nada: la imputación de los numéricos del monitor ocurrió antes, en la reducción a bronce (D10 de [BIDMC.md](../03_DATASETS/Elegidos/BIDMC.md)), y acá solo se audita y se propaga.

| #  | Celda                    | Contenido                                                                                                                   |
| -- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| 1  | MD cabecera              | Alcance C1, límites de BIDMC, citas (Pimentel et al., 2017; Makowski et al., 2021; Elgendi et al., 2013)                   |
| 2  | Config e imports         | Paths `../../data/{bronce,plata,oro}/ppg`; `FS=125`, `WINDOW_S=8`, `STEP_S=4`, `BANDPASS=(0.5, 8)`, rangos de auditoría, `SEED=42` |
| 3  | Ingesta                  | Lectura del CSV; asserts de esquema, 3 180 053 filas, 53 records, 46 sujetos, 0 NaN; `PLETH` a `float32`                   |
| 4  | Auditoría física         | NaN, flatline, valores fuera de rango, perfusión AC/DC y estadísticos por registro → `bidmc_audit.json`                    |
| 5  | Filtrado                 | `nk.ppg_clean(method="elgendi")` por registro; se conservan crudo y filtrado                                                |
| 6  | Ventaneo                 | 8 s (1 000 muestras), paso 4 s (500), por registro                                                                          |
| 7  | SQI y FC por ventana     | Picos Elgendi; `templatematch` por pulso; SNR Welch, skewness, kurtosis, AC/DC, dropout/flatline; `HR_est` y `HR_err`       |
| 8  | Umbrales y validación    | P10 de SQI/SNR/AC-DC, `Quality_Flag`, MAE/RMSE/Pearson/Bland-Altman global y por registro → JSONs de plata                  |
| 9  | EDA                      | Histogramas SpO2, HR/RR, morfología media, SQI/flags, AC/DC → cinco `fig_*.png`                                             |
| 10 | Export                   | `oro/ppg/set_a.parquet` + `plata/ppg/ppg_quality_per_window_125hz.csv`; asserts de conteos y no-NaN                         |
| 11 | MD cierre                | Resultados, limitaciones y estado C2                                                                                        |

---

## 2. Contratos y constantes

La celda 2 fija el contrato del pipeline.

### 2.1 Parámetros

| Constante         | Valor           | Rol                                                                            |
| ----------------- | --------------- | ------------------------------------------------------------------------------ |
| `FS`              | 125 Hz          | Tasa nativa de BIDMC; sin resampleo                                            |
| `WINDOW_S` / `WINDOW_N` | 8 s / 1 000 | Longitud de ventana                                                            |
| `STEP_S` / `STEP_N`     | 4 s / 500   | Paso entre ventanas (solape 50 %)                                              |
| `BANDPASS`        | `(0.5, 8)` Hz   | Banda de pulso de `nk.ppg_clean` (Elgendi et al., 2013)                        |
| `RANGE_SPO2`      | 70–100 %        | Rango fisiológico de auditoría — **decisión propia**                           |
| `RANGE_HR`        | 30–220 bpm      | Rango fisiológico de auditoría — **decisión propia**                           |
| `RANGE_RR`        | 4–60 rpm        | Rango fisiológico de auditoría — **decisión propia**                           |
| `SEED`            | 42              | Semilla global (`np.random.seed`)                                              |

### 2.2 Esquema de salida (capa oro, 9 columnas)

`Dataset`, `Subject`, `Record`, `Sample_Index`, `PPG`, `PPG_Raw`, `SpO2_Ref`, `HR_Ref`, `RR_Ref`.

`Dataset` vale `"BIDMC"`; `Subject` es el sujeto MIMIC de la reducción (D4), preservado para el split sujeto-wise de C2; `Record` identifica el registro; `Sample_Index` enumera 1–60 001 por registro. `PPG` es PLETH filtrada 0.5–8 Hz (entrada de un modelo futuro) y `PPG_Raw` la PLETH cruda (auditoría y morfología); ambas `float32`. `SpO2_Ref`, `HR_Ref` y `RR_Ref` son los numéricos del monitor a 125 Hz en step-hold (D5/D10); `HR_Ref` usa `HR` (FC del monitor), no `PULSE` (Pimentel et al., 2017). No hay `PPG_R`/`PPG_IR`/`Dual_Flag`: BIDMC es PLETH monocanal.

### 2.3 Artefactos y tamaños

| Artefacto                             | Forma / tamaño                            | Contenido                                                              |
| ------------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------- |
| `bidmc_audit.json`                    | 17 594 B                                  | Auditoría física de los 53 registros                                   |
| `ppg_quality_config.json`             | 4 549 B                                   | Umbrales P10, política y conteos de calidad                            |
| `ppg_quality_per_window_125hz.csv`    | 6 307 × 19 · 1 236 955 B                  | Una fila por ventana: SQI, métricas propias y validación de FC         |
| `hr_validation_summary.json`          | 17 273 B                                  | MAE/RMSE/Pearson/Bland-Altman global y por registro                    |
| `fig_*.png`                           | 5 figuras                                 | EDA (SpO2, HR/RR, morfología, SQI/flags, AC-DC)                        |
| `set_a.parquet`                       | 3 180 053 × 9 · 26 006 146 B              | BIDMC completo a 125 Hz, cinco señales `float32`, 0 NaN                |

Un solo CSV de ventanas concentra SQI y FC (decisión de diseño del plan): evita duplicar la grilla de ventanas entre `ppg_quality_per_window_125hz.csv` y un `hr_validation_windows_125hz.csv` separado.

---

## 3. Datos de entrada y capa bronce

`BIDMC-Reduced.csv` (155.13 MiB, 162 660 421 bytes; SHA256 `C4592C48…A3B0`) con esquema exacto:

```text
Record,Subject,Sample_Index,Time_s,PLETH,HR,PULSE,RR,SpO2
```

**53 registros de 8 min (480 s) de UCI (MIMIC-II), 46 sujetos, 3 180 053 filas = 53 × 60 001.** PLETH a 125 Hz; numéricos HR/PULSE/RR/SpO2 a 1 Hz en step-hold; PLETH adimensional (unidades NU del monitor, sin reescalado). Las decisiones de reducción **D1–D10** están completas en [Elegidos/BIDMC.md](../03_DATASETS/Elegidos/BIDMC.md); las que gobiernan este pipeline son:

| Decisión | Contenido                                                                                                              |
| -------- | ---------------------------------------------------------------------------------------------------------------------- |
| D3       | Solo se conserva `PLETH`; ECG y onda respiratoria quedan fuera                                                         |
| D4       | `Subject` = fuente MIMIC-II, para evitar fuga en validación sujeto-wise                                                |
| D5       | Numéricos 1 Hz → 125 Hz por step-hold por segundo; sin interpolación                                                   |
| D6       | Sin reescalado ni z-score: la señal queda en unidades del monitor                                                      |
| D10      | Faltantes crudos resueltos con forward-fill (back-fill al inicio); una columna todo-NaN lanza error en la reducción    |

La repetición de sujetos es parte del dataset, no un error: `s03386` ×4, `s11342` ×4, `s25323` ×2, un registro por sujeto en el resto. Implicación de lectura: cualquier split aleatorio por ventana filtraría información entre registros del mismo sujeto; el split sujeto-wise queda declarado para C2.

Límites de la fuente, relevantes para todo lo que sigue: registros de UCI inmóvil con PLETH ya procesada por el monitor (Pimentel et al., 2017); SpO2 en normoxia (83–100 % por muestra, mínimo de las medias por ventana 83.375 % en `bidmc_32` w20; mayoría 95–100); sin acelerómetro, por lo que no se puede validar SQI de movimiento.

---

## 4. Auditoría física (celda 4)

### 4.1 Diseño

La auditoría corre una vez por registro y persiste en `bidmc_audit.json` (marca temporal UTC, `fs`, rangos usados y un objeto por registro). Las métricas por registro son:

| Métrica         | Definición                                                       | Lectura                                                        |
| --------------- | ---------------------------------------------------------------- | -------------------------------------------------------------- |
| `N_Samples`     | Longitud del registro                                            | 60 001 en todos                                               |
| `NaN`           | Total de NaN en PLETH/SpO2/HR/RR                                 | 0 esperado (D10 los resolvió en la reducción)                  |
| `Flatline`      | `std(PLETH) < 1e-9`                                              | Canal muerto                                                   |
| `Pct_*_Out`     | % de muestras fuera del rango fisiológico (SpO2/HR/RR)           | Valores que el monitor no debió emitir                         |
| `AC_DC_pct`     | `(max − min)/|media| × 100` sobre el registro completo            | Perfusión cruda; con solo PLETH es descriptiva                 |
| `PLETH_Mean/Std`| Media y desviación de la señal                                   | Escala del canal según sesión del monitor                      |

Los tres rangos fisiológicos son **decisión propia** y aquí solo clasifican: la auditoría es descriptiva y no aborta —a diferencia del Módulo A, que valida unidades con guardas duras—. En BIDMC las señales y numéricos ya vienen procesados por el monitor y el objetivo es certificar continuidad y consistencia, no unidades.

### 4.2 Resultados

| Verificación                          | Resultado                                                                             |
| ------------------------------------- | ------------------------------------------------------------------------------------- |
| Registros auditados                   | 53 de 53                                                                              |
| NaN totales (PLETH/SpO2/HR/RR)        | 0                                                                                     |
| Canales flatline                      | 0                                                                                     |
| SpO2 fuera de 70–100 %               | 0 % en todos los registros                                                            |
| HR fuera de 30–220 bpm                | 0 % en todos los registros                                                            |
| RR fuera de 4–60 rpm                  | 0 % salvo `bidmc_13` (73.75 %) y `bidmc_05` (0.21 %)                                 |
| AC/DC de registro (min / mediana / max)| 70.01 % (`bidmc_19`) / 194.85 % / 252.08 % (`bidmc_23`)                               |
| `PLETH_Mean`                          | 0.397–0.497 NU en 44 registros; 1.737–1.929 NU en 9 (`bidmc_40, 42, 44–48, 52, 53`)   |

Lectura de los resultados:

- **Continuidad certificada.** Cero NaN y cero flatline: la reducción a bronce dejó los 53 registros completos y utilizables.
- **SpO2 y HR dentro de rango por construcción.** Los valores del monitor caen en el rango fisiológico en el 100 % de las muestras; la auditoría no detecta nada anómalo en esos dos canales, lo que también significa que no los valida contra una referencia independiente.
- **RR inservible en `bidmc_13`.** El 73.75 % de fuera de rango son 42 251 muestras con RR = 0 (más 2 000 por debajo de 4), un valor no fisiológico; en las ventanas, `RR_Ref` cae por debajo de 4 en 87 de 6 307. El canal RR no se usa en C1 (no hay modelo de respiración), pero `RR_Ref` se exporta: queda documentado como no validado.
- **Dos escalas de PLETH.** Nueve registros tienen media ≈1.8 NU y el resto ≈0.45 NU: es un offset de escala del monitor entre sesiones, no un cambio fisiológico. El pipeline no reescala (D6); C2 deberá decidir la normalización de entrada.

---

## 5. Filtrado (celda 5)

### 5.1 Implementación

Por cada registro, `proc[rec]["Clean"] = nk.ppg_clean(raw, sampling_rate=125, method="elgendi")`, con `raw` en `float64` y un assert de longitudes (`len(clean) == len(raw)`). En NeuroKit2 0.2.13 el método `elgendi` es un **pasa-banda Butterworth de orden 2, 0.5–8 Hz, aplicado con fase cero** (`scipy.signal.butter(..., output="sos")` + `sosfiltfilt`, vía `signal_filter`; Makowski et al., 2021). El doble pasaje hacia adelante y hacia atrás no distorsiona la fase y duplica la atenuación: en magnitud equivale a un Butterworth de orden 4, pero sin el retardo de grupo de un IIR causal. Es un filtro *offline*: usa muestras futuras.

Se conservan ambos vectores por registro (`Raw` y `Clean`, ambos `float32`), y la capa oro exporta los dos: `PPG` filtrada y `PPG_Raw` cruda. Así cualquier revisión del filtro se re-deriva de bronce sin volver a leer el CSV original.

### 5.2 Por qué 0.5–8 Hz

La banda 0.5–8 Hz es la que Elgendi et al. (2013) usan para detección de picos sistólicos, y es la que NeuroKit2 documenta como método de limpieza de referencia. El límite inferior (0.5 Hz = 30 rpm) saca deriva de línea de base y componente respiratoria; el superior (8 Hz) cubre con margen la fundamental cardíaca observada (0.86–2.20 Hz para 51.75–131.875 bpm en las ventanas) y sus primeros armónicos, y recorta ruido de alta frecuencia del monitor. A 125 Hz de muestreo, 8 Hz está muy por debajo de la Nyquist (62.5 Hz): no hay riesgo de plegado y el filtro no actúa como anti-aliasing porque no hay diezmado. El refinamiento respecto del borrador del plan —que preveía un Butterworth propio de orden 4— fue aprobado en la revisión previa a la implementación: usar el método de Elgendi tal como lo entrega NeuroKit2 mantiene la trazabilidad de la banda y de la implementación.

---

## 6. Ventaneo 8 s / paso 4 s (celda 6)

La grilla por registro es

$$
\text{starts} = \text{arange}\big(0,\ \len(\text{Clean}) - f_s \cdot 8 + 1,\ f_s \cdot 4\big),
$$

es decir, ventanas de 1 000 muestras con paso de 500 (solape 50 %). Con 60 001 muestras por registro resultan **119 ventanas por registro y 6 307 en total** (el assert del notebook exige al menos una ventana por registro). La ventana es `[start, start + 1000)`; las referencias numéricas de cada ventana son las medias de `SpO2`, `HR` y `RR` sobre ese intervalo (step-hold).

**Justificación (decisión propia).** Ocho segundos cubren ~8–12 pulsos a 60–90 bpm, suficientes para que el SQI por plantilla y la FC estimada tengan varios ciclos, y 1 000 muestras `float32` son 4 KB por canal, compatibles con el presupuesto de SRAM del MCU objetivo (el mismo criterio de tamaño que motivó la ventana de 3 s en el Módulo A). El solape del 50 % replica el criterio del Módulo A y suaviza la pérdida de eventos en los bordes. Con un registro fijo de 480 s, 119 ventanas por registro es una consecuencia directa de la grilla, no un parámetro independiente. Alternativas como ventanas por evento o por ciclo no aplican: BIDMC no tiene eventos anotados que segmentar.

La cobertura de SpO2 por ventana es 100 % por construcción (D5/D10, step-hold sin faltantes), así que el gate de cobertura ≥90 % que el plan reserva para `set_b` no se evalúa en C1; queda documentado para C2.

---

## 7. SQI y FC por ventana (celdas 7–8)

### 7.1 Detección de picos

Una sola vez por registro, sobre la señal completa y filtrada:

```python
_, info = nk.ppg_peaks(clean, sampling_rate=FS, method="elgendi")
peaks = info["PPG_Peaks"]
```

El método Elgendi (Elgendi et al., 2013; implementación de Makowski et al., 2021) corre sobre las 480 s continuas, no por ventana: así los picos no se pierden ni se duplican en los bordes de ventana. `N_Peaks` de cada ventana es la cantidad de picos con índice en `[start, start + 1000)`; en la práctica van de 1 a 18, mediana 12.

### 7.2 SQI `templatematch` por pulso

`nk.ppg_quality(clean, peaks=peaks, sampling_rate=FS, method="templatematch")` calcula, para cada pulso, el coeficiente de correlación entre la onda individual y una onda plantilla promedio: 1 es un pulso idéntico a la plantilla y 0, sin correlación con ella (Makowski et al., 2021). **En NeuroKit2 0.2.13 la función devuelve un vector por muestra**, porque interpola la correlación ciclo a ciclo sobre `np.arange(len(signal))` con retención (*step-hold*, `method="previous"`). El pipeline lo convierte en SQI por pulso indexando en los picos:

```python
quality_pulse = np.asarray(quality)[peaks]      # SQI por pulso
in_win = (peaks >= start) & (peaks < end)
sqi = float(np.nanmean(quality_pulse[in_win]))  # SQI de la ventana
```

El SQI de ventana promedia los pulsos cuyo pico cae dentro de ella; con `N_Peaks < 2` no hay promedio posible y queda `NaN`. Este es el mismo índice que usan las revisiones de calidad PPG (Desquins et al., 2022; Charlton et al., 2023) y su variante de artefactos de movimiento (Argüello-Prada & Castillo García, 2024), con la salvedad de que BIDMC no tiene movimiento.

### 7.3 Métricas propias por ventana

Además del SQI, cada ventana lleva cuatro descriptores calculados en el pipeline (no son métodos `*_windowed` de NeuroKit2, que devolverían un vector interpolado):

$$
\text{SNR}_{dB} = 10 \log_{10}\left(\frac{P_{\text{banda}}}{\max(P_{\text{total}} - P_{\text{banda}},\ \varepsilon)}\right),
\qquad
\text{AC/DC}_{pct} = \frac{\max(c) - \min(c)}{\left|\overline{r}\right|} \cdot 100
$$

donde $P_{\text{banda}}$ es la potencia de Welch (`scipy.signal.welch`, resolución por defecto) entre 0.5 y 8 Hz y $P_{\text{total}}$ la potencia total; $c$ es la ventana filtrada y $r$ la ventana cruda. La SNR es una **razón de potencia en banda**, no una SNR clásica contra una referencia: mide cuánta energía de la ventana cae en la banda de pulso. AC/DC es un proxy de perfusión (componente pulsátil sobre el nivel del monitor), en la familia del índice de perfusión de la literatura de SQI; la fórmula concreta —normalizar por la media cruda y usar rango en vez de amplitud pico— es **decisión propia**. Se suman `Skew` y `Kurt` (Fisher, sobre la ventana filtrada) como descriptores de forma: se persisten como EDA y **no participan del flag de calidad**. `dropout` (NaN o `std(raw) == 0`) y `flatline` (`std(raw) < 1e-9`) se calculan sobre la ventana cruda.

Todas las decisiones de esta subsección sin cita explícita son **decisión propia**, consistentes con las familias de SQI relevadas por las revisiones (Desquins et al., 2022; Argüello-Prada & Castillo García, 2024).

### 7.4 FC estimada y referencia

La FC por ventana sale de la interpolación por pulso de NeuroKit2:

```python
rate = nk.ppg_rate(peaks, sampling_rate=FS, desired_length=len(clean))
```

`ppg_rate` calcula 60/período entre picos y lo interpola sobre todas las muestras con spline monótono (Makowski et al., 2021); `HR_est` es la media de `rate[start:end]`, calculada solo si `N_Peaks >= 2`. La referencia `HR_Ref` es la media del canal `HR` del monitor en la ventana (step-hold); se usa `HR` y no `PULSE` porque es la FC del monitor derivada de la oximetría (Pimentel et al., 2017). `HR_err = HR_est − HR_Ref`.

---

## 8. Umbrales y política de calidad (celda 8)

### 8.1 Construcción de los umbrales

No se fijan valores absolutos: tras recolectar las 6 307 ventanas se calcula el **percentil 10** de `SQI_templatematch`, `SNR_dB` y `AC_DC_pct` con `np.nanpercentile`, y esos tres valores se persisten en `ppg_quality_config.json`. Los umbrales reales de la corrida:

| Criterio            | Umbral P10 (valor real) | Dirección |
| ------------------- | ----------------------- | --------- |
| `SQI_templatematch` | 0.9316                  | falla si < umbral (o NaN con `N_Peaks ≥ 2`) |
| `SNR_dB`            | 5.4149 dB               | falla si < umbral |
| `AC_DC_pct`         | 51.4284 %               | falla si < umbral |

**Decisión propia.** Usar percentiles en vez de umbrales fisiológicos fijos es el mismo criterio del gate del Módulo A: no se inventan valores de aprobación, se detectan los extremos de la propia distribución. Ventaja: robusto a la escala del monitor (el AC/DC tiene dos escalas de PLETH y los percentiles se adaptan). Límite: es **relativo** — por construcción cada criterio marca ~10 % de las ventanas (631 de 6 307), siempre, aunque toda la muestra fuera excelente.

### 8.2 Regla de decisión

$$ \text{Quality\_Flag} = \begin{cases} \text{low-quality} & \text{si hay flag duro} \\ \text{low-quality} & \text{si fallan} \ge 2 \text{ de los 3 criterios por percentil} \\ \text{ok} & \text{en otro caso} \end{cases} $$

- **Flags duros** (fuerzan `low-quality` sin importar los percentiles): `N_Peaks < 2`, `Dropout` o `Flatline`.
- **Criterios por percentil**: los tres de la tabla; el OR≥2 aplica solo a ellos.
- Un SQI `NaN` con `N_Peaks ≥ 2` también cuenta como falla del criterio SQI.
- El JSON `ppg_quality_config.json` persiste los umbrales, la política, las fallas por criterio (`fail_SQI`, `fail_SNR`, `fail_AC_DC`, `fail_hard`) y los conteos `ok`/`low-quality` por registro; la distribución de `N_Failures` por ventana vive en el CSV, no en el JSON.

### 8.3 Resultados

| Métrica                                          | Valor                       |
| ------------------------------------------------ | --------------------------- |
| Ventanas totales                                 | 6 307                       |
| `ok`                                             | 5 895 (93.5 %)              |
| `low-quality`                                    | 412 (6.5 %)                 |
| Fallas por SQI / SNR / AC-DC                     | 631 / 631 / 631 (10 % c/u)  |
| Ventanas con flag duro                           | 1                           |
| `N_Failures` = 0 / 1 / 2 / 3                     | 4 882 / 1 013 / 356 / 56    |
| Registros con las 119 ventanas `ok`              | 15 de 53                    |
| Peor registro (`low-quality`/119)                | `bidmc_40` (53), `bidmc_41` (46), `bidmc_19` (37), `bidmc_45` (36) |

Las 412 se descomponen en 356 ventanas que fallan exactamente dos criterios (302 SQI+SNR, 38 SQI+AC/DC, 16 SNR+AC/DC) y 56 que fallan los tres. La única ventana con flag duro es también la única sin FC: `bidmc_44`, ventana 73 (`T_start_s = 292`), con `N_Peaks = 1`, SQI `NaN`, SNR −1.37 dB y AC/DC 11.06 %. Su SQI `NaN` no cuenta como falla —el criterio solo falla con `N_Peaks ≥ 2`—, de modo que cae en las 356 por el par SNR+AC/DC, no entre las 56. El flag duro la marca `low-quality` y `HR_est` queda `NaN`. La política tolera una falla por percentil (1 013 ventanas `ok` con un criterio en rojo) y solo descarta cuando hay dos o más, o un indicio duro de que la ventana no tiene señal analizable.

---

## 9. Validación de FC (Bland-Altman)

### 9.1 Método

Sobre las ventanas con `HR_est` y `HR_Ref` no nulos (6 306 de 6 307), global y por registro:

$$
\text{MAE} = \frac{1}{N}\sum |e_i|, \qquad
\text{RMSE} = \sqrt{\frac{1}{N}\sum e_i^2}, \qquad
e_i = HR_{est,i} - HR_{ref,i},
$$

$$
\text{sesgo} = \bar{e}, \qquad
\text{LoA} = \bar{e} \pm 1.96 \cdot \text{DE}(e),
$$

más el coeficiente de Pearson. No se fija un umbral binario de aprobación: se persiste la concordancia completa (Bland & Altman, 1986) y la distribución del error queda en el CSV por ventana (`HR_err`). Todas las métricas quedan en `hr_validation_summary.json`.

### 9.2 Resultado global

| Métrica    | Valor           |
| ---------- | --------------- |
| Ventanas   | 6 307           |
| Válidas    | 6 306           |
| MAE        | 2.2344 bpm      |
| RMSE       | 5.4574 bpm      |
| Pearson r  | 0.9186          |
| Sesgo      | −1.0639 bpm     |
| LoA        | [−11.5551, 9.4274] bpm |

La FC estimada por picos reproduce la del monitor con un error absoluto medio de ~2.2 bpm y un sesgo de −1.06 bpm (subestimación leve); los límites de concordancia de ±~10 bpm muestran que el error medio esconde una cola ancha. La correlación global es alta (0.9186), pero está inflada por las diferencias de nivel de FC **entre** registros (sujetos con FC media distinta): es un artefacto de mezclar registros, no la concordancia intra-registro, que es la relevante para un monitor continuo (sección 9.3).

### 9.3 Resultado por registro

| Métrica (53 registros)              | Rango / valor                                                                 |
| ----------------------------------- | ----------------------------------------------------------------------------- |
| MAE                                 | 0.1982 (`bidmc_07`) – 12.2194 (`bidmc_40`); mediana **1.4862**                 |
| Registros con MAE < 1 / 1–2 / 2–4 / ≥4 | 21 / 11 / 13 / 8                                                            |
| Sesgo                               | negativo en 44 de 53 registros                                                |
| Pearson intra-registro              | negativo en 8 registros; > 0.7 en solo 9; mínimo −0.2374 (`bidmc_40`)         |

Peores registros:

| Registro   | MAE     | RMSE    | Pearson | Sesgo    | `low-quality`/119 |
| ---------- | ------- | ------- | ------- | -------- | ----------------- |
| `bidmc_40` | 12.2194 | 19.0861 | −0.2374 | −12.0137 | 53                |
| `bidmc_26` | 9.5499  | 10.7686 | −0.1809 | −9.3779  | 24                |
| `bidmc_41` | 9.1247  | 12.0938 | 0.1496  | +2.4644  | 46                |
| `bidmc_45` | 5.7608  | 6.8156  | 0.0688  | −0.3550  | 36                |
| `bidmc_25` | 5.4808  | 7.8665  | 0.0541  | −4.7982  | 3                 |
| `bidmc_53` | 4.9637  | 6.4815  | 0.2765  | −2.9186  | 1                 |
| `bidmc_24` | 4.3186  | 5.5293  | 0.1536  | −2.2100  | 0                 |
| `bidmc_04` | 4.1696  | 10.7318 | 0.3156  | −3.8950  | 4                 |
| `bidmc_07` | 0.1982  | 0.2496  | 0.6352  | +0.0865  | 0                 |

Casos que ilustran el patrón más allá de los extremos de MAE: `bidmc_01` tiene un MAE bajo (1.5508) pero correlación negativa (−0.1212) —el `HR` del monitor varía poco dentro del registro y la estimación no sigue esa variación fina—, y `bidmc_04` combina MAE 4.1696 con RMSE 10.7318, señal de errores de cola. Ambos refuerzan que el MAE por sí solo no cuenta toda la historia.

Dos lecturas obligatorias:

- **La dispersión per-record es el hallazgo principal de C1.** Que el MAE global sea 2.23 bpm no significa que la FC sea confiable en todos los registros: hay 8 registros con MAE ≥ 4 bpm y correlaciones intra-registro que caen hasta negativas. La causa candidata es la calidad diferencial de la señal del monitor entre sesiones (escala, perfusión, morfología), pero C1 no la aísla; queda como insumo para C2 y para el gate de calidad por ventana.
- **El flag de calidad no alcanza para filtrar errores de FC.** `bidmc_24` tiene 0 ventanas `low-quality` y aun así MAE 4.32; `bidmc_40` tiene 66 ventanas `ok` sobre 119 y su MAE es 12.22. Calidad de señal y exactitud de FC están correlacionadas pero no son lo mismo: el SQI detecta desviaciones morfológicas, no todo error de la tasa.

---

## 10. Exportación a capa oro (celda 10)

La exportación apila los 53 registros en un único DataFrame y escribe `set_a.parquet` con los 9 campos del esquema de la sección 2.2, cinco señales en `float32` y `Sample_Index` de 1 a 60 001. Los asserts de cierre verifican: columnas exactas y en orden; 0 NaN en `PPG`, `PPG_Raw`, `SpO2_Ref`, `HR_Ref`, `RR_Ref`; 3 180 053 filas; 53 records; `Sample_Index` mínimo 1 y máximo 60 001 por registro; más de 6 000 ventanas. El CSV de ventanas se escribe en el mismo paso (`ppg_quality_per_window_125hz.csv`, 19 columnas). Como en el Módulo A, los Parquet son reproducibles desde plata sin tocar bronce; acá no hay `clear_oro()` porque la única salida es `set_a` y se sobreescribe.

| Verificación                        | Resultado                    |
| ----------------------------------- | ---------------------------- |
| `set_a.parquet`                     | 3 180 053 filas × 9 col · 26 006 146 B |
| Señales en oro                      | `PPG`, `PPG_Raw`, `SpO2_Ref`, `HR_Ref`, `RR_Ref` en `float32` |
| NaN en señales de oro               | 0                            |
| CSV de ventanas                     | 6 307 × 19 · 1 236 955 B     |
| `Quality_Flag`                      | solo `ok` / `low-quality`    |

---

## 11. Evidencia, conclusiones y limitaciones

### 11.1 Conclusiones

1. El pipeline C1 corre de punta a punta sobre BIDMC y produce artefactos completos y trazables: bronce → plata (auditoría + calidad + FC) → oro (125 Hz, 9 columnas), con 0 NaN en las señales exportadas y sin escrituras sobre bronce.
2. La señal filtrada 0.5–8 Hz y los picos Elgendi son utilizables: 5 895 de 6 307 ventanas quedan `ok` y las 412 `low-quality` se reparten de forma interpretable (peores registros: `bidmc_40`, `bidmc_41`, `bidmc_19`, `bidmc_45`).
3. La FC estimada por picos concuerda en promedio con la del monitor (MAE 2.2344 bpm, RMSE 5.4574, sesgo −1.0639), pero **no de forma homogénea**: 8 registros superan 4 bpm de MAE y las correlaciones intra-registro bajan hasta valores negativos. Esa dispersión queda documentada como limitación y como insumo para C2.
4. C2 sigue bloqueado: BIDMC no tiene Rojo/IR ni ground truth independiente; el desbloqueo requiere OpenOximetry (DUA; Fong et al., 2025) o una cohorte propia con MAX30102.

### 11.2 Limitaciones

- **Normoxia.** SpO2 83–100 % por muestra (mínimo de las medias por ventana 83.375 %, `bidmc_32` w20; mayoría 95–100): no hay desaturaciones que permitan validar un modelo SpO2, y el propio SpO2 del monitor tiene sesgos conocidos (Sjoding et al., 2020; Cabanas et al., 2024).
- **UCI inmóvil.** Registros de pacientes en reposo, sin artefactos de movimiento: el SQI de movimiento no se puede validar y BIDMC no trae ACC (limitación registrada en [BIDMC.md](../03_DATASETS/Elegidos/BIDMC.md)).
- **PLETH monocanal del monitor.** No hay Rojo/IR ni señal cruda del sensor: la entrada ya pasó por el procesamiento del monitor, incluido su filtro y su control de ganancia (Pimentel et al., 2017).
- **Referencia de FC no independiente.** `HR_Ref` es el `HR` del mismo monitor: la concordancia mide acuerdo con la estimación del monitor, no con una referencia externa (ECG), y está acotada por la calidad de esa referencia.
- **Dispersión per-record.** MAE 0.1982–12.2194 (mediana 1.4862); 44 de 53 sesgos negativos. El MAE global de 2.23 bpm no debe leerse como error típico de un registro dado. La causa candidata (calidad del monitor por sesión) no se aísla en C1.
- **Pearson global inflado.** El 0.9186 global mezcla variabilidad entre registros; las correlaciones intra-registro son mucho menores (8 negativas) y son las que corresponden a un uso continuo.
- **Umbrales relativos.** Los P10 marcan ~10 % de las ventanas por criterio por construcción (631 cada uno): no son umbrales fisiológicos absolutos, no comparables entre corridas con otro corpus y no detectan una degradación global de la calidad.
- **Cobertura de RR.** `bidmc_13` tiene RR = 0 en 42 251 muestras (70.4 %), y 87 ventanas con `RR_Ref < 4`; `RR_Ref` se exporta pero no se valida en C1.
- **Sin validador de SpO2.** El gate de cobertura de SpO2 ≥90 % por ventana existe en el plan para `set_b`, pero no se aplica en C1 porque el step-hold garantiza 100 % por construcción; tampoco hay validación de SpO2 contra referencia.
- **pyPPG bloqueado.** `pyPPG 1.0.14` usa `np.NaN` (eliminado en NumPy 2) y no declara `dotmap`; las versiones ≥1.0.15 fijan `numpy==1.23.2`. C1 usa NeuroKit2 para picos/FC/SQI y documenta la evidencia en el plan; el reintento queda para C2 con otro entorno o versión futura (Goda et al., 2024).
- **SQI de una sola familia.** `templatematch` es un índice morfológico relativo; los descriptores propios (SNR, AC/DC, skew, kurt) ayudan a la EDA pero solo los tres primeros participan del flag.
- **Decisiones propias.** Banda de ventana (8 s/4 s), percentiles P10, política OR≥2, flags duros, fórmulas de SNR/AC-DC y rangos de auditoría (70–100 / 30–220 / 4–60) no están prescritos por la literatura citada: son aportes del pipeline, consistentes con las revisiones de SQI (Desquins et al., 2022; Argüello-Prada & Castillo García, 2024).

---

## 12. Fuentes primarias por decisión

Las fuentes primarias del proyecto se citan por su publicación oficial (ver [Fuentes.md](../02_FUENTES/Fuentes.md)) y este mapa resume el respaldo de cada decisión. Las celdas sin fuente son **decisión propia**.

| Decisión del pipeline                                       | Respaldo                                                                                     | Tipo                    |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------- |
| Dataset BIDMC y referencia `HR` del monitor (no `PULSE`)    | Pimentel et al. (2017)                                                                        | Directo                 |
| Banda 0.5–8 Hz y detección de picos sistólicos Elgendi      | Elgendi et al. (2013); Makowski et al. (2021)                                                 | Directo                 |
| `nk.ppg_clean(method="elgendi")` (Butterworth 2.º, fase cero) | Makowski et al. (2021); Elgendi et al. (2013)                                                | Directo                 |
| SQI `templatematch` por pulso y `ppg_rate`                  | Makowski et al. (2021); Desquins et al. (2022); Charlton et al. (2023)                        | Directo y revisión      |
| SQI espectrales/estadísticos y artefactos PPG               | Desquins et al. (2022); Argüello-Prada & Castillo García (2024); Charlton et al. (2023)       | Revisión / análogo      |
| MAE/RMSE/Pearson/Bland-Altman sin umbral binario            | Bland & Altman (1986)                                                                          | Directo                 |
| Reducción a bronce y decisiones D1–D10 (step-hold, sin reescalado) | Pimentel et al. (2017); BIDMC.md (documento interno)                                      | Directo / interno       |
| Sesgo de oximetría y bloqueo de C2                          | Sjoding et al. (2020); Cabanas et al. (2024)                                                   | Directo                 |
| Desbloqueo de C2 (OpenOximetry) y transferencia a wearable  | Fong et al. (2025); Liang et al. (2025)                                                        | Directo / contexto      |
| Bloqueo de pyPPG en NumPy 2                                 | Goda et al. (2024); evidencia técnica en el plan C                                              | Contexto                |
| Ventana 8 s / paso 4 s; percentiles P10; OR≥2 y flags duros; fórmulas SNR/AC-DC; rangos de auditoría | —                                                                       | Propio                  |

---

## 13. Referencias

Argüello-Prada, E. J., & Castillo García, J. F. (2024). Machine learning applied to reference signal-less detection of motion artifacts in photoplethysmographic signals: A review. *Sensors, 24*(22), Article 7193. https://doi.org/10.3390/s24227193

Bland, J. M., & Altman, D. G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement. *The Lancet, 327*(8476), 307–310. https://doi.org/10.1016/S0140-6736(86)90837-8

Cabanas, A. M., Valderrama Sáez, N. M., Collao-Caiconte, P. O., Martín-Escudero, P., Pagán, J., Jiménez-Herranz, E., & Ayala, J. L. (2024). Evaluating AI methods for pulse oximetry: Performance, clinical accuracy, and comprehensive bias analysis. *Bioengineering, 11*(11), Article 1061. https://doi.org/10.3390/bioengineering11111061

Charlton, P. H., Allen, J., Bailón, R., Baker, S., Behar, J. A., Chen, F., Clifford, G. D., Clifton, D. A., Davies, H. J., Ding, C., Ding, X., Dunn, J., Elgendi, M., Ferdoushi, M., Franklin, D., Gil, E., Hassan, M. F., Hernesniemi, J., Hu, X., ... Zhu, T. (2023). The 2023 wearable photoplethysmography roadmap. *Physiological Measurement, 44*(11), Article 111001. https://doi.org/10.1088/1361-6579/acead2

Desquins, T., Bousefsaf, F., Pruski, A., & Maaoui, C. (2022). A survey of photoplethysmography and imaging photoplethysmography quality assessment methods. *Applied Sciences, 12*(19), Article 9582. https://doi.org/10.3390/app12199582

Elgendi, M., Norton, I., Brearley, M., Abbott, D., & Schuurmans, D. (2013). Systolic peak detection in acceleration photoplethysmograms measured from emergency responders in tropical conditions. *PLoS ONE, 8*(10), Article e76585. https://doi.org/10.1371/journal.pone.0076585

Fong, N., Lipnick, M. S., Behnke, E., Chou, Y., Elmankabadi, S., Ortiz, L., Almond, C. S., Auchus, I., Burnett, G. W., Bisegerwa, R., Conrad, D. R., Hendrickson, C. M., Hooli, S., Kopotic, R., Leeb, G., Martin, D., McCollum, E. D., Monk, E. P., Moore, K. L., Jr., ... Law, T. J. (2025). Open access dataset and common data model for pulse oximeter performance data. *Scientific Data, 12*, Article 570. https://doi.org/10.1038/s41597-025-04870-8

Goda, M. Á., Charlton, P. H., & Behar, J. A. (2024). pyPPG: A Python toolbox for comprehensive photoplethysmography signal analysis. *Physiological Measurement, 45*(4), Article 045001. https://doi.org/10.1088/1361-6579/ad33a2

Liang, Z., Zhang, R., Shao, W., Karthik, K., Kourkchi, E., Rafatirad, S., & Homayoun, H. (2025). Rapid adaptation of SpO2 estimation to wearable devices via transfer learning on low-sampling-rate PPG. En *2025 IEEE 21st International Conference on Body Sensor Networks (BSN)* (pp. 1–4). IEEE. https://doi.org/10.48550/arXiv.2509.12515

Makowski, D., Pham, T., Lau, Z. J., Brammer, J. C., Lespinasse, F., Pham, H., Schölzel, C., & Chen, S. A. (2021). NeuroKit2: A Python toolbox for neurophysiological signal processing. *Behavior Research Methods, 53*(4), 1689–1696. https://doi.org/10.3758/s13428-020-01516-y

Pimentel, M. A. F., Johnson, A. E. W., Charlton, P. H., Birrenkott, D., Watkinson, P. J., Tarassenko, L., & Clifton, D. A. (2017). Toward a robust estimation of respiratory rate from pulse oximeters. *IEEE Transactions on Biomedical Engineering, 64*(8), 1914–1923. https://doi.org/10.1109/TBME.2016.2613124

Sjoding, M. W., Dickson, R. P., Iwashyna, T. J., Gay, S. E., & Valley, T. S. (2020). Racial bias in pulse oximetry measurement. *New England Journal of Medicine, 383*(25), 2477–2478. https://doi.org/10.1056/NEJMc2029240
