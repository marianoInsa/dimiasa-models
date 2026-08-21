# Taxonomía Unificada de Tipos de Caídas

## Objetivo

Los datasets utilizados en este trabajo describen distintos tipos de caídas, pero no comparten una taxonomía común. Mientras algunos diferencian la **causa** de la caída (resbalón, tropiezo o síncope), otros únicamente registran la **dirección** de la caída o el **mecanismo de impacto**.

Con el objetivo de facilitar la comparación entre datasets y permitir una evaluación consistente de los modelos, se definió la siguiente **taxonomía unificada**, basada en el mecanismo biomecánico que origina la caída. Esta clasificación preserva las etiquetas originales de cada dataset y evita introducir equivalencias que no estén respaldadas por los datos.

## Descripciones Oficiales por Dataset

### SisFall

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

| ID  | Descripción                                                              |
| --- | ------------------------------------------------------------------------ |
| T20 | Forward fall when trying to sit down                                     |
| T21 | Backward fall when trying to sit down                                    |
| T22 | Lateral fall when trying to sit down                                     |
| T23 | Forward fall when trying to get up                                       |
| T24 | Lateral fall when trying to get up                                       |
| T25 | Forward fall while sitting, caused by fainting                           |
| T26 | Lateral fall while sitting, caused by fainting                           |
| T27 | Backward fall while sitting, caused by fainting                          |
| T28 | Vertical (forward) fall while walking caused by fainting                 |
| T29 | Fall while walking, with use of hands to dampen fall, caused by fainting |
| T30 | Forward fall while walking caused by a trip                              |
| T31 | Forward fall while jogging caused by a trip                              |
| T32 | Forward fall while walking caused by a slip                              |
| T33 | Lateral fall while walking caused by a slip                              |
| T34 | Backward fall while walking caused by a slip                             |

### FallAllD

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

| ID  | Descripción                    |
| --- | ------------------------------ |
| 1   | Falling forward using hands    |
| 2   | Falling forward using knees    |
| 3   | Falling backwards              |
| 4   | Falling sideward               |
| 5   | Falling sitting in empty chair |

### UMAFall

| ID | Descripción        |
| --------------- | ------------------ |
| backwardFall    | Caída hacia atrás  |
| forwardFall     | Caída hacia adelante |
| lateralFall     | Caída lateral      |

## Taxonomía Unificada

|   ID    | Grupo                                            | Descripción                                                                       |
| :-----: | ------------------------------------------------ | --------------------------------------------------------------------------------- |
| **U1**  | **Resbalón al caminar**                          | Caídas producidas por pérdida de fricción durante la marcha.                      |
| **U2**  | **Tropiezo al caminar**                          | Caídas ocasionadas por un obstáculo durante la marcha.                            |
| **U3**  | **Tropiezo al trotar**                           | Tropiezo ocurrido durante jogging o carrera ligera.                               |
| **U4**  | **Síncope caminando o de pie**                   | Caídas provocadas por pérdida de conciencia desde una postura erguida.            |
| **U5**  | **Caída al intentar sentarse**                   | Pérdida del equilibrio durante la transición de pie a sentado.                    |
| **U6**  | **Caída al intentar levantarse**                 | Caídas durante la transición de sentado a de pie.                                 |
| **U7**  | **Síncope estando sentado**                      | Caídas por pérdida de conciencia desde una posición sentada.                      |
| **U8**  | **Caída desde la cama**                          | Caídas producidas durante movimientos o cambios de posición sobre la cama.        |
| **U9**  | **Caídas clasificadas únicamente por dirección** | El dataset únicamente informa la dirección de la caída, sin especificar su causa. |
| **U10** | **Caídas clasificadas por mecanismo de impacto** | El dataset diferencia únicamente la forma de impacto durante la caída.            |

## Cobertura por Dataset

### SisFall

| Grupo | Actividades   |
| ----- | ------------- |
| U1    | F01, F02, F03 |
| U2    | F04           |
| U3    | F05           |
| U4    | F06, F07      |
| U5    | F10, F11, F12 |
| U6    | F08, F09      |
| U7    | F13, F14, F15 |

### KFall

| Grupo | Actividades                  |
| ----- | ---------------------------- |
| U1    | T32, T33, T34                |
| U2    | T30                          |
| U3    | T31                          |
| U4    | T28, T29                     |
| U5    | T20, T21, T22                |
| U6    | T23, T24                     |
| U7    | T25, T26, T27                |

### FallAllD

| Grupo | Actividades                                                                                       |
| ----- | ------------------------------------------------------------------------------------------------- |
| U1    | A103, A104, A105, A106, A107, A108, A109, A110                                                   |
| U2    | A101, A102                                                                                       |
| U3    | A121, A122, A123, A124, A125, A126                                                               |
| U4    | A111, A112, A113, A114, A132, A133, A134, A135                                                   |
| U5    | A115, A116, A117, A118, A119, A120                                                               |
| U7    | A129, A130, A131                                                                                 |
| U8    | A127, A128                                                                                       |

### UPFall

| Grupo | Actividades |
| ----- | ----------- |
| U5    | 5           |
| U9    | 3, 4        |
| U10   | 1, 2        |

### UMAFall

| Grupo | Actividades                              |
| ----- | ---------------------------------------- |
| U9    | backwardFall, forwardFall, lateralFall   |

## Consideraciones

- La taxonomía se basa en el **mecanismo biomecánico de la caída** y no únicamente en la descripción textual utilizada por cada dataset.
- Se preservan las etiquetas originales para mantener la trazabilidad entre la taxonomía unificada y los datos de origen.
- Cuando un dataset proporciona menor nivel de detalle (por ejemplo, UP-Fall y UMAFall), sus etiquetas no se reinterpretan ni se asignan artificialmente a categorías más específicas.
- Esta clasificación constituye una representación común que permite comparar datasets heterogéneos y analizar posteriormente el impacto que tiene cada uno sobre el rendimiento del modelo de detección de caídas.
