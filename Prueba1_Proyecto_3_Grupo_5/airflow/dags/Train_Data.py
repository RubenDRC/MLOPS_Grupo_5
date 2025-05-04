# Train_Model.py
import os, pickle, psycopg2, pandas as pd, mlflow, mlflow.sklearn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

PG = {
    "host": "postgres-data",
    "port": 5432,
    "dbname": "data_db",
    "user": "admin",
    "password": "admingrupo5",
}

default_args = {"start_date": days_ago(1), "retries": 1}

def train():
    conn = psycopg2.connect(**PG)
    df   = pd.read_sql("SELECT * FROM diabetic_clean", conn)
    conn.close()

    y = df.pop("target")
    X = df.copy()

    encoders = {}
    for col in X.select_dtypes(include="object"):
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
    with open("/tmp/encoders.pkl", "wb") as f:
        pickle.dump(encoders, f)

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2,
                                              random_state=42, stratify=y)

    os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"
    os.environ["AWS_ACCESS_KEY_ID"]      = "admin"
    os.environ["AWS_SECRET_ACCESS_KEY"]  = "supersecret"

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("Proyecto_3_Diabetes_Readmission")
    mlflow.sklearn.autolog(
        log_model_signatures=True, log_input_examples=True,
        registered_model_name="RandomForest_Diabetes"
    )

    grid = GridSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        param_grid={"n_estimators":[100,200,300],
                    "max_depth":[10,20,30],
                    "max_features":["sqrt","log2"]},
        cv=3, verbose=2
    )

    with mlflow.start_run(run_name="rf_grid_diabetes"):
        grid.fit(X_tr, y_tr)
        best = grid.best_estimator_
        mlflow.log_params(grid.best_params_)
        mlflow.sklearn.log_model(best, "RandomForest_Diabetes")
        mlflow.log_artifact("/tmp/encoders.pkl")
        print("🏆 Mejor modelo:", grid.best_params_)

with DAG(
    dag_id="Train_Model",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["train","mlflow"]
) as dag:

    train_task = PythonOperator(task_id="train_model", python_callable=train)
