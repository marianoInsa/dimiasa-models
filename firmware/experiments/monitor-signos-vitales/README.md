# Monitor de signos vitales — prototipos experimentales

> Material de prototipos seriales y señales sintéticas. No es el baseline oficial ni forma parte de la validación vigente de Fase 5.

## Contenido

- `Agent1_ECG_ESP32/`: sketch ESP32 para inferencia INT8 y sus headers de configuración/modelo. Recibe 5000 muestras a 500 Hz y reduce a 2500 tomando una de cada dos. Las funciones de pasa-banda y notch actualmente dejan la señal sin cambios; los mensajes de éxito del sketch no significan que esos filtros se hayan aplicado. Usa `Chirale_TensorFlowLite`, no la configuración de la validación vigente.
- `envio seña_ecg/`: emisor serial y banco PTB-XL de 2158 registros, cada uno con 5000 muestras. El script carga el NPZ desde esta misma carpeta. El tamaño no coincide con el test oficial de 2113 registros y no hay aquí un manifiesto que pruebe que sea esa partición.
- `agente2-caida/`: sketch ESP32 de detección por reglas, con ventanas de 100 muestras a 100 Hz. El comentario de montaje en pecho pertenece a este prototipo; no describe el montaje lumbar de KFall usado en la validación vigente.
- `señal-caida/`: emisores seriales de escenarios sintéticos normal, caída y movimiento fuerte sin caída. Usan `COM3` y requieren una placa conectada; no son pruebas automatizadas.

La implementación de reglas que participa en la Fase 5 está en `firmware/esp32_validation/fall_agent.{h,cpp}` y sus pruebas nativas. El sketch de esta carpeta se conserva como referencia experimental, no como una segunda implementación activa.

## Límites de interpretación

- El clasificador ECG y su header son artefactos distintos del modelo oficial TinyECGNet de 250 Hz. Que compartan forma de entrada `[1, 2500, 1]` y parámetros de cuantización no demuestra igualdad de pesos ni de preprocesamiento.
- La reducción por selección de muestras no aplica un filtro antialias. No comparar resultados con el pipeline oficial sin reconstruir y validar el preprocesamiento y la partición de datos.
- Las señales de caída son sintéticas. No prueban rendimiento clínico ni reemplazan la evaluación por trials KFall.

Para usar los emisores seriales se requiere Python con NumPy y pySerial, una ESP32 compatible y configurar `PORT` en cada script que se vaya a ejecutar. El sketch ECG además requiere la biblioteca indicada en su encabezado.
