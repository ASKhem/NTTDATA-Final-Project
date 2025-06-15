from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2025, 6, 9),
    'retries': 1
}

with DAG('etl-pipeline', 
         default_args=default_args, 
         schedule_interval='@monthly', 
         catchup=False) as dag:

    run_data_quality = BashOperator(
        task_id='run_data_quality',
        bash_command='gcloud dataproc jobs submit pyspark gs://naturgy-gcs/scripts/data_quality.py --cluster=etl-naturgy --region=europe-southwest1 --py-files gs://naturgy-gcs/scripts/logger_config.py,gs://naturgy-gcs/scripts/excel_update.py,gs://naturgy-gcs/scripts/data_utils.py'
    )

    run_silver = BashOperator(
        task_id='run_silver',
        bash_command='gcloud dataproc jobs submit pyspark gs://naturgy-gcs/scripts/silver.py --cluster=etl-naturgy --region=europe-southwest1 --py-files gs://naturgy-gcs/scripts/logger_config.py,gs://naturgy-gcs/scripts/excel_update.py,gs://naturgy-gcs/scripts/data_utils.py'
    )

    run_gold = BashOperator(
        task_id='run_gold',
        bash_command='gcloud dataproc jobs submit pyspark gs://naturgy-gcs/scripts/gold.py --cluster=etl-naturgy --region=europe-southwest1 --py-files gs://naturgy-gcs/scripts/logger_config.py --files gs://naturgy-gcs/scripts/external_data.json'
    )

    run_data_quality >> run_silver >> run_gold
