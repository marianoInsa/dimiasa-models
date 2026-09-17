# Módulo B — Plan de Investigación de Dataset (ECG y Arritmias)

> Objetivo: clasificador 3 clases `Normal / Anormal / No-clasificable (ruido)` sobre single-lead tipo AD8232, 1D-CNN <1 MB, inferencia <200 ms, validación sujeto-wise igual que Módulo A.
> Restricción: solo open-access sin credentialing PhysioNet. Toda decisión respaldada por estudio validado. Mejoras no probadas solo como notas.

## 1. Base confirmada: MIT-BIH Arrhythmia Database (MITDB)

- Enlace: `https://physionet.org/content/mitdb/1.0.0/` — Open Access, ZIP 73.5 MB / 104.3 MB descomprimido, WFDB (`.dat/.hea/.atr`).
- Contenido verificado: 48 registros de 30 min, 47 sujetos (BIH Arrhythmia Lab 1975-1979, ~60% inpatients / 40% outpatients), 2 canales Holter, **360 Hz, 11 bits / 10 mV**, ~110.000 anotaciones latido-a-latido adjudicadas por 2+ cardiólogos.
- Citas obligatorias: Moody GB, Mark RG. *The impact of the MIT-BIH Arrhythmia Database.* IEEE Eng Med Biol 20(3):45-50, 2001. PMID 11446209. DOI dataset `10.13026/C2F305`. Más Mark et al. *An annotated ECG database for evaluating arrhythmia detectors.* IEEE TBME 29(8):600, 1982.
- Rol: **set_a (base)**. Gold-standard AAMI EC57, liviano, reproducible, compatible con `wfdb` (ya en `pyproject.toml`) y referencia `awni/ecg` Stanford de FASE 1. Canal MLII extraíble como subrogado single-lead Lead II tipo AD8232 (excepto los registros 102 y 104, cuyo primer canal es V5).
- Límite probado: cohorte pequeña y antigua, Holter limpio hospitalario, sin artefactos wearable (EMG, deriva, lead-off), sin clase Ruido, desbalance hacia N. Entrenar solo aquí sobreajusta y cae en sensor real (conclusión convergente de las 3 investigaciones B: ChatGPT/GEMINI/Sci-Bot).

## 2. Candidatos complementarios (todos open-access verificados en investigaciones)

| Dataset | Enlace | N / pacientes | Fs | Señal | Etiquetas | Anotador | Valor para triaje edge |
|---|---|---|---|---|---|---|---|
| CinC Challenge 2017 | `https://physionet.org/content/challenge-2017/1.0.0/` | 8.528 train (+3.658 test), 9-61 s | 300 Hz | single-lead AliveCor (consumo) | Normal / AF / Other / **Too Noisy** | manual + corrección experta | Única con clase Ruido explícita → alimenta 3ª clase SQA/portero |
| Icentia11k | `https://physionet.org/content/icentia11k-continuous-ecg/1.0/` | 11.000 pacientes, 541.794 segmentos, ≈2,77 mil millones de latidos (2.774.054.987 beats; licencia CC BY-NC-SA, uso no comercial) | 250 Hz 16-bit | single-lead real CardioSTAT (Lead I modificada), días/semana | NSR, AF, flutter, PAC/ESSV, PVC/ESV | 20 tecnólogos + senior (describir como expert-annotated, no solo cardiólogos) | Mejor equilibrio tamaño + wearable real + ambulatorio prolongado |
| CPSC2021 (4th China Challenge) | `https://physionet.org/content/cpsc2021/1.0.0/` | ~105 pacientes, 1.436 segmentos (730 Training_I + 706 Training_II; desglose por subtipo no publicado) | 200 Hz | Lead I/II extraídos de Holter 12-deriv. o wearable 3-deriv. | inicio/fin episodios AF | challenge | Detección de eventos/episodios en monitoreo continuo; el subset de test con hardware distinto no se libera (no usable como validación externa) |
| SHDB-AF | `https://physionet.org/content/shdb-af/1.0.1/` | 128 registros / 122 sujetos, ~24 h c/u (98 anotados) | 125 Hz orig., 200 Hz publicado | 2 canales CC5 mod. + NASA (Fukuda Holter) | AF, flutter, taquicardia auricular, otras TSV + clínica (edad, medicación) | personal cardiología | Validación externa moderna (Holter 2019-2023, población japonesa) → generalización cross-dataset vs MITDB EEUU 70s |
| PTB-XL | `https://physionet.org/content/ptb-xl/1.0.3/` | 21.799 registros / 18.869 pacientes, 10 s | 500 Hz + versión 100 Hz | 12 derivaciones (extraer Lead I/II) | 71 SCP-ECG → 5 superclases NORM/MI/STTC/CD/HYP + metadatos ruido (baseline_drift ~7%, static_noise ~15%) | hasta 2 cardiólogos, folds por paciente | Diversidad isquémica/morfológica + versión 100 Hz que ahorra 80% RAM (4 KB vs 19.5 KB en ventana 10 s float32) |
| BUT QDB (auxiliar SQA) | `https://physionet.org/content/butqdb/1.0.0/` | 18 registros single-lead >24 h free-living + acelerómetro 3 ejes | 1.000 Hz | single-lead + ACC | calidad experta 1-3 | expertos | Entrenar portero SQA separado, no clasificador clínico |

Fuentes: PhysioNet + Wagner et al. *PTB-XL.* Sci Data 7, 2020. DOI `10.1038/s41597-020-0495-6`; Clifford et al. CinC 2017; Reyna et al. *Will Two Do?* CinC 2021 (evidencia «dos derivaciones bastan» para algunas clases; diferencias mayores por diagnóstico individual); Kleyko et al. 2020 (transferencia CinC17→MITDB verificada solo para detección AF binaria); Shen et al. JMBE 2020 (wearable de electrodos secos; el paper no declara aval FDA).

## 3. Matriz de compatibilidad y fusión

| Eje | Divergencia | Decisión de homogenización | Respaldo |
|---|---|---|---|
| Fs (360/300/250/200/500/100/1000) | distinta resolución y RAM | **común 125 Hz** con `resample_poly` + Kaiser β=5 (igual que Módulo A a 50 Hz). Excepción: experimento PTB-XL-100Hz nativo documentado como variante memoria | práctica Challenge + cálculo GEMINI 100 Hz; 125 Hz alinea con el pipeline PPG del Módulo C (BIDMC nativo) y preserva QRS para <1 MB |
| Derivación | 1-lead real vs 12-deriv. vs 2 canales | usar 1 canal: MITDB MLII, Icentia Lead I mod., CinC17 single, CPSC Lead I/II, SHDB CC5, PTB-XL Lead I/II, BUT single | Reyna 2021 («dos derivaciones bastan» para algunas clases; diferencias mayores por diagnóstico individual) + Chen et al., iScience 2020 DOI 10.1016/j.isci.2020.100886 (single-lead ≈ 12-lead en CPSC2018) |
| Etiquetas | AAMI beat vs ritmo 30 s vs SNOMED/SCP vs calidad 1-3 | mapeo único a 3 clases: `Normal` = NSR/NORM/N; `Anormal` = AF/flutter/AT/TSV/PVC/PAC/MI/STTC/CD/HYP/VEB/SVEB; `No-clasificable` = Too Noisy / calidad 3 / lead-off. Tabla de mapeo versionada en `plata/` | AAMI EC57 + ontología SNOMED CinC2021 + SCP-ECG PTB-XL |
| Formato | WFDB mayoritario | ingesta WFDB con `wfdb`, esquema oro común (ver Plan_Implementacion) | Xie et al. WFDB Python 2023, DOI `10.13026/9njx-6322` |
| Anotador | cardiólogos (MITDB/PTB-XL) vs tecnólogos (Icentia) vs challenge | declarar nivel evidencia por fuente; Icentia como `expert-annotated/clinically curated`, no `cardiologist-validated` | página PhysioNet Icentia11k |
| Dominio | hospital limpio vs wearable ruidoso vs poblaciones | **roles separados, no mezcla ciega**: set_a solo MITDB; set_b combinado con pesos por rol (abajo) | recomendación ChatGPT-B §combinación + GEMINI hoja de ruta por fases |

## 4. Decisión

- **set_a (base, reproducir FASE 1 en días): MITDB solo.** Criterio de aceptación: pipeline bronce→oro + baseline 1D-CNN corriendo.
- **set_b (generalización): MITDB + CinC2017 + Icentia11k-subset + SHDB-AF + CPSC2021 + PTB-XL-Lead I.** Roles: Icentia11k = entrenamiento principal wearable (por subsets por costo 630k h); CinC2017 = entrenamiento/validación SQA (clase Ruido); CPSC2021 = validación temporal de episodios; SHDB-AF = validación externa **no mezclada en train** (pregunta: ¿funciona en población/hardware invisibles?); PTB-XL = diversidad morfológica; BUT QDB = auxiliar SQA.
- **Excluidos:** MIMIC-III Waveform Matched (requiere credentialing + DUA, viola filtro solo-abierto); Chapman-Shaoxing / CEAC2019 / Tongji (no verificados como open-access directo en esta ronda, quedan como candidatos futuros); Wearable DB Shen (enlace `shelab.cn` no verificado como descarga directa estable — reevaluar si se necesita gemelo AD8232 de electrodos secos).
- Costo: Icentia11k completo inviable en esta fase → usar subset estratificado documentado (semilla + IDs en `plata/`). Resto ≈12 GB con SHDB-AF (7,3 GB); ≈4,9 GB sin SHDB-AF.

## 5. Referencias mínimas a citar en notebooks

Moody-Mark 2001 (PMID 11446209); Mark et al. 1982; Pimentel et al. 2017 (IEEE TBME 64(8); para coherencia con Módulo C); Wagner et al. 2020 DOI `10.1038/s41597-020-0495-6`; Reyna et al. CinC 2021 DOI `10.23919/cinc53138.2021.9662687`; Kleyko et al. 2020 DOI `10.1088/2057-1976/ab6e1e`; Zheng et al. Sci Data 2020 DOI `10.1038/s41597-020-0386-x` (Chapman, contexto); Shen et al. JMBE 2020 DOI `10.1007/s40846-020-00554-3` (wearable); Xie et al. WFDB 2023 DOI `10.13026/9njx-6322`.

> [!NOTE] Posibles mejoras (no probadas, fuera del trabajo hasta decisión):
> - Preentrenamiento self-supervised/contrastivo en Icentia11k y fine-tuning en MITDB+CinC17 (propuesto por GEMINI-B, sin evidencia propia aún).
> - Aumento con inyección 50/60 Hz + CutMix1D de segmentos ruidosos reales (propuesto por GEMINI-B, calibrar antes).
> - SQA en cascada <50 KB antes del diagnóstico (arquitectura 2 etapas, validar ahorro energético en ESP32-S3).
