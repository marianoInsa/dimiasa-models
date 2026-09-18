# DiMIASA — Modelos Inteligentes para Salud y Ambiente

> - **Grupo de investigación:** Centro de Investigación Aplicada en Tecnologías de la Información y la Comunicación (**CInApTIC**).
> - **Institución:** Universidad Tecnológica Nacional, Facultad Regional Resistencia — Departamento de Ingeniería en Sistemas de Información
> - **Proyecto marco:** Diseño de Modelos Inteligentes de IoT Aplicados a Salud y Ambiente (**DiMIASA**)

---

## Descripción

Este repositorio contiene los modelos de ciencia de datos e inteligencia artificial desarrollados en el marco del proyecto DiMIASA.

El módulo activo implementa un pipeline de **detección de caídas** a partir de las magnitudes vectoriales **AVM** (aceleración) y **GVM** (giroscopio) derivadas de la IMU. Los datos crudos de cinco datasets públicos se normalizan a 50 Hz y se consolidan en dos conjuntos (**set_a**, 5 datasets; **set_b**, 4 sin UMAFall) para entrenar un modelo **CNN-BiLSTM** de 2 canales con validación cruzada sujeto-wise.

---

## Estructura del repositorio

```
├── notebooks/
│    ├── fase_1/               ← Preprocesamiento y entrenamiento
│    │   ├── 00_Preprocesamiento.ipynb
│    │   ├── 01_Entrenamiento.ipynb
│    │   ├── 01_Entrenamiento_2.ipynb   ← Cross-dataset (UMAFall como holdout)
│    │   └── 01-Entrenamiento-GPU.ipynb
│    ├── fase_2/               ← Compresión (cuantización LiteRT)
│    │   └── 02_Compresion.ipynb
│    ├── experiments/           ← Exploración y pruebas
│    └── data/                  ← Arquitectura de datos
│        ├── bronce/falls       ← Datos crudos
│        ├── plata/falls        ← Métricas
│        ├── oro/falls          ← Datos maduros para entrenamiento
│        └── modelos/falls      ← Modelos entrenados (.keras, .joblib, resultados JSON)
│
├── doc/                           ← Documentación, diseños y fuentes
├── check-gpu-status.ps1           ← Verificación del entorno para entrenar en GPU
├── pyproject.toml
└── AGENTS.md
```

> **⚠ Requisito previo:** descargar los CSV reducidos `{Dataset}-Reduced.csv` (SisFall, KFall, FallAllD, UPFall, UMAFall) y crear la carpeta `notebooks/data/bronce/falls` para colocarlos allí. Sin esos archivos crudos no es posible ejecutar `00_Preprocesamiento.ipynb`.

---

## 📊 Datasets soportados

| Dataset  | Frecuencia original | Frecuencia normalizada | Señales    | Filas a 50 Hz |
| -------- | ------------------- | ---------------------- | ---------- | ------------- |
| SisFall  | 200 Hz              | 50 Hz                  | Acc + Gyro | 3,922,862     |
| FallAllD | 238 Hz              | 50 Hz                  | Acc + Gyro | 1,747,000     |
| KFall    | 100 Hz              | 50 Hz                  | Acc + Gyro | 1,979,852     |
| UPFall   | 18.4 Hz             | 50 Hz                  | Acc + Gyro | 792,665       |
| UMAFall  | 20 Hz               | 50 Hz                  | Acc + Gyro | 398,637       |

> El paper de UP-Fall describe los IMU crudos a 100 Hz, pero el archivo consolidado (y el bronce usado) está a ≈18.4 Hz.

---

## 🧹 Preprocesamiento (`00_Preprocesamiento.ipynb`)

Pipeline ETL que normaliza los datos crudos a **50 Hz** con esquema estándar de 14 columnas. Organizado en tres capas de almacenamiento:

- **`bronce/falls`**: CSVs crudos e inmutables de los datasets.
- **`plata/falls`**: métricas de calidad por trial y configuraciones JSON de filtrado.
- **`oro/falls`**: datos finales en Parquet a 50 Hz.

### Pasos del proceso

1. **Ingesta** — lee los CSVs desde `bronce`.
2. **Auditoría de unidades físicas** — valida NaN, mediana de AVM ≈ 1 g, canales muertos y saturación por full-scale.
3. **Validación de etiquetas** — verifica que solo existan `Fall`/`ADL` sin mezcla en un trial; reporta la distribución por dataset.
4. **Métricas de fidelidad por trial** (sobre **AVM y GVM**, solo caídas) — compara una ventana de 2 s centrada en el pico del trial original contra su versión resampleada a 50 Hz:
   - SNR en banda útil (dB)
   - Correlación de Pearson
   - Desfase del pico (ms)
   - Atenuación del pico (%)
   - Estadísticos descriptivos pre/post (media, std, mediana, P05, P95)
   - Resultado persistido en `resampling_metrics_per_trial_50hz.csv`
5. **Filtrado de calidad** — descarta trials que no cumplen umbrales:
   - Pearson `r ≥ 0.85`, desfase `≤ 100 ms`, atenuación `≤ 25 %`
   - Política **OR ≥ 2**: una métrica falla si falla en AVM _o_ GVM; el trial se descarta si fallan al menos 2 de 3 métricas o si es demasiado corto
   - Resultado persistido en `trial_quality_config.json`
6. **Resampleo definitivo** — filtro Butterworth pasa-bajos de orden 4 a 8 Hz con fase cero (`sosfiltfilt`) y luego `resample_poly` con ventana Kaiser (β = 5) a 50 Hz; deriva AVM/GVM y aplica el esquema de 14 columnas.
7. **Exportación** — genera en `oro`:
   - `set_a.parquet`: 5 datasets (~564 MB, 8.841.016 filas)
   - `set_b.parquet`: 4 datasets sin UMAFall (~538 MB, 8.442.379 filas)

### Esquema de salida (oro)

```
Dataset, Subject, Activity_Label, Activity_Code, Trial, Sample_Index,
Ax, Ay, Az, Gx, Gy, Gz, AVM, GVM
```

### Unidades físicas

- Aceleración (`Ax`, `Ay`, `Az`): en g (1 g ≈ 9.81 m/s²)
- Giroscopio (`Gx`, `Gy`, `Gz`): en °/s

---

## 🧠 Entrenamiento (`01_Entrenamiento.ipynb`) - _sin GPU_

Entrena un modelo **CNN-BiLSTM** de 2 canales (`AVM`, `GVM`) para clasificación binaria `Fall`/`ADL` sobre ventanas de 3 s (150 timesteps, 50 % de solapamiento) construidas a partir de la capa `oro/falls/`.

### Pasos del proceso

1. **Mapeo a taxonomía unificada** — asigna cada código de caída a los grupos F1–F10.
2. **Ventaneo precomputado** — genera ventanas etiquetadas por pico de AVM (±1.5 s); el resto queda como `ADL`.
3. **Validación cruzada sujeto-wise** — `StratifiedGroupKFold(K=5)` sobre `Dataset_Subject`, con partición interna de validación del 10 %. El `StandardScaler` se ajusta solo con datos de train para evitar filtraciones.
4. **Entrenamiento** — arquitectura Conv1D + BiLSTM con `BinaryCrossentropy`, optimizador `Adam` (lr = 1e-3), batch 64, hasta 200 épocas, `class_weight={0: 2.0, 1: 1.0}`, `EarlyStopping(patience=10)` y `ReduceLROnPlateau`.
5. **Evaluación** — Sensibilidad / Especificidad / Precisión agregadas entre folds, matriz de confusión con top-3 grupos de la taxonomía por cuadrante, y entrenamiento final por configuración.

### Configuraciones experimentales

| Config | Datasets               | Propósito                               |
| ------ | ---------------------- | --------------------------------------- |
| set_a  | 5 datasets             | Incluir UMAFall                         |
| set_b  | 4 datasets sin UMAFall | Evaluar impacto del resampleo sintético |

### Salidas (`notebooks/data/modelos/falls/`)

- `set_{a,b}_final.keras` + `set_{a,b}_scaler.joblib` — modelo y escalador listos para inferencia.
- `comparison_results.json` — métricas por fold y agregadas.

> Esta variante subsamplea a 15 000 ventanas por clase para train, 1 000 para validación y 5 000 para test, y entrena hasta 200 épocas con `EarlyStopping(patience=10)` para acotar tiempos en CPU.

### Resultados vigentes

| Config | Sensibilidad    | Especificidad   | Precisión       |
| ------ | --------------- | --------------- | --------------- |
| set_a  | 0.9772 ± 0.0096 | 0.9922 ± 0.0032 | 0.9799 ± 0.0082 |
| set_b  | 0.9742 ± 0.0132 | 0.9934 ± 0.0025 | 0.9823 ± 0.0063 |

> Media ± desvío entre los 5 folds de `StratifiedGroupKFold(5)`. Detalle por fold en `comparison_results.json`.

### Cross-dataset (`01_Entrenamiento_2.ipynb`)

- Entrena una única configuración con los cuatro datasets de `set_b` y evalúa **UMAFall** como holdout externo (4 315 ventanas, 324 de caída).

| Config        | Sensibilidad    | Especificidad   | Precisión       |
| ------------- | --------------- | --------------- | --------------- |
| Vista Natural | 0.9846 ± 0.0020 | 0.9917 ± 0.0012 | 0.9064 ± 0.0120 |
| Balanceado    | 0.9846 ± 0.0020 | 0.9920 ± 0.0054 | 0.9920 ± 0.0053 |

---

## 🧪 Entrenamiento (`01-Entrenamiento-GPU.ipynb`) - _con GPU_

Variante experimental del notebook anterior que aprovecha una GPU NVIDIA (Linux nativo o WSL2; en Windows nativo TF ≥ 2.11 no expone GPU). Diferencias clave:

- **Auto-detección de GPU** — activa `mixed_precision=mixed_float16` si hay GPU disponible; la salida del modelo se fuerza a `float32`.
- **8 canales y dataset completo** — usa `Ax`…`Gz` + `AVM`/`GVM` (la variante CPU usa solo `AVM`/`GVM`) y, sin subsampleo, las ~101 k ventanas de `set_a` y ~97 k de `set_b` con `class_weight` dinámico según el ratio natural de cada fold.
- **Hiperparámetros ampliados** — 40 épocas, batch 512, patience 10.
- **Salidas previstas** — `set_{a,b}_final_gpu.keras`, `set_{a,b}_scaler_gpu.joblib` y `comparison_results_gpu.json`.

> Si no detecta GPU, sigue ejecutable en CPU pero será muy lento.

---

## ✅ Verificación del entorno GPU (`check-gpu-status.ps1`)

Script de PowerShell que verifica si Windows está listo para ejecutar `01-Entrenamiento-GPU.ipynb` (variante experimental). Ejecutar desde la raíz del proyecto:

```shell
.\check-gpu-status.ps1
```

Chequea en orden e informa `[PASS]` / `[WARN]` / `[FAIL]` con remediación accionable:

1. Sistema operativo
2. Python (versión compatible con `pyproject.toml`: 3.10–3.13)
3. Hardware GPU y VRAM total (≥ 4 GB recomendado)
4. Driver NVIDIA (`nvidia-smi`)
5. TensorFlow con soporte GPU (CUDA; DirectML como alternativa)
6. Datos oro en disco (`set_a.parquet`, `set_b.parquet`)
7. Espacio libre (≥ 5 GB)
8. Presencia del notebook GPU

Exit code `0` = entorno listo; `1` = hay bloqueantes `[FAIL]` a resolver. Acepta `-ProjectRoot` para apuntar a otra raíz. No requiere venv activado: detecta Python del PATH o `.venv\Scripts\python.exe`.

---

## 🧪 Tests

El proyecto utiliza `pytest`. Para correr la suite de pruebas localmente:

```bash
# Tests unitarios e integración
uv run pytest -m "not slow" -v

# Todos los tests
uv run pytest -v
```

---

## 🐍 Solución a problemas de dependencias (Python 3.14+)

Si `uv add` o `uv sync` falla por incompatibilidad de plataforma (TensorFlow no soporta Python 3.14+), forzá el uso de una versión compatible:

```bash
# 1. Instalar Python 3.13 de forma aislada
uv python install 3.13

# 2. Recrear el entorno virtual con esa versión
uv venv --python 3.13

# 3. Sincronizar todas las dependencias
uv sync
```

> El archivo `pyproject.toml` restringe explícitamente la versión con `requires-python = ">=3.10, <3.14"`.
