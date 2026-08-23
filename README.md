# DiMIASA — Modelos Inteligentes para Salud y Ambiente

> **Grupo de investigación:** Centro de Investigación Aplicada en Tecnologías de la Información y la Comunicación (**CInApTIC**)
> **Institución:** Universidad Tecnológica Nacional, Facultad Regional Resistencia — Departamento de Ingeniería en Sistemas de Información
> **Proyecto marco:** Diseño de Modelos Inteligentes de IoT Aplicados a Salud y Ambiente (**DiMIASA**)

---

## Descripción

Este repositorio contiene los modelos de ciencia de datos e inteligencia artificial desarrollados en el marco del proyecto DiMIASA.

El módulo activo implementa un pipeline de **detección de caídas** a partir de datos de acelerómetro y giroscopio (IMU). Los datos crudos de cuatro datasets públicos se normalizan a 100 Hz y se utilizan para entrenar un modelo **CNN-LSTM** con validación cruzada sujeto-wise.

Los notebooks están diseñados para ejecutarse en **Google Colab**.

---

## Estructura del repositorio

```
├── dimiasa_models/
│   └── falls/
│       └── training_lib.py        ← Entrenamiento CNN-LSTM y evaluación
│
├── notebooks/
│   └── falls/
│       ├── pipeline/              ← Flujo principal (ejecutar en orden)
│       │   ├── 00_Preprocesamiento.ipynb
│       │   └── 01_Entrenamiento.ipynb
│       └── experiments/           ← Exploración y pruebas
│           ├── 00-E01-FallAllD-Resampling.ipynb
│           ├── 01-E01-UMAFall-Resampling.ipynb
│           ├── 02-E01-SisFall-UPFall-Resampling.ipynb
│           ├── 03-E02-Resampleo-Unificado.ipynb
│           ├── 04-E02-Resampleo-Unificado (100 Hz).ipynb
│           ├── 05-E03-Preparacion-Final.ipynb
│           └── 06_E03_Preparacion_Final_100Hz.ipynb
│
├── doc/                           ← Documentación, diseños y fuentes
├── pyproject.toml
└── AGENTS.md
```

---

## 🚀 Ejecución en Google Colab

El pipeline se ejecuta en dos pasos en orden:

| Paso | Notebook | Abrir en Colab |
|------|----------|----------------|
| 1 | Preprocesamiento | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/marianoInsa/dimiasa-models/blob/main/notebooks/falls/pipeline/00_Preprocesamiento.ipynb) |
| 2 | Entrenamiento | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/marianoInsa/dimiasa-models/blob/main/notebooks/falls/pipeline/01_Entrenamiento.ipynb) |

La carpeta `experiments/` contiene notebooks de exploración y pruebas utilizados durante el desarrollo del pipeline.

---

## ⚙️ Configuración del entorno

El pipeline lee y escribe datos desde **Azure Data Lake Storage**. Las credenciales deben estar en un archivo `.env` en la raíz del proyecto:

```env
AZURE_STORAGE_ACCOUNT_NAME=<nombre_de_la_cuenta>
AZURE_STORAGE_ACCOUNT_KEY=<clave_de_acceso>
```

En Google Colab, cargá el archivo `.env` en la sesión o montá Google Drive donde esté almacenado antes de ejecutar las celdas de conexión.

---

## 📊 Datasets soportados

| Dataset   | Frecuencia original | Frecuencia normalizada | Señales      |
|-----------|--------------------|-----------------------|--------------|
| SisFall   | 200 Hz             | 100 Hz                | Acc + Gyro   |
| FallAllD  | 238 Hz             | 100 Hz                | Acc + Gyro   |
| KFall     | 100 Hz             | 100 Hz (sin cambio)   | Acc + Gyro   |
| UPFall    | 100 Hz             | 100 Hz (sin cambio)   | Acc + Gyro   |

Los datos normalizados se almacenan en la capa **oro** del Data Lake en formato Parquet.

---

## 🧪 Tests

El proyecto utiliza `pytest`. Para correr la suite de pruebas localmente:

```bash
# Tests unitarios e integración (excluye tests lentos que requieren TF fit)
uv run pytest -m "not slow" -v

# Todos los tests (incluye entrenamiento real, más lento)
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
