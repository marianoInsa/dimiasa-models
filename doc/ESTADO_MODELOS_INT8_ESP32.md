# Estado de los modelos INT8 para ESP32 — módulos A (caídas) y B (ECG)

**Fecha:** 2026-10-10
**Repo:** `/home/insa/Code/dimiasa-models`
**Objetivo:** evaluar experimentalmente los modelos A y B en un ESP32 clásico con Arduino y TensorFlow Lite Micro.

---

## 1. Resumen ejecutivo

| Módulo | Modelo | Tamaño | Estado |
|---|---|---:|---|
| **B** — ECG (AD8232) | `agent1_tinyecgnet_sequential_int8.tflite` | 18.584 B (18,1 KiB) | ✅ Exportado a C, verificado. Baseline sintético ejecutado en ESP32. |
| **A** — caídas (MPU6050) | `litefallnet_sisfall_int8.tflite` | 45.256 B (44,2 KiB) | 🧪 Apto para esta evaluación experimental externa. El gate de producción en UPFall sigue sin aprobarse. |

El pipeline de conversión y empaquetado está **terminado y verificado para ambos módulos**. Hay un sketch Arduino de baseline sintético; falta el firmware de reproducción serial, el preprocesamiento de señales reales y la prueba con los datasets.

**Alcance del modelo A:** puede ejecutarse en la placa para la validación experimental solicitada. El resultado externo de UPFall documentado en la sección 4 mantiene pendiente el gate de producción; no bloquea esta prueba ni autoriza una afirmación clínica.

### Baseline sintético en Arduino

Sketch: [`firmware/esp32_int8_baseline/esp32_int8_baseline.ino`](../firmware/esp32_int8_baseline/esp32_int8_baseline.ino). Ejecutado con ESP32 clásico, Arduino IDE, ESP32 Core 2.0.17, `TensorFlowLite_ESP32` 1.0.0 y una arena compartida de 80 KiB.

| Modelo | Salida INT8 | Valor desquantizado | Clasificación | Tiempo `Invoke()` informado |
|---|---:|---:|---|---:|
| LiteFallNet | -106 | 0,0859 | Actividad normal | ~638 ms |
| TinyECGNet | 57 | 0,7227 | ECG anormal | ~1113 ms |

Ambos modelos pasaron la comprobación del esquema, el registro de operadores, `AllocateTensors()` e `Invoke()`. El heap libre informado pasó de 267.276 a 267.012 bytes. Las entradas fueron sintéticas: este resultado demuestra integración básica y reutilización secuencial de arena, no paridad del preprocesamiento ni precisión sobre señales de los datasets. Para compilar, los cuatro headers de modelo/configuración deben estar disponibles en el include path de Arduino; los artefactos fuente permanecen en `notebooks/data/modelos/`, ignorado por Git.

---

## 2. Módulo B — ECG (estado: listo)

### Artefactos

| Archivo | Descripción |
|---|---|
| `notebooks/data/modelos/ecg/tinyecgnet_ptb_xl_250hz/tflite/agent1_tinyecgnet_sequential_int8.tflite` | Origen. 18.584 B. sha256 `e4fd65e3bb19ceb3312d6d23e6b8a795a882ed032edddb420844f605ea389de0` |
| `.../firmware/agent1_tinyecgnet_sequential_int8_model.h` | Byte array C, generado |
| `.../firmware/agent1_tinyecgnet_sequential_int8_config.h` | Constantes de cuantización, generadas |
| `scripts/export_tflite_header.py` | Generador de ambos headers (nuevo) |

### Contrato de interfaz

```
Entrada:  [1, 2500, 1] int8   escala 0.081706210970878601   cero -18
Salida:   [1, 1]       int8   escala 0.00390625            cero -128
Techo entrada representable: 11.847400590777397 (valor real)
Decisión:  ANORMAL si q_salida >= 0   (equivalente a p >= 0,5)
```

### Preprocesamiento obligatorio antes de la inferencia

1. Muestrear la salida analógica del AD8232 con el ADC del ESP32 a **250 Hz**, 2500 muestras.
2. Bandpass Butterworth **orden 4, 0,5–40 Hz**, `sosfiltfilt` (fase cero).
3. Notch `iirnotch(50 Hz, Q=30)`, `filtfilt`.
4. **Z-score por ventana**: `(x − media) / max(desvío, 1e-8)`, con la media y el desvío calculados **sobre esa misma ventana de 2500 muestras**, ya filtrada. No hay constantes globales: el firmware debe calcularlas.
5. Reshape a `[1, 2500, 1]`.
6. Cuantizar: `q = clip(rint(z / 0.081706210970878601 + (-18)), −128, 127)`.

**No hace falta calibrar a mV**: el z-score por ventana elimina el offset de continua y la escala. Lo que sí importa es el piso de ruido del ADC.

⚠️ **Los filtros son no causales.** El firmware tiene que bufferingar la ventana completa antes de filtrar. Esto es viable porque el modelo consume la ventana entera de todos modos.

⚠️ **Los coeficientes scipy no están en ningún header.** Hay que exportarlos antes de escribir el C.

### Verificaciones realizadas

| Verificación | Resultado |
|---|---|
| Bytes del header ≡ `.tflite` | ✅ sha256 idéntico, 18.584 B |
| `alignas(16) static const unsigned char` | ✅ |
| Sección de linker | ✅ `.rodata` (flash), no `.data` (RAM) |
| Include guard, `_len` con `sizeof()` | ✅ |
| Constantes de cuantización leídas del `.tflite` | ✅ 18/18 |
| Compila en C11 y gnu17 con `-Wall -Wextra` | ✅ sin warnings |
| Sufijo `f` en todos los flotantes | ✅ |
| Idempotencia (dos corridas → mismos sha256) | ✅ |
| Falla limpio ante `.tflite` inválido o ausente | ✅ exit≠0, mensaje en español, sin archivos parciales |
| `ruff check` / `ruff format --check` | ✅ |

### Archivos eliminados (obsoletos)

- `tflite/agent1_tinyecgnet_sequential_int8.h` — generado con `xxd -i`. **El array sin `const` iba a `.data`, o sea 18.584 B de RAM en un chip con ~320 KB de heap.** Sin `alignas(16)`, sin include guard.
- `firmware/agent1_ecg_sequential_config.h` — no incluía la escala ni el zero point de **entrada**.

### Presupuesto estimado en placa

| Métrica | Valor |
|---|---|
| Arena TFLM | **72.500 B (~70,8 KiB)** — simulación de liveness sobre el grafo |
| MACs | 487.320 |
| Latencia est. ESP32-WROOM-32 con esp-nn | **~3,3 ms** |
| Latencia est. sin esp-nn (ANSI C) | ~16,2 ms |

---

## 3. Módulo A — caídas (baseline experimental ejecutado; gate de producción pendiente)

### Artefactos

| Archivo | Descripción |
|---|---|
| `notebooks/data/modelos/falls/litefallnet_sisfall/litefallnet_sisfall.keras` | 284.051 B, 14.635 parámetros. **No tocar.** |
| `.../litefallnet_sisfall_eval.npz` | 18 MB. Splits de calibración, validación, test y evaluación externa |
| `.../litefallnet_sisfall_int8.tflite` | 45.256 B. sha256 `4454b1f678e228576f1f5a456575dcf4efacbe2b76e9c211a9677ea9be8ed987` |
| `.../litefallnet_sisfall_int8_model.h` | Byte array C, generado |
| `.../litefallnet_sisfall_int8_config.h` | Constantes de cuantización, generadas |
| `.../litefallnet_sisfall_int8_report.json` | Informe completo, incluido el veredicto |
| `notebooks/03_Entrenamiento_LiteFallNet_SisFall.ipynb` | Entrenamiento |
| `notebooks/04_Cuantizacion_LiteFallNet_LiteRT_ESP32.ipynb` | Conversión y empaquetado |

### Arquitectura

LiteFallNet **sin la capa GRU** (el GRU no existe como operador en TFLite; se descompone en miles de ops). 25 capas, 14.635 parámetros.

```
Input [150, 2]
  BatchNormalization
  Conv1D 32 k3 dilation 2 causal ─┐
  BN, LeakyReLU(0.2)               │
  Conv1D 32 k3 dilation 2 causal ─┤ Add (atajo 1x1) ─→ LeakyReLU(0.2)
  SE: GlobalAvgPool → Dense 2 relu → Dense 32 sigmoid → Multiply
  SeparableConv1D 64 k3 → LeakyReLU(0.2) → MaxPool(2) → BatchNormalization
  GlobalMaxPool ⊕ GlobalAvgPool → Dense 64 → LeakyReLU(0.2) → Dense 1 sigmoid
```

### Operadores (13 tipos, 37 instancias, todos BUILTIN)

`ADD` 3 · `CONCATENATION` 1 · `CONV_2D` 4 · `DEPTHWISE_CONV_2D` 1 · `FULLY_CONNECTED` 4 · `LEAKY_RELU` 4 · `LOGISTIC` 2 · `MAX_POOL_2D` 1 · `MEAN` 2 · `MUL` 3 · `PAD` 2 · `REDUCE_MAX` 1 · `RESHAPE` 9

Cero FlexOps, cero operadores custom. Los 13 están en la whitelist de `esp-tflite-micro` v1.4.1. El notebook valida esto automáticamente antes de escribir nada.

### Contrato de interfaz

```
Entrada:  [1, 150, 2] int8   escala 0.001511237001977861   cero -128
Salida:   [1, 1]       int8   escala 0.00390625            cero -128
Rango de entrada representable: [0.000000, 0.385365]
Techo físico derivado: AVM ≤ 10,68 g   |   GVM ≤ 1334,9 °/s
Decisión:  CAÍDA si q_salida >= 0
```

Canal 0 = AVM, canal 1 = GVM.

### Preprocesamiento obligatorio

```
1. Leer 6 ejes del MPU6050 por I²C
2. AVM = sqrt(Ax² + Ay² + Az²)   [g]
   GVM = sqrt(Gx² + Gy² + Gz²)   [°/s]      sin división por 9.81
3. Butterworth orden 4, lowpass 8 Hz, sosfiltfilt   (fs nativa)
4. resample_poly a 50 Hz, Kaiser β=5, padtype="line"
5. AVM_norm = AVM / 27.712812921102035     (= √3 × 16,0 g)
   GVM_norm = GVM / 3464.1016151377544     (= √3 × 2000,0 °/s)
6. Ventana de 150 muestras (3,0 s), paso 75
7. Cuantizar: q = clip(rint(x / 0.001511237001977861 + (-128)), −128, 127)
```

**No hay StandardScaler ni archivo `.joblib`.** La normalización es una división por constante; la primera `BatchNormalization` del modelo queda aprendida en los pesos y se pliega en la conversión. Los divisores están en `litefallnet_sisfall_metadata.json` y ahora también en el `.h` de config.

Etiquetado: `0` = ADL, `1` = caída. Positiva si el centro de la ventana está a ≤ 1,5 s del pico de AVM del trial.

### Presupuesto estimado en placa

| Métrica | Valor |
|---|---|
| Arena TFLM | **19.636 B (~19,2 KiB)** |
| MACs | 826.239 |
| Latencia est. ESP32-WROOM-32 con esp-nn | **~5,5 ms** |

---

## 4. Gate de producción del modelo A (no bloquea esta validación experimental)

### Gate actual

La cuantización INT8 no puede perder más de **2 puntos porcentuales** frente al modelo Keras. Evaluación externa obligatoria (UPFall, dataset no visto en entrenamiento).

| Conjunto | Métrica | Keras | INT8 | Δ | Gate |
|---|---|---:|---:|---:|---|
| SisFall validación | precisión | 0,9732 | 0,9376 | −0,036 | ✅ |
| SisFall validación | recall | 0,9801 | 0,9815 | +0,001 | ✅ |
| SisFall prueba | precisión | 0,9621 | 0,9449 | −0,017 | ✅ |
| SisFall prueba | recall | 0,9758 | 0,9772 | +0,001 | ✅ |
| **UPFall externo** | **precisión** | **0,7458** | **0,5066** | **−0,239** | ❌ |
| UPFall externo | recall | 0,8237 | 0,8933 | +0,070 | ✅ |

`estado_candidato: no_listo_para_despliegue` describe el gate de producción. Para esta evaluación experimental se acepta ejecutar el modelo en la placa y medirlo sobre los datos seleccionados.

En UPFall **1 de cada 2 detecciones es falsa alarma**. Además el recall sube: el modelo grita "caída" ante casi todo.

### Hipótesis original y su refutación

La hipótesis inicial fue: *la escala de entrada define un techo de 10,68 g / 1334,9 °/s y las caídas fuertes se recortan contra el mismo código int8*. Es cierto que hay saturación (0,0611 % de las muestras de UPFall, 160 ventanas de 9745).

Se probó ampliar el techo recalibrando con ventanas estiradas hasta el rango físico del sensor. **Experimento controlado, barrido completo:**

| Techo | AVM máx | GVM máx | val P | test P | upfall P | saturación UPFall |
|---:|---:|---:|---:|---:|---:|---:|
| **0,385** (original) | 10,68 g | 1335 °/s | **0,9476** | **0,9565** | 0,5066 | 0,0611 % |
| 0,500 | 13,86 g | 1732 °/s | 0,8963 | 0,8835 | **0,6107** | 0,0225 % |
| 0,650 | 18,01 g | 2252 °/s | 0,7100 | 0,7475 | 0,4707 | 0,0053 % |
| 0,800 | 22,17 g | 2771 °/s | 0,6938 | 0,7399 | 0,4352 | 0,0013 % |
| 1,000 | 27,71 g | 3464 °/s | 0,6093 | 0,6718 | 0,3807 | 0,0000 % |

**Ningún techo pasa el gate.** Y el dato decisivo: a techo 0,650 la saturación es casi cero (0,0053 %) pero la precisión en UPFall es **peor** que con el techo original. **La saturación no es la causa dominante.** El problema es sensibilidad del modelo a la cuantización en sí.

**El estiramiento sintético se revirtió.** No aportaba nada y agrega complejidad.

### Causa probable

Dos candidatos, en orden de probabilidad:

1. **Cuantización contra la rama SE.** El bloque Squeeze-Excitation multiplica las features por una compuerta sigmoid. En int8 esa compuerta tiene ~256 niveles; el error relativo se amplifica al multiplicar. `esp-nn` solo acelera `elementwise_mul` 1,6–3,8×.
2. **Umbral sobre una sigmoid de 256 niveles.** La salida tiene escala 1/256. Un desplazamiento de ±1 LSB mueve la probabilidad ±0,0039 y puede voltear la decisión en ventanas cerca del umbral. Con ~4000 ventanas de caída por evaluación y un umbral duro en 0,5, esto genera falsos positivos de forma sistemática.

### Camino recomendado

**Quantization-aware training (QAT) con fine-tuning.** Es la vía estándar para este problema y el propio mensaje de error del notebook ya lo señalaba. Opciones a evaluar:

- `keras_quantization` de Keras 3 (`QuantizeDMPerChannelConfig`) — ya está disponible, no requiere `tensorflow_model_optimization`.
- Fine-tuning starting from `litefallnet_sisfall.keras` con capas de cuantización simulada y `normalization=False` en BatchNorm durante el entrenamiento cuantizado.
- Probar la variante **sin bloque SE** o con SE de bottleneck mayor (`r=8` en vez de `r=16`, es decir 4 unidades en vez de 2) para ver si la cuantización se estabiliza.

**Restricción vigente:** no reentrenar, no tocar el `.keras`. Esa restricción fue la que hizo imposible cerrar el problema. Hay que levantarla explícitamente.

---

## 5. Cambios aplicados en esta sesión

### Notebook 04 (conversión del módulo A)

| Cambio | Estado |
|---|---|
| Saturación de entrada medida y reportada en los tres conjuntos | ✅ aplicado |
| Techo de entrada y cobertura del rango físico como diagnóstico (ya no como error) | ✅ aplicado |
| Gate externo (UPFall) obligatorio para aprobar, no chequeo posterior | ✅ aplicado |
| `litefallnet_sisfall_int8_config.h` con todos los `#define` de cuantización y preprocesamiento | ✅ aplicado |
| `alignas(16) static const unsigned char` + `#include <stdalign.h>` | ✅ aplicado |
| Sufijo `f` en todos los flotantes | ✅ aplicado |
| `print` con argumentos invertidos | ✅ corregido |
| Estiramiento sintético del representativo | ⏪ **revertido** tras el barrido |

### ECG

| Cambio | Estado |
|---|---|
| `scripts/export_tflite_header.py` (nuevo, ponytail) | ✅ escrito y verificado |
| Headers regenerados con `const` + `alignas(16)` → `.rodata` | ✅ |
| Header de config con escala de entrada (faltaba) | ✅ |
| `.h` de `xxd -i` eliminado (era RAM) | ✅ |
| `agent1_ecg_sequential_config.h` obsoleto eliminado | ✅ |

### Tests

`tests/test_litefallnet_notebooks.py` — **10 tests, todos en verde.** Cubren estructura del notebook, validación de arreglos, gate sin holdout, contrato de dataset de entrenamiento y contrato de artefactos INT8.

---

## 6. Pendiente

### Pendiente para producción (no bloquea la prueba experimental)

1. **Decidir el camino de cuantización del módulo A.** El PTQ no supera el gate externo actual. QAT queda como trabajo futuro de producción; no cambiar ni reentrenar el modelo durante esta evaluación.

### Para completar la validación experimental

2. **Mantener Arduino Core 2.0.17 y `TensorFlowLite_ESP32` 1.0.0** para aislar la validación sobre el baseline ya ejecutado. La migración a ESP-IDF y la aceleración `esp-nn` quedan fuera de esta prueba.

3. **Exportar los coeficientes de filtro del ECG a C.** No están en ningún header. Deben incluir las condiciones iniciales de estado estacionario de `sosfiltfilt`/`filtfilt`: implementar el filtro con IC en cero introduce un error RMS de **0,067** sobre un ECG real, que destruye la señal de forma silenciosa.

4. **Validar el preprocesamiento en C contra scipy antes de flashear**, con un harness nativo en la PC. Criterio: `max|Δ| < 1e-6`.

5. **No se requiere cablear el AD8232 para la reproducción de datasets.** El host enviará `adc_count_sim`; la validación con sensores físicos corresponde a una fase posterior.

6. **Confirmar el criterio de éxito antes de medir**, como exige `doc/PLAN_VALIDACION_EXPERIMENTAL_AB_ESP32.md`. Distinguir las mediciones sintéticas de este baseline de las mediciones pendientes con datasets.

### Notas de riesgo

- El baseline sintético ya demuestra soporte básico en la placa. Aún falta medir el uso real de arena y heap durante el preprocesamiento y la reproducción de datos; las latencias sintéticas no sustituyen esas mediciones.
- La evaluación de UPFall muestra que la diferencia entre el dominio de entrenamiento y uno nuevo es del orden de 24 puntos de precisión al cuantizar. Cualquier evaluación futura con un tercer dataset debería repetir ese chequeo.
- Los pesos y activaciones de `esp-nn` asumen alineación de 16 bytes. Verificado que los arrays caen en `.rodata` y no en `.data`.
