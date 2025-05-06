import os
import mlflow
import pandas as pd
import pickle
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from mlflow.tracking import MlflowClient
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def entrenar_modelo():
    # Conexión a PostgreSQL
    engine = create_engine('postgresql+psycopg2://admin:admingrupo5@postgres-data:5432/data_db')
    df = pd.read_sql("SELECT * FROM diabetic_data_clean", engine)

    print(f"Filas leídas: {len(df)}")
    if df.empty:
        raise ValueError("La tabla 'diabetic_data_clean' está vacía.")

    # Preprocesamiento
    X = df.drop(columns=['readmitted'])
    y = df['readmitted']

    label_encoders = {}
    for col in X.columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le

    le_y = LabelEncoder()
    y = le_y.fit_transform(y)

    with open("/tmp/label_encoders.pkl", "wb") as f:
        pickle.dump(label_encoders, f)
    with open("/tmp/label_encoder_y.pkl", "wb") as f:
        pickle.dump(le_y, f)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # MLflow config
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://10.152.183.232:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'

    mlflow.set_tracking_uri("http://10.152.183.196:5000")
    mlflow.set_experiment("Proyecto_3_Diabetes_Readmission")

    param_grid = {
        "n_estimators": [50, 100],
        "max_depth": [5, 10],
        "max_features": [5, 10]
    }

    model = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3, verbose=2)

    with mlflow.start_run(run_name="rf_diabetes_all_varchar") as run:
        model.fit(X_train, y_train)

        mlflow.log_params(model.best_params_)
        mlflow.sklearn.log_model(model.best_estimator_, "RandomForestModel")
        mlflow.log_artifact("/tmp/label_encoders.pkl")
        mlflow.log_artifact("/tmp/label_encoder_y.pkl")

        print(f"Modelo entrenado con parámetros: {model.best_params_}")

        # Registrar y promover modelo manualmente
        client = MlflowClient()
        result = mlflow.register_model(
            model_uri=f"runs:/{run.info.run_id}/RandomForestModel",
            name="RandomForestModel"
        )

        client.transition_model_version_stage(
            name="RandomForestModel",
            version=result.version,
            stage="Production",
            archive_existing_versions=True
        )

with DAG(
    dag_id='Train_Model',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
) as dag:

    tarea_entrenar_modelo = PythonOperator(
        task_id='entrenar_modelo',
        python_callable=entrenar_modelo
    )

