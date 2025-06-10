# etl.py
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, broadcast
from logger_config import logger
from data_quality import get_data, validate_energy_schema, validate_weather_schema

def clean_energy_data(df):
    """
    Limpia y preprocesa el DataFrame de energía.
    """
    logger.info("Iniciando limpieza del dataset de energía.")
    
    # Eliminar duplicados
    df_cleaned = df.dropDuplicates(['time'])
    logger.info(f"Registros después de eliminar duplicados: {df_cleaned.count()}")
    
    # Eliminar las 18 filas con nulos generalizados
    df_cleaned = df_cleaned.dropna(subset=["generation fossil brown coal or lignite"])
    logger.info(f"Registros después de eliminar filas con nulos generalizados: {df_cleaned.count()}")
    
    # Imputación de nulos con la mediana
    logger.info("Calculando medianas para imputación de nulos.")
    medians = {
        'generation biomass': df_cleaned.approxQuantile('generation biomass', [0.5], 0.01)[0],
        'generation fossil oil': df_cleaned.approxQuantile('generation fossil oil', [0.5], 0.01)[0],
        'generation hydro pumped storage consumption': df_cleaned.approxQuantile('generation hydro pumped storage consumption', [0.5], 0.01)[0],
        'generation hydro run-of-river and poundage': df_cleaned.approxQuantile('generation hydro run-of-river and poundage', [0.5], 0.01)[0],
        'generation marine': df_cleaned.approxQuantile('generation marine', [0.5], 0.01)[0],
        'generation waste': df_cleaned.approxQuantile('generation waste', [0.5], 0.01)[0],
        'total load actual': df_cleaned.approxQuantile('total load actual', [0.5], 0.01)[0]
    }
    
    df_cleaned = df_cleaned.fillna(medians)
    logger.info("Imputación de nulos con mediana completada.")
    
    # Imputación de columnas completamente nulas con 'Unknown'
    df_cleaned = df_cleaned.fillna({
        'generation hydro pumped storage aggregated': 'Unknown',
        'forecast wind offshore eday ahead': 'Unknown'
    })
    logger.info("Imputación de columnas categóricas con 'Unknown' completada.")
    
    return df_cleaned

def clean_weather_data(df):
    """
    Limpia y preprocesa el DataFrame del clima.
    """
    logger.info("Iniciando limpieza del dataset del clima.")
    
    # Eliminar duplicados
    df_cleaned = df.dropDuplicates(["dt_iso", "city_name"])
    logger.info(f"Registros después de eliminar duplicados: {df_cleaned.count()}")
    
    # Conversión de unidades
    logger.info("Convirtiendo unidades (Temperatura a Celsius, Viento a km/h).")
    for temp_col in ["temp", "temp_min", "temp_max"]:
        df_cleaned = df_cleaned.withColumn(temp_col, col(temp_col) - 273.15)
    df_cleaned = df_cleaned.withColumn('wind_speed', col('wind_speed') * 3.6)
    
    # Renombrar columna de tiempo
    df_cleaned = df_cleaned.withColumnRenamed("dt_iso", "time")
    
    # Filtrar outliers
    logger.info("Filtrando valores atípicos de presión y viento.")
    df_cleaned = df_cleaned.filter((col("pressure") >= 800) & (col("pressure") <= 1100))
    df_cleaned = df_cleaned.filter((col("wind_speed") >= 0) & (col("wind_speed") <= 248))
    
    # Eliminar columnas no deseadas
    logger.info("Eliminando columnas no deseadas (weather_id, weather_icon).")
    df_cleaned = df_cleaned.drop('weather_id', 'weather_icon')
    
    logger.info(f"Limpieza del dataset del clima completada. Registros finales: {df_cleaned.count()}")
    return df_cleaned

def main():
    """
    Punto de entrada principal del script ETL.
    Orquesta la lectura, limpieza y escritura de los datasets.
    """
    logger.info("Iniciando pipeline ETL principal.")
    spark = SparkSession.builder.appName("NaturgyETL").getOrCreate()

    # --- CONFIGURACIÓN DE RUTAS ---
    gcs_bucket_name = "naturgy-gcs"
    input_path_energy = f"gs://{gcs_bucket_name}/raw_data/energy_dataset.csv"
    input_path_weather = f"gs://{gcs_bucket_name}/raw_data/weather_features.csv"
    
    output_path_energy = f"gs://{gcs_bucket_name}/silver_data/energy_silver.parquet"
    output_path_weather = f"gs://{gcs_bucket_name}/silver_data/weather_features_silver.parquet"
    
    logger.info(f"Bucket de GCS configurado: {gcs_bucket_name}")
    logger.info(f"Ruta de salida para Energía (Silver): {output_path_energy}")
    logger.info(f"Ruta de salida para Clima (Silver): {output_path_weather}")

    try:
        # --- LECTURA Y LIMPIEZA DE DATOS ---
        raw_energy_df = get_data(spark, input_path_energy)
        valid_energy_schema=validate_energy_schema(raw_energy_df)
        if valid_energy_schema:
            clean_energy_df = clean_energy_data(raw_energy_df)
        raw_weather_df = get_data(spark, input_path_weather)
        valid_weather_schema=validate_weather_schema(raw_weather_df)
        if valid_weather_schema:
            clean_weather_df = clean_weather_data(raw_weather_df)

        # --- Forzar la materialización de los DataFrames limpios ---

        if valid_energy_schema & valid_weather_schema:
            logger.info("Cacheando DataFrames limpios para optimizar la ejecución.")
            clean_energy_df.cache()
            clean_weather_df.cache()
            # Ejecutar una acción para disparar el cacheo
            logger.info(f"Número de filas en el DF de energía limpio y cacheado: {clean_energy_df.count()}")
            logger.info(f"Número de filas en el DF de clima limpio y cacheado: {clean_weather_df.count()}")

            # --- ESCRITURA DE LA CAPA SILVER ---
            logger.info("--- Iniciando la escritura de los datos limpios (Capa Silver) ---")
            
            logger.info(f"Escribiendo fichero de energía limpio en: {output_path_energy}")
            clean_energy_df.write.mode("overwrite").parquet(output_path_energy)
            logger.info("Escritura de energía (Silver) completada.")
            
            logger.info(f"Escribiendo fichero de clima limpio en: {output_path_weather}")
            clean_weather_df.write.mode("overwrite").parquet(output_path_weather)
            logger.info("Escritura de clima (Silver) completada.")

    except Exception as e:
        logger.error(f"Ha ocurrido un error en el pipeline ETL: {e}", exc_info=True)
        raise

    finally:
        logger.info("Deteniendo la sesión de Spark.")
        spark.stop()
        logging.shutdown()

if __name__ == "__main__":
    main()
