"""
DAG: Train_Model
Entrena un modelo SVM y lo guarda en /models/model_svm.pkl
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import pandas as pd
import mysql.connector
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score

default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

def train_svm_model():
    try:
        # Conexión a MySQL
        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="airflow"
        )
        cursor = conn.cursor()

        # Leer la tabla "penguins_clean"
        cursor.execute("SELECT * FROM penguins_clean")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df_clean = pd.DataFrame(rows, columns=cols)
        print(f"Filas leídas de 'penguins_clean': {df_clean.shape[0]}")

        cursor.close()

        # Features y target
        X = df_clean[['island', 'culmen_length_mm', 'culmen_depth_mm',
                      'flipper_length_mm', 'body_mass_g', 'sex']]
        y = df_clean['species']

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        numeric_cols = ['culmen_length_mm', 'culmen_depth_mm',
                        'flipper_length_mm', 'body_mass_g']
        cat_cols_island = ['island']
        cat_cols_sex = ['sex']

        transformer = ColumnTransformer([
            ('onehot_island', OneHotEncoder(drop='first'), cat_cols_island),
            ('onehot_sex', OneHotEncoder(drop='if_binary'), cat_cols_sex),
            ('scaler', StandardScaler(), numeric_cols)
        ], remainder='drop')

        pipeline_svm = Pipeline([
            ('preprocessor', transformer),
            ('classifier', SVC(random_state=42))
        ])

        # Entrenar
        pipeline_svm.fit(X_train, y_train)

        # Métricas
        y_pred = pipeline_svm.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print("== SVM (SVC) ==")
        print(f"Accuracy: {acc}")
        print(classification_report(y_test, y_pred))
        
        model_directory = "/data/models"
        os.makedirs(model_directory, exist_ok=True)
        
       # Guardar modelo en el volumen compartido
        model_path = os.path.join(model_directory, "model_svm.pkl")
        joblib.dump(pipeline_svm, model_path)
        print(f"Modelo guardado en {model_path}")

    except Exception as e:
        print("Error entrenando el modelo:", e)
        raise e
    finally:
        if conn:
            conn.close()
        print("Conexión cerrada.")

with DAG(
    dag_id='Train_Model',
    description='Entrena modelo SVM y lo guarda en /models',
    default_args=default_args,
    schedule_interval=None,  # se ejecuta solo por trigger
    catchup=False
) as dag:

    tarea_entrenar_svm = PythonOperator(
        task_id='train_svm_model',
        python_callable=train_svm_model
    )

    tarea_entrenar_svm
