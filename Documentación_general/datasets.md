# Documentación de Datasets

## Resumen General

Este proyecto contiene dos datasets principales relacionados con energía y clima en España. Los datos cubren el período desde 2015 hasta 2018 con registros horarios.

## 1. Energy Dataset (`energy_dataset.csv`)

### Información General
- **Número de filas**: 35,064 registros
- **Número de columnas**: 29 columnas
- **Período temporal**: 2015-01-01 a 2018-12-31 (datos horarios)
- **Región**: España
- **Frecuencia**: Horaria

### Descripción de Columnas

#### Columna Temporal
- **`time`**: Timestamp en formato ISO 8601 con zona horaria (+01:00)

#### Generación por Fuente de Energía (MW)
- **`generation biomass`**: Generación de energía a partir de biomasa
- **`generation fossil brown coal/lignite`**: Generación a partir de lignito/carbón pardo
- **`generation fossil coal-derived gas`**: Generación a partir de gas derivado del carbón
- **`generation fossil gas`**: Generación a partir de gas natural
- **`generation fossil hard coal`**: Generación a partir de carbón duro
- **`generation fossil oil`**: Generación a partir de petróleo
- **`generation fossil oil shale`**: Generación a partir de esquisto bituminoso
- **`generation fossil peat`**: Generación a partir de turba
- **`generation geothermal`**: Generación geotérmica
- **`generation hydro pumped storage aggregated`**: Almacenamiento hidroeléctrico por bombeo (agregado)
- **`generation hydro pumped storage consumption`**: Consumo de almacenamiento hidroeléctrico por bombeo
- **`generation hydro run-of-river and poundage`**: Generación hidroeléctrica de pasada y embalse
- **`generation hydro water reservoir`**: Generación hidroeléctrica de embalse
- **`generation marine`**: Generación marina (olas, mareas)
- **`generation nuclear`**: Generación nuclear
- **`generation other`**: Otras fuentes de generación
- **`generation other renewable`**: Otras fuentes renovables
- **`generation solar`**: Generación solar
- **`generation waste`**: Generación a partir de residuos
- **`generation wind offshore`**: Generación eólica marina
- **`generation wind onshore`**: Generación eólica terrestre

#### Pronósticos (MW)
- **`forecast solar day ahead`**: Pronóstico solar para el día siguiente
- **`forecast wind offshore eday ahead`**: Pronóstico eólico marino para el día siguiente
- **`forecast wind onshore day ahead`**: Pronóstico eólico terrestre para el día siguiente

#### Demanda y Carga (MW)
- **`total load forecast`**: Pronóstico de carga total
- **`total load actual`**: Carga total real

#### Precios (EUR/MWh)
- **`price day ahead`**: Precio del día siguiente
- **`price actual`**: Precio real

### Calidad de Datos
- **Completitud General**: 93.06%
- **Valores Faltantes**:
  - `generation hydro pumped storage aggregated`: 100.0% de valores faltantes.
  - `forecast wind offshore eday ahead`: 100.0% de valores faltantes.
  - Otras columnas como `total load actual`, `generation biomass`, y `generation fossil hard coal` tienen un pequeño porcentaje de datos faltantes (entre 0.05% y 0.1%).

### Columnas Interesantes para Target
1. **`total load actual`**: Variable objetivo principal para predicción de demanda
2. **`price actual`**: Variable objetivo para predicción de precios
3. **`generation solar`**: Para modelos de energía renovable
4. **`generation wind onshore`**: Para modelos de energía eólica
5. **`generation nuclear`**: Para análisis de energía base

---

## 2. Weather Features Dataset (`weather_features.csv`)

### Información General
- **Número de filas**: 178,396 registros
- **Número de columnas**: 17 columnas
- **Período temporal**: 2015-01-01 a 2018-12-31 (datos horarios)
- **Ubicaciones**: Madrid, Valencia, Bilbao, Barcelona y Sevilla
- **Frecuencia**: Horaria

### Descripción de Columnas

#### Información Temporal y Geográfica
- **`dt_iso`**: Timestamp en formato ISO 8601 con zona horaria
- **`city_name`**: Nombre de la ciudad

#### Variables Meteorológicas
- **`temp`**: Temperatura actual (Kelvin)
- **`temp_min`**: Temperatura mínima (Kelvin)
- **`temp_max`**: Temperatura máxima (Kelvin)
- **`pressure`**: Presión atmosférica (hPa)
- **`humidity`**: Humedad relativa (%)
- **`wind_speed`**: Velocidad del viento (m/s)
- **`wind_deg`**: Dirección del viento (grados)
- **`clouds_all`**: Cobertura de nubes (%)

#### Precipitación
- **`rain_1h`**: Lluvia en la última hora (mm)
- **`rain_3h`**: Lluvia en las últimas 3 horas (mm)
- **`snow_3h`**: Nieve en las últimas 3 horas (mm)

#### Información del Clima
- **`weather_id`**: ID del código meteorológico
- **`weather_main`**: Categoría principal del clima (clear, clouds, rain, etc.)
- **`weather_description`**: Descripción detallada del clima
- **`weather_icon`**: Código del icono meteorológico

### Calidad de Datos
- **Completitud General**: 100.00%
- **Valores Faltantes**: No hay valores faltantes en este dataset.

### Unidades de Medida
- **Temperatura**: Kelvin (para convertir a Celsius: K - 273.15)
- **Presión**: Hectopascales (hPa)
- **Humedad**: Porcentaje (%)
- **Viento**: Metros por segundo (m/s) y grados (°)
- **Precipitación**: Milímetros (mm)
- **Nubes**: Porcentaje de cobertura (%)

### Columnas Interesantes para Features
1. **`temp`**: Temperatura - factor clave para demanda energética
2. **`wind_speed`**: Velocidad del viento - correlacionada con generación eólica
3. **`clouds_all`**: Cobertura de nubes - afecta generación solar
4. **`humidity`**: Humedad - puede afectar demanda de climatización
5. **`pressure`**: Presión atmosférica - indicador de patrones meteorológicos
6. **`weather_main`**: Condiciones generales - útil para categorización

---

## Relación Entre Datasets

Ambos datasets están **100% sincronizados temporalmente** y pueden combinarse usando la columna de tiempo (`time` y `dt_iso`) para análisis integrados de:

1. **Correlación clima-energía**: Cómo las condiciones meteorológicas afectan la generación y demanda
2. **Predicción de demanda**: Usar variables meteorológicas para predecir consumo energético
3. **Optimización de renovables**: Correlacionar generación solar/eólica con condiciones climáticas
4. **Análisis de precios**: Entender cómo el clima influye en los precios energéticos

## Casos de Uso Sugeridos

1. **Predicción de Demanda Energética**: Usar `total load actual` como target y variables meteorológicas como features
2. **Predicción de Generación Renovable**: Predecir `generation solar` y `generation wind onshore` usando datos climáticos
3. **Análisis de Precios**: Modelar `price actual` considerando generación, demanda y condiciones meteorológicas
4. **Optimización de Mix Energético**: Analizar la complementariedad entre diferentes fuentes de energía
