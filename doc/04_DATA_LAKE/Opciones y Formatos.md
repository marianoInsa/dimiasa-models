
---

Google da 5 GB gratis pero hay que registrarse con tarjeta de crédito: https://cloud.google.com/storage

Tu consumo de espacio dependerá estrictamente de cómo guardes los datos:

- **Si usas CSV o JSON:** Es probable que te quedes sin espacio. Al duplicar los datos entre Plata y Oro, si tus 3 GB iniciales se reducen a 2.5 GB en Plata, al replicarlos con transformaciones en Oro sumarás otros 2.5 GB. Alcanzarás los 5 GB de límite muy rápido.
- **Si usas Parquet o Delta Lake:** Sí te alcanzará. Estos formatos comprimen el almacenamiento de forma columnar (hasta un 75% menos que un CSV). Tus 3 GB de datos crudos podrían reducirse a menos de 800 MB en Plata, y la capa Oro ocuparía incluso menos. El total combinado de ambas carpetas rondaría los 1.5 GB, quedando lejos del límite de 5 GB.

---------------------
