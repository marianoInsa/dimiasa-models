# Preparación de datasets reducidos para el prototipo ESP32

## Dependencias

```bash
python -m pip install numpy pandas h5py
```

## Ejecución

Ajustá rutas y nombres según los archivos locales:

```bash
python prepare_test_datasets.py \
  --fall-csv /ruta/UMAFall-Reduced.csv \
  --ecg-h5 /ruta/ecg_dataset.h5 \
  --out ./datasets_esp32 \
  --fall-trials-per-class 10 \
  --ecg-records-per-class 20 \
  --test-fold 10 \
  --seed 20261010
```

Esto genera 10 trials de caídas y 10 ADL (si hay suficientes trials de al menos 60 muestras) y 20 registros ECG NORMAL + 20 ANORMAL del fold 10. Para una prueba mínima se pueden bajar los parámetros.

## Archivos generados

- `fall_stream.csv`: seis ejes de cada trial seleccionado, a 20 Hz. El firmware de reproducción debe procesar un trial por vez y no concatenar el final de un trial con el siguiente.
- `fall_window_manifest.csv`: ventanas de 60 muestras (3 s), con salto de 30 (1,5 s) y etiqueta de referencia por ventana.
- `ecg_records.csv`: un registro por ECG, con clase, paciente y fold.
- `ecg_stream.csv`: señal Lead-II original con 2.500 muestras a 250 Hz, además de `adc_count_sim` salvo que se use `--no-adc-simulation`.
- `scenario_manifest.csv`: combinaciones artificiales para cubrir las cuatro filas principales de la tabla de triaje.
- `summary.json`: recuentos, semilla y advertencias.

## Precauciones

1. El script no aplica filtros ni cuantización de entrada; eso le corresponde al firmware, una sola vez.
2. Se asume que `Activity_Label` permite identificar `Fall` y `ADL`. Si los nombres reales son distintos, adaptá `class_from_activity()`.
3. La etiqueta `model_target_reference` para cada ventana de caída usa el pico de magnitud calculado a partir de los tres ejes de aceleración y la regla de ±30 muestras (1,5 s) indicada en la descripción. Confirmá que coincide exactamente con el código de etiquetado del entrenamiento.
4. El campo `adc_count_sim` es una conversión afín sintética a conteos de 12 bits, con una única escala compartida por todos los registros seleccionados. No representa una calibración física del módulo AD8232. Como el firmware realiza z-score por ventana, la transformación afín positiva debería conservar la forma normalizada salvo efectos de cuantización/filtrado; verificá la paridad contra una señal de referencia.
5. Los escenarios de triaje combinan muestras de UMAFall y ECG de PTB-XL sin sincronía ni identidad compartida. Son útiles para probar el flujo, la tabla y el registro, pero no para afirmar que el sistema detecta trauma real ni reduce falsos positivos clínicos.
6. La clase ANORMAL de PTB-XL no equivale específicamente a taquicardia.
