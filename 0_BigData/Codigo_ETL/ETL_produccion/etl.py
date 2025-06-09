# etl.py
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, broadcast
from logger_config import logger
from data_quality import clean_energy_data, clean_weather_data, get_data

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
        clean_energy_df = clean_energy_data(raw_energy_df)

        raw_weather_df = get_data(spark, input_path_weather)
        clean_weather_df = clean_weather_data(raw_weather_df)

        # --- Forzar la materialización de los DataFrames limpios ---
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
