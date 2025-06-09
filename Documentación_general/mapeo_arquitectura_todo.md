# Guía de Mapeo: TODO vs Arquitectura del Proyecto
Basándome en la imagen de la arquitectura del proyecto y el archivo TODO.md, aquí tienes una guía detallada que mapea cada tarea del TODO con los componentes específicos de la arquitectura:

## 📊 Bloque 1: Infraestructura y Datos
### Tarea 3: Documentación Inicial
Ubicación en Arquitectura: Documentación transversal
Carpeta del Proyecto: 0_BigData/Documentacion_BigData/

- Modelo de datos → Define la estructura de datos que fluirá por todo el pipeline
- Plan de pruebas → Establece validaciones para cada etapa del ETL
### Tarea 4: Pipeline ETL con Spark
Ubicación en Arquitectura:

- Ingesta de datos: Cloud Functions (activación) → Cloud Scheduler
- Procesamiento: Cloud Dataproc (Spark) en la "Pipeline de datos (ETL)"
- Almacenamiento: Cloud Storage (capas raw/silver)
Carpeta del Proyecto: 0_BigData/Codigo_ETL/ETL_produccion/

Flujo específico en la arquitectura:

1.  **Lectura desde GCS**: El pipeline lee desde la capa `raw`.
2.  **Procesamiento Spark**: El clúster de `Cloud Dataproc` ejecuta la limpieza y transformación.
3.  **Escritura en Capa Silver**: El resultado se guarda como ficheros Parquet en la capa `silver` de GCS.
4.  **Consumo posterior**:
    *   **BI**: Un proceso posterior (ej. otra Cloud Function, Dataflow) carga los datos de la capa `silver` a `BigQuery`.
    *   **ML/EDA**: Los notebooks o pipelines de Vertex AI leen directamente de la capa `silver` para realizar la unión y el feature engineering.
### Tarea 5: Calidad del Dato
Ubicación en Arquitectura: Integrado en el pipeline de Spark (Cloud Dataproc)
Carpeta del Proyecto: 0_BigData/Scripts_Adicionales_BigData/

- Las validaciones se ejecutan dentro del procesamiento Spark
- Los reportes se almacenan en BigQuery para consulta
### Tarea 6: Dashboard Power BI
Ubicación en Arquitectura:

- Fuente de datos: BigQuery (DWH)
- Consumidor externo: Power BI (aparece como "Analista Stakeholder" en fuentes externas)
Carpeta del Proyecto: 0_BigData/Dashboard_PBI/

## 🤖 Bloque 2: Inteligencia Artificial
### Tarea 7: Feature Engineering Avanzado
Ubicación en Arquitectura:

- Datos fuente: BigQuery → Pipeline de ML/Data (Bajo Demanda)
- Procesamiento: Vertex AI Workbench (DATAPROC) - zona derecha
- Almacenamiento features: Vertex AI Feature Store
Carpeta del Proyecto: 1_InteligenciaArtificial/Notebook_IA/

### Tarea 8: Entrenamiento y Evaluación
Ubicación en Arquitectura:

- Entrenamiento: Vertex AI Workbench → Vertex AI Training
- Modelos: Vertex AI Model Registry
- Evaluación: Vertex AI Pipelines (flujo completo)
Carpetas del Proyecto:

- 1_InteligenciaArtificial/Scripts_IA/ (código de entrenamiento)
- 1_InteligenciaArtificial/Modelo_Entrenado/ (artefactos del modelo)
## 📋 Bloque 3: Entrega Final
### Tarea 9: Consolidación de Entregables
Ubicación en Arquitectura: Transversal - todos los componentes
Carpeta del Proyecto: Todas las carpetas del proyecto

### Tarea 10: Documentación Final
Ubicación en Arquitectura: Documentación del sistema completo
Carpeta del Proyecto: 1_InteligenciaArtificial/Informe_IA/

### Tarea 11: Entrega y Exposición
Ubicación en Arquitectura: Presentación del sistema completo
Carpeta del Proyecto: Raíz del proyecto + presentación

## 🔄 Flujo de Trabajo Recomendado
1. Documentación (Tarea 3) → Establece las bases
2. ETL Pipeline (Tarea 4) → Implementa el flujo principal de datos
3. Calidad de Datos (Tarea 5) → Valida el pipeline
4. Dashboard (Tarea 6) → Visualiza los datos procesados
5. Feature Engineering (Tarea 7) → Prepara datos para ML
6. Modelos IA (Tarea 8) → Desarrolla la inteligencia artificial
7. Consolidación (Tareas 9-11) → Finaliza y presenta
## 💡 Consejos de Implementación
- Paralelización: Las tareas 3, 4 y 7 pueden trabajarse en paralelo una vez completada la documentación inicial
- Dependencias críticas: Tarea 4 debe completarse antes de la 5 y 6; Tarea 7 antes de la 8
- Iteración: El desarrollo de IA (tareas 7-8) puede requerir volver a ajustar el ETL (tarea 4)
