from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, dayofmonth, dayofweek, weekofyear, when, expr, lit, create_map, sha2, concat_ws, AnalysisException
from itertools import chain
from logger_config import logger

spark = SparkSession.builder.appName("SparkModeling").getOrCreate()

gcs_bucket_name = "naturgy-gcs"
input_path_energy = f"gs://{gcs_bucket_name}/silver_data/energy_silver.parquet"
input_path_weather = f"gs://{gcs_bucket_name}/silver_data/weather_features_silver.parquet"

weather_df=spark.read.parquet(input_path_weather)
energy_df=spark.read.parquet(input_path_energy)

# ============================
# DIM_time
# ============================
dim_time = weather_df.select("time").withColumn("year", year("time")) \
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
    .withColumn("timeID", sha2(col("time").cast("string"), 256))

dim_time=dim_time.drop('day')

#Ordenación columnas
desired_order_time = ["timeID", "time", "week_day", "week_number_of_month", "month", "season", "year"]
dim_time = dim_time.select(*desired_order_time)


# ============================
# DIM_city
# ============================
city_data = {
    "Madrid": {"latitude": 40.414852, "longitude": -3.69765, "province_population": 6825000},
    "Barcelona": {"latitude": 41.38594, "longitude": 2.17451, "province_population": 5877672},
    "Valencia": {"latitude": 39.47192, "longitude": -0.37593, "province_population": 2710808},
    "Seville": {"latitude": 37.38995, "longitude": -5.98578, "province_population":  1968624 },
    "Bilbao": {"latitude": 43.26292, "longitude": -2.93623, "province_population": 1153000},
}

dim_city = weather_df.select("city_name").distinct().withColumn("cityID", sha2(col('city_name'), 256))


dim_city = dim_city.withColumn("latitude", lit("Unknown")) \
                         .withColumn("longitude", lit("Unknown")) \
                         .withColumn("province_population", lit("Unknown"))

for city, attrs in city_data.items():
    dim_city = dim_city.withColumn("latitude",
        when(col("city_name") == city, lit(attrs["latitude"])).otherwise(col("latitude")))

    dim_city = dim_city.withColumn("longitude",
        when(col("city_name") == city, lit(attrs["longitude"])).otherwise(col("longitude")))

    dim_city = dim_city.withColumn("province_population",
        when(col("city_name") == city, lit(attrs["province_population"])).otherwise(col("province_population")))

#Ordenación columnas
desired_order_city = ["cityID", "city_name", "latitude", "longitude", "province_population"]
dim_city = dim_city.select(*desired_order_city)

# ============================
# FACT_weather -> no entiendo qué está pasando con los joins
# ============================
# Unimos con city para tener cityID
fact_weather = weather_df.join(dim_city, ["city_name"], "left") \
    .selectExpr( "time", "cityID",
                "temp", "temp_min", "temp_max", "pressure", "humidity", "wind_speed", "wind_deg",
                "rain_1h", "rain_3h", "snow_3h", "clouds_all",
                "weather_main", "weather_description") \
    .withColumn("weatherID", sha2(concat_ws("_", "time", "cityID"), 256))


# ============================
# DIM_energy_type
# ============================
# Extraemos los tipos de energía de las columnas de generación
energy_columns = [col for col in energy_df.columns if col.startswith("generation")]
energy_types = [(col_name.replace("generation ", ""),
                True if any(kw in col_name for kw in ["biomass", "geothermal", "renewable", "hydro", "marine", "solar", "wind" ]) else False)
                for col_name in energy_columns]

dim_energy_type = spark.createDataFrame(energy_types, ["name", "is_renewable"]) \
    .withColumn("energyID", sha2(col("name").cast("string"), 256))

#Ordenación columnas
desired_order_type = ["energyID", "name", "is_renewable"]
dim_energy_type = dim_energy_type.select(*desired_order_type)

# ============================
# FACT_energy_generation
# ============================

mappings = list(chain.from_iterable([(lit(k.replace("generation ", "")), col(k)) for k in energy_columns]))

# aquí cambio de estilo 'wide' a 'long
energy_long_df = energy_df.select("time", *energy_columns) \
    .select("time", create_map(*mappings).alias("generation_map")) \
    .selectExpr("time", "explode(generation_map) as (energy_name, value)")

fact_energy_generation = energy_long_df.join(dim_energy_type, energy_long_df.energy_name == dim_energy_type.name, "left") \
    .selectExpr( "time", "energyID", "value") \
    .withColumn("generationID", sha2(concat_ws("_", "time", "energyID"), 256))

#Ordenación columnas
desired_order_generation = ["generationID", "time", "energyID", "value"]
fact_energy_generation = fact_energy_generation.select(*desired_order_generation)


# ============================
# FACT_energy_usage
# ============================
fact_energy_usage = energy_df.selectExpr(
    "time",
    "`price actual` as price_actual",
    "`total load actual` as total_load_actual",
    "`generation waste` as generation_waste"
) \
.withColumn("usageID", sha2(col("time").cast("string"), 256))


# ============================
# FACT_electricity_forecast
# ============================
fact_elec_forecast = energy_df.selectExpr(
    "time",
    "`price day ahead` as price_forecast",
    "`total load forecast` as total_load_forecast"
) \
.withColumn("elecForecastID", sha2(col("time").cast("string"), 256))


# ============================
# FACT_weather_forecast
# ============================
fact_weather_forecast = energy_df.selectExpr(
    "time",
    "`forecast solar day ahead` as forecast_solar_day_ahead",
    "`forecast wind onshore day ahead` as forecast_wind_onshore_day_ahead"
) \
.withColumn("weatherForecastID", sha2(col("time").cast("string"), 256))


# ============================
# JOINS con dim_time
# ============================
fact_weather = fact_weather.join(dim_time.select("time", "timeID"), on="time", how="left") \
    .drop("time")
fact_energy_generation = fact_energy_generation.join(dim_time.select("time", "timeID"), on="time", how="left") \
    .drop("time")
fact_energy_usage = fact_energy_usage.join(dim_time.select("time", "timeID"), on="time", how="left") \
    .drop("time")
fact_elec_forecast = fact_elec_forecast.join(dim_time.select("time", "timeID"), on="time", how="left") \
    .drop("time")
fact_weather_forecast = fact_weather_forecast.join(dim_time.select("time", "timeID"), on="time", how="left") \
    .drop("time")


def take_new_data(df, name, unique_key):
    try:
        existing_table = spark.read \
            .format("bigquery") \
            .option("table", f"naturgy-gcs.naturgy_data.{name}") \
            .load()
        table_exists = True
    except AnalysisException:
        table_exists = False

    if table_exists:
        new_data = df.join(existing_table, on=unique_key, how="left_anti")
    else:
        new_data = df 
    return new_data

def save_table(df, name, unique_key):
    new_data=take_new_data(df, name, unique_key)
    new_data.write \
    .format("bigquery") \
    .option("table", f"naturgy-gcp.naturgy_data.{name}") \
    .option("temporaryGcsBucket", "temporal_bucket_trials") \
    .mode("append") \
    .save()

save_table(dim_time, "dim_time", ["time"])
save_table(dim_city, "dim_city", ["city_name"])
save_table(dim_energy_type, "dim_energy_type", ["name"])
save_table(fact_weather, "fact_weather", ["time"])
save_table(fact_energy_usage, "fact_energy_usage", ["time", "energyID"])
save_table(fact_weather_forecast, "fact_weather_forecast", ["time", "cityID"])
save_table(fact_elec_forecast, "fact_elec_forecast", ["time"])
save_table(fact_energy_generation, "fact_energy_generation", ["time"])

spark.stop()
