# Guía de uso

Esta guía explica cómo preparar el proyecto, revisar los análisis y probar la ESP32. La prueba usa señales guardadas en archivos: la computadora las envía por USB y la placa las procesa.

## 1. Preparar el proyecto

Se necesita Python 3.10 a 3.13 y el administrador de entornos `uv`. Desde la carpeta principal del repositorio, instalar las dependencias:

```bash
uv sync --no-install-project --extra dev --extra serial
```

Los archivos de datos no están incluidos en Git. Para los análisis de caídas se usan los CSV reducidos de `notebooks/data/bronce/falls/`. La preparación de la prueba ESP32 también necesita el archivo HDF5 de ECG ubicado en `notebooks/data/oro/ecg/ptb_xl_250hz_lead_ii/`.

Para ejecutar las pruebas de software sin conectar una placa:

```bash
uv run --no-sync pytest -m "not slow" -v
```

## 2. Revisar los análisis

Los análisis están en la carpeta `notebooks/`. Por ejemplo, los notebooks de caídas están en `notebooks/fase_1/modulo_a_caidas/`. Se pueden abrir con Jupyter o Google Colab. Para ejecutarlos localmente, elegir el entorno Python preparado en el paso anterior y comprobar que los archivos de datos requeridos estén en `notebooks/data/`. Ejecutar las celdas en orden.

## 3. Preparar una prueba pequeña

Si los dos archivos de entrada están disponibles, este comando crea una prueba pequeña de caídas y ECG:

```bash
uv run --no-sync python scripts/esp32_dataset_preparation/prepare_test_datasets.py --fall-csv notebooks/data/bronce/falls/KFall-Reduced.csv --ecg-h5 notebooks/data/oro/ecg/ptb_xl_250hz_lead_ii/PTB_XL_senal_250Hz_derivacion_II.h5 --out notebooks/data/esp32_simulation/rule_based/smoke --fall-trials-per-class 3 --ecg-records-per-class 5 --scenarios-per-cell 5 --seed 20261010
```

El conjunto `smoke` sirve para comprobar rápidamente la conexión. La prueba más amplia se crea con el mismo script y con 10 ensayos de caída y 20 registros de ECG por clase.

## 4. Preparar y cargar el firmware desde Arduino IDE

La prueba registrada usó Arduino IDE 2.3.10, soporte ESP32 2.0.17 y `TensorFlowLite_ESP32` 1.0.0. Se recomienda usar esas versiones para reproducir los mismos resultados. La placa probada fue una ESP-WROOM-32.

1. Instalar Arduino IDE y el soporte para placas ESP32 siguiendo la guía oficial de Espressif; seleccionar la versión 2.0.17 del soporte.
2. Instalar `TensorFlowLite_ESP32` versión 1.0.0 desde el administrador de bibliotecas.
3. Abrir `firmware/esp32_validation/esp32_validation.ino` en Arduino IDE.
4. Seleccionar una placa ESP32 compatible y el puerto USB donde aparece conectada.
5. Compilar y cargar el programa desde los botones de Arduino IDE.

El firmware trabaja a 115200 baudios. Cerrar el Monitor Serie de Arduino IDE antes de ejecutar el reproductor: ambos programas no pueden usar el mismo puerto a la vez.

## 5. Enviar la prueba a la placa

Reemplazar `COM5` por el puerto que muestra Arduino IDE. En Linux o macOS suele tener un nombre distinto, por ejemplo `/dev/ttyUSB0`.

```bash
uv run --no-sync python scripts/esp32_simulation/replay.py run --port COM5 --dataset-dir notebooks/data/esp32_simulation/rule_based/smoke --mode fast --output reports/esp32_validation/mi-prueba
```

El resultado queda en `reports/esp32_validation/mi-prueba/`, junto con el resumen de la ejecución. `fast` envía los datos tan rápido como permite la conexión; el modo `paced` intenta respetar la frecuencia de muestreo de las señales.

## Problemas frecuentes

- **El puerto no se puede abrir:** cerrar el Monitor Serie y cualquier otro programa que esté usando la placa.
- **Faltan archivos de entrada:** descargar y preparar los conjuntos descritos en [metodología](metodologia.md).
- **La placa no aparece:** revisar el cable USB, el puerto seleccionado y la instalación del soporte ESP32.

## Documentación oficial de las herramientas

- [Arduino IDE](https://docs.arduino.cc/software/ide-v2)
- [Instalación de placas ESP32 en Arduino IDE](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
- [Guía de Arduino-ESP32](https://docs.espressif.com/projects/arduino-esp32/en/latest/)
- [Biblioteca TensorFlowLite_ESP32](https://docs.arduino.cc/libraries/tensorflowlite_esp32)
- [Python](https://docs.python.org/3/)
- [uv: gestión de entornos y dependencias](https://docs.astral.sh/uv/guides/projects/)
- [PySerial](https://pyserial.readthedocs.io/en/latest/)
- [TensorFlow Lite para microcontroladores](https://ai.google.dev/edge/litert/microcontrollers/overview)
- [Jupyter](https://docs.jupyter.org/en/latest/)
- [Google Colab](https://colab.research.google.com/notebooks/intro.ipynb)
- [NumPy](https://numpy.org/doc/)
- [pandas](https://pandas.pydata.org/docs/)
- [SciPy](https://docs.scipy.org/doc/scipy/)
- [scikit-learn](https://scikit-learn.org/stable/)
- [TensorFlow](https://www.tensorflow.org/guide)
