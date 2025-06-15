from logger_config import logger

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