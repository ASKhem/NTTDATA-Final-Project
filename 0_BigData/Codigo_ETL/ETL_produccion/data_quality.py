# data_quality.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum
from logger_config import logger
from functools import reduce

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


if __name__ == '__main__':
    """
    Punto de entrada para ejecutar el informe de calidad de datos como un script independiente.
    """
    logger.info("Iniciando el script de informe de calidad de datos.")
    
    spark = SparkSession.builder.appName("DataQualityReport").getOrCreate()

    # --- ANÁLISIS DEL DATASET DEL CLIMA ---
    logger.info("--- Iniciando análisis del dataset del clima (weather_features.csv) ---")
    weather_df = get_data(spark, "weather_features.csv")
    if weather_df:
        count_duplicates(weather_df, ["dt_iso", "city_name"])
        count_nulls(weather_df)
        weather_quality_rules(weather_df)

    # --- ANÁLISIS DEL DATASET DE ENERGÍA ---
    logger.info("--- Iniciando análisis del dataset de energía (energy_dataset.csv) ---")
    energy_df = get_data(spark, "energy_dataset.csv")
    if energy_df:
        count_duplicates(energy_df, ["time"])
        count_nulls(energy_df)

    logger.info("El script de informe de calidad de datos ha finalizado.")
    spark.stop()
