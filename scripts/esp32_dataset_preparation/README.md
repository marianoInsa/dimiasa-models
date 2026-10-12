# Preparación de datasets de reproducción para la validación ESP32 (A por reglas + ECG)

Genera los datos de entrada del reproductor Ubuntu → ESP32 para el agente de caídas por reglas (A) y para TinyECGNet (B). A usa KFall nativo a 100 Hz; B usa PTB-XL fold 10 a 250 Hz. No reutiliza ni sobrescribe los conjuntos UMAFall previos.

## Dependencias

```bash
python -m pip install numpy pandas h5py
```

## Ejecución

```bash
python prepare_test_datasets.py \
  --fall-csv notebooks/data/bronce/falls/KFall-Reduced.csv \
  --ecg-h5 notebooks/data/oro/ecg/ptb_xl_250hz_lead_ii/PTB_XL_senal_250Hz_derivacion_II.h5 \
  --out notebooks/data/esp32_simulation/rule_based/full \
  --fall-trials-per-class 10 \
  --ecg-records-per-class 20 \
  --scenarios-per-cell 5 \
  --seed 20261010
```

Para la suite mínima: `--fall-trials-per-class 3 --ecg-records-per-class 5 --out …/rule_based/smoke`.

## Archivos generados

- `fall_stream.csv`: trials KFall completos, seis ejes a 100 Hz, recortados a ventanas completas de 100 muestras. Reproducir un trial por vez; nunca concatenar el final de un trial con el siguiente.
- `fall_trial_manifest.csv`: una fila por trial (`source_samples`, `stream_samples`, `trim_remainder`, `windows`, `rate_hz`).
- `ecg_records.csv`: metadatos por registro ECG seleccionado (clase, paciente, fold).
- `ecg_stream.csv`: 2.500 muestras Lead-II a 250 Hz por registro; incluye `adc_count_sim` salvo que se use `--no-adc-simulation`.
- `scenario_manifest.csv`: 20 escenarios sintéticos que cubren las cuatro celdas de la tabla de triaje, referenciando `fall_trial_id` y `ecg_id`.
- `summary.json`: recuentos, hashes de las fuentes, supuestos y advertencias.

## Precauciones

1. El script no filtra, remuestrea ni cuantiza: eso corresponde al firmware, con el mismo preprocesamiento del modelo.
2. Cada trial conserva `floor(N/100)*100` muestras para que toda ventana entregada esté completa; el resto se registra en `trim_remainder`. Un bloque truncado por el transporte no puede producir `ADL`.
3. El prototipo validado monta el sensor en cintura/lumbar, consistente con KFall; el «Pecho» del sketch donante no aplica a esta corrida.
4. KFall no conserva ancla temporal de impacto: A se evalúa por trial, sin latencia desde evento.
5. `adc_count_sim` es una conversión afín sintética a 12 bits, con una única escala compartida; no es calibración física del AD8232. Es la ruta primaria de comparación de B; la señal original queda como referencia secundaria.
6. La clase `ANORMAL` de PTB-XL no equivale a taquicardia. Los escenarios KFall/PTB-XL son artificiales, sin sincronía ni paciente compartido.
7. El script valida integridad al terminar (IDs únicos, índices consecutivos, cardinalidades y referencias con `merge(validate=...)`) y falla ante cualquier huérfano o recuento inesperado.
