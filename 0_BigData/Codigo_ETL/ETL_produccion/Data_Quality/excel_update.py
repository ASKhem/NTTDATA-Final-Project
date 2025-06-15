from pyspark.sql import SparkSession
from openpyxl import load_workbook
from io import BytesIO
import gcsfs
from google.cloud import storage

def generate_data_report(gcs_bucket_name):
    spark = SparkSession.builder.appName("DataReport").getOrCreate()

    ruta_excel_gcs = f"gs://{gcs_bucket_name}/reports/dq_report.xlsx"
    weather_report = f"gs://{gcs_bucket_name}/reports/weather_quality_checks.csv"
    energy_report = f"gs://{gcs_bucket_name}/reports/energy_quality_checks.csv"
    salida_excel_local = "dq_report_results.xlsx"
    salida_excel_gcs = f"reports/dq_report_results.xlsx"

    weather_hoja = 'Tiempo'
    col_weather, col_total_weather = 'D', 'E'
    energy_hoja = 'Energia'
    col_energy, col_total_energy = 'D', 'E'

    weather_df = spark.read.csv(weather_report, header=True, inferSchema=True)
    energy_df = spark.read.csv(energy_report, header=True, inferSchema=True)

    weather_data = weather_df.collect()[0]
    energy_data = energy_df.collect()[0]

    fs = gcsfs.GCSFileSystem()
    with fs.open(ruta_excel_gcs, 'rb') as f:
        in_mem_file = BytesIO(f.read())

    wb = load_workbook(in_mem_file)
    hoja_wth = wb[weather_hoja]
    hoja_eng = wb[energy_hoja]

    total_rows_weather = weather_df.collect()[0][-1]
    for i, valor in enumerate(weather_data, start=2):
        hoja_wth[f'{col_weather}{i}'] = valor
        if valor != '-':
            hoja_wth[f'{col_total_weather}{i}'] = total_rows_weather

    total_rows_energy = energy_df.collect()[0][-1]
    for i, valor in enumerate(energy_data, start=2):
        hoja_eng[f'{col_energy}{i}'] = valor
        if valor != '-':
            hoja_eng[f'{col_total_energy}{i}'] = total_rows_energy

    wb.save(salida_excel_local)

    client = storage.Client()
    bucket = client.bucket(gcs_bucket_name)
    blob = bucket.blob(salida_excel_gcs)
    blob.upload_from_filename(salida_excel_local)

    print("Reporte realizado con éxito y guardado en GCS.")
    spark.stop()
