
# Proyecto 2 MLOps

## Descripción General
Este proyecto implementa un pipeline completo de MLOps usando contenedores de Docker, donde cada servicio cumple un rol independiente y se comunican a través de redes de Docker. El entorno incluye:

1. **Airflow** - Orquestador de flujos de trabajo (DAGs) para ingesta de datos, entrenamiento y registro de modelos.
2. **MySQL (x3)** - Una instancia para la metadata de Airflow. Otra para almacenar datos/procesados (por ejemplo, la tabla covertype). Una tercera para el tracking de MLflow (almacena experimentos, runs, métricas).
3. **MinIO** - Almacenamiento de artefactos estilo S3, donde MLflow guarda modelos y archivos (label encoders, etc.).
4. **MLflow Server** - Servidor de tracking para registrar experimentos, métricas y versiones de modelo. Configurado para usar MySQL como “backend store” y MinIO como “artifact store”. 
5. **MLflow Server** - Servicio de inferencia que carga el modelo desde MLflow y expone un endpoint REST /predict.
6. **streamlit** - Interfaz gráfica para que el usuario final ingrese datos y obtenga inferencias (puerto 8503).

Con esta arquitectur se cubre todo el ciclo: recolección y procesamiento de datos (Airflow) → entrenamiento y registro en MLflow → almacenamiento de artefactos (MinIO) → base de datos de experimentos (MySQL/MLflow) → servicio de inferencia (FastAPI) → interfaz final (Streamlit).

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
│       ├── Preprocess_Data.py
│       └── Train_Data.py
│        
├── fastapi/                # Carpeta con Dockerfile y main.py de FastAPI
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── streamlit/ (opcional)   # Carpeta para la app Streamlit de interfaz
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

#### **Paso 1: Iniciar MinIO**
```bash
docker-compose up -d
```

#### **Paso 2: Iniciar las instancias de MySQL**
```bash
docker-compose up -d 
```

#### **Paso 3: Iniciar MLflow Server**
```bash
sudo systemctl start mlflow_serv.service
```

#### **Paso 4: Iniciar JupyterLab**
```bash
docker build -t jupyterlab ./jupyterlab

docker run -it --name jupyterlab --rm -e TZ=America/Bogota -p 8888:8888 -v $PWD:/work jupyterlab:latest
```

#### **Paso 5: Iniciar FastAPI**
```bash
docker build -t fastapi ./fastapi

docker run -d --name fastapi -p 8000:8000 fastapi
```

### 3. Verificar que los contenedores estén corriendo
```bash
docker ps
```

## Prueba de Inferencia con FastAPI

### 1. Realizar una Predicción
```
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
```

## Maquina de ejecución

### IP
```
10.43.101.195

```
## Autores
Desarrollado por Grupo 5.

