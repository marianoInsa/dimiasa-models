# Taxonomía Unificada de Tipos de Caídas

## Objetivo

Los datasets utilizados en este trabajo describen distintos tipos de caídas, pero no comparten una taxonomía común. Mientras algunos diferencian la **causa** de la caída (resbalón, tropiezo o síncope), otros únicamente registran la **dirección** de la caída o el **mecanismo de impacto**.

Con el objetivo de facilitar la comparación entre datasets y permitir una evaluación consistente de los modelos, se definió la siguiente **taxonomía unificada**, basada en el mecanismo biomecánico que origina la caída. Esta clasificación preserva las etiquetas originales de cada dataset y evita introducir equivalencias que no estén respaldadas por los datos.

## Taxonomía Unificada

| ID | Grupo | Descripción | Etiquetas originales |
|:--:|--------|-------------|----------------------|
| **U1** | **Resbalón al caminar** | Caídas producidas por pérdida de fricción durante la marcha. | **SisFall:** F01, F02, F03.<br>**FallAllD:** Walking slip forward/backward (± recovery, ± rotation).<br>**KFall:** F13, F14, F15. |
| **U2** | **Tropiezo al caminar** | Caídas ocasionadas por un obstáculo durante la marcha. | **SisFall:** F04.<br>**FallAllD:** Walking trip forward (± recovery).<br>**KFall:** F11. |
| **U3** | **Tropiezo al trotar** | Tropiezo ocurrido durante jogging o carrera ligera. | **SisFall:** F05.<br>**FallAllD:** Jogging trip forward (± recovery).<br>**KFall:** F12. |
| **U4** | **Síncope caminando o de pie** | Caídas provocadas por pérdida de conciencia desde una postura erguida. | **SisFall:** F06, F07.<br>**FallAllD:** Walking fainting (forward, backward, lateral, vertical).<br>**KFall:** F09, F10. |
| **U5** | **Caída al intentar sentarse** | Pérdida del equilibrio durante la transición de pie a sentado. | **SisFall:** F10, F11, F12.<br>**FallAllD:** Trying to sit (forward, backward, lateral; ± recovery).<br>**KFall:** F01, F02, F03.<br>**UP-Fall:** Empty-chair fall. |
| **U6** | **Caída al intentar levantarse** | Caídas durante la transición de sentado a de pie. | **SisFall:** F08, F09.<br>**FallAllD:** Trying to stand up (forward, backward, lateral; ± recovery).<br>**KFall:** F04, F05. |
| **U7** | **Síncope estando sentado** | Caídas por pérdida de conciencia desde una posición sentada. | **SisFall:** F13, F14, F15.<br>**FallAllD:** Sitting fainting (forward, backward, lateral).<br>**KFall:** F06, F07, F08. |
| **U8** | **Caída desde la cama** | Caídas producidas durante movimientos o cambios de posición sobre la cama. | **FallAllD:** Bed rotation fall (± recovery). |
| **U9** | **Caídas clasificadas únicamente por dirección** | El dataset únicamente informa la dirección de la caída, sin especificar su causa. | **UMAFall:** Forward, Backward, Lateral. |
| **U10** | **Caídas clasificadas por mecanismo de impacto** | El dataset diferencia únicamente la forma de impacto durante la caída. | **UP-Fall:** Forward with hands, Forward with knees, Backward, Lateral. |

## Cobertura por Dataset

| Grupo | SisFall | FallAllD | KFall | UMAFall | UP-Fall |
|--------|:-------:|:--------:|:-----:|:-------:|:-------:|
| U1. Resbalón al caminar | ✓ | ✓ | ✓ | — | — |
| U2. Tropiezo al caminar | ✓ | ✓ | ✓ | — | — |
| U3. Tropiezo al trotar | ✓ | ✓ | ✓ | — | — |
| U4. Síncope caminando o de pie | ✓ | ✓ | ✓ | — | — |
| U5. Intentando sentarse | ✓ | ✓ | ✓ | — | ✓ |
| U6. Intentando levantarse | ✓ | ✓ | ✓ | — | — |
| U7. Síncope sentado | ✓ | ✓ | ✓ | — | — |
| U8. Caída desde la cama | — | ✓ | — | — | — |
| U9. Sólo dirección | — | — | — | ✓ | — |
| U10. Sólo mecanismo de impacto | — | — | — | — | ✓ |

## Consideraciones

- La taxonomía se basa en el **mecanismo biomecánico de la caída** y no únicamente en la descripción textual utilizada por cada dataset.
- Se preservan las etiquetas originales para mantener la trazabilidad entre la taxonomía unificada y los datos de origen.
- Cuando un dataset proporciona menor nivel de detalle (por ejemplo, UMAFall o UP-Fall), sus etiquetas no se reinterpretan ni se asignan artificialmente a categorías más específicas.
- Esta clasificación constituye una representación común que permite comparar datasets heterogéneos y analizar posteriormente el impacto que tiene cada uno sobre el rendimiento del modelo de detección de caídas.