# Load_Data.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

import os, requests, boto3, botocore, pandas as pd, psycopg2
from psycopg2.extras import execute_values

S3_EP   = "http://minio:9000"
BKT     = "datasets"
CSV_OBJ = "diabetic_data.csv"
CHUNK   = 15_000

AWS_KEY = "admin"
AWS_SEC = "supersecret"

PG = {
    "host": "postgres-data",
    "port": 5432,
    "dbname": "data_db",
    "user": "admin",
    "password": "admingrupo5",
}

default_args = {"start_date": days_ago(1), "retries": 1}

def _s3():
    return boto3.client(
        "s3", endpoint_url=S3_EP,
        aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SEC
    )

def download_if_needed():
    try:
        _s3().head_object(Bucket=BKT, Key=CSV_OBJ)
        print("✔️  Dataset ya existe en MinIO.")
        return
    except botocore.exceptions.ClientError:
        pass

    url = "https://archive.ics.uci.edu/static/public/296/diabetic_data.csv"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    _s3().put_object(Bucket=BKT, Key=CSV_OBJ, Body=resp.content)
    print(" Dataset descargado y subido a MinIO.")

def ingest_to_postgres():
    storage_opts = {
        "client_kwargs": {"endpoint_url": S3_EP},
        "key": AWS_KEY, "secret": AWS_SEC
    }
    uri = f"s3://{BKT}/{CSV_OBJ}"

    conn = psycopg2.connect(**PG)
    cur  = conn.cursor()
    batch = 0

    for chunk in pd.read_csv(uri, chunksize=CHUNK, storage_options=storage_opts):
        batch += 1
        chunk.columns = [c.replace("-", "_") for c in chunk.columns]
        values = [tuple(row) for row in chunk.itertuples(index=False, name=None)]
        cols   = ','.join(f'"{c}"' for c in chunk.columns)
        execute_values(
            cur,
            f"INSERT INTO diabetic_raw ({cols}) VALUES %s",
            values,
            page_size=1000
        )
        conn.commit()
        print(f" Lote {batch}: {len(values)} filas.")

    cur.close(); conn.close()
    print(" Ingesta terminada.")

with DAG(
    dag_id="Load_Data",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["ingesta","postgres","minio"]
) as dag:

    download = PythonOperator(task_id="download_dataset", python_callable=download_if_needed)
    ingest   = PythonOperator(task_id="ingest_to_postgres", python_callable=ingest_to_postgres)
    trigger  = TriggerDagRunOperator(
        task_id="trigger_preprocess",
        trigger_dag_id="Preprocess_Data",
        wait_for_completion=False
    )

    download >> ingest >> trigger
