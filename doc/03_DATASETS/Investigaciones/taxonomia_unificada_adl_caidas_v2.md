# Taxonomía Unificada de ADL y Caídas — v2

## 0. Qué cambia respecto a la v1 y por qué

La versión anterior clasificaba las caídas en 10 grupos (U1–U10) usando **causa** para ocho de ellos (U1–U8) y cambiando a **dirección** (U9) o **mecanismo de impacto** (U10) para los datasets menos detallados. Esto genera categorías no comparables entre sí, al menos un error de mapeo verificable (ver §6.3, FallAllD), pérdida de información que un dataset sí registra (rotación/recuperación en FallAllD), y ninguna taxonomía para ADL.

Esta versión reemplaza la lista plana por una **clasificación facetada**: varios ejes independientes que se registran en paralelo, cada dataset mapeado solo a los ejes que efectivamente documenta (el resto queda como "no documentado", no forzado). Este es el enfoque que usan los marcos de referencia de la literatura clínica y biomecánica de caídas (§1), y es coherente con cómo FallAllD ya nombra sus propias actividades.

Cambios concretos:
- Causa, dirección, mecanismo de impacto, rotación corporal y recuperación/finalización pasan a ser **ejes separados**, no una jerarquía única.
- Se corrige el agrupamiento de A123–A126 de FallAllD (estaban como "tropiezo", son "resbalón" según la propia tabla de descripciones).
- Se añade una taxonomía unificada de ADL (13 grupos), inexistente en la v1.
- Se documenta explícitamente cuándo una ausencia es un vacío real del dataset y no un descuido de mapeo.
- Se marcan dos puntos que no pude verificar contra la fuente primaria (ver §7).

---

## 1. Marco conceptual y fuentes

### 1.1 Qué cuenta como "caída"

La definición clínica estándar, usada en la literatura de geriatría y de detección de caídas, describe una caída como un evento en el que la persona termina, de forma no intencional, en el suelo o en un nivel inferior de apoyo (Kellogg International Work Group on the Prevention of Falls by the Elderly, 1987; Tinetti et al., 1988). Esta definición importa para la taxonomía porque **excluye** los episodios en los que la persona pierde el equilibrio pero recupera una posición sostenida (sentarse de nuevo, agarrarse de un mueble) sin llegar al suelo.

Esto explica una asimetría real entre los datasets: SisFall (D11) y KFall (D15) registran *"sitting a moment, trying to get up, and collapse into a chair"* como **ADL**, no como caída — porque la persona termina sentada, no en el suelo. FallAllD, en cambio, sí incluye una activdad equivalente ("fail to stand up from a sofa/chair, after half standing", A015) también como ADL, consistente con el mismo criterio. Pero UP-Fall clasifica *"falling sitting in empty chair"* como una de sus 5 caídas oficiales, y un dataset externo bien conocido (UniMiB SHAR: Micucci, Mobilio & Napoletano, 2017) también trata *"falling backward while trying to sit on a chair"* como caída, no como ADL. Es decir: la frontera ADL/Caída para "terminar sentado en lugar de en el suelo" **no es consistente ni siquiera a nivel de todo el campo**, no solo entre los 5 datasets de este proyecto. Esto se documenta explícitamente en §7.2 en vez de resolverse por decreto.

### 1.2 Marcos de clasificación de caídas en la literatura

Dos líneas de trabajo, ambas verificadas, sustentan el diseño facetado:

- **Noury et al. (2007, 2008)** propusieron un esquema de clasificación y evaluación de detectores de caída pensado explícitamente para permitir comparación entre estudios, dada la falta de un "benchmark" común — el mismo problema que motiva este documento. Su propuesta separa características del sujeto, posición inicial, dirección y circunstancia, en vez de una única jerarquía de tipos de caída.
- **Robinovitch et al. (2013)**, del grupo de Simon Fraser University, analizaron 227 caídas reales de adultos mayores en cuidado a largo plazo, grabadas en video con un cuestionario estructurado (Yang et al., 2013). Encontraron que el mecanismo causal más frecuente fue el desplazamiento incorrecto de peso (41% de los casos), seguido de tropiezo (21%) y golpe o choque contra un objeto (11%). Trabajos derivados del mismo grupo estudiaron **dirección** de la caída, **rotación corporal** durante el descenso y **uso de manos/brazos** como respuestas protectoras como variables independientes entre sí (Schonnop et al., 2013; Komisar et al., 2022), y un estudio específico de ese mismo grupo analizó las caídas durante transiciones sentado↔de pie como categoría propia (Komisar et al., 2022) — exactamente la separación que la v1 acertaba parcialmente (U5 vs. U6) pero sin sostenerla de forma consistente en el resto de la taxonomía.
- **Bagalà et al. (2012)** evaluaron algoritmos de detección contra caídas reales del proyecto FARSEEING, reforzando que causa, dirección y circunstancia son ejes que se reportan por separado en la literatura de caídas reales, no como una única etiqueta.

Nota importante de alcance: estos tres estudios describen **caídas reales en adultos mayores**, mientras que los 5 datasets de este proyecto son **caídas simuladas por voluntarios** (mayoritariamente jóvenes, cayendo sobre colchonetas). Uso estos marcos para la *estructura* de la clasificación (qué ejes son biomecánicamente relevantes), no para asumir que las proporciones de causas observadas en caídas reales se replican en los datos simulados. La propia FallAllD (Saleh, Abbas & Le Jeannès, 2021) discute esta limitación de protocolo de simulación en datasets de caídas en general, y vale para los 5 datasets aquí revisados.

### 1.3 Riesgo de caída vs. mecanismo de la caída (por qué no se mezclan)

La literatura clínica separa **factores de riesgo** (por qué una persona es propensa a caer: intrínsecos como debilidad muscular o deterioro cognitivo, extrínsecos como iluminación deficiente — CDC, 2017) de las **circunstancias del evento** (qué pasó en esta caída puntual: resbalón, tropiezo, síncope). Esta taxonomía clasifica exclusivamente lo segundo, porque es lo que un sensor puede registrar; los factores de riesgo son información demográfica/clínica que ninguno de los 5 datasets captura de forma sistemática.

### 1.4 Actividades de la vida diaria: aclaración de terminología

El término "ADL" en estos 5 datasets (y en la literatura de reconocimiento de actividad humana en general — Lara & Labrador, 2013) designa simplemente "movimientos cotidianos no relacionados con una caída" (caminar, sentarse, subir escaleras). Esto es distinto del uso clínico de "ADL" en geriatría (índice de Katz: bañarse, vestirse, comer, etc., para medir independencia funcional). Es una convención establecida en el campo de HAR/detección de caídas, no un error de este proyecto, pero vale aclararlo para no mezclar ambos sentidos al citar literatura.

---

## 2. Principio de diseño: ejes independientes, no jerarquía única

Cada caída se describe con hasta 6 valores independientes. Si un dataset no documenta un eje para un código dado, ese eje queda como **ND (no documentado)** — no se fuerza una equivalencia. Esto resuelve directamente los problemas §1–5 de la crítica: la dirección de una caída de UMAFall (que solo documenta dirección) queda en el mismo eje y con los mismos valores que la dirección de una caída de SisFall (que además documenta causa), así que son comparables en ese eje sin forzar el resto.

### Leyenda de ejes (Caídas)

| Eje | Nombre | Valores posibles |
|---|---|---|
| **1** | Actividad previa | Reutiliza los grupos G1–G8 de la taxonomía de ADL (§3) + ND |
| **2** | Mecanismo causal | RESB (resbalón) · TROP (tropiezo) · SINC (síncope/pérdida de conciencia) · PEQ-S (pérdida de equilibrio al sentarse) · PEQ-L (pérdida de equilibrio al levantarse) · REPOS (reacomodo en cama) · GOLPE (golpe/choque, no representado en ningún dataset del proyecto — ver §5) · ND |
| **3** | Dirección | ADEL (adelante) · ATR (atrás) · LAT (lateral) · VERT (vertical) · ND |
| **4** | Mecanismo de impacto / respuesta protectora | MANOS · RODIL (rodillas) · MESA (manos sobre mueble/mesa) · SILLA (termina en silla/mueble) · DIRECTO (sin respuesta protectora registrada) · ND |
| **5** | Rotación corporal durante la caída | SI · NO · ND |
| **6** | Recuperación / finalización | COMPL (caída completa, llega al suelo) · RECUP (recupera el equilibrio, cuasi-caída) · ND |

El Eje 1 reutiliza los grupos de ADL a propósito: la "actividad previa" de una caída **es** un estado de ADL interrumpido, así que usar el mismo vocabulario en ambas taxonomías evita mantener dos sistemas de etiquetas para la misma idea.

---

## 3. Taxonomía Unificada de ADL

| Grupo | Nombre | Descripción |
|---|---|---|
| **G1** | Marcha | Caminar a paso normal o rápido, en línea recta o con giro. |
| **G2** | Trote / carrera | Jogging o carrera ligera, a cualquier velocidad. |
| **G3** | Escaleras | Subir o bajar escaleras, a cualquier velocidad. |
| **G4** | Bipedestación estática | De pie, sin desplazamiento, durante un período sostenido. |
| **G5** | Sedestación estática | Sentado (silla o sofá) sin desplazamiento, durante un período sostenido. |
| **G6** | Decúbito estático | Acostado (cama) sin cambio de posición, durante un período sostenido. |
| **G7** | Transición sentado↔de pie | Sentarse o levantarse (silla, sofá, auto, o el suelo), en cualquier velocidad, incluida la transición normal. |
| **G8** | Transición decúbito↔sentado | Acostarse o levantarse de la cama, incluidos los cambios de posición mientras se está acostado. |
| **G9** | Flexión de tronco / recogida de objetos | Agacharse (con o sin flexionar rodillas) para recoger algo del piso, con o sin regreso a la posición inicial. |
| **G10** | Salto | Saltar o dar pequeños brincos sin que constituya una caída. |
| **G11** | Cuasi-caída / recuperación de equilibrio | Tropezar sin caer, o iniciar una caída y recuperar el equilibrio terminando en una posición sostenida (p. ej. colapsar de vuelta a una silla al intentar levantarse). Clase de "falso positivo difícil" para un detector de caídas. |
| **G12** | Gestos y actividades instrumentales | Aplaudir, saludar con la mano, levantar/mover brazos, simular una llamada, abrir una puerta. |
| **G13** | Contextos de transporte | De pie o sentado en transporte en movimiento (bus, metro), uso de ascensor, entrar/salir de un auto. |

Los grupos G1–G13 solo clasifican ADL. G11 merece atención aparte: es la clase que más le importa a un detector de caídas porque es la más fácil de confundir con una caída real, y su cobertura es muy desigual entre datasets (ver §5).

---

## 4. Descripciones oficiales por dataset y mapeo a la taxonomía

Las descripciones se preservan literalmente de la documentación de cada dataset (citas en §8). Los identificadores oficiales (D##, F##, A###, T##, y los números de UP-Fall) permiten trazabilidad hacia los datos crudos.

### 4.1 SisFall

Fuente: Sucerquia, López & Vargas-Bonilla (2017). 19 ADL + 15 caídas, 38 sujetos (23 jóvenes, 15 adultos mayores). Sensor único en la cintura.

**ADL**

| ID | Descripción | Grupo |
|---|---|---|
| D01 | Walking slowly | G1 |
| D02 | Walking quickly | G1 |
| D03 | Jogging slowly | G2 |
| D04 | Jogging quickly | G2 |
| D05 | Walking upstairs and downstairs slowly | G3 |
| D06 | Walking upstairs and downstairs quickly | G3 |
| D07 | Slowly sit in a half height chair, wait a moment, and up slowly | G7 |
| D08 | Quickly sit in a half height chair, wait a moment, and up quickly | G7 |
| D09 | Slowly sit in a low height chair, wait a moment, and up slowly | G7 |
| D10 | Quickly sit in a low height chair, wait a moment, and up quickly | G7 |
| D11 | Sitting a moment, trying to get up, and collapse into a chair | **G11** (cuasi-caída; no llega al suelo — ver §1.1) |
| D12 | Sitting a moment, lying slowly, wait a moment, and sit again | G8 |
| D13 | Sitting a moment, lying quickly, wait a moment, and sit again | G8 |
| D14 | Being on one's back change to lateral position, wait a moment, and change to one's back | G8 |
| D15 | Standing, slowly bending at knees, and getting up | G9 |
| D16 | Standing, slowly bending without bending knees, and getting up | G9 |
| D17 | Standing, get into a car, remain seated and get out of the car | G13 |
| D18 | Stumble while walking | **G11** |
| D19 | Gently jump without falling (trying to reach a high object) | G10 |

**Caídas** (Eje1=Actividad previa, Eje2=Causa, Eje3=Dirección, Eje4=Impacto, Eje5=Rotación, Eje6=Recuperación)

| ID | Descripción oficial | E1 | E2 | E3 | E4 | E5 | E6 |
|---|---|---|---|---|---|---|---|
| F01 | Fall forward while walking caused by a slip | G1 | RESB | ADEL | ND | ND | COMPL |
| F02 | Fall backward while walking caused by a slip | G1 | RESB | ATR | ND | ND | COMPL |
| F03 | Lateral fall while walking caused by a slip | G1 | RESB | LAT | ND | ND | COMPL |
| F04 | Fall forward while walking caused by a trip | G1 | TROP | ADEL | ND | ND | COMPL |
| F05 | Fall forward while jogging caused by a trip | G2 | TROP | ADEL | ND | ND | COMPL |
| F06 | Vertical fall while walking caused by fainting | G1 | SINC | VERT | ND | ND | COMPL |
| F07 | Fall while walking, use of hands on a table to dampen fall, caused by fainting | G1 | SINC | ND | MESA | ND | COMPL |
| F08 | Fall forward when trying to get up | G7 | PEQ-L | ADEL | ND | ND | COMPL |
| F09 | Lateral fall when trying to get up | G7 | PEQ-L | LAT | ND | ND | COMPL |
| F10 | Fall forward when trying to sit down | G7 | PEQ-S | ADEL | ND | ND | COMPL |
| F11 | Fall backward when trying to sit down | G7 | PEQ-S | ATR | ND | ND | COMPL |
| F12 | Lateral fall when trying to sit down | G7 | PEQ-S | LAT | ND | ND | COMPL |
| F13 | Fall forward while sitting, caused by fainting or falling asleep | G5 | SINC | ADEL | ND | ND | COMPL |
| F14 | Fall backward while sitting, caused by fainting or falling asleep | G5 | SINC | ATR | ND | ND | COMPL |
| F15 | Lateral fall while sitting, caused by fainting or falling asleep | G5 | SINC | LAT | ND | ND | COMPL |

### 4.2 KFall

Fuente: Yu, Jang & Xiong (2021). 21 ADL + 15 caídas, 32 sujetos jóvenes coreanos. Sensor único en zona lumbar, con video sincronizado.

**ADL**

| ID | Descripción | Grupo |
|---|---|---|
| D01 | Stand for 30 s | G4 |
| D02 | Stand, slowly bend the back with or without bending at knees, tie shoe lace, and get up | G9 |
| D03 | Pick up an object from the floor | G9 |
| D04 | Gently jump (try to reach an object) | G10 |
| D05 | Stand, sit to the ground, wait a moment, and get up with normal speed | G7 (transición extendida a nivel de suelo) |
| D06 | Walk normally with turn (4 m) | G1 |
| D07 | Walk quickly with turn (4 m) | G1 |
| D08 | Jog normally with turn (4 m) | G2 |
| D09 | Jog quickly with turn (4 m) | G2 |
| D10 | Stumble while walking | **G11** |
| D11 | Sit on a chair for 30 s | G5 |
| D12 | Sit on the sofa (back is inclined to the support) for 30 s | G5 |
| D13 | Sit down to a chair normally, and get up from a chair normally | G7 |
| D14 | Sit down to a chair quickly, and get up from a chair quickly | G7 |
| D15 | Sit a moment, trying to get up, and collapse into a chair | **G11** |
| D16 | Stand, sit on the sofa (back is inclined to the support), and get up normally | G7 |
| D17 | Lie on the bed for 30 s | G6 |
| D18 | Sit a moment, lie down to the bed normally, and get up normally | G8 |
| D19 | Sit a moment, lie down to the bed quickly, and get up quickly | G8 |
| D20 | Walk upstairs and downstairs normally (five steps) | G3 |
| D21 | Walk upstairs and downstairs quickly (five steps) | G3 |

**Caídas**

| ID | Task | Descripción oficial | E1 | E2 | E3 | E4 | E5 | E6 |
|---|---|---|---|---|---|---|---|---|
| F01 | T20 | Forward fall when trying to sit down | G7 | PEQ-S | ADEL | ND | ND | COMPL |
| F02 | T21 | Backward fall when trying to sit down | G7 | PEQ-S | ATR | ND | ND | COMPL |
| F03 | T22 | Lateral fall when trying to sit down | G7 | PEQ-S | LAT | ND | ND | COMPL |
| F04 | T23 | Forward fall when trying to get up | G7 | PEQ-L | ADEL | ND | ND | COMPL |
| F05 | T24 | Lateral fall when trying to get up | G7 | PEQ-L | LAT | ND | ND | COMPL |
| F06 | T25 | Forward fall while sitting, caused by fainting | G5 | SINC | ADEL | ND | ND | COMPL |
| F07 | T26 | Lateral fall while sitting, caused by fainting | G5 | SINC | LAT | ND | ND | COMPL |
| F08 | T27 | Backward fall while sitting, caused by fainting | G5 | SINC | ATR | ND | ND | COMPL |
| F09 | T28 | Vertical (forward) fall while walking caused by fainting | G1 | SINC | VERT | ND | ND | COMPL |
| F10 | T29 | Fall while walking, use of hands to dampen fall, caused by fainting | G1 | SINC | ND | MANOS | ND | COMPL |
| F11 | T30 | Forward fall while walking caused by a trip | G1 | TROP | ADEL | ND | ND | COMPL |
| F12 | T31 | Forward fall while jogging caused by a trip | G2 | TROP | ADEL | ND | ND | COMPL |
| F13 | T32 | Forward fall while walking caused by a slip | G1 | RESB | ADEL | ND | ND | COMPL |
| F14 | T33 | Lateral fall while walking caused by a slip | G1 | RESB | LAT | ND | ND | COMPL |
| F15 | T34 | Backward fall while walking caused by a slip | G1 | RESB | ATR | ND | ND | COMPL |

Nota: KFall no tiene un equivalente de "fall backward when trying to get up" (solo adelante y lateral). Es una asimetría real del dataset, no un vacío de mapeo — probablemente porque es más difícil de simular de forma segura.

### 4.3 FallAllD

Fuente: Saleh, Abbas & Le Jeannès (2021). 44 ADL + 35 caídas. Sensores en cuello, muñeca y cintura. Es el dataset con la convención de nombres más facetada de origen (actividad–causa–dirección–rotación–recuperación), lo cual esta v2 aprovecha en vez de descartar.

**ADL**

| ID | Descripción | Grupo |
|---|---|---|
| A001–A004 | Start/clapping/stop/one clap of hands | G12 |
| A005–A007 | Start/waving/stop hands | G12 |
| A008–A010 | Raising/moving hand up-down | G12 |
| A011 | Hand shaking | G12 |
| A012 | Beating a table with your hand | G12 |
| A013 | Sitting down | G7 |
| A014 | Standing up | G7 |
| A015 | Fail to stand up from a sofa/chair (after half standing) | **G11** (cuasi-caída, no llega al suelo) |
| A016 | Lying down on a bed | G8 |
| A017 | Changing position (turning) in the bed | G8 |
| A018 | Rising up from a bed | G8 |
| A019–A022 | Start/walking/stop/quick walking | G1 |
| A023 | Stumbling while walking without falling | **G11** |
| A024–A025 | Jogging slowly/quickly | G2 |
| A026–A027 | Jumping slightly/strongly | G10 |
| A028 | Bending down (pick up object) and raising up | G9 |
| A029–A036 | Start/up/stop/down stairs, normal y rápido | G3 |
| A037–A040 | Start/stop ascending/descending using a lift | G13 |
| A041–A042 | Standing/sitting in a moving bus/metro | G13 |
| A043–A044 | Start/stop jogging | G2 |

**Caídas**

| ID | Descripción oficial | E1 | E2 | E3 | E4 | E5 | E6 |
|---|---|---|---|---|---|---|---|
| A101 | Walking–stumbling/tripping–forward–no rotation–no recovery | G1 | TROP | ADEL | ND | NO | COMPL |
| A102 | ídem, with recovery | G1 | TROP | ADEL | ND | NO | RECUP |
| A103 | Walking–slipping–forward–no rotation–no recovery | G1 | RESB | ADEL | ND | NO | COMPL |
| A104 | ídem, with recovery | G1 | RESB | ADEL | ND | NO | RECUP |
| A105 | Walking–slipping–forward–with rotation–no recovery | G1 | RESB | ADEL | ND | SI | COMPL |
| A106 | ídem, with recovery | G1 | RESB | ADEL | ND | SI | RECUP |
| A107 | Walking–slipping–backward–no rotation–no recovery | G1 | RESB | ATR | ND | NO | COMPL |
| A108 | ídem, with recovery | G1 | RESB | ATR | ND | NO | RECUP |
| A109 | Walking–slipping–backward–with rotation–no recovery | G1 | RESB | ATR | ND | SI | COMPL |
| A110 | ídem, with recovery | G1 | RESB | ATR | ND | SI | RECUP |
| A111 | Walking–fainting/syncope–backward–no rotation–no recovery | G1 | SINC | ATR | ND | NO | COMPL |
| A112 | *(idéntica a A111 en la fuente — ver §7.1)* | G1 | SINC | ATR | ND | NO | COMPL |
| A113 | Walking–fainting/syncope–lateral–no rotation–no recovery | G1 | SINC | LAT | ND | NO | COMPL |
| A114 | Walking–fainting/syncope–forward–no rotation–no recovery (hands on table) | G1 | SINC | ADEL | MESA | NO | COMPL |
| A115 | Attempting to sit/lie down–losing balance–forward–no rotation–no recovery | G7* | PEQ-S | ADEL | ND | NO | COMPL |
| A116 | ídem, with recovery | G7* | PEQ-S | ADEL | ND | NO | RECUP |
| A117 | ídem, backward, no recovery | G7* | PEQ-S | ATR | ND | NO | COMPL |
| A118 | ídem, backward, with recovery | G7* | PEQ-S | ATR | ND | NO | RECUP |
| A119 | ídem, lateral, no recovery | G7* | PEQ-S | LAT | ND | NO | COMPL |
| A120 | ídem, lateral, with recovery | G7* | PEQ-S | LAT | ND | NO | RECUP |
| A121 | Jogging–stumbling/tripping–forward–no rotation–no recovery | G2 | TROP | ADEL | ND | NO | COMPL |
| A122 | ídem, with recovery | G2 | TROP | ADEL | ND | NO | RECUP |
| A123 | Jogging–**slipping**–forward–no rotation–no recovery | G2 | **RESB** | ADEL | ND | NO | COMPL |
| A124 | ídem, with recovery | G2 | **RESB** | ADEL | ND | NO | RECUP |
| A125 | ídem, with rotation, no recovery | G2 | **RESB** | ADEL | ND | SI | COMPL |
| A126 | ídem, with rotation, with recovery | G2 | **RESB** | ADEL | ND | SI | RECUP |
| A127 | Lying in bed–changing position/rotating–lateral–no rotation–no recovery | G6 | REPOS | LAT | ND | NO | COMPL |
| A128 | ídem, with recovery | G6 | REPOS | LAT | ND | NO | RECUP |
| A129 | Sitting on a chair–fainting/syncope–forward–no rotation–no recovery | G5 | SINC | ADEL | ND | NO | COMPL |
| A130 | ídem, backward | G5 | SINC | ATR | ND | NO | COMPL |
| A131 | ídem, lateral | G5 | SINC | LAT | ND | NO | COMPL |
| A132 | Standing for a while–fainting/syncope–forward–no rotation–no recovery | G4 | SINC | ADEL | ND | NO | COMPL |
| A133 | ídem, backward | G4 | SINC | ATR | ND | NO | COMPL |
| A134 | ídem, lateral | G4 | SINC | LAT | ND | NO | COMPL |
| A135 | ídem, vertical (sliding down a wall slowly) | G4 | SINC | VERT | DIRECTO | NO | COMPL |

**A123–A126 quedan marcados en negrita porque corrigen un error de la v1**: la tabla de cobertura original los agrupaba junto a A121/A122 bajo "Tropiezo al trotar" (U3), pese a que su propia descripción dice *"slipping"*, no *"stumbling/tripping"*. Aquí quedan bajo RESB (resbalón), consistente con G1/G2 tratando resbalón y tropiezo como valores del mismo eje en vez de categorías separadas por actividad previa.

`*` en A115–A120: FallAllD describe la actividad previa como "sit/lie down" de forma ambigua (no distingue explícitamente silla de cama). La mapeo a G7 asume que se trata de un intento de sentarse (consistente con el equivalente de SisFall/KFall), no de acostarse. Es una decisión de diseño documentada, no un dato verificado — ver §7.3.

### 4.4 UP-Fall

Fuente: Martínez-Villaseñor et al. (2019). 6 ADL + 5 caídas, 17 sujetos jóvenes. Multimodal (IMU, EEG, infrarrojo, cámaras).

**ADL**

| ID | Descripción | Grupo |
|---|---|---|
| 6 | Walking | G1 |
| 7 | Standing | G4 |
| 8 | Sitting | G5 |
| 9 | Picking up an object | G9 |
| 10 | Jumping | G10 |
| 11 | Laying | G6 |

**Caídas**

| ID | Descripción oficial | E1 | E2 | E3 | E4 | E5 | E6 |
|---|---|---|---|---|---|---|---|
| 1 | Falling forward using hands | ND | ND | ADEL | MANOS | ND | COMPL |
| 2 | Falling forward using knees | ND | ND | ADEL | RODIL | ND | COMPL |
| 3 | Falling backwards | ND | ND | ATR | ND | ND | COMPL |
| 4 | Falling sideward | ND | ND | LAT | ND | ND | COMPL |
| 5 | Falling sitting in empty chair | G7* | PEQ-S* | ND | SILLA | ND | COMPL |

UP-Fall no documenta actividad previa ni causa para los códigos 1–4 en la fuente revisada (a diferencia de SisFall/KFall/FallAllD); quedan en ND en vez de asumir "de pie" por comparación con otros datasets. El código 5 se interpreta por analogía con el patrón de otros datasets, marcado con `*` — ver §7.4.

### 4.5 UMAFall

Fuente: Casilari, Santoyo-Ramón & Cano-García (2017). 12 ADL + 3 caídas, hasta 19 sujetos. 5 puntos de sensor corporal.

**ADL**

| ID | Descripción | Grupo |
|---|---|---|
| Walking | Walking | G1 |
| Jogging | Jogging | G2 |
| Hopping | Hopping on one leg | G10 |
| Bending | Bending down and raising up | G9 |
| GoUpstairs | Climbing stairs (up) | G3 |
| GoDownstairs | Climbing stairs (down) | G3 |
| Sitting_GettingUpOnAChair | Sitting down on and getting up from a chair | G7 |
| LyingDown_OnABed | Lying down and getting up from a bed | G8 |
| MakingACall | Making a phone call | G12 |
| OpeningDoor | Opening a door | G12 |
| HandsUp | Raising hands up | G12 |
| Aplausing | Applauding | G12 |

**Caídas**

| ID | Descripción oficial | E1 | E2 | E3 | E4 | E5 | E6 |
|---|---|---|---|---|---|---|---|
| forwardFall | Forward fall | ND | ND | ADEL | ND | ND | COMPL |
| backwardFall | Backward fall | ND | ND | ATR | ND | ND | COMPL |
| lateralFall | Lateral fall | ND | ND | LAT | ND | ND | COMPL |

---

## 5. Cobertura cruzada

### 5.1 Caídas, por mecanismo causal (Eje 2)

| Mecanismo | SisFall | KFall | FallAllD | UP-Fall | UMAFall |
|---|---|---|---|---|---|
| RESB (resbalón) | ✓ caminando | ✓ caminando | ✓ caminando, trotando | — | — |
| TROP (tropiezo) | ✓ caminando | ✓ caminando, trotando | ✓ caminando, trotando | — | — |
| SINC (síncope) | ✓ caminando, sentado | ✓ caminando, sentado | ✓ caminando, de pie, sentado | — | — |
| PEQ-S (al sentarse) | ✓ | ✓ | ✓ | ✓ (asumido) | — |
| PEQ-L (al levantarse) | ✓ | ✓ | — (solo como cuasi-caída, G11) | — | — |
| REPOS (reacomodo en cama) | — | — | ✓ | — | — |
| GOLPE (golpe/choque) | — | — | — | — | — |
| Solo dirección (causa ND) | — | — | — | ✓ 3 de 5 códigos | ✓ los 3 códigos |

GOLPE queda en la tabla sin cobertura a propósito: Robinovitch et al. (2013) lo identifican como el tercer mecanismo más frecuente en caídas reales (11%), y ningún dataset del proyecto lo simula. Es una limitación real de los 5 datasets, no un vacío de esta taxonomía — se incluye el eje para no tener que rediseñar la tabla si en el futuro se incorpora un dataset que sí lo cubra.

PEQ-L merece atención: solo SisFall y KFall tienen una caída *completa* (llega al suelo) al fallar un intento de levantarse. FallAllD tiene el evento análogo, pero clasificado como cuasi-caída (A015, no llega al suelo) — así que si el objetivo es evaluar un modelo específicamente en "caída completa al intentar levantarse", FallAllD no aporta ejemplos positivos para esa clase, solo negativos difíciles.

### 5.2 ADL, por grupo

| Grupo | SisFall | KFall | FallAllD | UP-Fall | UMAFall |
|---|---|---|---|---|---|
| G1 Marcha | ✓ | ✓ | ✓ | ✓ | ✓ |
| G2 Trote | ✓ | ✓ | ✓ | — | ✓ |
| G3 Escaleras | ✓ | ✓ | ✓ | — | ✓ |
| G4 De pie estático | — | ✓ | — | ✓ | — |
| G5 Sentado estático | — | ✓ | — | ✓ | — |
| G6 Decúbito estático | — | ✓ | — | ✓ | — |
| G7 Transición sentado/pie | ✓ | ✓ | ✓ | — | ✓ |
| G8 Transición cama | ✓ | ✓ | ✓ | — | ✓ |
| G9 Flexión/recogida | ✓ | ✓ | ✓ | ✓ | ✓ |
| G10 Salto | ✓ | ✓ | ✓ | ✓ | ✓ |
| **G11 Cuasi-caída** | ✓ | ✓ | ✓ | **—** | **—** |
| G12 Gestos/instrumentales | — | — | ✓ | — | ✓ |
| G13 Transporte | ✓ | — | ✓ | — | — |

La fila G11 es la más relevante operativamente: **UP-Fall y UMAFall no incluyen ningún ejemplo de cuasi-caída** (tropiezo sin caer, colapso recuperado). Un modelo evaluado únicamente contra esos dos datasets no está siendo puesto a prueba contra el tipo de evento que más comúnmente se confunde con una caída real; sus métricas de especificidad en ese escenario van a estar infladas respecto a lo que mostraría frente a SisFall, KFall o FallAllD.

---

## 6. Casos límite y decisiones de diseño

Cada decisión no trivial queda documentada aquí, en vez de resuelta en silencio dentro de una tabla.

**6.1 — Frontera ADL/Caída para "terminar sentado en lugar de en el suelo".** Ver §1.1. No se resuelve unificando: se documenta la inconsistencia (SisFall/KFall la tratan como ADL, UP-Fall y UniMiB SHAR —externo— la tratan como caída) y se preserva la clasificación original de cada dataset. Forzar una única convención aquí sería repetir el error que se le critica a la v1.

**6.2 — Corrección A123–A126 de FallAllD.** Documentado en §4.3. Es un error de mapeo verificable contra la propia fuente, no una diferencia de criterio.

**6.3 — Vacío de PEQ-L (caída completa) en FallAllD.** Documentado en §5.1. Es un vacío real del dataset (solo tiene la versión "cuasi-caída" de este evento), no un descuido de mapeo.

**6.4 — D05 de KFall ("sit to the ground").** Se incluyó dentro de G7 (transición sentado↔de pie) ampliando la definición del grupo a cualquier superficie de apoyo (silla, sofá o suelo), en vez de crear un grupo nuevo solo para esta variante. Alternativa descartada: tratarlo como caso aparte — se prefirió no fragmentar la taxonomía por un único código.

---

## 7. Puntos no verificados (léase antes de usar el archivo para etiquetar datos)

**7.1 — A111 y A112 de FallAllD** aparecen con texto idéntico en la documentación revisada (*"Walking – fainting/syncope – backward – no rotation – no recovery"*, ambos). No pude confirmar contra el archivo de metadatos crudo de FallAllD (bloqueado por verificación anti-bot durante esta investigación) si es un duplicado real en el dataset o un error de transcripción en algún punto de la cadena de documentación. **Recomendación: verificar contra `FallAllD_Files_to_Python_Struct` o el `.mat` original antes de usar A112 en un pipeline de evaluación.**

**7.2 — UP-Fall, actividad 5 ("falling sitting in empty chair").** No pude acceder al texto completo del protocolo experimental (mismo bloqueo anti-bot) para confirmar si describe una pérdida de equilibrio al intentar sentarse (mi interpretación, análoga a SisFall/KFall) o un protocolo distinto. La fila en §4.4 refleja una inferencia razonable, no un dato confirmado.

**7.3 — A115–A120 de FallAllD ("sit/lie down").** La descripción oficial no distingue explícitamente entre intento de sentarse (silla) e intento de acostarse (cama). Se optó por la primera lectura por consistencia con SisFall/KFall — ver §6.

**7.4 — UP-Fall, actividad previa de los códigos 1–4.** No documentada en la fuente revisada; se dejó en ND en vez de asumir "de pie" por comparación con otros datasets (ver §4.4).

---

## 8. Referencias

Bagalà, F., Becker, C., Cappello, A., Chiari, L., Aminian, K., Hausdorff, J. M., Zijlstra, W., & Klenk, J. (2012). Evaluation of accelerometer-based fall detection algorithms on real-world falls. *PLOS ONE, 7*(5), e37062. https://doi.org/10.1371/journal.pone.0037062

Casilari, E., Santoyo-Ramón, J. A., & Cano-García, J. M. (2017). UMAFall: A multisensor dataset for the research on automatic fall detection. *Procedia Computer Science, 110*, 32–39. https://doi.org/10.1016/j.procs.2017.06.110

CDC (Centers for Disease Control and Prevention). (2017). *Risk factors for falls* [Fact sheet]. National Center for Injury Prevention and Control. https://www.cdc.gov/steadi/media/pdfs/STEADI-FactSheet-RiskFactors-508.pdf

Komisar, V., van Schooten, K. S., Aguiar, O. M. G., Shishov, N., & Robinovitch, S. N. (2022). Circumstances of falls during sit-to-stand transfers in older people: A cohort study of video-captured falls in long-term care. *Archives of Physical Medicine and Rehabilitation* (ScienceDirect). https://www.sciencedirect.com/science/article/abs/pii/S0003999322017117

Lara, O. D., & Labrador, M. A. (2013). A survey on human activity recognition using wearable sensors. *IEEE Communications Surveys & Tutorials, 15*(3), 1192–1209. https://doi.org/10.1109/SURV.2012.110112.00192

Martínez-Villaseñor, L., Ponce, H., Brieva, J., Moya-Albor, E., Núñez-Martínez, J., & Peñafort-Asturiano, C. (2019). UP-Fall detection dataset: A multimodal approach. *Sensors, 19*(9), 1988. https://doi.org/10.3390/s19091988

Micucci, D., Mobilio, M., & Napoletano, P. (2017). UniMiB SHAR: A dataset for human activity recognition using acceleration data from smartphones. *Applied Sciences, 7*(10), 1101. https://doi.org/10.3390/app7101101

Noury, N., Fleury, A., Rumeau, P., Bourke, A. K., Ó Laighin, G., Rialle, V., & Lundy, J. E. (2007). Fall detection — Principles and methods. *29th Annual International Conference of the IEEE Engineering in Medicine and Biology Society*, 1663–1666.

Noury, N., Rumeau, P., Bourke, A. K., Ó Laighin, G., & Lundy, J. E. (2008). A proposal for the classification and evaluation of fall detectors. *IRBM, 29*(6), 340–349. https://doi.org/10.1016/j.irbm.2008.08.002

Robinovitch, S. N., Feldman, F., Yang, Y., Schonnop, R., Leung, P. M., Sarraf, T., Sims-Gould, J., & Loughin, M. (2013). Video capture of the circumstances of falls in elderly people residing in long-term care: An observational study. *The Lancet, 381*(9860), 47–54. https://doi.org/10.1016/S0140-6736(12)61263-X

Saleh, M., Abbas, M., & Le Jeannès, R. B. (2021). FallAllD: An open dataset of human falls and activities of daily living for classical and deep learning applications. *IEEE Sensors Journal, 21*(2), 1849–1858. https://doi.org/10.1109/JSEN.2020.3018335

Schonnop, R., Yang, Y., Feldman, F., Robinson, E., Loughin, M., & Robinovitch, S. N. (2013). Prevalence of and factors associated with head impact during falls in older adults in long-term care. *CMAJ, 185*(17), E803–E810. https://doi.org/10.1503/cmaj.130498

Sucerquia, A., López, J. D., & Vargas-Bonilla, J. F. (2017). SisFall: A fall and movement dataset. *Sensors, 17*(1), 198. https://doi.org/10.3390/s17010198

Tinetti, M. E., Williams, T. F., & Mayewski, R. (1988). Fall risk index for elderly patients based on number of chronic disabilities. *The American Journal of Medicine, 80*(3), 429–434.

Yang, Y., Schonnop, R., Feldman, F., & Robinovitch, S. N. (2013). Development and validation of a questionnaire for analyzing real-life falls in long-term care captured on video. *BMC Geriatrics, 13*, 40. https://doi.org/10.1186/1471-2318-13-40

Yu, X., Jang, J., & Xiong, S. (2021). A large-scale open motion dataset (KFall) and benchmark algorithms for detecting pre-impact fall of the elderly using wearable inertial sensors. *Frontiers in Aging Neuroscience, 13*, 692865. https://doi.org/10.3389/fnagi.2021.692865

Kellogg International Work Group on the Prevention of Falls by the Elderly. (1987). The prevention of falls in later life. *Danish Medical Bulletin, 34*(Suppl 4), 1–24.
