# Taxonomía Unificada de ADL y Caídas

## Objetivo

Los datasets utilizados en este trabajo describen distintos tipos de caídas y actividades de la vida diaria (ADL), pero no comparten una taxonomía común. Mientras algunos diferencian la **causa** de la caída (resbalón, tropiezo o síncope), otros únicamente registran la **dirección** de la caída o el **mecanismo de impacto**.

Con el objetivo de facilitar la comparación entre datasets y permitir una evaluación consistente de los modelos CNN-LSTM, se definió la siguiente **taxonomía unificada**, basada en el mecanismo biomecánico que origina la caída (grupos F1–F10) y en el tipo de movimiento para las ADL (grupos A1–A13). Esta clasificación preserva las etiquetas originales de cada dataset y evita introducir equivalencias que no estén respaldadas por los datos.

La **dirección** de cada caída se registra como dato informativo por dataset (ADEL/ATR/LAT/VERT/ND), no como eje de agrupación: subdividir los grupos por dirección deja celdas con muy pocas muestras para comparar métricas de forma significativa.

Esta revisión incorpora los hallazgos de la investigación documentada en `taxonomia_unificada_adl_caidas_v2.md`.

## Descripciones Oficiales por Dataset

### SisFall

#### Actividades de la vida diaria (ADL):

| ID  | Descripción                                                                             |
| --- | --------------------------------------------------------------------------------------- |
| D01 | Walking slowly                                                                          |
| D02 | Walking quickly                                                                         |
| D03 | Jogging slowly                                                                          |
| D04 | Jogging quickly                                                                         |
| D05 | Walking upstairs and downstairs slowly                                                  |
| D06 | Walking upstairs and downstairs quickly                                                 |
| D07 | Slowly sit in a half height chair, wait a moment, and up slowly                         |
| D08 | Quickly sit in a half height chair, wait a moment, and up quickly                       |
| D09 | Slowly sit in a low height chair, wait a moment, and up slowly                          |
| D10 | Quickly sit in a low height chair, wait a moment, and up quickly                        |
| D11 | Sitting a moment, trying to get up, and collapse into a chair                           |
| D12 | Sitting a moment, lying slowly, wait a moment, and sit again                            |
| D13 | Sitting a moment, lying quickly, wait a moment, and sit again                           |
| D14 | Being on one's back change to lateral position, wait a moment, and change to one's back |
| D15 | Standing, slowly bending at knees, and getting up                                       |
| D16 | Standing, slowly bending without bending knees, and getting up                          |
| D17 | Standing, get into a car, remain seated and get out of the car                          |
| D18 | Stumble while walking                                                                   |
| D19 | Gently jump without falling (trying to reach a high object)                             |

#### Caídas:

| ID  | Descripción                                                                         |
| --- | ----------------------------------------------------------------------------------- |
| F01 | Fall forward while walking caused by a slip                                         |
| F02 | Fall backward while walking caused by a slip                                        |
| F03 | Lateral fall while walking caused by a slip                                         |
| F04 | Fall forward while walking caused by a trip                                         |
| F05 | Fall forward while jogging caused by a trip                                         |
| F06 | Vertical fall while walking caused by fainting                                      |
| F07 | Fall while walking, with use of hands in a table to dampen fall, caused by fainting |
| F08 | Fall forward when trying to get up                                                  |
| F09 | Lateral fall when trying to get up                                                  |
| F10 | Fall forward when trying to sit down                                                |
| F11 | Fall backward when trying to sit down                                               |
| F12 | Lateral fall when trying to sit down                                                |
| F13 | Fall forward while sitting, caused by fainting or falling asleep                    |
| F14 | Fall backward while sitting, caused by fainting or falling asleep                   |
| F15 | Lateral fall while sitting, caused by fainting or falling asleep                    |

### KFall

#### Actividades de la vida diaria (ADL):

| ID  | Descripción                                                                             |
| --- | --------------------------------------------------------------------------------------- |
| D01 | Stand for 30 s                                                                          |
| D02 | Stand, slowly bend the back with or without bending at knees, tie shoe lace, and get up |
| D03 | Pick up an object from the floor                                                        |
| D04 | Gently jump (try to reach an object)                                                    |
| D05 | Stand, sit to the ground, wait a moment, and get up with normal speed                   |
| D06 | Walk normally with turn (4 m)                                                           |
| D07 | Walk quickly with turn (4 m)                                                            |
| D08 | Jog normally with turn (4 m)                                                            |
| D09 | Jog quickly with turn (4 m)                                                             |
| D10 | Stumble while walking                                                                   |
| D11 | Sit on a chair for 30 s                                                                 |
| D12 | Sit on the sofa (back is inclined to the support) for 30 s                              |
| D13 | Sit down to a chair normally, and get up from a chair normally                          |
| D14 | Sit down to a chair quickly, and get up from a chair quickly                            |
| D15 | Sit a moment, trying to get up, and collapse into a chair                               |
| D16 | Stand, sit on the sofa (back is inclined to the support), and get up normally           |
| D17 | Lie on the bed for 30 s                                                                 |
| D18 | Sit a moment, lie down to the bed normally, and get up normally                         |
| D19 | Sit a moment, lie down to the bed quickly, and get up quickly                           |
| D20 | Walk upstairs and downstairs normally (five steps)                                      |
| D21 | Walk upstairs and downstairs quickly (five steps)                                       |

#### Caídas:

| ID  | Task crudo | Descripción                                                         |
| --- | ---------- | ------------------------------------------------------------------- |
| F01 | T20        | Forward fall when trying to sit down                                |
| F02 | T21        | Backward fall when trying to sit down                               |
| F03 | T22        | Lateral fall when trying to sit down                                |
| F04 | T23        | Forward fall when trying to get up                                  |
| F05 | T24        | Lateral fall when trying to get up                                  |
| F06 | T25        | Forward fall while sitting, caused by fainting                      |
| F07 | T26        | Lateral fall while sitting, caused by fainting                      |
| F08 | T27        | Backward fall while sitting, caused by fainting                     |
| F09 | T28        | Vertical (forward) fall while walking caused by fainting            |
| F10 | T29        | Fall while walking, use of hands to dampen fall, caused by fainting |
| F11 | T30        | Forward fall while walking caused by a trip                         |
| F12 | T31        | Forward fall while jogging caused by a trip                         |
| F13 | T32        | Forward fall while walking caused by a slip                         |
| F14 | T33        | Lateral fall while walking caused by a slip                         |
| F15 | T34        | Backward fall while walking caused by a slip                        |

### FallAllD

#### Actividades de la vida diaria (ADL):

| ID   | Descripción                                                             |
| ---- | ----------------------------------------------------------------------- |
| A001 | Start clapping hands                                                    |
| A002 | Clapping hands                                                          |
| A003 | Stop clapping hands                                                     |
| A004 | Clap hands one time                                                     |
| A005 | Start waving hands                                                      |
| A006 | Waving hands                                                            |
| A007 | Stop waving hands                                                       |
| A008 | Raising hand up                                                         |
| A009 | Moving hand down                                                        |
| A010 | Moving hand up then down immediately                                    |
| A011 | Hand shaking                                                            |
| A012 | Beating a table with your hand                                          |
| A013 | Sitting down                                                            |
| A014 | Standing up                                                             |
| A015 | Fail to stand up from a sofa/chair (after half standing)                |
| A016 | Lying down on a bed                                                     |
| A017 | Changing position (turning) in the bed                                  |
| A018 | Rising up from a bed                                                    |
| A019 | Start walking                                                           |
| A020 | Walking slowly or in moderate speed                                     |
| A021 | Stop walking                                                            |
| A022 | Walking quickly                                                         |
| A023 | Stumbling while walking without falling                                 |
| A024 | Jogging slowly                                                          |
| A025 | Jogging quickly                                                         |
| A026 | Jumping slightly                                                        |
| A027 | Jumping strongly                                                        |
| A028 | Bending down (e.g. to pick something up from floor) and then raising up |
| A029 | Start going upstairs                                                    |
| A030 | Going upstairs                                                          |
| A031 | Stop going upstairs                                                     |
| A032 | Start going downstairs                                                  |
| A033 | Going downstairs                                                        |
| A034 | Stop going downstairs                                                   |
| A035 | Going upstairs quickly                                                  |
| A036 | Going downstairs quickly                                                |
| A037 | Start ascending using a lift                                            |
| A038 | Stop ascending using a lift                                             |
| A039 | Start descending using a lift                                           |
| A040 | Stop descending using a lift                                            |
| A041 | Standing in a moving bus/metro                                          |
| A042 | Sitting in a moving bus/metro                                           |
| A043 | Start jogging                                                           |
| A044 | Stop jogging                                                            |

#### Caídas:

| ID   | Descripción                                                                                                 |
| ---- | ----------------------------------------------------------------------------------------------------------- |
| A101 | Walking – stumbling/tripping – forward – no rotation – no recovery                                          |
| A102 | Walking – stumbling/tripping – forward – no rotation – with recovery                                        |
| A103 | Walking – slipping – forward – no rotation – no recovery                                                    |
| A104 | Walking – slipping – forward – no rotation – with recovery                                                  |
| A105 | Walking – slipping – forward – with rotation – no recovery                                                  |
| A106 | Walking – slipping – forward – with rotation – with recovery                                                |
| A107 | Walking – slipping – backward – no rotation – no recovery                                                   |
| A108 | Walking – slipping – backward – no rotation – with recovery                                                 |
| A109 | Walking – slipping – backward – with rotation – no recovery                                                 |
| A110 | Walking – slipping – backward – with rotation – with recovery                                               |
| A111 | Walking – fainting/syncope – backward – no rotation – no recovery                                           |
| A112 | Walking – fainting/syncope – backward – no rotation – no recovery                                           |
| A113 | Walking – fainting/syncope – lateral – no rotation – no recovery                                            |
| A114 | Walking – fainting/syncope – forward – no rotation – no recovery (hands on table protection)                |
| A115 | Attempting to sit/lie down – losing balance – forward – no rotation – no recovery                           |
| A116 | Attempting to sit/lie down – losing balance – forward – no rotation – with recovery                         |
| A117 | Attempting to sit/lie down – losing balance – backward – no rotation – no recovery                          |
| A118 | Attempting to sit/lie down – losing balance – backward – no rotation – with recovery                        |
| A119 | Attempting to sit/lie down – losing balance – lateral – no rotation – no recovery                           |
| A120 | Attempting to sit/lie down – losing balance – lateral – no rotation – with recovery                         |
| A121 | Jogging – stumbling/tripping – forward – no rotation – no recovery                                          |
| A122 | Jogging – stumbling/tripping – forward – no rotation – with recovery                                        |
| A123 | Jogging – slipping – forward – no rotation – no recovery                                                    |
| A124 | Jogging – slipping – forward – no rotation – with recovery                                                  |
| A125 | Jogging – slipping – forward – with rotation – no recovery                                                  |
| A126 | Jogging – slipping – forward – with rotation – with recovery                                                |
| A127 | Lying in bed – changing position/rotating – lateral – no rotation – no recovery                             |
| A128 | Lying in bed – changing position/rotating – lateral – no rotation – with recovery                           |
| A129 | Sitting on a chair – fainting/syncope – forward – no rotation – no recovery                                 |
| A130 | Sitting on a chair – fainting/syncope – backward – no rotation – no recovery                                |
| A131 | Sitting on a chair – fainting/syncope – lateral – no rotation – no recovery                                 |
| A132 | Standing for a while – fainting/syncope – forward – no rotation – no recovery                               |
| A133 | Standing for a while – fainting/syncope – backward – no rotation – no recovery                              |
| A134 | Standing for a while – fainting/syncope – lateral – no rotation – no recovery                               |
| A135 | Standing for a while – fainting/syncope – vertical – no rotation – no recovery (sliding down a wall slowly) |

### UPFall

#### Actividades de la vida diaria (ADL):

| ID  | Descripción          |
| --- | -------------------- |
| 6   | Walking              |
| 7   | Standing             |
| 8   | Sitting              |
| 9   | Picking up an object |
| 10  | Jumping              |
| 11  | Laying               |

#### Caídas:

| ID  | Descripción                    |
| --- | ------------------------------ |
| 1   | Falling forward using hands    |
| 2   | Falling forward using knees    |
| 3   | Falling backwards              |
| 4   | Falling sideward               |
| 5   | Falling sitting in empty chair |

### UMAFall

#### Actividades de la vida diaria (ADL):

| ID                        | Descripción                                 |
| ------------------------- | ------------------------------------------- |
| Walking                   | Walking                                     |
| Jogging                   | Jogging                                     |
| Hopping                   | Hopping on one leg                          |
| Bending                   | Bending down and raising up                 |
| GoUpstairs                | Climbing stairs (up)                        |
| GoDownstairs              | Climbing stairs (down)                      |
| Sitting_GettingUpOnAChair | Sitting down on and getting up from a chair |
| LyingDown_OnABed          | Lying down and getting up from a bed        |
| MakingACall               | Making a phone call                         |
| OpeningDoor               | Opening a door                              |
| HandsUp                   | Raising hands up                            |
| Aplausing                 | Applauding                                  |

#### Caídas:

| ID           | Descripción   |
| ------------ | ------------- |
| forwardFall  | Forward fall  |
| backwardFall | Backward fall |
| lateralFall  | Lateral fall  |

## Taxonomía Unificada de Caídas

|  ID  | Grupo                                            | Descripción                                                                       |
| :--: | ------------------------------------------------ | --------------------------------------------------------------------------------- |
| **F1**  | **Resbalón al caminar**                          | Caídas producidas por pérdida de fricción durante la marcha.                      |
| **F2**  | **Tropiezo al caminar**                          | Caídas ocasionadas por un obstáculo durante la marcha.                            |
| **F3**  | **Tropiezo al trotar**                           | Tropiezo ocurrido durante jogging o carrera ligera.                               |
| **F4**  | **Síncope caminando o de pie**                   | Caídas provocadas por pérdida de conciencia desde una postura erguida.            |
| **F5**  | **Caída al intentar sentarse**                   | Pérdida del equilibrio durante la transición de pie a sentado.                    |
| **F6**  | **Caída al intentar levantarse**                 | Caídas durante la transición de sentado a de pie.                                 |
| **F7**  | **Síncope estando sentado**                      | Caídas por pérdida de conciencia desde una posición sentada.                      |
| **F8**  | **Caída desde la cama**                          | Caídas producidas durante movimientos o cambios de posición sobre la cama.        |
| **F9**  | **Caídas clasificadas únicamente por dirección** | El dataset únicamente informa la dirección de la caída, sin especificar su causa. |
| **F10** | **Caídas clasificadas por mecanismo de impacto** | El dataset diferencia únicamente la forma de impacto durante la caída.            |

## Taxonomía Unificada de ADL

| Grupo | Nombre | Descripción |
|---|---|---|
| **A1** | Marcha | Caminar a paso normal o rápido, en línea recta o con giro. |
| **A2** | Trote / carrera | Jogging o carrera ligera, a cualquier velocidad. |
| **A3** | Escaleras | Subir o bajar escaleras, a cualquier velocidad. |
| **A4** | Bipedestación estática | De pie, sin desplazamiento, durante un período sostenido. |
| **A5** | Sedestación estática | Sentado (silla o sofá) sin desplazamiento, durante un período sostenido. |
| **A6** | Decúbito estático | Acostado (cama) sin cambio de posición, durante un período sostenido. |
| **A7** | Transición sentado↔de pie | Sentarse o levantarse (silla, sofá, auto, o el suelo), en cualquier velocidad, incluida la transición normal. |
| **A8** | Transición decúbito↔sentado | Acostarse o levantarse de la cama, incluidos los cambios de posición mientras se está acostado. |
| **A9** | Flexión de tronco / recogida de objetos | Agacharse (con o sin flexionar rodillas) para recoger algo del piso, con o sin regreso a la posición inicial. |
| **A10** | Salto | Saltar o dar pequeños brincos sin que constituya una caída. |
| **A11** | Cuasi-caída / recuperación de equilibrio | Tropezar sin caer, o iniciar una caída y recuperar el equilibrio terminando en una posición sostenida (p. ej. colapsar de vuelta a una silla al intentar levantarse). Clase de "falso positivo difícil" para un detector de caídas. |
| **A12** | Gestos y actividades instrumentales | Aplaudir, saludar con la mano, levantar/mover brazos, simular una llamada, abrir una puerta. |
| **A13** | Contextos de transporte | De pie o sentado en transporte en movimiento (bus, metro), uso de ascensor, entrar/salir de un auto. |

**A11** es la clase que más le importa a un detector de caídas: es la más fácil de confundir con una caída real, y su cobertura es muy desigual entre datasets (ver Consideraciones).

## Cobertura por Dataset

Leyenda de dirección: **ADEL** adelante · **ATR** atrás · **LAT** lateral · **VERT** vertical · **ND** no documentado.

### SisFall

#### Caídas

| Grupo | Direcciones      | Actividades   |
| ----- | ---------------- | ------------- |
| F1    | ADEL, ATR, LAT   | F01, F02, F03 |
| F2    | ADEL             | F04           |
| F3    | ADEL             | F05           |
| F4    | VERT, ND         | F06, F07      |
| F5    | ADEL, ATR, LAT   | F10, F11, F12 |
| F6    | ADEL, LAT        | F08, F09      |
| F7    | ADEL, ATR, LAT   | F13, F14, F15 |

#### ADL

| Grupo | Actividades          |
| ----- | -------------------- |
| A1    | D01, D02             |
| A2    | D03, D04             |
| A3    | D05, D06             |
| A7    | D07, D08, D09, D10   |
| A11   | D11, D18             |
| A8    | D12, D13, D14        |
| A9    | D15, D16             |
| A13   | D17                  |
| A10   | D19                  |

### KFall

#### Caídas

| Grupo | Direcciones      | Actividades   |
| ----- | ---------------- | ------------- |
| F1    | ADEL, ATR, LAT   | F13, F14, F15 |
| F2    | ADEL             | F11           |
| F3    | ADEL             | F12           |
| F4    | VERT, ND         | F09, F10      |
| F5    | ADEL, ATR, LAT   | F01, F02, F03 |
| F6    | ADEL, LAT        | F04, F05      |
| F7    | ADEL, ATR, LAT   | F06, F07, F08 |

#### ADL

| Grupo | Actividades                     |
| ----- | ------------------------------- |
| A4    | D01                             |
| A9    | D02, D03                        |
| A10   | D04                             |
| A7    | D05, D13, D14, D16              |
| A1    | D06, D07                        |
| A2    | D08, D09                        |
| A11   | D10, D15                        |
| A5    | D11, D12                        |
| A6    | D17                             |
| A8    | D18, D19                        |
| A3    | D20, D21                        |

### FallAllD

#### Caídas

| Grupo | Direcciones               | Actividades                        |
| ----- | ------------------------- | ---------------------------------- |
| F1    | ADEL, ATR                 | A103–A110, A123–A126               |
| F2    | ADEL                      | A101, A102, A121, A122             |
| F4    | ADEL, ATR, LAT, VERT      | A111–A114, A132–A135               |
| F5    | ADEL, ATR, LAT            | A115–A120                          |
| F7    | ADEL, ATR, LAT            | A129–A131                          |
| F8    | LAT                       | A127, A128                         |

#### ADL

| Grupo | Actividades                  |
| ----- | ---------------------------- |
| A12   | A001–A012                    |
| A7    | A013, A014                   |
| A11   | A015, A023                   |
| A8    | A016–A018                    |
| A1    | A019–A022                    |
| A2    | A024, A025, A043, A044       |
| A10   | A026, A027                   |
| A9    | A028                         |
| A3    | A029–A036                    |
| A13   | A037–A042                    |

### UPFall

#### Caídas

| Grupo | Direcciones | Actividades |
| ----- | ----------- | ----------- |
| F5    | ND          | 5           |
| F9    | ATR, LAT    | 3, 4        |
| F10   | ADEL        | 1, 2        |

#### ADL

| Grupo | Actividades |
| ----- | ----------- |
| A1    | 6           |
| A4    | 7           |
| A5    | 8           |
| A9    | 9           |
| A10   | 10          |
| A6    | 11          |

### UMAFall

#### Caídas

| Grupo | Direcciones   | Actividades                        |
| ----- | ------------- | ---------------------------------- |
| F9    | ADEL, ATR, LAT | forwardFall, backwardFall, lateralFall |

#### ADL

| Grupo | Actividades                                  |
| ----- | -------------------------------------------- |
| A1    | Walking                                      |
| A2    | Jogging                                      |
| A10   | Hopping                                      |
| A9    | Bending                                      |
| A3    | GoUpstairs, GoDownstairs                     |
| A7    | Sitting_GettingUpOnAChair                    |
| A8    | LyingDown_OnABed                             |
| A12   | MakingACall, OpeningDoor, HandsUp, Aplausing |

## Consideraciones

- La taxonomía se basa en el **mecanismo biomecánico de la caída** (F1–F10) y en el **tipo de movimiento** para las ADL (A1–A13), y no únicamente en la descripción textual utilizada por cada dataset.
- Se preservan las etiquetas originales para mantener la trazabilidad entre la taxonomía unificada y los datos de origen.
- Cuando un dataset proporciona menor nivel de detalle (por ejemplo, UP-Fall y UMAFall), sus etiquetas no se reinterpretan ni se asignan artificialmente a categorías más específicas; quedan en F9 (solo dirección) o F10 (solo mecanismo de impacto).
- La **dirección** de la caída se registra como columna informativa en todas las tablas de cobertura, no como eje de agrupación: subdividir por dirección (adelante/atrás/lateral) dejaría celdas con 1–3 muestras en SisFall y KFall, insuficientes para comparar métricas por categoría.
- **Frontera ADL/caída "terminar sentado en lugar de en el suelo":** no es consistente entre datasets ni en la literatura (Kellogg, 1987). SisFall (D11) y KFall (D15) lo registran como ADL; UP-Fall (caída 5) como caída. Se preserva la clasificación original de cada dataset: D11/D15/A015/D18/A023 quedan en **A11** (cuasi-caída), y la caída 5 de UP-Fall queda en **F5** sin reinterpretar.
- **A123–A126 de FallAllD** quedan en **F1** (resbalón), corrigiendo la versión anterior que los agrupaba como tropiezo: su propia descripción oficial dice *"slipping"*, no *"stumbling/tripping"*.
- **Cobertura desigual de A11 (cuasi-caída):** UP-Fall y UMAFall no incluyen ningún ejemplo de cuasi-caída (tropiezo sin caer, colapso recuperado). Un modelo evaluado únicamente contra esos dos datasets no es puesto a prueba contra el tipo de evento que más comúnmente se confunde con una caída real; su especificidad en ese escenario estará inflada respecto a la que mostraría frente a SisFall, KFall o FallAllD.
- Esta clasificación constituye una representación común que permite agrupar las actividades de los distintos datasets y analizar el impacto que tiene cada categoría sobre el rendimiento del modelo de detección de caídas.

## Referencias

Kellogg International Work Group on the Prevention of Falls by the Elderly. (1987). The prevention of falls in later life. *Danish Medical Bulletin, 34*(Suppl 4), 1–24.

Noury, N., Rumeau, P., Bourke, A. K., Ó Laighin, G., & Lundy, J. E. (2008). A proposal for the classification and evaluation of fall detectors. *IRBM, 29*(6), 340–349. https://doi.org/10.1016/j.irbm.2008.08.002

Robinovitch, S. N., Feldman, F., Yang, Y., Schonnop, R., Leung, P. M., Sarraf, T., Sims-Gould, J., & Loughin, M. (2013). Video capture of the circumstances of falls in elderly people residing in long-term care: An observational study. *The Lancet, 381*(9860), 47–54. https://doi.org/10.1016/S0140-6736(12)61263-X

Komisar, V., van Schooten, K. S., Aguiar, O. M. G., Shishov, N., & Robinovitch, S. N. (2022). Circumstances of falls during sit-to-stand transfers in older people: A cohort study of video-captured falls in long-term care. *Archives of Physical Medicine and Rehabilitation* (ScienceDirect). https://www.sciencedirect.com/science/article/abs/pii/S0003999322017117

Saleh, M., Abbas, M., & Le Jeannès, R. B. (2021). FallAllD: An open dataset of human falls and activities of daily living for classical and deep learning applications. *IEEE Sensors Journal, 21*(2), 1849–1858. https://doi.org/10.1109/JSEN.2020.3018335