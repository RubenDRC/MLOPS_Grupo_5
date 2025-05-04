# Drop_And_Create_Table.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from airflow.exceptions import AirflowException
import psycopg2, os

PG = {
    "host": "postgres-data",
    "port": 5432,
    "dbname": "data_db",
    "user": "admin",
    "password": "admingrupo5",
}

default_args = {"start_date": days_ago(1), "retries": 1}

def _connect():
    return psycopg2.connect(**PG)

def eliminar_tablas():
    with _connect() as conn, conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS diabetic_clean;")
        cur.execute("DROP TABLE IF EXISTS diabetic_raw;")
    print("  Tablas antiguas eliminadas.")

def crear_tabla_raw():
    ddl = """
    CREATE TABLE diabetic_raw (
        encounter_id              BIGINT PRIMARY KEY,
        patient_nbr               BIGINT,
        race                      VARCHAR(50),
        gender                    VARCHAR(10),
        age                       VARCHAR(20),
        weight                    VARCHAR(20),
        admission_type_id         SMALLINT,
        discharge_disposition_id  SMALLINT,
        admission_source_id       SMALLINT,
        time_in_hospital          SMALLINT,
        payer_code                VARCHAR(30),
        medical_specialty         VARCHAR(100),
        num_lab_procedures        SMALLINT,
        num_procedures            SMALLINT,
        num_medications           SMALLINT,
        number_outpatient         SMALLINT,
        number_emergency          SMALLINT,
        number_inpatient          SMALLINT,
        diag_1                    VARCHAR(10),
        diag_2                    VARCHAR(10),
        diag_3                    VARCHAR(10),
        number_diagnoses          SMALLINT,
        max_glu_serum             VARCHAR(20),
        A1Cresult                 VARCHAR(20),
        metformin                 VARCHAR(10),
        repaglinide               VARCHAR(10),
        nateglinide               VARCHAR(10),
        chlorpropamide            VARCHAR(10),
        glimepiride               VARCHAR(10),
        acetohexamide             VARCHAR(10),
        glipizide                 VARCHAR(10),
        glyburide                 VARCHAR(10),
        tolbutamide               VARCHAR(10),
        pioglitazone              VARCHAR(10),
        rosiglitazone             VARCHAR(10),
        acarbose                  VARCHAR(10),
        miglitol                  VARCHAR(10),
        troglitazone              VARCHAR(10),
        tolazamide                VARCHAR(10),
        examide                   VARCHAR(10),
        citoglipton               VARCHAR(10),
        insulin                   VARCHAR(10),
        glyburide_metformin       VARCHAR(10),
        glipizide_metformin       VARCHAR(10),
        glimepiride_pioglitazone  VARCHAR(10),
        metformin_rosiglitazone   VARCHAR(10),
        metformin_pioglitazone    VARCHAR(10),
        change_flag               VARCHAR(5),
        diabetesMed               VARCHAR(5),
        readmitted                VARCHAR(10)
    );
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(ddl)
    print(" Tabla 'diabetic_raw' creada.")

with DAG(
    dag_id="Drop_And_Create_Table",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["postgres","setup"]
) as dag:

    drop = PythonOperator(task_id="eliminar_tablas", python_callable=eliminar_tablas)
    create = PythonOperator(task_id="crear_tabla_raw", python_callable=crear_tabla_raw)
    trigger = TriggerDagRunOperator(
        task_id="lanzar_load_data",
        trigger_dag_id="Load_Data",
        wait_for_completion=False
    )

    drop >> create >> trigger
