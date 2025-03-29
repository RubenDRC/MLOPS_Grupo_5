from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import pandas as pd
import mysql.connector
import os

# Definir los argumentos del DAG
default_args = {
    'start_date': days_ago(1),
    'retries': 1
}

# Ruta del archivo CSV
data_file = '/data/penguins_size.csv'

# Función para validar la existencia del archivo
def FileValidator():
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"El archivo {data_file} no existe. No se puede continuar con la carga de datos.")
    print(f"El archivo {data_file} existe. Se procederá con la carga de datos.")

# Función para cargar los datos de pingüinos en la base de datos
def LoadData():
    conn = None
    cursor = None
    try:
        # Cargar los datos desde el CSV
        df = pd.read_csv(data_file)

        # Eliminar nulls  para evitar el error en MySQL
        df = df.dropna()



        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="airflow"
        )
        cursor = conn.cursor()
        
        # Insertar los datos en la tabla
        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO penguins (species, island, culmen_length_mm, culmen_depth_mm, flipper_length_mm, body_mass_g, sex) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (row['species'], row['island'], row['culmen_length_mm'], row['culmen_depth_mm'], row['flipper_length_mm'], row['body_mass_g'], row['sex'])
            )
        
        conn.commit()
        print("Datos de pingüinos cargados correctamente en la base de datos.")
    except Exception as e:
        print(f"Error al cargar los datos: {e}")        
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexión a MySQL cerrada correctamente.")

# Definir el DAG
with DAG(
    dag_id='Load_Data',    
    description='Elimina y crea tabla en MySql',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:


    # Tarea para validar la existencia del archivo
    tarea_validar_archivo = PythonOperator(
        task_id='validar_archivo',
        python_callable=FileValidator
    )

    # Tarea para cargar los datos en la base de datos
    tarea_cargar_datos = PythonOperator(
        task_id='cargar_datos',
        python_callable=LoadData
    )

    # Tarea para disparar el siguiente DAG automáticamente
    
    trigger_siguiente_tarea= TriggerDagRunOperator(
        task_id='trigger_Load_Data',
        trigger_dag_id='Preprocess_Data',  # Nombre del DAG a ejecutar
        wait_for_completion=False  # Si True, espera a que el segundo DAG termine antes de completar este DAG
    )

    tarea_validar_archivo >> tarea_cargar_datos >> trigger_siguiente_tarea


    try:
    # Cargar el dataset desde CSV
    df = pd.read_csv("/work/data/penguins_size.csv").dropna()

    # Conexión a MySQL
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Consulta SQL optimizada para inserción masiva
    query = """
        INSERT INTO penguins (species, island, culmen_length_mm, culmen_depth_mm, flipper_length_mm, body_mass_g, sex)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    # Convertir el dataframe a una lista de tuplas para ejecutar con `executemany`
    data_tuples = list(df.itertuples(index=False, name=None))
    
    # Insertar los datos en una sola llamada para mejorar rendimiento
    cursor.executemany(query, data_tuples)

    # Confirmar cambios
    conn.commit()
    print(f"Datos cargados exitosamente. Registros insertados: {cursor.rowcount}")

    # Cerrar conexiones
    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print(f"Error al conectar a MySQL: {err}")

except FileNotFoundError:
    print("Error: El archivo CSV no fue encontrado.")










from fastapi import FastAPI, HTTPException
from typing import Optional
import random
import json
import time
import csv
import os

MIN_UPDATE_TIME = 300 ## Aca pueden cambiar el tiempo minimo para cambiar bloque de información

app = FastAPI()

# Elevation,
# Aspect,
# Slope,
# Horizontal_Distance_To_Hydrology,
# Vertical_Distance_To_Hydrology,
# Horizontal_Distance_To_Roadways,
# Hillshade_9am,
# Hillshade_Noon,
# Hillshade_3pm,
# Horizontal_Distance_To_Fire_Points,
# Wilderness_Area,
# Soil_Type,
# Cover_Type

@app.get("/")
async def root():
    return {"Proyecto 2": "Extracción de datos, entrenamiento de modelos."}


# Cargar los datos del archivo CSV
data = []
with open('/data/covertype.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)
    for row in reader:
        data.append(row)

batch_size = len(data) // 10

# Definir la función para generar la fracción de datos aleatoria
def get_batch_data(batch_number:int, batch_size:int=batch_size):
    start_index = batch_number * batch_size
    end_index = start_index + batch_size
    # Obtener datos aleatorios dentro del rango del grupo
    random_data = random.sample(data[start_index:end_index], batch_size // 10)
    return random_data

# Cargar información previa si existe
if os.path.isfile('/data/timestamps.json'):
    with open('/data/timestamps.json', "r") as f:
        timestamps = json.load(f)
        
else:
    # Definir el diccionario para almacenar los timestamps de cada grupo e incializar el conteo, inicia en -1 para no agregar logica adicional de conteo
    timestamps = {str(group_number): [0, -1] for group_number in range(1, 11)} # el valor está definido como [timestamp, batch]

# Definir la ruta de la API
@app.get("/data")
async def read_data(group_number: int):
    global timestamps

    # Verificar si el número de grupo es válido
    if group_number < 1 or group_number > 10:
        raise HTTPException(status_code=400, detail="Número de grupo inválido")
    # Verificar si el número de conteo es adecuado
    if timestamps[str(group_number)][1] >= 10:
        raise HTTPException(status_code=400, detail="Ya se recolectó toda la información minima necesaria")
    
    current_time = time.time()
    last_update_time = timestamps[str(group_number)][0]
    
    # Verificar si han pasado más de 5 minutos desde la última actualización
    if current_time - last_update_time > MIN_UPDATE_TIME: 
        # Actualizar el timestamp y obtener nuevos datos
        timestamps[str(group_number)][0] = current_time
        timestamps[str(group_number)][1] += 2 if timestamps[str(group_number)][1] == -1 else 1
    
    # Utilizar los mismos datos que la última vez (una parte del mismo grupo de información)
    random_data = get_batch_data(group_number)
    with open('/data/timestamps.json', 'w') as file:
        file.write(json.dumps(timestamps))
    
    return {"group_number": group_number, "batch_number": timestamps[str(group_number)][1], "data": random_data}

@app.get("/restart_data_generation")
async def restart_data(group_number: int):
    # Verificar si el número de grupo es válido
    if group_number < 1 or group_number > 10:
        raise HTTPException(status_code=400, detail="Número de grupo inválido")

    timestamps[str(group_number)][0] = 0
    timestamps[str(group_number)][1] = -1
    with open('/data/timestamps.json', 'w') as file:
        file.write(json.dumps(timestamps))
    return {'ok'}