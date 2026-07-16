---
tags:
  - ambiente
---
# Humedad relativa
> La **humedad relativa** es una magnitud meteorológica que indica la cantidad de vapor de agua presente en el aire, expresada como un porcentaje de la cantidad máxima de vapor que ese mismo aire podría retener a una temperatura determinada antes de saturarse.

La medición de la **humedad relativa (HR)** en entornos de [[Internet de las Cosas Médicas (IoMT)]] es fundamental para garantizar condiciones ambientales óptimas en hospitales, laboratorios, clínicas y en el cuidado domiciliario de pacientes.

## Cómo repercute en el cuidado de la salud
La humedad relativa es uno de los parámetros ambientales que se monitorean con mayor frecuencia para proteger la salud y evaluar la seguridad del entorno de un paciente o trabajador. Su impacto e importancia en el ecosistema médico destacan en dos áreas:

- **Evaluación de riesgos ambientales:** Se monitorea continuamente junto con la temperatura ambiente, los niveles de CO2​ y la radiación UV para generar un perfil del microclima. Esto es clave para advertir sobre condiciones perjudiciales que puedan agravar la salud, como el **estrés térmico** en entornos laborales o residenciales.
- **Cálculo de la verdadera [[Temperatura Cutánea|Temperatura Central]]:** En los sistemas IoMT modernos, la humedad relativa es una covariable vital. Los algoritmos de procesamiento la integran en modelos de regresión múltiple (junto al flujo de calor local, la temperatura ambiente y la tasa metabólica) para **predecir con alta precisión la verdadera temperatura central del cuerpo humano** a partir de simples lecturas en la piel.

## Cómo se mide
La humedad relativa se mide utilizando **sensores ambientales digitales** (como el modelo **BME680**) o higrómetros de bajo consumo. En el contexto médico moderno, estos biosensores se integran en **nodos portátiles (wearables)** que las personas llevan consigo (por ejemplo, adheridos al cuerpo o montados en un casco protector) para capturar el entorno inmediato. Para transmitir sus lecturas, los sensores suelen utilizar interfaces de comunicación serial como I2C, enviando los datos a un microcontrolador que luego los transmite a la nube para la supervisión médica.

---
