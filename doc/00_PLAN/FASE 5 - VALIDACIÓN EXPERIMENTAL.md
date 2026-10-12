# FASE 5 - VALIDACIÓN EXPERIMENTAL

> **Estado:** ⬜ Validación con datasets pendiente. El baseline sintético de LiteFallNet + TinyECGNet queda como antecedente; la corrida vigente sustituye LiteFallNet por el agente de caídas basado en reglas. Consultar el [plan vigente para ESP32 y Ubuntu](../PLAN_VALIDACION_EXPERIMENTAL_AB_ESP32.md).

## Alcance vigente

Validar la integridad USB/Serial, el agente A de caídas basado en reglas con trials KFall nativos a 100 Hz, TinyECGNet INT8 como agente B con ECG PTB-XL a 250 Hz, la regla de triaje y el rendimiento técnico. Solo B usa TensorFlow Lite Micro. La ESP32 usa Arduino Core 2.0.17 y `TensorFlowLite_ESP32` 1.0.0; Ubuntu reproduce los datasets seleccionados.

## Secuencia

1. Congelar las reglas de A, las versiones/hash de TinyECGNet, los contratos de datos y los criterios de aceptación.
2. Preparar manifiestos KFall a 100 Hz y ECG a 250 Hz; ejecutar las pruebas offline de la máquina de estados y la referencia ECG.
3. Comprobar paridad del preprocesamiento ECG C/C++ contra SciPy antes de flashear.
4. Añadir el protocolo USB/Serial y probar A por reglas y B por inferencia de forma individual.
5. Probar las cuatro combinaciones de triaje, las entradas inválidas y el reset entre trials.
6. Ejecutar `smoke`, luego `full`, en reproducción rápida; medir después la reproducción temporizada a 100 Hz para A y 250 Hz para B, además de resiliencia serial.
7. Guardar resultados, configuración, versiones y hashes para poder repetir la corrida.

## Interpretación

La validación no mide adquisición desde sensores físicos, conectividad Wi-Fi/MQTT ni latencia contra la nube. KFall usa un IMU en espalda baja mientras el agente donante declara pecho; reportar esta diferencia. Los escenarios combinan trials KFall y PTB-XL sin sincronía ni identidad común; validan integración y triaje del prototipo, no diagnóstico clínico ni reducción de falsas alarmas en pacientes. A se evalúa por trial, no por ventanas solapadas. El trabajo futuro con sensor de pecho, red y comparación clínica requiere un protocolo experimental aparte.
