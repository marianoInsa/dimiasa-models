
---

Aquí tienes los 3 prompts diseñados específicamente para tu proyecto DiMIASA. Están estructurados para obligar a la IA a buscar en repositorios académicos (PhysioNet, IEEE DataPort, Mendeley Data, Figshare) y filtrar basura de internet.

---

### Prompt para el Módulo A: Detección de Caídas (IMU / MPU6050)

Contexto del Proyecto: Estoy desarrollando un prototipo de Internet de las Cosas Médicas (IoMT) llamado DiMIASA, enfocado en un sistema multiagente para triaje médico resiliente. Este sistema correrá inferencia en el edge (ESP32, y si es posible, Raspberry Pi 4/5) usando modelos TensorFlow Lite livianos (< 1 MB).

Objetivo de la Búsqueda: Realiza un Deep Research para encontrar datasets públicos y validados científicamente sobre Detección de Caídas (Fall Detection) y Actividades de la Vida Diaria (ADL) basados en sensores inerciales (IMU).

Requisitos técnicos del dataset:

1. Tipo de sensor: Acelerómetro de 3 ejes (y preferiblemente giroscopio), similar a lo que capturaría un sensor MPU6050 o un wearable de muñeca/cintura.

2. Exclusiones: NO quiero datasets basados en cámaras, visión computacional (Kinect) ni radares. Solo series temporales inerciales.

3. Baseline actual: Ya conozco y utilizo el dataset "SisFall". Necesito alternativas que lo complementen.

4. Criterios de valor: Busca datasets que incluyan artefactos de movimiento, personas de la tercera edad (si es posible), y una buena proporción de clases negativas (ADLs que parecen caídas pero no lo son, como sentarse bruscamente).

Formato de entrega esperado: Entrégame una tabla comparativa con al menos 4 datasets. Para cada uno indica: Nombre, Enlace al repositorio (ej. IEEE DataPort, Mendeley, PhysioNet), Frecuencia de muestreo (Hz), Número de sujetos, Tipos de actividades, y el paper científico de validación original.

---

### Prompt para el Módulo B: ECG y Arritmias (AD8232)

Contexto del Proyecto: Estoy desarrollando un prototipo de Internet de las Cosas Médicas (IoMT) para triaje clínico en el edge (ESP32, y si es posible, Raspberry Pi 4/5). Estoy construyendo un pipeline de clasificación de señales con redes 1D-CNN que deben pesar menos de 1 MB.

Objetivo de la Búsqueda: Realiza un Deep Research exhaustivo para encontrar datasets públicos, de acceso libre y validados clínicamente que contengan señales de Electrocardiograma (ECG).

Requisitos técnicos del dataset:

1. Tipo de señal: ECG de una sola derivación (Single-lead ECG) o que permita extraer una derivación específica, asimilable a lo que captura un sensor analógico de bajo costo como el AD8232.

2. Baseline actual: Ya estoy utilizando el "MIT-BIH Arrhythmia Database" de PhysioNet. Necesito bases de datos más modernas o con diferentes condiciones.

3. Criterios de valor: Tienen alta prioridad los datasets orientados a wearables (monitoreo ambulatorio u Holter), que contengan ruido del mundo real (artefactos de movimiento, desconexión de electrodos, interferencia de línea base). Me interesan especialmente los repositorios que hayan sido usados en los "PhysioNet / Computing in Cardiology Challenges" recientes.

Formato de entrega esperado: Devuélveme un reporte estructurado con 4 o 5 opciones. Por cada dataset especifica: Nombre, Enlace directo, Número de registros/pacientes, Frecuencia de muestreo (Hz), Patologías o arritmias etiquetadas, y por qué es un buen complemento para el clásico MIT-BIH en un contexto de monitoreo portátil ruidoso.

---

### Prompt para el Módulo C: SpO2 y Oximetría (MAX30102)

Contexto del Proyecto: Estoy desarrollando un sistema IoMT de triaje médico multiagente. Necesito entrenar redes neuronales temporales (TCN o 1D-CNN) que ingieran señales biomédicas crudas para estimar parámetros vitales en dispositivos edge de bajos recursos (ESP32, y si es posible, Raspberry Pi 4/5).

Objetivo de la Búsqueda: Realiza un Deep Research para encontrar datasets públicos orientados a Fotopletismografía (PPG) y estimación de Oximetría de Pulso (SpO2) o Frecuencia Cardíaca/Respiratoria.

Requisitos técnicos del dataset:

1. Tipo de señal: Necesito la forma de onda cruda continua (waveform) del PPG, no solo los números tabulados ya calculados. Debe ser similar a lo que entrega un sensor óptico como el MAX30102.

2. Etiquetado (Ground Truth): Es OBLIGATORIO que el dataset incluya mediciones clínicas de referencia sincronizadas con la señal PPG (ej. niveles de SpO2% extraídos de monitores multiparamétricos o gases en sangre, y frecuencia cardíaca).

3. Baseline actual: Ya estoy utilizando el "BIDMC PPG and Respiration Dataset".

4. Criterios de valor: Busca datasets que incluyan episodios de desaturación de oxígeno (hipoxia, apnea del sueño), estrés fisiológico (ej. pilotos en altitud, pruebas de esfuerzo) o datasets específicos que contengan las dos longitudes de onda (Rojo e Infrarrojo) separadas, ya que esto es ideal para hardware MAX30102.

Formato de entrega esperado: Presenta 4 opciones sólidas extraídas de repositorios como PhysioNet, Nature Scientific Data, o IEEE. Detalla: Nombre, Enlace, Formato de los datos (ej. WFDB, CSV), Presencia de onda cruda vs datos numéricos, Contexto clínico (ej. UCI, sueño, altitud), y el paper DOI de referencia.

---

### 💡 Un consejo para cuando uses los resultados:

Cuando la IA te devuelva las respuestas, fíjate muy bien en la **frecuencia de muestreo (Hz)** de los datasets que encuentre. Como tu plan (Spec v0.3) está diseñado para ingerir datos a 125 Hz (BIDMC) y 200 Hz (SisFall), si un nuevo dataset viene a 500 Hz o a 50 Hz, tendrás que agregar un pequeño paso de _Resampling_ (remuestreo) usando `scipy.signal.resample` en tu código Python antes de pasárselo a tus modelos.