
---
**Documentación de Azure:**
* [DataLakeFileClient Class](https://learn.microsoft.com/en-us/python/api/azure-storage-file-datalake/azure.storage.filedatalake.datalakefileclient?view=azure-python)
* [StorageStreamDownloader Class](https://learn.microsoft.com/en-us/python/api/azure-storage-file-datalake/azure.storage.filedatalake.storagestreamdownloader?view=azure-python)

---
# 📘 Conexión a Azure Data Lake Gen2 desde Python

## 1. Configuración Inicial y Arquitectura

Para trabajar con ADLS Gen2 (que utiliza un espacio de nombres jerárquico), la librería oficial y recomendada es `azure-storage-file-datalake`.

En la arquitectura de datos (especialmente en el patrón **Medallion Architecture**), organizarás tu información en contenedores que representan diferentes estados de madurez del dato:

### 📌 Instalación del Entorno

Ejecuta este comando en tu terminal o en una celda de Google Colab:

```Bash
!pip install azure-storage-file-datalake pandas pyarrow fastparquet
```

> [!Note]
> Añadimos `pyarrow` y `fastparquet` porque los vas a necesitar para interactuar con el formato Parquet en las capas Plata y Oro.

## 2. Código Base: Lectura (Bronce) y Escritura (Plata)

Este script centraliza la conexión mediante **Connection String** (Cadena de conexión). Es ideal para entornos de desarrollo y pruebas por su costo cero de configuración.

```Python
import os
import io
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient

# 1. Credenciales (Mantén esto seguro, idealmente usa variables de entorno en producción)
CONNECTION_STRING = "TU_CADENA_DE_CONEXION_AQUI"

# 2. Inicializar el cliente del Data Lake
try:
    service_client = DataLakeServiceClient.from_connection_string(CONNECTION_STRING)
    print("Conexión exitosa con Azure Data Lake.")
except Exception as e:
    print(f"Error al conectar: {e}")
```

### Capa Bronce: Leer archivo

```Python
try:
    # Conexión al contenedor y ruta del archivo
    file_system_client_bronce = service_client.get_file_system_client(file_system="bronce")
    directory_client = file_system_client_bronce.get_directory_client("datos_crudos")
    file_client_bronce = directory_client.get_file_client("ventas.csv")

    # Descargar el archivo a la memoria (Formato binario/bytes)
    download = file_client_bronce.download_file()
    content_bytes = download.readall()
    
    # Cargar directamente en Pandas usando un buffer de memoria
    df_bronce = pd.read_csv(io.BytesIO(content_bytes))
    print("Archivo de Bronce cargado en DataFrame con éxito.")
    
    # --- SIMULACIÓN DE PROCESAMIENTO (Transformación a Plata) ---
    # Convertimos los nombres de las columnas a mayúsculas como ejemplo de limpieza
    df_plata = df_bronce.copy()
    df_plata.columns = [col.upper() for col in df_plata.columns]

except Exception as e:
    print(f"Error en procesamiento de Capa Bronce: {e}")
```

### Capa Plata: Escribir en formato Parquet

```Python
try:
    file_system_client_plata = service_client.get_file_system_client(file_system="plata")
    file_client_plata = file_system_client_plata.create_file("datos_limpios/ventas_procesadas.parquet")
    
    # Convertir el DataFrame de Pandas a bytes en formato Parquet
    parquet_buffer = io.BytesIO()
    df_plata.to_parquet(parquet_buffer, index=False)
    datos_a_subir = parquet_buffer.getvalue()
    
    # Subida eficiente en una sola operación (Evita costos extra por chunks)
    file_client_plata.append_data(data=datos_a_subir, offset=0, length=len(datos_a_subir))
    file_client_plata.flush_data(position=len(datos_a_subir))
    print("Archivo subido con éxito a la capa Plata en formato Parquet.")

except Exception as e:
    print(f"Error al escribir en Capa Plata: {e}")
```

## 3. Integración con Pandas (Según Formato)

Cuando descargas datos con `download_file().readall()`, obtienes un objeto tipo `<class 'bytes'>`. Para que Pandas lo entienda sin escribir un archivo físico en el disco de Colab, usamos `io.BytesIO`.

### Fórmulas de Conversión Básica:

```Python
# Contenido previamente descargado: content = download.readall()

# 1. Para CSV
df = pd.read_csv(io.BytesIO(content))

# 2. Para JSON
df = pd.read_json(io.BytesIO(content))

# 3. Para Parquet
df = pd.read_parquet(io.BytesIO(content))
```

### ==**🔍 Importante: Mitigación de consumo de RAM en archivos grandes==**

Si el archivo es **gigante** y no cabe en la RAM de Colab, no uses el método clásico de bytes. La forma más limpia y eficiente en Python para hacer streaming directo desde Azure a Pandas (sin devorarte la RAM) es usar la librería secundaria `adlfs` que se conecta nativamente con Pandas:

```Python
# Alternativa para archivos masivos (Requiere: pip install adlfs)
storage_options = {'connection_string': CONNECTION_STRING}

# Pandas lee el archivo en bloques directamente desde la red
df_gigante = pd.read_csv("abfss://bronce@TU_STORAGE_ACCOUNT_NAME.dfs.core.windows.net/datos_crudos/ventas.csv", storage_options=storage_options)
```

## 4. Estrategia de Formatos de Almacenamiento

Es una excelente práctica de ingeniería de datos diferenciar los formatos según la capa en la que te encuentres:

|**Capa**|**Formato Ideal**|**Razón Técnica**|
|---|---|---|
|**Bronce (Crudos)**|`CSV` / `JSON`|Almacena los datos exactamente como llegaron del origen (auditoría pura). No se alteran.|
|**Plata / Oro**|`Parquet`|Formato columnar altamente comprimido. Reduce costos de almacenamiento en Azure y acelera las consultas de analítica un 100x.|

## 5. ⚠️ Alertas de Costos y Buenas Prácticas (Costo Cero)

Azure Storage no solo cobra por los Gigabytes almacenados, sino por las **operaciones (llamadas a la API)**. Sigue estas reglas para no salir del esquema gratuito:

- **El combo `.append_data()` + `.flush_data()`:** Al escribir, procura enviar todo el bloque de datos pesado en un solo `append` y cierra con un solo `flush`. Si haces bucles para subir un archivo de 10MB en pedacitos de 10KB, Azure te cobrará miles de operaciones de escritura.
    
- **Cuidado con `list_paths()`:** Evita colocar métodos que listen subcarpetas dentro de bucles `while` o `for` interminables. Cada listado consume operaciones de lectura (Clase B) que pueden acumularse rápidamente.
    
- **Ojo con la librería asíncrona (`azure.storage.filedatalake.aio`):** La extensión `.aio` pertenece al ecosistema **Asíncrono** (Asyncio). Si tu script es lineal y normal (sincrónico), **no uses la carpeta `.aio`**, mantente con el import tradicional (`azure.storage.filedatalake`), de lo contrario tu código arrojará errores de corrutinas no esperadas (`Coroutines`).