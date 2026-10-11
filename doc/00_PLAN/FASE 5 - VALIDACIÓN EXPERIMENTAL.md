# FASE 5 - VALIDACIÓN EXPERIMENTAL

> **Estado:** ⬜ Validación con datasets pendiente. El baseline de inferencia sintética está guardado; consultar el [plan vigente A/B para ESP32 y Ubuntu](../PLAN_VALIDACION_EXPERIMENTAL_AB_ESP32.md).

## Alcance vigente

Validar la integridad del protocolo USB/Serial, el preprocesamiento, las inferencias INT8 de los módulos A (caídas) y B (ECG), la regla de triaje y el rendimiento técnico. La ESP32 usa Arduino Core 2.0.17 y `TensorFlowLite_ESP32` 1.0.0; Ubuntu reproduce los datasets seleccionados.

## Secuencia

1. Congelar versiones, hashes, contratos de entrada/salida y criterios de aceptación.
2. Validar los manifiestos y generar la referencia Python de los modelos.
3. Comprobar el preprocesamiento C/C++ contra SciPy antes de flashear.
4. Añadir el protocolo serial secuencial y probar cada agente por separado.
5. Probar las cuatro combinaciones de la tabla de triaje y los casos inválidos.
6. Ejecutar `smoke`, luego `full`, en reproducción rápida; medir después la reproducción temporizada y los fallos de comunicación.
7. Guardar resultados, configuración, versiones y hashes para poder repetir la corrida.

## Interpretación

La validación actual no mide sensores físicos, conectividad Wi-Fi/MQTT ni latencia contra la nube. Los escenarios combinan UMAFall y PTB-XL sin sincronía ni identidad común; validan integración y reglas del prototipo, no diagnóstico clínico ni reducción de falsas alarmas en pacientes. Las métricas de caídas son por ventana y no deben leerse como eventos independientes. El trabajo futuro de sensores físicos, red y comparación clínica requiere un protocolo experimental aparte.
