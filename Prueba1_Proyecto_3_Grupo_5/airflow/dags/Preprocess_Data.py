# Preprocess_Data.py
import psycopg2, pandas as pd, boto3, os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from psycopg2.extras import execute_values

S3_EP   = "http://minio:9000"
BKT     = "datasets"
IDS_OBJ = "IDS_mapping.csv"
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
    return boto3.client("s3", endpoint_url=S3_EP,
                        aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SEC)

def preprocess():
    # ---- leer raw desde Postgres
    conn = psycopg2.connect(**PG)
    df = pd.read_sql("SELECT * FROM diabetic_raw", conn)

    # ---- limpiar
    df.replace("?", pd.NA, inplace=True)

    # ---- mapping IDS
    try:
        obj = _s3().get_object(Bucket=BKT, Key=IDS_OBJ)["Body"].read()
    except Exception:
        obj = requests.get(
            "https://archive.ics.uci.edu/static/public/296/IDS_mapping.csv"
        ).content
        _s3().put_object(Bucket=BKT, Key=IDS_OBJ, Body=obj)

    mapping = pd.read_csv(pd.compat.StringIO(obj.decode()))
    for campo in ["admission_type_id", "discharge_disposition_id", "admission_source_id"]:
        m = mapping[mapping["field"] == campo][["code", "description"]]
        df = df.merge(m, how="left", left_on=campo, right_on="code")\
               .drop(columns=[campo, "code"])\
               .rename(columns={"description": f"{campo}_desc"})

    df["target"] = (df["readmitted"] == "<30").astype(int)
    df.drop(columns=["weight"], inplace=True)

    # ---- guardar tabla clean
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS diabetic_clean;")
        cols_sql = ", ".join(f'"{c}" TEXT' for c in df.columns if c != "target")
        cur.execute(f"CREATE TABLE diabetic_clean ({cols_sql}, target SMALLINT);")
        execute_values(
            cur,
            f'INSERT INTO diabetic_clean ({",".join(df.columns)}) VALUES %s',
            df.values.tolist(), page_size=2000
        )
        conn.commit()
    conn.close()
    print(f"🧹 Preprocesamiento OK ({len(df)} filas).")

with DAG(
    dag_id="Preprocess_Data",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["preprocess","postgres"]
) as dag:

    proc = PythonOperator(task_id="preprocess", python_callable=preprocess)
    trigger = TriggerDagRunOperator(
        task_id="trigger_train",
        trigger_dag_id="Train_Model",
        wait_for_completion=False
    )
    proc >> trigger
