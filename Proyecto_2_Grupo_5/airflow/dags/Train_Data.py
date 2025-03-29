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
from datetime import datetime

# Configuración de la conexión a MySQL
DB_CONFIG = {
    "host": "10.43.101.195",
    "user": "admin",
    "password": "admingrupo5",
    "database": "data_db",
    "port": 3308
}

# Función para obtener datos desde MySQL
def obtener_datos():
    try:
        # Conectar a MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Obtener datos del conjunto de datos 'covertype'
        cursor.execute("SELECT * FROM covertype")
        df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

        # Cerrar conexión a MySQL
        cursor.close()
        conn.close()

        print("Datos cargados exitosamente desde MySQL")
        return df

    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        raise

# Función para preparar los datos y dividirlos en entrenamiento y prueba
def preparar_datos(df):
    # Separar las características y la variable objetivo
    X = df.drop(columns=["Cover_Type"])  # Asumimos que 'Cover_Type' es la columna objetivo
    y = df["Cover_Type"]

    # Convertir la variable objetivo a valores numéricos con LabelEncoder
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    # Guardar el LabelEncoder para usarlo en la inferencia
    with open("/tmp/label_encoder.pkl", "wb") as f:
        pickle.dump(label_encoder, f)

    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test, "/tmp/label_encoder.pkl"

# Función para realizar el entrenamiento con GridSearchCV y registrar el modelo en MLflow
def entrenar_modelo(X_train, y_train, label_encoder_path):
    # Configuración de MLflow
    mlflow.set_tracking_uri("http://10.43.101.195:5000")
    mlflow.set_experiment("covertype_model_experiment")

    # Definir GridSearch con hiperparámetros
    param_grid = {
        "n_estimators": [25, 50, 75, 100],
        "max_depth": [4, 6, 8, 10],
        "max_features": [5, 10, 15]
    }

    # Crear modelo base
    rf = RandomForestClassifier(random_state=42)

    # Aplicar GridSearchCV para encontrar la mejor combinación
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, verbose=2)

    # Ejecutar el entrenamiento y registrar el modelo en MLflow
    with mlflow.start_run(run_name="rf_grid_search_covertype"):
        grid_search.fit(X_train, y_train)

        # Obtener mejor modelo
        best_model = grid_search.best_estimator_

        # Registrar hiperparámetros en MLflow
        mlflow.log_params(grid_search.best_params_)

        # Guardar el mejor modelo en MLflow
        mlflow.sklearn.log_model(best_model, "RandomForestModel")

        # Subir el LabelEncoder a MLflow
        mlflow.log_artifact(label_encoder_path)

        print(f"Mejor modelo encontrado con parámetros: {grid_search.best_params_}")

    print("Todos los experimentos fueron registrados en MLflow.")

# Definición del DAG
with DAG(
    dag_id='entrenamiento_random_forest_covertype_dag',
    start_date=datetime(2025, 3, 28),
    schedule_interval=None,  # Esto asegura que el DAG se ejecute manualmente
    catchup=False
) as dag:

    # Tarea para obtener los datos desde MySQL
    tarea_obtener_datos = PythonOperator(
        task_id='obtener_datos',
        python_callable=obtener_datos,
        dag=dag
    )

    # Tarea para preparar los datos (se ejecuta después de obtener los datos)
    tarea_preparar_datos = PythonOperator(
        task_id='preparar_datos',
        python_callable=preparar_datos,
        op_args=["{{ task_instance.xcom_pull(task_ids='obtener_datos') }}"],  # Usamos XCom para pasar los datos
        dag=dag
    )

    # Tarea para entrenar el modelo (se ejecuta después de preparar los datos)
    tarea_entrenar_modelo = PythonOperator(
        task_id='entrenar_modelo',
        python_callable=entrenar_modelo,
        op_args=["{{ task_instance.xcom_pull(task_ids='preparar_datos') }}"],  # Usamos XCom para pasar los datos
        dag=dag
    )

    # Definir la secuencia de ejecución de las tareas
    tarea_obtener_datos >> tarea_preparar_datos >> tarea_entrenar_modelo
