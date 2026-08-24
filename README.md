# DiMIASA — Modelos Inteligentes para Salud y Ambiente

> **Grupo de investigación:** Centro de Investigación Aplicada en Tecnologías de la Información y la Comunicación (**CInApTIC**)
> **Institución:** Universidad Tecnológica Nacional, Facultad Regional Resistencia — Departamento de Ingeniería en Sistemas de Información
> **Proyecto marco:** Diseño de Modelos Inteligentes de IoT Aplicados a Salud y Ambiente (**DiMIASA**)

---

## Descripción

Este repositorio contiene los modelos de ciencia de datos e inteligencia artificial desarrollados en el marco del proyecto DiMIASA.

El módulo activo implementa un pipeline de **detección de caídas** a partir de datos de acelerómetro y giroscopio (IMU). Los datos crudos de cinco datasets públicos se normalizan a 50 Hz y se utilizan para entrenar un modelo **CNN-LSTM** con validación cruzada sujeto-wise.

---

## Estructura del repositorio

```
├── notebooks/
│    ├── pipeline/              ← Flujo principal (ejecutar en orden)
│    │   ├── 00_Preprocesamiento.ipynb
│    │   └── 01_Entrenamiento.ipynb
│    ├── experiments/           ← Exploración y pruebas
|    └── data/                  ← Arquitectura de datos
|        ├── bronce/falls       ← Datos crudos
|        ├── plata/falls        ← Métricas
|        └── oro/falls          ← Datos maduros para entrenamiento
│
├── doc/                           ← Documentación, diseños y fuentes
├── pyproject.toml
└── AGENTS.md
```

---

## 📊 Datasets soportados

| Dataset  | Frecuencia original | Frecuencia normalizada | Señales    | Filas a 50 Hz |
| -------- | ------------------- | ---------------------- | ---------- | ------------- |
| SisFall  | 200 Hz              | 50 Hz                  | Acc + Gyro | 3,962,612     |
| FallAllD | 238 Hz              | 50 Hz                  | Acc + Gyro | 1,792,000     |
| KFall    | 100 Hz              | 50 Hz                  | Acc + Gyro | 1,998,789     |
| UPFall   | 100 Hz              | 50 Hz                  | Acc + Gyro | 147,295       |
| UMAFall  | 20 Hz               | 50 Hz                  | Acc + Gyro | 408,882       |

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
4. **Métricas de fidelidad por trial** (sobre **AVM y GVM**) — compara cada trial original contra su versión resampleada a 50 Hz:
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
6. **Resampleo definitivo** — `resample_poly` con ventana Kaiser (β = 5) a 50 Hz; deriva AVM/GVM y aplica el esquema de 14 columnas.
7. **Exportación** — genera en `oro`:
   - `set_a.parquet`: 5 datasets (~528 MB)
   - `set_b.parquet`: 4 datasets sin UMAFall (~503 MB)

### Esquema de salida (oro)

```
Dataset, Subject, Activity_Label, Activity_Code, Trial, Sample_Index,
Ax, Ay, Az, Gx, Gy, Gz, AVM, GVM
```

### Unidades físicas

- Aceleración (`Ax`, `Ay`, `Az`): en g (1 g ≈ 9.81 m/s²)
- Giroscopio (`Gx`, `Gy`, `Gz`): en °/s

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
