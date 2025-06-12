# etl.py
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, broadcast
from logger_config import logger
from data_quality import get_data, validate_energy_schema, validate_weather_schema
from delta.tables import DeltaTable
from delta import configure_spark_with_delta_pip


def clean_energy_data(df):
    """
    Limpia y preprocesa el DataFrame de energía.
    """
    logger.info("Iniciando limpieza del dataset de energía.")
    
    # Eliminar duplicados
    df_cleaned = df.dropDuplicates(['time'])
    df_cleaned = df_cleaned.toDF(*[col.replace(" ", "_")
                 .replace("(", "")
                 .replace(")", "")
                 .replace("{", "")
                 .replace("}", "")
                 .replace(";", "")
                 .replace(",", "")
                 .replace("\t", "")
                 .replace("\n", "")
                 .replace("=", "")
                 for col in df_cleaned.columns])
    logger.info(f"Registros después de eliminar duplicados: {df_cleaned.count()}")
    
    # Eliminar las 18 filas con nulos generalizados
    df_cleaned = df_cleaned.dropna(subset=["generation_fossil_brown_coal_or_lignite"])
    logger.info(f"Registros después de eliminar filas con nulos generalizados: {df_cleaned.count()}")
    
    # Imputación de nulos con la mediana
    logger.info("Calculando medianas para imputación de nulos.")
    medians = {
        'generation_biomass': df_cleaned.approxQuantile('generation_biomass', [0.5], 0.01)[0],
        'generation_fossil_oil': df_cleaned.approxQuantile('generation_fossil_oil', [0.5], 0.01)[0],
        'generation_hydro_pumped_storage_consumption': df_cleaned.approxQuantile('generation_hydro_pumped_storage_consumption', [0.5], 0.01)[0],
        'generation_hydro_run-of-river_and_poundage': df_cleaned.approxQuantile('generation_hydro_run-of-river_and_poundage', [0.5], 0.01)[0],
        'generation_marine': df_cleaned.approxQuantile('generation_marine', [0.5], 0.01)[0],
        'generation_waste': df_cleaned.approxQuantile('generation_waste', [0.5], 0.01)[0],
        'total_load_actual': df_cleaned.approxQuantile('total_load_actual', [0.5], 0.01)[0]
    }
    
    df_cleaned = df_cleaned.fillna(medians)
    logger.info("Imputación de nulos con mediana completada.")
    
    # Imputación de columnas completamente nulas con 'Unknown'
    df_cleaned = df_cleaned.fillna({
        'generation_hydro_pumped_storage_aggregated': 'Unknown',
        'forecast_wind_offshore_eday_ahead': 'Unknown'
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
    df_cleaned = df_cleaned.toDF(*[col.replace(" ", "_")
                 .replace("(", "")
                 .replace(")", "")
                 .replace("{", "")
                 .replace("}", "")
                 .replace(";", "")
                 .replace(",", "")
                 .replace("\t", "")
                 .replace("\n", "")
                 .replace("=", "")
                 for col in df_cleaned.columns])
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
   
    builder = SparkSession.builder \
    .appName("sparkETL") \

    spark = configure_spark_with_delta_pip(builder).getOrCreate()

    logger.info(f"  VERSION SPARK: {spark.version}")

    # --- CONFIGURACIÓN DE RUTAS ---
    gcs_bucket_name = "naturgy-gcs"
    input_path_energy = f"gs://{gcs_bucket_name}/raw_data/energy_dataset.csv"
    input_path_weather = f"gs://{gcs_bucket_name}/raw_data/weather_features.csv"
    
    output_path_energy = f"gs://{gcs_bucket_name}/silver_data/energy_silver.delta"
    output_path_weather = f"gs://{gcs_bucket_name}/silver_data/weather_features_silver.delta"
    
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
            try:
                delta_table = DeltaTable.forPath(spark, output_path_energy)
                delta_table.alias("existing") \
                    .merge(
                        clean_energy_df.alias("new"),
                        "existing.time = new.time"
                    ) \
                    .whenMatchedUpdateAll() \
                    .whenNotMatchedInsertAll() \
                    .execute()
                print('ATENCIONNNNNNNNN delta ya existia')

            except:
                clean_energy_df.write.format("delta").mode("overwrite").save(output_path_energy)
                print('ATENCIONNNNNNNNN guardando en silver delta')

            logger.info("Escritura de energía (Silver) completada.")
            
            logger.info(f"Escribiendo fichero de clima limpio en: {output_path_weather}")
            try:
                delta_table = DeltaTable.forPath(spark, output_path_weather)
                delta_table.alias("existing") \
                    .merge(
                        clean_weather_df.alias("new"),
                        "existing.time = new.time AND existing.city_name=new.city_name"
                    ) \
                    .whenMatchedUpdateAll() \
                    .whenNotMatchedInsertAll() \
                    .execute()
            except:
                clean_weather_df.write.format("delta").mode("overwrite").save(output_path_weather)

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
