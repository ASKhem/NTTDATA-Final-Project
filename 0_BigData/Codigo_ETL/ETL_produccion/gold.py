from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, year, month, dayofmonth, dayofweek, weekofyear, when, expr, lit,
    create_map, sha2, concat_ws, explode, sequence

)
from itertools import chain
from pyspark.sql.utils import AnalysisException
from py4j.protocol import Py4JJavaError
from logger_config import logger
import json

def create_spark_session():
    """Inicializa y devuelve una SparkSession."""
    logger.info("Creando SparkSession...")
    return SparkSession.builder.appName("SparkModeling").getOrCreate()

def read_data(spark):
    """
    Lee los datasets desde GCS.

    :param spark: sesión de spark creada
    :return weather_df, energy_df: DataFrames a modelar
    """
    logger.info("Leyendo datos desde GCS...")
    gcs_bucket_name = "naturgy-gcs"
    input_path_energy = f"gs://{gcs_bucket_name}/silver_data/energy_silver.parquet"
    input_path_weather = f"gs://{gcs_bucket_name}/silver_data/weather_features_silver.parquet"
    
    weather_df = spark.read.parquet(input_path_weather)
    weather_df = weather_df.toDF(*[col.strip() for col in weather_df.columns])

    energy_df = spark.read.parquet(input_path_energy)
    energy_df = energy_df.toDF(*[col.strip() for col in energy_df.columns])

    logger.info("Datos cargados correctamente.")
    return weather_df, energy_df






def process_dim_time(weather_df, spark):
    """
    Genera la tabla dimensión de tiempo.
    :param weather_df: DataFrame weather
    :return dim_time: dimensión del tiempo
    """
    time_bounds = weather_df.selectExpr(
    "min(time) as min_time",
    "max(time) as max_time"
    ).collect()[0]

    min_time = time_bounds["min_time"]
    max_time = time_bounds["max_time"]
    time_df = spark.createDataFrame(
        [(min_time, max_time)],
        ["start", "end"]
    ).select(
        explode(
            sequence(
                lit(min_time),
                lit(max_time),
                expr("interval 1 hour")
            )
        ).alias("time")
    )


    logger.info("Procesando tabla dim_time...")
    dim_time = time_df.withColumn("year", year("time")) \
        .withColumn("month", month("time")) \
        .withColumn("week_day", dayofweek("time")) \
        .withColumn("week_number_of_month", weekofyear("time")) \
        .withColumn("day", dayofmonth(col("time"))) \
        .withColumn("season", when(
            ((col("month") == 12) & (col("day") >= 21)) | ((col("month") == 1)) | ((col("month") == 2)) | ((col("month") == 3) & (col("day") <= 20)),
            "winter"
        ).when(
            ((col("month") == 3) & (col("day") >= 21)) | ((col("month") == 4)) | ((col("month") == 5)) | ((col("month") == 6) & (col("day") <= 20)),
            "spring"
        ).when(
            ((col("month") == 6) & (col("day") >= 21)) | ((col("month") == 7)) | ((col("month") == 8)) | ((col("month") == 9) & (col("day") <= 20)),
            "summer"
        ).otherwise("autumn")) \
        .withColumn("timeID", sha2(col("time").cast("string"), 256)) \
        .drop("day")

    desired_order_time = ["timeID", "time", "week_day", "week_number_of_month", "month", "season", "year"]
    dim_time = dim_time.select(*desired_order_time)
    return dim_time

def process_dim_city(weather_df):
    """
    Genera la tabla dimensión de ciudades.
    
    :param weather_df: DataFrame weather
    :return dim_city: dimensión de la ciudad
    """
    logger.info("Procesando tabla dim_city...")
    with open("external_data.json", "r") as file:
        data = json.load(file)

    city_data = data["city_data"]

    dim_city = weather_df.select("city_name").distinct().withColumn("cityID", sha2(col('city_name'), 256)) \
        .withColumn("latitude", lit("Unknown")) \
        .withColumn("longitude", lit("Unknown")) \
        .withColumn("province_population", lit("Unknown"))

    for city, attrs in city_data.items():
        dim_city = dim_city.withColumn("latitude", when(col("city_name") == city, lit(attrs["latitude"])).otherwise(col("latitude")))
        dim_city = dim_city.withColumn("longitude", when(col("city_name") == city, lit(attrs["longitude"])).otherwise(col("longitude")))
        dim_city = dim_city.withColumn("province_population", when(col("city_name") == city, lit(attrs["province_population"])).otherwise(col("province_population")))

    desired_order_city = ["cityID", "city_name", "latitude", "longitude", "province_population"]
    return dim_city.select(*desired_order_city)

def process_fact_weather(weather_df, dim_city, dim_time):
    """
    Genera la tabla de hechos del clima.
        :param weather_df: DataFrame weather
        :param dim_city: dimensión ciudad
        :return fact_weather: tabla de hechos del tiempo
    """
    logger.info("Procesando tabla fact_weather...")
    return weather_df.join(dim_city, ["city_name"], "left") \
        .join(dim_time.select("time", "timeID"), ["time"], "left") \
        .select(
            "timeID", "cityID", "temp", "temp_min", "temp_max", "pressure", "humidity",
            "wind_speed", "wind_deg", "rain_1h", "rain_3h", "snow_3h", "clouds_all",
            "weather_main", "weather_description") \
        .withColumn("weatherID", sha2(concat_ws("_", "timeID", "cityID"), 256))

def process_dim_energy_type(energy_df, spark):
    """
    Genera la tabla dimensión de tipos de energía.
        :param energy_df: DataFrame energy
        :param dim_energy_type: dimensión tipo de energía    
    """
    logger.info("Procesando tabla dim_energy_type...")
    energy_columns = [col for col in energy_df.columns if col.startswith("generation")]
    
    with open("external_data.json", "r") as file:
        data = json.load(file)

    renewable_energies = data["renewable_energies"]
    energy_types = [(col_name.replace("generation ", ""),
                    any(kw in col_name for kw in renewable_energies))
                    for col_name in energy_columns]
    dim_energy_type = spark.createDataFrame(energy_types, ["name", "is_renewable"]) \
        .withColumn("energyID", sha2(col("name").cast("string"), 256))

    return dim_energy_type.select("energyID", "name", "is_renewable")

def process_fact_energy_generation(energy_df, dim_energy_type):
    """
    Transforma datos de energía de ancho a largo (wide to long).

    :param energy_df: DataFrame energy
    :param dim_energy_type: dimensión tipo energía
    :return fact_energy_generation: tabla de hechos sobre la generación de energía    
    """
    logger.info("Procesando tabla fact_energy_generation...")
    energy_columns = [col for col in energy_df.columns if col.startswith("generation")]
    mappings = list(chain.from_iterable([(lit(k.replace("generation ", "")), col(k)) for k in energy_columns]))
    energy_long_df = energy_df.select("time", *energy_columns) \
        .select("time", create_map(*mappings).alias("generation_map")) \
        .select("time", explode("generation_map").alias("energy_name", "value"))
    
    energy_long_df = energy_long_df.withColumn("value", col("value").cast("int"))

    return energy_long_df.join(dim_energy_type, energy_long_df.energy_name == dim_energy_type.name, "left") \
        .select("time", "energyID", "value") \
        .withColumn("generationID", sha2(concat_ws("_", "time", "energyID"), 256))

def process_fact_energy_usage(energy_df):
    """
    Genera la tabla de uso de energía.
    :param energy_df: DataFrame energy
    :return fact_energy_usage: tabla de hechos sobre el consumo de energía    
    """
    logger.info("Procesando tabla fact_energy_usage...")
    return energy_df.selectExpr(
        "time",
        "`price actual` as price_actual",
        "`total load actual` as total_load_actual",
        "`generation waste` as generation_waste"
    ).withColumn("usageID", sha2(col("time").cast("string"), 256))

def process_fact_elec_forecast(energy_df):
    """
    Genera la tabla de predicción de electricidad.
    :param energy_df: DataFrame energy
    :return fact_elec_forecast: tabla de hechos sobre la predicción de generación de energía   
    """
    logger.info("Procesando tabla fact_elec_forecast...")
    return energy_df.selectExpr(
        "time",
        "`price day ahead` as price_forecast",
        "`total load forecast` as total_load_forecast"
    ).withColumn("elecForecastID", sha2(col("time").cast("string"), 256))

def process_fact_weather_forecast(energy_df):
    """
    Genera la tabla de predicción del clima.
    :param energy_df: DataFrame energy
    :return fact_weather_forecast: tabla de hechos sobre predicciones del tiempo
    """
    logger.info("Procesando tabla fact_weather_forecast...")
    return energy_df.selectExpr(
        "time",
        "`forecast solar day ahead` as forecast_solar_day_ahead",
        "`forecast wind onshore day ahead` as forecast_wind_onshore_day_ahead"
    ).withColumn("weatherForecastID", sha2(col("time").cast("string"), 256))

def join_with_time_id(fact_df, dim_time):
    """
    Join de una tabla de hechos con su timeID desde la dimensión de tiempo.
    :param fact_df: tabla de hechos
    :param dim_time: dimensión del tiempo
    :return tablas enlazadas
    """
    return fact_df.join(dim_time.select("time", "timeID"), on="time", how="left").drop("time")

def take_new_data(df, name, unique_key, spark):
    """
    Compara la nueva tabla con BigQuery para evitar duplicados.

    :param df: DataFrame a guardar
    :param name: nombre de la tabla
    :param unique_key: lista de columnas clave
    :return df: DataFrame a insertar
    """
    try:
        logger.info(f"Comprobando existencia de tabla: {name}")
        existing_table = spark.read \
            .format("bigquery") \
            .option("table", f"gold_data.{name}") \
            .load()
        return df.join(existing_table, on=unique_key, how="left_anti")
    except (AnalysisException, Py4JJavaError):
        logger.info(f"Tabla {name} no existe aún, se considerará toda la tabla como nueva.")
        return df

def save_table(df, name, unique_key, spark):
    """
    Guarda la tabla en BigQuery.
    :param df: Dataframe a insertar
    :param name: nombre de la tabla
    :param unique_key: columnas únicas de la tabla
    """
    logger.info(f"Guardando tabla: {name}")
    new_data = take_new_data(df, name, unique_key, spark)
    new_data.write \
        .format("bigquery") \
        .option("table", f"gold_data.{name}") \
        .option("temporaryGcsBucket", "temporal_bucket_trials") \
        .mode("append") \
        .save()

def main():
    spark = create_spark_session()
    weather_df, energy_df = read_data(spark)

    dim_time = process_dim_time(weather_df, spark)
    dim_city = process_dim_city(weather_df)
    fact_weather = process_fact_weather(weather_df, dim_city, dim_time)
    dim_energy_type = process_dim_energy_type(energy_df, spark)
    fact_energy_generation = process_fact_energy_generation(energy_df, dim_energy_type)
    fact_energy_usage = process_fact_energy_usage(energy_df)
    fact_elec_forecast = process_fact_elec_forecast(energy_df)
    fact_weather_forecast = process_fact_weather_forecast(energy_df)

    # fact_weather = join_with_time_id(fact_weather, dim_time)
    fact_energy_generation = join_with_time_id(fact_energy_generation, dim_time)
    fact_energy_usage = join_with_time_id(fact_energy_usage, dim_time)
    fact_elec_forecast = join_with_time_id(fact_elec_forecast, dim_time)
    fact_weather_forecast = join_with_time_id(fact_weather_forecast, dim_time)

    save_table(dim_time, "dim_time", ["time"], spark)
    save_table(dim_city, "dim_city", ["city_name"], spark)
    save_table(dim_energy_type, "dim_energy_type", ["name"], spark)
    save_table(fact_weather, "fact_weather", ["timeID", "cityID"], spark)
    save_table(fact_energy_usage, "fact_energy_usage", ["timeID"], spark)
    save_table(fact_weather_forecast, "fact_weather_forecast", ["timeID"], spark)
    save_table(fact_elec_forecast, "fact_elec_forecast", ["timeID"], spark)
    save_table(fact_energy_generation, "fact_energy_generation", ["timeID", "energyID"], spark)

    logger.info("Proceso finalizado.")
    spark.stop()

if __name__ == "__main__":
    main()

