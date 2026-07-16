---
tags:
  - ambiente
---
# Intensidad lumínica
> La **intensidad lumínica** (o luminosidad ambiental) es la magnitud que indica la cantidad o el nivel de luz presente en un entorno determinado.

## Cómo repercute en el cuidado de la salud
En los ecosistemas de [[Internet de las Cosas Médicas (IoMT)]] y proyectos de vida asistida, la luminosidad se monitorea continuamente como una variable del **microclima y entorno** del paciente. Su principal utilidad médica es la **correlación etiológica de eventos adversos**:

- **Detección de síncopes (desmayos):** En los [[Sistemas Multiagente (MAS)|sistemas de triaje multiagente]], si el dispositivo detecta una **caída abrupta de la luminosidad** (lo que ocurre si el paciente colapsa y el sensor queda cubierto contra el suelo) simultáneamente con una lectura de **hipotensión arterial**, el sistema cruza estos datos y emite una **alerta CRÍTICA (ROJA)**, identificando un desmayo o depresión circulatoria aguda inminente.

## Cómo se mide
Se mide a través de **sensores de luminosidad o luz ambiental**. En el contexto clínico, el hardware se implementa de la siguiente manera:

- **Unidades ambientales:** Módulos fijos instalados en el hogar del paciente que capturan la luz ambiente en conjunto con la temperatura, humedad y presión.
- **Sensores integrados de bajo consumo:** Chips especializados (como el modelo Si1145) que pueden medir tanto la luz ambiental visible como el índice de radiación ultravioleta (UV) de forma simultánea, consumiendo muy poca energía para su uso prolongado.

---
