from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from ...main import *

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 18),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_extraction',
    default_args=default_args,
    description='Extract data from LinkedIn, JobSpider, and PostJobFree',
    schedule_interval=timedelta(days=1),  # Adjust the schedule interval as needed
)

# Define tasks
extract_linkedin_task = PythonOperator(
    task_id='extract_linkedin_data',
    python_callable=extract_linkedin_data,
    dag=dag,
)

extract_jobspider_task = PythonOperator(
    task_id='extract_jobspider_data',
    python_callable=extract_jobspider_data,
    dag=dag,
)

extract_postjobfree_task = PythonOperator(
    task_id='extract_postjobfree_data',
    python_callable=extract_postjobfree_data,
    dag=dag,
)

store_data_task = PythonOperator(
    task_id='store_extracted_data',
    python_callable=store_data,
    op_args=['{{ task_instance.xcom_pull(task_ids="extract_linkedin_data") }}',
             '{{ task_instance.xcom_pull(task_ids="extract_jobspider_data") }}',
             '{{ task_instance.xcom_pull(task_ids="extract_postjobfree_data") }}'],
    dag=dag,
)

# Define task dependencies
[extract_linkedin_task, extract_jobspider_task, extract_postjobfree_task] >> store_data_task
