import os
import mlflow
import mlflow.sklearn
import pandas as pd
import mysql.connector
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Configuración de la conexión a MySQL
DB_CONFIG = {
    "host": "10.43.101.195",
    "user": "admin",
    "password": "admingrupo5",
    "database": "data_db",
    "port": 3308
}

# Función para entrenar el modelo
def entrenar_modelo():
    # Conectar a MySQL
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Obtener datos de la tabla 'covertype_clean'
    cursor.execute("SELECT * FROM covertype_clean")
    df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

    # Cerrar conexión a MySQL
    cursor.close()
    conn.close()

    # Separar características y variable objetivo
    X = df.drop(columns=["Cover_Type"])
    y = df["Cover_Type"]

    # Convertir columnas categóricas
    columnas_categoricas = ['Wilderness_Area', 'Soil_Type']
    label_encoders = {}
    for col in columnas_categoricas:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le

    # Guardar codificadores
    with open("/tmp/label_encoders.pkl", "wb") as f:
        pickle.dump(label_encoders, f)

    # Convertir variable objetivo
    label_encoder_y = LabelEncoder()
    y = label_encoder_y.fit_transform(y)
    with open("/tmp/label_encoder_y.pkl", "wb") as f:
        pickle.dump(label_encoder_y, f)

    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Configuración de las variables de entorno de S3 y AWS
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = "http://10.43.101.195:9000"
    os.environ['AWS_ACCESS_KEY_ID'] = 'admin'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'supersecret'

    # Configuración de MLflow
    mlflow.set_tracking_uri("http://10.43.101.195:5000")
    mlflow.set_experiment("Proyecto_2_Grupo_5")

    # Autolog sin registrar firma (por compatibilidad con Pydantic v1)
    mlflow.sklearn.autolog(
        log_model_signatures=True,
        log_input_examples=True,
        registered_model_name="RandomForestModel"
    )

    # Grid search
    param_grid = {
        "n_estimators": [25, 50, 75, 100],
        "max_depth": [4, 6, 8, 10],
        "max_features": [5, 10, 15]
    }

    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, verbose=2)

    # Entrenamiento y logging
    with mlflow.start_run(run_name="rf_grid_search_covertype"):
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_

        mlflow.log_params(grid_search.best_params_)
        mlflow.sklearn.log_model(best_model, "RandomForestModel")        
        mlflow.log_artifact("/tmp/label_encoders.pkl")
        mlflow.log_artifact("/tmp/label_encoder_y.pkl")

        print(f"Mejor modelo encontrado con parámetros: {grid_search.best_params_}")
        print("Todos los experimentos fueron registrados en MLflow.")

# Definición del DAG
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

    tarea_entrenar_modelo

