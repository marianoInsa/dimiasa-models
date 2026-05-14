# DiMIASA - Entrenamiento de Modelos

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Analizar los modelos inteligentes y ciencia de datos para usar en los modelos de IoT.

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         dimiasa_models and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── dimiasa_models   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes dimiasa_models a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

## 🚀 Guía de Ejecución

### Prerequisito: datos SisFall
Descarga el dataset SisFall y coloca los sujetos en `data/raw/sisfall/`.
Se necesitan al menos 5 sujetos por grupo:
- Adultos jóvenes: `SA01/`, `SA02/`, `SA03/`, `SA04/`, `SA05/`
- Adultos mayores: `SE01/`, `SE02/`, `SE03/`, `SE04/`, `SE05/`

### Ejecutar el pipeline (script)
La forma más directa de correr el pipeline completo (ingest → preprocess → train → evaluate):

```bash
uv run python main.py
```

El script carga la configuración desde `FallsConfig` (editable en `dimiasa_models/falls/config.py`),
entrena el modelo y guarda resultados en `models/falls/` y `reports/figures/falls/`.

### Explorar el pipeline (notebook)
Para explorar el pipeline paso a paso con visualizaciones intermedias:

```bash
# Abrir Jupyter y ejecutar el notebook
uv run jupyter notebook notebooks/01_falls_pipeline.ipynb
```

### Tests
El proyecto utiliza `pytest`. Para correr la suite de pruebas:

```bash
# Tests unitarios e integración (excluye tests lentos que requieren TF fit)
uv run pytest tests/falls/ -m "not slow" -v

# Todos los tests (incluye entrenamiento real, más lento)
uv run pytest tests/falls/ -v
```

--------

## 🐍 Solución a Problemas de Dependencias (Python 3.14+)

Si el comando `uv add` o `uv sync` falla por incompatibilidad de plataforma (ej. TensorFlow no soporta Python 3.14+), debes forzar el uso de una versión aislada compatible ejecutando en tu terminal:

```bash
# 1. Instalar la versión compatible de Python de forma aislada
uv python install 3.13

# 2. Recrear el entorno virtual forzando esa versión
uv venv --python 3.13

# 3. Sincronizar y reinstalar todas las dependencias del proyecto
uv sync
```

> Nota: Asegúrate de que el archivo `pyproject.toml` mantenga la restricción establecida en la línea `requires-python = ">=3.10, <3.14"`.

--------
