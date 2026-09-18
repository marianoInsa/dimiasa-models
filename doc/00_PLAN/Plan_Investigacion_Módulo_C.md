# Módulo C — Plan de Investigación de Dataset (SpO2 y Oximetría)

> Objetivo: pipeline + modelo regresión `PPG cruda → SpO2% media ventana 8 s` para sensor tipo MAX30102 (Rojo+IR), TCN/1D-CNN <1 MB, validación sujeto-wise igual que Módulo A.
> Restricción: solo open-access sin credentialing PhysioNet. Toda decisión respaldada por estudio validado. Mejoras no probadas solo como notas.

## 1. Base confirmada: BIDMC PPG and Respiration Dataset

- Enlace: `https://physionet.org/content/bidmc/1.0.0/` — Open Access, 207.7 MB, triple formato WFDB + CSV + MAT.
- Contenido verificado: 53 registros × 8 min (~7 h), UCI Beth Israel Deaconess. Señales **PPG + ECG Lead II + respiración impedancia a 125 Hz**; numéricos **HR/RR/SpO2 a 1 Hz**; anotación manual de respiraciones por 2 anotadores; extraído de MIMIC-II matched waveform.
- Cita obligatoria: Pimentel et al. *Towards a Robust Estimation of Respiratory Rate from Pulse Oximeters.* IEEE TBME 64(8):1914-1923, 2017. DOI `10.1109/TBME.2016.2613124`. DOI dataset `10.13026/C2208R`.
- Rol: **set_a (base)**. Única base liviana con pareja `PPG monocanal 125 Hz + SpO2 numérico 1 Hz` sincronizados, ambos derivados del monitor (sin SaO2 de referencia) → encaja exacto con target ventana 8 s (1.000 muestras) → SpO2 medio. Linaje MIMIC sin DUA. Compatible `NeuroKit2` (ya en `pyproject.toml`) para validar pipeline FASE 1 antes de entrenar; `pyPPG` queda bloqueado por NumPy 2 (evidencia y decisión en [Plan_Implementacion_Módulo_C](Plan_Implementacion_Módulo_C.md)).
- Límite probado: ~7 h, UCI inmóvil, sesgo normoxia 95-100% (colapso de varianza bajo 90%), PPG monocanal procesado por monitor (sin Rojo/IR separados), poco movimiento vs muñeca (conclusión convergente ChatGPT/GEMINI/Sci-Bot C).

## 2. Candidatos complementarios (open-access)

| Dataset | Enlace | N / contexto | Fs / formato | Onda + ground truth | Rojo+IR | Valor |
|---|---|---|---|---|---|---|
| Pulse Transit Time PPG | `https://physionet.org/content/pulse-transit-time-ppg/1.1.0/` DOI `10.13026/jpan-6n92` | 22 sanos, reposo/caminar/correr, 2×MAX30101 + Cortex-M4 | 500 Hz WFDB+CSV; pleth_1 Rojo ~660 nm, pleth_2 IR ~880 nm, pleth_3 verde ~537 nm + ECG/ACC/giro/presión | SpO2 (iHealth Air, puntual al inicio/fin de actividad) + HR/BP | **sí explícito** | Único gemelo hardware MAX3010x → representación óptica real (el orden de canales pleth_1/pleth_2 está contradictorio en la ficha del dataset; verificar en los .hea antes de usar) |
| OpenOximetry Repository | `https://physionet.org/content/openox-repo/1.1.1/` | desaturación controlada lab (CLDS), sanos (CLDS); cohortes clínicas en curso | CSV Common Data Model | PPG cruda+procesada, **SaO2 co-oximetría arterial** + SpO2, mesetas 70-100%, tono piel | sí (Rojo+IR sin escalar, con reserva de sincronía) | Gold-standard hipoxia, corrige sesgo normoxia BIDMC (requiere DUA; Restricted Access — fuera del filtro 'solo open-access sin credentialing' hasta decisión explícita; PPG crudo solo subset a 86 Hz y no sincronizado) |
| VitalDB | `https://vitaldb.net` / espejo PhysioNet `vitaldb/1.0.0` | 6.388 cirugías, intraoperatorio | `SNUADC/PLETH` 500 Hz, `.vital`→CSV/EDF/MAT vía Vital Recorder | numéricos con resolución 1–7 s + capnografía | no (PLETH monitor) | Robustez clínica + multitarea HR/RR/SpO2, desaturaciones intraoperatorias |
| UQ Vital Signs | `https://outbox.eait.uq.edu.au/uqdliu3/uqvitalsignsdataset/` | 32 casos anestesia general/espinal/sedación | CSV 10 ms | Pleth + SpO2/Pulse/HR/awRR/etCO2/ART/ECG | no | Supervisión continua multimodal, ventanas supervisadas directas (licencia CC BY-NC, uso no comercial) |
| CapnoBase | `http://www.capnobase.org` (Borealis) | 42 segmentos × 8 min (29 niños/13 adultos) + calibración 124×2 min, anestesia | PPG 100 Hz orig. / 300 Hz export, CSV/MAT | capnograma CO2 + picos sistólicos y artefactos anotados a mano | no | Benchmark FR desde PPG (error típico ~1 resp/min), referencia experta + artefactos marcados |
| SensSmartTech | PhysioNet DOI `10.13026/fy9p-n277` | 32 voluntarios, 338×30 s, reposo vs post-esfuerzo (FC 83±11→143±14) | PPG MAX86150 100 Hz (660 + 880 nm según datasheet MAX86150; la ficha del dataset dice ~800 nm) + ECG 500 Hz/PCG/ACC | HR ref ECG | sí (dual) | Pretrain invariancia movimiento a 100 Hz, tensor 2×500 en 5 s ideal edge |
| Apnoea simulada 2026 | `https://physionet.org/content/respiratory-oximetry-apnoea/1.0.0/` DOI `10.13026/s45r-k263` | 20 adultos, breath-hold 10/20 s + PEEP, sensor cuello reflectivo | 660 + 940 nm crudas sincronizadas | SpO2 comercial sin desaturación observada | sí | Pipeline Rojo/IR + apnea, **no** regresión SpO2 |

Fuentes: Mehrgardt et al. 2022 (PTT DOI `10.13026/jpan-6n92`); Fong et al. *Open Access Dataset…* Sci Data 12:570, 2025. DOI `10.1038/s41597-025-04870-8` (versión repo PhysioNet DOI `10.13026/be2e-cn29`); Lee et al. *VitalDB…* Sci Data 9:279, 2022. DOI `10.1038/s41597-022-01411-5`; Lee-Jung *Vital Recorder* Sci Rep 2018 DOI `10.1038/s41598-018-20062-4`; Liu et al. Anesth Analg 2012 DOI `10.1213/ANE.0b013e318241f7c0` (UQ); Karlen et al. IEEE TBME 2013 DOI `10.1109/TBME.2013.2246160` + Garde et al. PLoS ONE 2014 (CapnoBase); Reiss et al. Sensors 2019 (PPG-DaLiA, CNN 26k params ~32 KB int8: prueba de tamaño factible, pero el modelo es de FC, no de SpO2); Pimentel 2017 (BIDMC).

## 3. Matriz de compatibilidad y fusión

| Eje | Divergencia | Decisión | Respaldo |
|---|---|---|---|
| Fs (500/300/125/100/64) | distinta resolución | **común 125 Hz** (nativo BIDMC) con `resample_poly` Kaiser β=5; variante documentada 100 Hz para SensSmartTech/CapnoBase si conviene RAM | GEMINI-C: 100 Hz conserva muesca dicrota; 125 Hz preserva pipeline único |
| Canales | Rojo+IR separados vs PLETH monocanal | esquema oro dual: `PPG_R, PPG_IR` cuando existen; `PPG` monocanal en resto con flag `canal_dual=0/1`. Modelo acepta 1-2 canales (depthwise separable) | PTT + SensSmartTech únicos duales; resto PLETH monitor |
| Ground truth | SpO2 1 Hz vs 2 Hz vs SaO2 arterial vs sin SpO2 | target único: **media SpO2 en ventana 8 s** (interpolar numéricos a ventana, excluir ventanas sin cobertura ≥90%). SaO2 solo para calibración/evaluación hipoxia, no mezcla directa | práctica MIMIC/VitalDB (Sci-Bot-C aviso 1) |
| Sincronía | OpenOximetry crudos Rojo/IR sin sincronía total publicada; apnoea sin desaturación | OpenOximetry como **fine-tuning/evaluación hipoxia**, no como train principal hasta verificar sincronía por encuentro (y sujeto a aprobación del DUA; Restricted Access); apnoea solo pipeline | ChatGPT-C §§A-B |
| Formato | WFDB / CSV / MAT / `.vital` | ingesta `wfdb` + CSV + `bidmc_data.mat` + Vital Recorder export; esquema oro común (ver Plan_Implementacion) | Xie WFDB 2023; Lee-Jung 2018 |
| Dominio | UCI inmóvil vs ejercicio vs quirófano vs lab hipoxia | roles separados, no mezcla ciega (abajo) | estrategia 3 etapas ChatGPT-C + 2 etapas GEMINI-C |

## 4. Decisión

- **set_a (base): BIDMC solo.** Aceptación: pipeline PPG + validación de FC/calidad (NeuroKit2) + EDA; sin modelo SpO2 en FASE 1 (C2 bloqueado hasta GT independiente).
- **set_b (generalización): BIDMC + PTT-PPG + OpenOximetry + VitalDB + UQ + CapnoBase (+ SensSmartTech como pretrain movimiento).** Roles: PTT = representación óptica hardware; VitalDB/UQ = fisiología clínica multitarea; OpenOximetry (requiere DUA, decisión pendiente): especialización hipoxia 70-90% solo si se aprueba el acceso; no usable como train bajo el filtro actual; CapnoBase = validación exclusiva de FR (la fuente prohíbe explícitamente entrenar/ajustar algoritmos con él); SensSmartTech = pretrain invariancia movimiento. Apnoea 2026 = desarrollo pipeline Rojo/IR, no train SpO2.
- **Excluidos:** MIMIC-III Waveform Matched (credentialing + DUA, viola filtro; BIDMC ya aporta su linaje abierto); PPG-DaLiA/WESAD (sin SpO2, solo HR/estrés — futuros si se añade rama FC/estrés); MESA/polisomnografía y altitud 2024-25 (sin DOI/enlace verificable en esta ronda).
- PPG-DaLiA se cita como existencia probada de CNN 26k params (~32 KB int8, Reiss 2019) para credibilidad <1 MB.

## 5. Referencias mínimas

Pimentel 2017 (IEEE TBME 64(8):1914-1923; online 2016) DOI `10.1109/TBME.2016.2613124`; Mehrgardt 2022 DOI `10.13026/jpan-6n92`; Fong 2025 DOI `10.1038/s41597-025-04870-8`; Lee 2022 DOI `10.1038/s41597-022-01411-5`; Lee-Jung 2018 DOI `10.1038/s41598-018-20062-4`; Karlen 2013 DOI `10.1109/TBME.2013.2246160`; Goda et al. pyPPG 2024 (Physiol Meas 45:045001) DOI `10.1088/1361-6579/ad33a2`; Makowski et al. NeuroKit2 2021 DOI `10.3758/s13428-020-01516-y`; Reiss 2019 (Deep PPG).

> [!NOTE] Posibles mejoras (no probadas, fuera del trabajo hasta decisión):
> - Cohorte propia MAX30102 con apneas voluntarias/ejercicio etiquetando caídas ≥3% en 10-90 s (Jung 2018 define caída ≥3% y ventana 10-90 s; es detección de eventos, no calibración R→SpO2; Sci-Bot-C) para calibrar ratio R→SpO2 real.
> - Multitarea PPG→{HR,RR,SpO2,BP} con encoder compartido para multiagente (sugerido ChatGPT-C/VitalDB).
> - QAT con calibración en desaturaciones OpenOximetry para no distorsionar AC/DC (propuesto GEMINI-C).
