#ifndef AGENT1_TINYECGNET_SEQUENTIAL_INT8_CONFIG_H
#define AGENT1_TINYECGNET_SEQUENTIAL_INT8_CONFIG_H

/* Generado por scripts/export_tflite_header.py desde agent1_tinyecgnet_sequential_int8.tflite. No editar. */

/* Ventana de analisis, leida de la forma de entrada del .tflite. */
#define FRECUENCIA_HZ 250
#define TAMANO_VENTANA 2500
#define PASO_MUESTRAS 2500
#define NUM_CANALES 1
#define FORMA_ENTRADA {1, 2500, 1}

/* Cuantizacion de entrada: q = clip(rint(x / ESCALAF + CERO), -128, 127). */
#define ENTRADA_ESCALAF 0.081706210970878601f
#define ENTRADA_CERO -18

/* Valor real maximo representable en la entrada cuantizada. */
#define TECHO_ENTRADA_REAL 11.847400590777397f

/* Cuantizacion de salida: p = (q - SALIDA_CERO) * SALIDA_ESCALAF. */
#define SALIDA_ESCALAF 0.00390625f
#define SALIDA_CERO -128

#define UMBRAL 0.5f
#define UMBRAL_SALIDA_INT8 0
#define UMBRAL_RECONSTRUIDO 0.5f

#endif
