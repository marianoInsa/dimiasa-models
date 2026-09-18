# Wiki del proyecto DiMIASA

Documentación interna del proyecto DiMIASA (CInApTIC / UTN FRRe): plan de trabajo, conceptos médicos y técnicos, fuentes, datasets y pipelines.

## Tablero de avance

Leyenda: ✅ Completado · ⏭️ Siguiente · ⏸️ Postergado · 🔄 En curso · ⬜ Pendiente

| Etapa                                                                                   | Estado        | Evidencia                                                                                                                                                                                |
| --------------------------------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FASE 1 · Módulo A — Caídas (MPU6050)                                                    | ✅ Completado | [00_Preprocesamiento](../notebooks/fase_1/modulo_a_caidas/00_Preprocesamiento.ipynb) + [01_Entrenamiento](../notebooks/fase_1/modulo_a_caidas/01_Entrenamiento.ipynb); resultados en `notebooks/data/modelos/falls/` |
| FASE 1 · Módulo B — ECG (AD8232)                                                        | ⏭️ Siguiente  | -                                                                                                                                                                                        |
| FASE 1 · Módulo C — SpO2 (MAX30102)                                                     | ✅ C1 completado · ⏸️ C2 bloqueado | C1 ejecutado 18-sep-2026 (commit `5ee0d6b`; pipeline PPG + FC/calidad, sin modelo SpO2): [00_Preprocesamiento-PPG](../notebooks/fase_1/modulo_c_ppg/00_Preprocesamiento-PPG.ipynb) + [preprocesamiento-ppg](04_PIPELINE/preprocesamiento-ppg.md); artefactos en `notebooks/data/plata/ppg/` y `notebooks/data/oro/ppg/set_a.parquet`; estado en [Plan_Implementacion_Módulo_C](00_PLAN/Plan_Implementacion_Módulo_C.md) |
| [FASE 2 — Conversión LiteRT](00_PLAN/FASE%202%20-%20CONVERSIÓN%20LiteRT.md)             | 🔄 En curso (Módulo A)  | [02_Compresion](../notebooks/fase_2/02_Compresion.ipynb)                                                                                                                                                                                        |
| [FASE 3 — Sensores físicos](00_PLAN/FASE%203%20-%20SENSORES%20FÍSICOS.md)               | ⬜ Pendiente  | -                                                                                                                                                                                        |
| [FASE 4 — Sistema multiagente](00_PLAN/FASE%204%20-%20SISTEMA%20MULTIAGENTE.md)         | ⬜ Pendiente  | -                                                                                                                                                                                        |
| [FASE 5 — Validación experimental](00_PLAN/FASE%205%20-%20VALIDACIÓN%20EXPERIMENTAL.md) | ⬜ Pendiente  | -                                                                                                                                                                                        |

### Resultados actuales (Módulo A)

- ETL a 50 Hz con esquema oro de 14 columnas, ventana de 3 s (150 timesteps, 50 % overlap) y CNN-BiLSTM
- Split sujeto-wise con StratifiedGroupKFold(5)
- Configuración CPU con subsampleo de 5k/clase.
- Métricas:
  - **set_a** (5 datasets, 119 sujetos) Sens 0.9780 ± 0.0109 · Spec 0.9935 ± 0.0023 · Prec 0.9822 ± 0.0064
  - **set_b** (4 datasets sin UMAFall, 101 sujetos) Sens 0.9806 ± 0.0072 · Spec 0.9916 ± 0.0046 · Prec 0.9764 ± 0.0127.
    > Nota: falta evaluación cross-dataset

## Cómo leer esta wiki

- Plan y fases → [PLAN DE TRABAJO](00_PLAN/PLAN%20DE%20TRABAJO.md)
- Conceptos (medicina, señales, modelos, ambiente) → `01_CONCEPTOS/`
- Literatura y papers → [Fuentes](02_FUENTES/Fuentes.md)
- Datasets, experimentos y decisiones de datos → [Estrategia](03_DATASETS/Elegidos/Estrategia.md)
- Pipeline construido y su fundamentación → `04_PIPELINE/`
