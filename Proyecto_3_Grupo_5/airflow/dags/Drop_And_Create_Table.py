from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import psycopg2

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def create_table_postgres():
    conn = psycopg2.connect(
        host="postgres-data",
        database="data_db",
        user="admin",
        password="admingrupo5",
        port=5432
    )
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS diabetic_data;")
    cursor.execute("""
        CREATE TABLE diabetic_data (
            race VARCHAR,
            gender VARCHAR,
            age VARCHAR,
            weight VARCHAR,
            admission_type_id VARCHAR,
            discharge_disposition_id VARCHAR,
            admission_source_id VARCHAR,
            time_in_hospital VARCHAR,
            payer_code VARCHAR,
            medical_specialty VARCHAR,
            num_lab_procedures VARCHAR,
            num_procedures VARCHAR,
            num_medications VARCHAR,
            number_outpatient VARCHAR,
            number_emergency VARCHAR,
            number_inpatient VARCHAR,
            diag_1 VARCHAR,
            diag_2 VARCHAR,
            diag_3 VARCHAR,
            number_diagnoses VARCHAR,
            max_glu_serum VARCHAR,
            a1cresult VARCHAR,
            metformin VARCHAR,
            repaglinide VARCHAR,
            nateglinide VARCHAR,
            chlorpropamide VARCHAR,
            glimepiride VARCHAR,
            acetohexamide VARCHAR,
            glipizide VARCHAR,
            glyburide VARCHAR,
            tolbutamide VARCHAR,
            pioglitazone VARCHAR,
            rosiglitazone VARCHAR,
            acarbose VARCHAR,
            miglitol VARCHAR,
            troglitazone VARCHAR,
            tolazamide VARCHAR,
            examide VARCHAR,
            citoglipton VARCHAR,
            insulin VARCHAR,
            glyburide_metformin VARCHAR,
            glipizide_metformin VARCHAR,
            glimepiride_pioglitazone VARCHAR,
            metformin_rosiglitazone VARCHAR,
            metformin_pioglitazone VARCHAR,
            change VARCHAR,
            diabetesmed VARCHAR,
            readmitted VARCHAR
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabla 'diabetic_data' creada exitosamente con columnas en minúsculas y con guiones bajos.")

with DAG(
    dag_id='Drop_And_Create_Table',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    drop_create_table = PythonOperator(
        task_id='drop_create_table',
        python_callable=create_table_postgres
    )

    trigger_load_data = TriggerDagRunOperator(
        task_id='trigger_load_data',
        trigger_dag_id='Load_Data'
    )

    drop_create_table >> trigger_load_data

