# data_quality.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum
from logger_config import logger
from pyspark.sql.types import *


def validate_weather_schema(df):
    expected_columns = [
        "dt_iso", "cityID", "temp", "temp_min", "temp_max", "pressure", "humidity",
        "wind_speed", "wind_deg", "rain_1h", "rain_3h", "snow_3h", "clouds_all",
        "weather_id", "weather_main", "weather_description", "weather_icon"
    ]
    if df.columns == expected_columns:
        return True
    else:
        missing = [col for col in expected_columns if col not in df.columns]
        extra = [col for col in df.columns if col not in expected_columns]
        logger.info('Invalid weather schema')
        return False

def validate_energy_schema(df):
    fixed_columns = ["time","forecast solar day ahead","forecast wind offshore eday ahead", 
                     "forecast wind onshore day ahead","total load forecast",
                     "total load actual", "price day ahead","price actual"]
    
    generation_prefix = "generation "

    columns = df.columns
    missing_fixed = [col for col in fixed_columns if col not in columns]
    if missing_fixed:
        logger.info('Invalid energy schema')
        return False

    generation_columns = [col for col in columns if col.startswith(generation_prefix)]

    if len(generation_columns) == 0:
        logger.info('Invalid energy schema')
        return False

    allowed_columns = set(fixed_columns) | set(generation_columns)
    extra_columns = [col for col in columns if col not in allowed_columns]
    if extra_columns:
        logger.info('Invalid energy schema')
        return False

    return True


def get_data(spark, input_path):
    """
    Lee los datos desde un fichero CSV y registra la información básica.
    """
    logger.info(f"Leyendo datos desde: {input_path}")
    try:
        df = spark.read.csv(input_path, header=True, inferSchema=True)
        logger.info(f"Total de registros leídos: {df.count()}")
        
        logger.info(f"Esquema de datos para {input_path}:")
        # Capturamos el schema para loggearlo de forma limpia
        schema_string = df.schema.simpleString()
        logger.info(f"\n{schema_string}")

        return df
    except Exception as e:
        logger.error(f"Error al leer los datos desde {input_path}: {e}")
        return None

def count_duplicates(df, target_columns):
    """
    Cuenta y registra el número de registros duplicados y no duplicados.
    """
    if not df:
        logger.warning("DataFrame de entrada para count_duplicates es None. Saltando paso.")
        return
    
    try:
        total_count = df.count()
        df_dup = df.groupBy(target_columns).count().filter(col("count") > 1)
        duplicate_count = df_dup.count()
        
        logger.info(f"Análisis de duplicados en columnas: {target_columns}")
        logger.info(f"Número de registros duplicados encontrados: {duplicate_count}")
        logger.info(f"Número de registros no duplicados: {total_count - duplicate_count}")
    except Exception as e:
        logger.error(f"Error en count_duplicates: {e}")


def count_nulls(df):
    """
    Cuenta y registra el número de valores nulos por columna.
    """
    if not df:
        logger.warning("DataFrame de entrada para count_nulls es None. Saltando paso.")
        return
        
    try:
        logger.info("Iniciando recuento de valores nulos por columna.")
        null_counts_df = df.select([spark_sum(col(c).isNull().cast('int')).alias(c) for c in df.columns])
        
        # Convertimos el resultado a un formato más legible para el log
        null_counts_dict = null_counts_df.collect()[0].asDict()
        logger.info(f"Recuento de nulos: {null_counts_dict}")
    except Exception as e:
        logger.error(f"Error en count_nulls: {e}")


def weather_quality_rules(df):
    """
    Aplica reglas de calidad de datos específicas para el dataset del clima.
    """
    if not df:
        logger.warning("DataFrame de entrada para weather_quality_rules es None. Saltando paso.")
        return

    try:
        logger.info("Aplicando reglas de calidad de datos al dataset del clima.")
        
        # Chequeo de rangos de valores
        quality_checks = {
            "temp_range": df.filter((col("temp") >= 238.15) & (col("temp") <= 321.15)).count(),
            "temp_min_range": df.filter((col("temp_min") >= 238.15) & (col("temp_min") <= 321.15)).count(),
            "temp_max_range": df.filter((col("temp_max") >= 238.15) & (col("temp_max") <= 321.15)).count(),
            "pressure_range": df.filter((col("pressure") >= 800) & (col("pressure") <= 1100)).count(),
            "humidity_range": df.filter((col("humidity") >= 0) & (col("humidity") <= 100)).count(),
            "wind_speed_range": df.filter((col("wind_speed") >= 0) & (col("wind_speed") <= 68.88)).count(),
            "wind_deg_range": df.filter((col("wind_deg") >= 0) & (col("wind_deg") <= 360)).count(),
            "rain_1h_positive": df.filter(col("rain_1h") >= 0).count(),
            "rain_3h_positive": df.filter(col("rain_3h") >= 0).count(),
            "snow_3h_positive": df.filter(col("snow_3h") >= 0).count(),
            "clouds_all_range": df.filter((col("clouds_all") >= 0) & (col("clouds_all") <= 100)).count()
        }
        
        logger.info(f"Resultados de las reglas de calidad (recuento de registros válidos): {quality_checks}")
        
    except Exception as e:
        logger.error(f"Error en weather_quality_rules: {e}")


if __name__ == '__main__':
    """
    Punto de entrada para ejecutar el informe de calidad de datos como un script independiente.
    """
    logger.info("Iniciando el script de informe de calidad de datos.")
    
    spark = SparkSession.builder.appName("DataQualityReport").getOrCreate()

    # --- ANÁLISIS DEL DATASET DEL CLIMA ---
    logger.info("--- Iniciando análisis del dataset del clima (weather_features.csv) ---")
    weather_df = get_data(spark, "weather_features.csv")
    valid_weather_schema=validate_weather_schema(weather_df)
    if weather_df & valid_weather_schema:
        count_duplicates(weather_df, ["dt_iso", "city_name"])
        count_nulls(weather_df)
        weather_quality_rules(weather_df)

    # --- ANÁLISIS DEL DATASET DE ENERGÍA ---
    logger.info("--- Iniciando análisis del dataset de energía (energy_dataset.csv) ---")
    energy_df = get_data(spark, "energy_dataset.csv")
    valid_energy_schema=validate_energy_schema(energy_df)
    if energy_df & valid_energy_schema:
        count_duplicates(energy_df, ["time"])
        count_nulls(energy_df)

    logger.info("El script de informe de calidad de datos ha finalizado.")
    spark.stop()
