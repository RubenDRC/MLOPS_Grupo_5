import os
import mlflow
import pandas as pd
import pickle
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from mlflow.tracking import MlflowClient
from mlflow.models.signature import infer_signature

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def entrenar_y_evaluar_modelo():
    # Conexión a PostgreSQL
    engine = create_engine('postgresql+psycopg2://admin:admingrupo5@postgres-data:5432/data_db')
    df = pd.read_sql("SELECT * FROM clean_data", engine)

    if df.empty:
        raise ValueError("La tabla 'clean_data' está vacía.")
    print(f"Filas leídas: {len(df)}")

    # Procesar columna de fecha
    df['prev_sold_date'] = pd.to_datetime(df['prev_sold_date'], errors='coerce')
    df['prev_sold_year'] = df['prev_sold_date'].dt.year.fillna(0)
    df.drop(columns=['prev_sold_date'], inplace=True)

    # Separar features y target
    X = df.drop(columns=['price'])
    y = df['price'].astype(float)

    # Codificar columnas categóricas
    categorical_cols = X.select_dtypes(include='object').columns
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le

    # Guardar encoders como artefacto
    with open("/tmp/label_encoders.pkl", "wb") as f:
        pickle.dump(label_encoders, f)

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # MLflow config
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://minio:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("Proyecto_Final")

    param_grid = {
        "n_estimators": [50],
        "max_depth": [5, 10],
        "max_features": [5,10]
    }

    model = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=3)

    with mlflow.start_run(run_name="RandomForest_Housing") as run:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)

        mlflow.log_params(model.best_params_)
        mlflow.log_metric("mse", mse)

        # Agregar la firma del modelo
        signature = infer_signature(X_train, model.predict(X_train))
        mlflow.sklearn.log_model(model.best_estimator_, "model", signature=signature)

        mlflow.log_artifact("/tmp/label_encoders.pkl")

        print(f"MSE del nuevo modelo: {mse:.4f}")

        # Registro del modelo
        client = MlflowClient()
        model_name = "RandomForestModel_Move"

        new_model = mlflow.register_model(
            model_uri=f"runs:/{run.info.run_id}/model",
            name=model_name
        )

        try:
            prod_model = client.get_latest_versions(name=model_name, stages=["Production"])[0]
            prod_run = client.get_run(prod_model.run_id)
            prod_mse = float(prod_run.data.metrics["mse"])
            print(f"MSE modelo en producción: {prod_mse:.4f}")

            if mse < prod_mse:
                print("Promoviendo nuevo modelo (mejor MSE)")
                client.transition_model_version_stage(model_name, new_model.version, stage="Production", archive_existing_versions=True)
            else:
                print("Modelo actual mantiene mejor desempeño. El nuevo no será promovido.")
        except IndexError:
            print("No hay modelo en producción. Promoviendo el primero.")
            client.transition_model_version_stage(model_name, new_model.version, stage="Production")

with DAG(
    dag_id='train_model',
    default_args=default_args,
    description="Entrena modelo de regresión para housing y reinicia el ciclo de datos",
    schedule_interval=None,
    catchup=False
) as dag:

    entrenar = PythonOperator(
        task_id='entrenar_y_evaluar_modelo',
        python_callable=entrenar_y_evaluar_modelo
    )

    trigger_reset_data = TriggerDagRunOperator(
        task_id='trigger_drop_and_create_table',
        trigger_dag_id='drop_and_create_raw_table'
    )

    entrenar >> trigger_reset_data

