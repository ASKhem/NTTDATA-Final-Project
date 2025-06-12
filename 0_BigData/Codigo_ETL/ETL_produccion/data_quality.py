from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import col, avg, sum as spark_sum
from logger_config import logger
from pyspark.sql.types import *
from collections import OrderedDict

def validate_weather_schema(df):
    expected_columns = [
        "dt_iso", "city_name", "temp", "temp_min", "temp_max", "pressure", "humidity",
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
    logger.info(f"Leyendo datos desde: {input_path}")
    try:
        df = spark.read.csv(input_path, header=True, inferSchema=True)
        logger.info(f"Total de registros leídos: {df.count()}")
        schema_string = df.schema.simpleString()
        logger.info(f"\n{schema_string}")
        return df
    except Exception as e:
        logger.error(f"Error al leer los datos desde {input_path}: {e}")
        return None

def count_duplicates(df, target_columns, report_data):
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
        report_data.update({'duplicates': total_count - duplicate_count, 'sep': '-'})
        return report_data
    except Exception as e:
        logger.error(f"Error en count_duplicates: {e}")

def count_nulls(df, report_data):
    if not df:
        logger.warning("DataFrame de entrada para count_non_nulls es None. Saltando paso.")
        return
    try:
        logger.info("Iniciando recuento de valores no nulos por columna.")
        
        total_rows = df.count()
        
        null_counts_df = df.select([spark_sum(col(c).isNull().cast('int')).alias(c) for c in df.columns])
        null_counts_dict = null_counts_df.collect()[0].asDict()
        non_null_counts_dict = {col: total_rows - nulls for col, nulls in null_counts_dict.items()}
        logger.info(f"Recuento de valores no nulos: {non_null_counts_dict}")
        report_data.update(non_null_counts_dict)
        
        return report_data
    except Exception as e:
        logger.error(f"Error en count_non_nulls: {e}")

def weather_quality_rules(df, report_data):
    if not df:
        logger.warning("DataFrame de entrada para weather_quality_rules es None. Saltando paso.")
        return
    try:
        logger.info("Aplicando reglas de calidad de datos al dataset del clima.")
        quality_checks = OrderedDict([
            ("temp", df.filter((col("temp") >= 238.15) & (col("temp") <= 321.15)).count()),
            ("temp_min", df.filter((col("temp_min") >= 238.15) & (col("temp_min") <= 321.15)).count()),
            ("temp_max", df.filter((col("temp_max") >= 238.15) & (col("temp_max") <= 321.15)).count()),
            ("ud_celsius", df.filter((col("temp") >= -50) & (col("temp") <= 60)).count()),
            ("pressure", df.filter((col("pressure") >= 800) & (col("pressure") <= 1100)).count()),
            ("wind_speed", df.filter((col("wind_speed") >= 0) & (col("wind_speed") <= 68.88)).count()),
            ("ud_kmh", df.count() if df.select(avg("wind_speed")).first()[0] > 7 else 0),
            ("wind_deg", df.filter((col("wind_deg") >= 0) & (col("wind_deg") <= 360)).count()),
            ("rain_1h", df.filter(col("rain_1h") >= 0).count()),
            ("rain_3h", df.filter(col("rain_3h") >= 0).count()),
            ("snow_3h", df.filter(col("snow_3h") >= 0).count()),
            ("humidity", df.filter((col("humidity") >= 0) & (col("humidity") <= 100)).count()),
            ("clouds_all", df.filter((col("clouds_all") >= 0) & (col("clouds_all") <= 100)).count()),
        ])
        logger.info(f"Resultados de calidad (weather): {spark.createDataFrame([Row(**quality_checks)])}")
        report_data.update(quality_checks)
        return report_data
    except Exception as e:
        logger.error(f"Error en weather_quality_rules: {e}")

def energy_quality_rules(energy_df, report_data, weather_df):
    if not energy_df:
        logger.warning("DataFrame de entrada para energy_quality_rules es None. Saltando paso.")
        return
    try:
        logger.info("Aplicando reglas de calidad de datos al dataset de energía.")
        weather_df = weather_df.withColumnRenamed("dt_iso", "time")
        joined_df = energy_df.join(weather_df.select("time").distinct(), on="time", how="left")
        missing_matches_count = joined_df.filter(col("time").isNull()).count()
        matched_rows_count = energy_df.count() - missing_matches_count
        weather_df = weather_df.withColumnRenamed("time", "dt_iso")
        quality_checks = OrderedDict([
            ("price day ahead", energy_df.filter((col("price day ahead") >= 0)).count()),
            ("price actual", energy_df.filter((col("price actual") >= 0)).count()),
            ("integrity", matched_rows_count),
        ])
        logger.info(f"Resultados de calidad (energy): {spark.createDataFrame([Row(**quality_checks)])}")
        report_data.update(quality_checks)
        return report_data
    except Exception as e:
        logger.error(f"Error en energy_quality_rules: {e}")

if __name__ == '__main__':
    logger.info("Iniciando el script de informe de calidad de datos.")
    spark = SparkSession.builder.appName("DataQualityReport").getOrCreate()

    gcs_bucket_name = "naturgy-gcs"

    # --- ANÁLISIS DEL DATASET DEL CLIMA ---
    logger.info("--- Iniciando análisis del dataset del clima (weather_features.csv) ---")
    weather_quality_checks = {}
    weather_df = get_data(spark, f"gs://{gcs_bucket_name}/raw_data/weather_features.csv")
    valid_weather_schema = validate_weather_schema(weather_df)
    if valid_weather_schema:
        weather_quality_checks = count_duplicates(weather_df, ["dt_iso", "city_name"], weather_quality_checks)
        weather_quality_checks = count_nulls(weather_df, weather_quality_checks)
        weather_quality_checks = weather_quality_rules(weather_df, weather_quality_checks)
        weather_quality_checks.update({'total_rows': weather_df.count()})
        weather_quality_checks_df = spark.createDataFrame([Row(**OrderedDict(weather_quality_checks))])
        weather_quality_checks_df.coalesce(1).write.csv(f"gs://{gcs_bucket_name}/reports/weather_quality_checks.csv", header=True, mode="overwrite")

    # --- ANÁLISIS DEL DATASET DE ENERGÍA ---
    logger.info("--- Iniciando análisis del dataset de energía (energy_dataset.csv) ---")
    energy_quality_checks = {}
    energy_df = get_data(spark, f"gs://{gcs_bucket_name}/raw_data/energy_dataset.csv")
    valid_energy_schema = validate_energy_schema(energy_df)
    if valid_energy_schema:
        energy_quality_checks = count_duplicates(energy_df, ["time"], energy_quality_checks)
        energy_quality_checks = count_nulls(energy_df, energy_quality_checks)
        energy_quality_checks = energy_quality_rules(energy_df, energy_quality_checks, weather_df)
        energy_quality_checks.update({'total_rows': energy_df.count()})
        energy_quality_quality_checks_df = spark.createDataFrame([Row(**OrderedDict(energy_quality_checks))])
        energy_quality_quality_checks_df.coalesce(1).write.csv(f"gs://{gcs_bucket_name}/reports/energy_quality_checks.csv", header=True, mode="overwrite")

    logger.info("El script de informe de calidad de datos ha finalizado.")
    spark.stop()
