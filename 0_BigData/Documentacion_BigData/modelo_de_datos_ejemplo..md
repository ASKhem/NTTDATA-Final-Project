# Modelo de Datos del Proyecto Naturgy (ejemplo)

Este documento describe la estructura y el esquema de los datos a lo largo de las diferentes fases del pipeline de datos, desde la ingesta inicial hasta el almacenamiento final para análisis.

## 1. Modelo de Datos Crudo (Raw)

Los datos crudos son una copia exacta de los ficheros originales, almacenados en la capa "raw" de Google Cloud Storage.

### a. `energy_dataset.csv`

| Nombre de Columna | Tipo de Dato | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `time` | String | Timestamp en formato UTC. | `2015-01-01 00:00:00+01:00` |
| `generation biomass`| Float | Generación de energía (MW) a partir de biomasa. | `449.0` |
| `generation fossil brown coal/lignite` | Float | Generación de energía (MW) a partir de carbón/lignito. | `520.0` |
| `generation fossil gas` | Float | Generación de energía (MW) a partir de gas fósil. | `4844.0` |
| `generation fossil hard coal` | Float | Generación de energía (MW) a partir de carbón duro. | `4821.0` |
| `generation fossil oil` | Float | Generación de energía (MW) a partir de petróleo. | `335.0` |
| `generation hydro pumped storage consumption` | Float | Consumo de almacenamiento por bombeo hidroeléctrico. | `499.0` |
| `generation hydro run-of-river and poundage` | Float | Generación hidroeléctrica de pasada y embalse. | `1057.0` |
| `generation hydro water reservoir` | Float | Generación de energía de embalses de agua. | `2960.0` |
| `generation nuclear` | Float | Generación de energía nuclear. | `7096.0` |
| `generation other` | Float | Generación de otras fuentes. | `43.0` |
| `generation other renewable` | Float | Generación de otras renovables. | `73.0` |
| `generation solar` | Float | Generación de energía solar. | `49.0` |
| `generation waste` | Float | Generación a partir de residuos. | `252.0` |
| `generation wind onshore` | Float | Generación eólica terrestre. | `6378.0` |
| `forecast solar day ahead` | Float | Previsión de generación solar para el día siguiente. | `17.0` |
| `forecast wind onshore day ahead` | Float | Previsión de generación eólica para el día siguiente. | `6436.0` |
| `total load forecast` | Float | Previsión de la carga total. | `26118.0` |
| `total load actual` | Float | Carga total real. | `25385.0` |
| `price day ahead` | Float | Precio del mercado para el día siguiente (€/MWh). | `50.1` |
| `price actual` | Float | Precio real del mercado spot (€/MWh). | `65.41` |

### b. `weather_features.csv`

| Nombre de Columna | Tipo de Dato | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `dt_iso` | String | Timestamp en formato UTC con información de la ciudad. | `2015-01-01 00:00:00+01:00 UTC` |
| `city_name` | String | Nombre de la ciudad. | `Valencia` |
| `temp` | Float | Temperatura en Kelvin. | `270.475` |
| `temp_min` | Float | Temperatura mínima en Kelvin. | `270.475` |
| `temp_max` | Float | Temperatura máxima en Kelvin. | `270.475` |
| `pressure` | Integer | Presión atmosférica en hPa. | `1001` |
| `humidity` | Integer | Humedad en %. | `77` |
| `wind_speed` | Integer | Velocidad del viento en m/s. | `1` |
| `wind_deg` | Integer | Dirección del viento en grados. | `62` |
| `rain_1h` | Float | Volumen de lluvia en la última hora (mm). | `0.0` |
| `rain_3h` | Float | Volumen de lluvia en las últimas 3 horas (mm). | `0.0` |
| `snow_3h` | Float | Volumen de nieve en las últimas 3 horas (mm). | `0.0` |
| `clouds_all` | Integer | Nubosidad en %. | `0` |
| `weather_id` | Integer | ID de la condición climática. | `800` |
| `weather_main` | String | Descripción principal del clima. | `Clear` |
| `weather_description` | String | Descripción detallada del clima. | `clear sky` |
| `weather_icon` | String | ID del icono del clima. | `01n` |

## 2. Modelo de Datos Procesado (Processed)

Este modelo describe la tabla final que se almacenará en Google BigQuery después del proceso ETL con Spark.

**Nombre de la tabla:** `energy_weather_data`

| Nombre de Columna | Tipo de Dato | Descripción | Origen / Transformación |
| :--- | :--- | :--- | :--- |
| `timestamp` | Timestamp | Fecha y hora de la medición. | `time` (convertido a Timestamp) |
| `city` | String | Ciudad de la medición climática. | `city_name` |
| `temp_celsius` | Float | Temperatura en grados Celsius. | `temp` (convertido de Kelvin) |
| `humidity` | Integer | Humedad en %. | `humidity` |
| `wind_speed` | Integer | Velocidad del viento en m/s. | `wind_speed` |
| `clouds` | Integer | Nubosidad en %. | `clouds_all` |
| `weather_condition` | String | Descripción principal del clima. | `weather_main` |
| `total_load_actual` | Float | Carga total real (MW). | `total_load_actual` |
| `total_load_forecast` | Float | Previsión de carga total (MW). | `total_load_forecast` |
| `price_actual` | Float | Precio real del mercado (€/MWh). | `price_actual` |
| `price_day_ahead` | Float | Precio del mercado para el día siguiente (€/MWh). | `price_day_ahead` |
| `generation_solar` | Float | Generación solar (MW). | `generation solar` |
| `generation_wind` | Float | Generación eólica (MW). | `generation wind onshore` |
| `generation_hydro` | Float | Generación hidroeléctrica total (MW). | Suma de `generation hydro...` |
| `generation_fossil` | Float | Generación fósil total (MW). | Suma de `generation fossil...` |
| `generation_renewable`| Float | Generación renovable total (MW). | Suma de `biomass`, `other renewable`, `solar`, `wind`, `hydro` |
| `load_forecast_error`| Float | Error de predicción de carga (MW). | `total_load_actual` - `total_load_forecast` |
| `year` | Integer | Año de la medición. | Extraído de `timestamp` |
| `month` | Integer | Mes de la medición. | Extraído de `timestamp` |
| `day_of_week` | Integer | Día de la semana. | Extraído de `timestamp` |
| `hour` | Integer | Hora del día. | Extraído de `timestamp` |

## 3. Modelo de Datos para Análisis (Analytics)

El modelo para análisis será la misma tabla `energy_weather_data` almacenada en BigQuery. Esta tabla está diseñada para ser consultada directamente por Power BI para la creación de dashboards y por los notebooks de Jupyter para el entrenamiento de modelos de Machine Learning.
