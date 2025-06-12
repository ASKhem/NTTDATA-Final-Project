# Plan de Proyecto Detallado - Naturgy

## Bloque 1: Infraestructura y Datos

- ✅ **1. Configuración del Entorno Cloud (GCP)**
  - ✅ Creación del bucket en Google Cloud Storage (GCS) para datos crudos y procesados.
  - ✅Configuración del Data Warehouse en Google BigQuery.
  - ✅ Creación de un clúster de Google Cloud Dataproc para la ejecución de Spark.
  - (Opcional) Configuración del entorno de desarrollo de IA en Vertex AI Workbench.

- ✅ **2. Selección set de datos y definición caso de uso**
  - ✅ Confirmación de los datasets (`energy_dataset.csv`, `weather_features.csv`).
  - ✅ Carga de los datasets crudos a la capa "raw" de GCS.

- ⬜️ **3. Documentación Inicial**
  - ⬜️ Creación del documento de modelo de datos ([`modelo_de_datos_ejemplo.md`](./0_BigData/Documentacion_BigData/modelo_de_datos_ejemplo..md)).
  - ⬜️ Creación del documento de plan de pruebas ([`plan_de_pruebas_ejemplo.md`](./0_BigData/Documentacion_BigData/plan_de_pruebas_ejemplo.md)) la parte teórica se podría encontrar en ([`plan_de_pruebas_teorico.md`](./0_BigData/Documentacion_BigData/plan_de_pruebas_teorico.md)).

- ✅ **4. Implementación Ingesta y Modelado (Pipeline ETL con Spark)**
  - ✅ Lectura de datos desde GCS.
  - ✅ Limpieza y transformación de los datasets (Capa Silver).
  - ✅ Aplicación de reglas de negocio y feature engineering básico (ej. conversión Kelvin a Celsius).
  - ✅ Escritura de los datos procesados en formato Parquet en la capa "silver" de GCS.
  - ✅ **Consumo de Capa Silver**:
    - ✅ Carga de los datos de GCS a BigQuery para consumo de BI.

- ⬜️ **5. Revisión y Ejecución de Calidad del Dato**
  - ⬜️ Implementación de las validaciones del [`plan_de_pruebas_ejemplo.md`](./0_BigData/Documentacion_BigData/plan_de_pruebas_ejemplo.md) en el script de Spark.
  - ⬜️ Generación de un reporte de calidad.
  - ✅ Ejecución formal del plan de pruebas documentando evidencias.

- ⬜️ **6. Implementación Dashboard Power BI**
  - ✅ Conexión de Power BI a la tabla final en BigQuery.
  - ✅ Modelado de datos en Power BI (medidas DAX, jerarquías).
  - ⬜️ Creación del cuadro de mando interactivo.

## Bloque 2: Inteligencia Artificial

- ⬜️ **7. Feature Engineering Avanzado (Local)**
  - ✅ Análisis Exploratorio de Datos (EDA) en un entorno local (ej. Jupyter Notebook).
  - ✅ Estudio de distribución, correlaciones, etc.
  - ✅ Creación de características específicas para el modelo (lags, medias móviles, indicadores de eventos climáticos).
  - ✅ Generación de la función/pipeline de preprocesamiento para asegurar la reproducibilidad.
  - ✅ División de datos en train/test de forma cronológica.

- ✅ **8. Entrenamiento y Evaluación de Modelos**
  - ✅ Experimentos comparando distintos modelos (mínimo 2, incluyendo una red neuronal).
  - ✅ Justificación de algoritmos e hiperparámetros.
  - ✅ Para la red neuronal: justificación de la arquitectura, función de activación y de error.
  - ✅ Comparativa de métricas (MAE, RMSE, R², etc.) en train y test.
  - ✅ Selección del mejor modelo.

## Bloque 3: Entrega Final

- ⬜️ **9. Consolidación de Entregables**
  - ⬜️ Organización de todo el código (ETL, IA), scripts, notebooks y artefactos (`.pbix`, modelo `.pkl`/`.h5`).

- ⬜️ **10. Generación de Documentación Final**
  - ⬜️ Informe de IA (máx. 3 páginas).
  - ⬜️ Documentación de diseño y pruebas actualizada.
  - ⬜️ Preparación de la presentación para la exposición (PPT).

- ⬜️ **11. Entrega y Exposición**
    - ⬜️ Entrega final del proyecto.
    - ⬜️ Exposición del trabajo.
