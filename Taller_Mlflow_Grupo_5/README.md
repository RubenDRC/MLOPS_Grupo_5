# Proyecto MLOps con Docker

## Descripción
Este proyecto implementa una arquitectura MLOps basada en cinco instancias independientes:

1. **FastAPI** - Servicio de inferencia de modelos almacenados en MLflow.
2. **JupyterLab** - Entorno de experimentación y entrenamiento de modelos.
3. **MinIO** - Almacenamiento de artefactos en un bucket S3.
4. **MySQL (x2)** - Base de datos para MLflow y otra para almacenar datos.
5. **MLflow Server** - Servidor de tracking para registrar experimentos y modelos.

Cada servicio es desplegado de manera independiente y se comunican a través de la red pública.

## Estructura del Proyecto

```
./MLOps_Project
├── fastapi/               # Código y Dockerfile para FastAPI
├── jupyterlab/            # Código y Dockerfile para JupyterLab
├── mysql/                 # Configuración para instancias de MySQL
├── minio/                 # Configuración de MinIO
├── mlflow_server/         # Configuración del servicio MLflow
├── docker-compose-minio.yml  # Docker Compose para MinIO
├── docker-compose-mysql.yml  # Docker Compose para MySQL (2 instancias)p
├── mlflow_serv.service    # Servicio de MLflow como systemd
└── README.md              # Documentación del proyecto
```

## Servicios Implementados

### 1. FastAPI (Inferencia de modelos)
- Construido con **FastAPI**.
- Se conecta a **MLflow** para cargar modelos en producción.
- Expone un endpoint REST para realizar predicciones.

### 2. JupyterLab (Entrenamiento y Experimentación)
- Se ejecuta en un contenedor separado con su propio Dockerfile.
- Se conecta a **MLflow** y **MySQL** para almacenar experimentos y datos.
- Ejecuta scripts de entrenamiento y preprocesamiento de datos.

### 3. MinIO (Almacenamiento de artefactos)
- Emula un servicio de almacenamiento **S3**.
- Se usa para almacenar modelos y artefactos generados por MLflow.

### 4. MySQL (Instancias separadas)
- **MySQL - MLflow**: Base de datos para la gestión de experimentos y modelos.
- **MySQL - Datos**: Base de datos para almacenar datos procesados desde JupyterLab.

### 5. MLflow Server (Tracking de Modelos)
- Se ejecuta como un servicio independiente con **systemd**.
- Registra experimentos y almacena modelos en MinIO.
- Se conecta a la base de datos MySQL dedicada a MLflow.

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
```{
    "island": "Biscoe",
    "culmen_length_mm": 50.0,
    "culmen_depth_mm": 18.5,
    "flipper_length_mm": 200.0,
    "body_mass_g": 4000.0,
    "sex": "MALE"
  }'
```

## Maquina de ejecución

### IP
```10.43.101.195
```
## Autores
Desarrollado por Grupo 5.

