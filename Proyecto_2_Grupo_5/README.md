
# Proyecto 2 MLOps

## Descripción General
Este proyecto implementa un pipeline completo de MLOps usando contenedores de Docker, donde cada servicio cumple un rol independiente y se comunican a través de redes de Docker. El entorno incluye:

1. **Airflow** - Orquestador de flujos de trabajo (DAGs) para ingesta de datos, entrenamiento y registro de modelos.
2. **MySQL (x3)** - Una instancia para la metadata de Airflow. Otra para almacenar datos/procesados (por ejemplo, la tabla covertype). Una tercera para el tracking de MLflow (almacena experimentos, runs, métricas).
3. **MinIO** - Almacenamiento de artefactos estilo S3, donde MLflow guarda modelos y archivos (label encoders, etc.).
4. **MLflow Server** - Servidor de tracking para registrar experimentos, métricas y versiones de modelo. Configurado para usar MySQL como “backend store” y MinIO como “artifact store”. 
5. **MLflow Server** - Servicio de inferencia que carga el modelo desde MLflow y expone un endpoint REST /predict.
6. **Streamlit** - Interfaz gráfica para que el usuario final ingrese datos y obtenga inferencias (puerto 8503).

Con esta arquitectura se cubre todo el ciclo: recolección y procesamiento de datos (Airflow) → entrenamiento y registro en MLflow → almacenamiento de artefactos (MinIO) → base de datos de experimentos (MySQL/MLflow) → servicio de inferencia (FastAPI) → interfaz final (Streamlit).

## Estructura del Proyecto

```
MLOps_Project/
├── airflow/                # Carpeta con configuración y DAGs de Airflow
│   ├── Dockerfile
│   ├── requirements.txt
│   └── dags/
│       ├── Config_MLFlow.py
│       ├── Drop_And_Create_Table.py
│       ├── Load_Data.py
│       ├── Preprocess_Data.py
│       └── Train_Data.py
│        
├── fastapi/                # Carpeta con Dockerfile y main.py de FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── streamlit/              # Carpeta para la app Streamlit de interfaz
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── docker-compose.yaml     # Orquesta y levanta todos los servicios
├── mlflo_serv.service      # Servicio systemd para MLflow 
├── .env                    # Variables de entorno 
└── README.md   
```

## Servicios Implementados

### 1. Airflow
- **Orquestación** de tareas a través de DAGs.
- Descarga datos de una API externa, los inserta en MySQL, los limpia y finalmente desencadena el entrenamiento del modelo.
- Guarda logs y metadatos en la base MySQL correspondiente a “airflow”.

### 2. MySQL (x3 instancias)
- **mysql_airflow:** Base de datos interna de Airflow (tablas de tareas, DAGs, usuarios, etc.).
- **mysql_data:** Contiene tablas de datos (por ejemplo, covertype) donde se almacenan las muestras traídas por Airflow.
- **mysql_mlflow:** Almacena la información de experimentos, parámetros, métricas y versiones de modelo de MLflow.

### 3. MinIO 
- Servicio tipo S3 para **almacenar artefactos** de MLflow

### 4. MLflow Server (Tracking de Modelos)
- Servidor de tracking que registra: Experimentos (nombre, descripción). Runs (métricas, parámetros). Versiones de modelo (subidas a un registry). 
- Apunta a MySQL (mysql_mlflow) como “backend store” y a MinIO como “artifact store”.

### 5. FastAPI
- Servicio **REST** para exponer el **modelo entrenado** en MLflow.
- Carga la versión de modelo que esté en stage “Production”.
- Responde a endpoints como /predict recibiendo un JSON con datos de entrada.

### 6. Streamlit
- Interfaz gráfica para que el usuario ingrese valores y obtenga la predicción del modelo.
- Se comunica con FastAPI (un requests.post a /predict).
- Expuesto en el puerto 8503.

## Pasos para la Ejecución

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd MLOps_Project
```

### 2. Levantar los servicios en orden

En este proyecto, la mayoría de servicios se definen en el **docker-compose.yaml** (Airflow, MySQL, MinIO, FastAPI y Streamlit). Sin embargo, **MLflow** se levanta de forma externa con un archivo `.service` (no dentro de Docker).

A continuación, se presenta el procedimiento para iniciar el proceso:


#### **Paso 1: Levantar los contenedores**:
```bash
docker-compose up -d
```
Esto inicia:
- Airflow (puerto 8080)
- MySQL (puertos 3306, 3307, 3308)
- MinIO (puertos 9000/9001)
- FastAPI (puerto 8000)
- Streamlit (puerto 8503).

#### **Paso 2: Iniciar MLflow Server**
```bash
sudo systemctl start mlflow_serv.service
```
Se Debería tener MLflow disponible en http://10.43.101.195:5000.

### 3. Verificar que los contenedores estén corriendo
```bash
docker ps
```

#### 4. Puertos y direcciones de acceso
**Airflow:**

- http://10.43.101.195:8080

**MinIO:**

- Consola: http://10.43.101.195:9001

- Endpoint S3: http://10.43.101.195:9000

**MySQL:**

- Airflow: Puerto 3306

- MLflow: Puerto 3307

- Datos: Puerto 3308

- MLflow (externo): http://10.43.101.195:5000

- FastAPI: http://10.43.101.195:8000 (Swagger en /docs)

- Streamlit: http://10.43.101.195:8503


## Prueba de Inferencia con FastAPI

### 1. Realizar una Predicción
```
Ejemplo de JSON a enviar a POST /predict

{
  "Elevation": 2596,
  "Aspect": 51,
  "Slope": 3,
  "Horizontal_Distance_To_Hydrology": 258,
  "Vertical_Distance_To_Hydrology": 0,
  "Horizontal_Distance_To_Roadways": 510,
  "Hillshade_9am": 221,
  "Hillshade_Noon": 232,
  "Hillshade_3pm": 148,
  "Horizontal_Distance_To_Fire_Points": 6279,
  "Wilderness_Area": "Rawah",
  "Soil_Type": "C7745"
}

En respuesta se obtendra un JSON con la predicción, por ejemplo:
{
  "model_used": "RandomForestModel",
  "version": "1",
  "prediction": [2]
}
```
## Uso de Streamlit
En http://10.43.101.195:8503, se encontrará una interfaz para ingresar valores de Elevation, Slope, etc. y presionar “Predecir”. La app enviará un POST a http://10.43.101.195:8000/predict y mostrará la respuesta directamente en pantalla.

Parámetros de ejemplo:
- Elevation: 2500
- Aspect: 45
- Slope: 10
- Wilderness_Area: “Rawah”
- Soil_Type: “C7745”
- etc...

## Video Tutorial
Si desea ver una demostración de la **implementación, ejecución y resultados, puede consultar el siguiente video:** https://www.youtube.com/watch?v=od4n5W0470s

## Maquina de ejecución

### IP
```
10.43.101.195

```
## Autores
Desarrollado por Grupo 5.

