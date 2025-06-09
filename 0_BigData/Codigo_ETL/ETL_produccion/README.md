# Documentación del Pipeline ETL de Producción

Este directorio contiene los scripts de Python que conforman el pipeline de Extracción, Transformación y Carga (ETL) para los datos de energía y clima del proyecto. El pipeline está diseñado para ser ejecutado en un entorno de Apache Spark, como Google Dataproc.

## Estructura del Directorio

-   `etl.py`: Es el orquestador principal del pipeline.
-   `data_quality.py`: Contiene funciones para la limpieza y validación de la calidad de los datos.
-   `logger_config.py`: Configura un logger centralizado para registrar los eventos del pipeline, con integración a Google Cloud Logging.

## Descripción de los Módulos

### `logger_config.py`

Este módulo configura el sistema de logging para toda la aplicación.

-   **Función `setup_logging()`**:
    -   Intenta configurar un logger que envía los registros directamente a **Google Cloud Logging**. Esto es ideal para la monitorización en entornos de producción en GCP.
    -   Si la configuración de Google Cloud Logging falla (por ejemplo, al ejecutar el código localmente sin las credenciales adecuadas), establece un logger básico que imprime los mensajes en la consola.
-   **Variable `logger`**:
    -   Una instancia del logger configurado que se puede importar y utilizar en otros módulos para asegurar un registro consistente.

### `data_quality.py`

Este fichero contiene toda la lógica relacionada con la limpieza, transformación y validación de los datos de los datasets de energía y clima.

-   **`get_data(spark, input_path)`**: Lee un fichero CSV desde la ruta especificada, infiere el esquema y registra información básica como el número de registros y el esquema del DataFrame.
-   **`count_duplicates(df, target_columns)`**: Calcula y registra el número de filas duplicadas basándose en un conjunto de columnas clave.
-   **`count_nulls(df)`**: Calcula y registra el número de valores nulos para cada columna del DataFrame.
-   **`weather_quality_rules(df)`**: Aplica un conjunto de reglas de validación específicas para el dataset del clima (rangos de temperatura, presión, etc.).
-   **`clean_energy_data(df)`**: Orquesta la limpieza del dataset de energía. Los pasos incluyen:
    1.  Eliminación de duplicados por la columna `time`.
    2.  Eliminación de filas con valores nulos en columnas críticas.
    3.  Imputación de valores nulos en columnas numéricas utilizando la **mediana**.
    4.  Imputación de valores nulos en columnas categóricas con el valor `'Unknown'`.
-   **`clean_weather_data(df)`**: Orquesta la limpieza del dataset del clima. Los pasos incluyen:
    1.  Eliminación de duplicados por las columnas `dt_iso` y `city_name`.
    2.  Conversión de unidades: temperatura de Kelvin a Celsius y velocidad del viento de m/s a km/h.
    3.  Renombrado de la columna `dt_iso` a `time` para consistencia.
    4.  Filtrado de valores atípicos (outliers) en `pressure` y `wind_speed`.
    5.  Eliminación de columnas no necesarias para el análisis (`weather_id`, `weather_icon`).

### `etl.py`

Este es el script principal que ejecuta el pipeline ETL de principio a fin.

-   **Función `main()`**:
    1.  **Inicialización**: Inicia una sesión de Spark.
    2.  **Configuración de Rutas**: Define las rutas de entrada (en `gs://<bucket>/raw_data/`) y de salida para la capa Silver (en `gs://<bucket>/silver_data/`) en Google Cloud Storage.
    3.  **Lectura y Limpieza**: Llama a las funciones de `data_quality.py` para leer y limpiar los datasets de energía y clima.
    4.  **Escritura en Capa Silver**: Guarda los dos DataFrames limpios (energía y clima) en formato Parquet en una ubicación centralizada de Google Cloud Storage. Estos ficheros constituyen la capa "Silver" de datos, que sirve como una fuente de verdad única y fiable para los equipos de Business Intelligence y Machine Learning.
    5.  **Finalización**: Detiene la sesión de Spark de forma segura.

## Ejecución del Pipeline

Para ejecutar este pipeline, es necesario empaquetar este directorio (`ETL_produccion`) y enviarlo como un trabajo de PySpark a un clúster de Dataproc.

El comando de ejecución en `gcloud` sería similar a este:

```bash
gcloud dataproc jobs submit pyspark gs://<ruta-al-fichero>/etl.py \
    --cluster=<nombre-del-cluster> \
    --region=<region> \
    --py-files=gs://<ruta-al-zip>/produccion_etl.zip
```

Donde `produccion_etl.zip` es un fichero comprimido que contiene `data_quality.py` y `logger_config.py`.
