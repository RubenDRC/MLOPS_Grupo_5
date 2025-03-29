import mysql.connector
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.exceptions import AirflowException

# Definición de la configuración de la base de datos
DB_CONFIG = {
    "host": "10.43.101.195",
    "user": "admin",
    "password": "admingrupo5",
    "database": "data_db",
    "port": 3308
}

# Función de preprocesamiento de datos
def preprocesar_datos():
    try:
        # Conectar a MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Extraer los datos de la tabla original
        cursor.execute("SELECT * FROM covertype")
        df = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

        # Preprocesamiento: eliminar valores nulos
        df.dropna(inplace=True)

        # Eliminar la tabla si ya existe
        cursor.execute("DROP TABLE IF EXISTS covertype_clean")

        # Crear la tabla limpia
        cursor.execute('''
            CREATE TABLE covertype_clean (
                id INT AUTO_INCREMENT PRIMARY KEY,
                elevation INT,
                aspect INT,
                slope INT,
                horizontal_distance_to_hydrology INT,
                vertical_distance_to_hydrology INT,
                horizontal_distance_to_roadways INT,
                hillshade_9am INT,
                hillshade_noon INT,
                hillshade_3pm INT,
                horizontal_distance_to_fire_points INT,
                horizontal_distance_to_wildfire_ignition_points INT,
                wilderness_area_1 INT,
                wilderness_area_2 INT,
                wilderness_area_3 INT,
                wilderness_area_4 INT,
                soil_type_1 INT,
                soil_type_2 INT,
                soil_type_3 INT,
                soil_type_4 INT,
                soil_type_5 INT,
                soil_type_6 INT,
                soil_type_7 INT,
                soil_type_8 INT,
                soil_type_9 INT,
                soil_type_10 INT,
                soil_type_11 INT,
                soil_type_12 INT,
                soil_type_13 INT,
                soil_type_14 INT,
                soil_type_15 INT,
                soil_type_16 INT,
                soil_type_17 INT,
                soil_type_18 INT,
                soil_type_19 INT,
                soil_type_20 INT,
                soil_type_21 INT,
                soil_type_22 INT,
                soil_type_23 INT,
                soil_type_24 INT,
                soil_type_25 INT,
                soil_type_26 INT,
                soil_type_27 INT,
                soil_type_28 INT,
                soil_type_29 INT,
                soil_type_30 INT,
                soil_type_31 INT,
                soil_type_32 INT,
                soil_type_33 INT,
                soil_type_34 INT,
                soil_type_35 INT,
                soil_type_36 INT,
                soil_type_37 INT,
                soil_type_38 INT,
                soil_type_39 INT,
                soil_type_40 INT,
                cover_type INT
            );
        ''')

        # Seleccionar solo las columnas necesarias
               # Este paso se ajusta según las columnas que realmente tengas en tu DataFrame
        df = df[['elevation', 'aspect', 'slope', 'horizontal_distance_to_hydrology', 
                 'vertical_distance_to_hydrology', 'horizontal_distance_to_roadways', 
                 'hillshade_9am', 'hillshade_noon', 'hillshade_3pm', 
                 'horizontal_distance_to_fire_points', 'horizontal_distance_to_wildfire_ignition_points', 
                 'wilderness_area_1', 'wilderness_area_2', 'wilderness_area_3', 'wilderness_area_4', 
                 'soil_type_1', 'soil_type_2', 'soil_type_3', 'soil_type_4', 'soil_type_5', 'soil_type_6',
                 'soil_type_7', 'soil_type_8', 'soil_type_9', 'soil_type_10', 'soil_type_11', 'soil_type_12',
                 'soil_type_13', 'soil_type_14', 'soil_type_15', 'soil_type_16', 'soil_type_17', 'soil_type_18',
                 'soil_type_19', 'soil_type_20', 'soil_type_21', 'soil_type_22', 'soil_type_23', 'soil_type_24',
                 'soil_type_25', 'soil_type_26', 'soil_type_27', 'soil_type_28', 'soil_type_29', 'soil_type_30',
                 'soil_type_31', 'soil_type_32', 'soil_type_33', 'soil_type_34', 'soil_type_35', 'soil_type_36',
                 'soil_type_37', 'soil_type_38', 'soil_type_39', 'soil_type_40', 'cover_type']]
        
        # Convertir a tuplas
        data = [tuple(row) for row in df.to_numpy()]

        # Insertar los datos limpios en la nueva tabla
        query = """
            INSERT INTO covertype_clean (
                elevation, aspect, slope, horizontal_distance_to_hydrology, vertical_distance_to_hydrology,
                horizontal_distance_to_roadways, hillshade_9am, hillshade_noon, hillshade_3pm,
                horizontal_distance_to_fire_points, horizontal_distance_to_wildfire_ignition_points, 
                wilderness_area_1, wilderness_area_2, wilderness_area_3, wilderness_area_4,
                soil_type_1, soil_type_2, soil_type_3, soil_type_4, soil_type_5, soil_type_6, soil_type_7,
                soil_type_8, soil_type_9, soil_type_10, soil_type_11, soil_type_12, soil_type_13, soil_type_14,
                soil_type_15, soil_type_16, soil_type_17, soil_type_18, soil_type_19, soil_type_20, soil_type_21,
                soil_type_22, soil_type_23, soil_type_24, soil_type_25, soil_type_26, soil_type_27, soil_type_28,
                soil_type_29, soil_type_30, soil_type_31, soil_type_32, soil_type_33, soil_type_34, soil_type_35,
                soil_type_36, soil_type_37, soil_type_38, soil_type_39, soil_type_40, cover_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(query, data)


        # Confirmar cambios
        conn.commit()
        print(f"Datos preprocesados exitosamente. Registros insertados: {cursor.rowcount}")

        # Cerrar conexiones
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        raise AirflowException(f"Error al conectar a MySQL: {err}")

# Definición del DAG
with DAG(
    dag_id='mysql_penguins_preprocesamiento_dag',
    start_date=datetime(2025, 3, 28),
    schedule_interval='@daily',  # Esto significa que el DAG se ejecutará todos los días
    catchup=False
) as dag:

    # Definición de la tarea que ejecuta la función de preprocesamiento
    preprocesar_datos_task = PythonOperator(
        task_id='preprocesar_datos',
        python_callable=preprocesar_datos,
        dag=dag
    )

    trigger_train_model = TriggerDagRunOperator(
        task_id='trigger_train_model_dag',
        trigger_dag_id='Train_Model',
        wait_for_completion=False
    )

preprocesar_datos_task >> trigger_train_model