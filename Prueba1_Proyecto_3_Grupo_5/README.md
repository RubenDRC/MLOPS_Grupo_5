# Proyecto 3 MLOps

## Descripción General
Este proyecto implementa un pipeline completo de MLOps desplegado sobre **Kubernetes con MicroK8s**, donde cada servicio se ejecuta en un contenedor independiente y se comunica a través de servicios de red internos. El entorno incluye:

1. **Airflow** - Orquestador de flujos de trabajo (DAGs) para ingesta de datos, entrenamiento y registro de modelos.
2. **PostgreSQL (x3)** - Una instancia para la metadata de Airflow, otra para almacenar datos procesados y otra para MLflow (experimentos, métricas).
3. **MinIO** - Almacenamiento de artefactos tipo S3, donde MLflow guarda modelos y otros archivos.
4. **MLflow Server** - Servidor de tracking para registrar experimentos, métricas y versiones de modelos. Usa PostgreSQL como backend y MinIO como artifact store.
5. **FastAPI** - Servicio de inferencia que carga modelos desde MLflow y expone un endpoint REST `/predict`.
6. **Streamlit** - Interfaz gráfica para ingresar datos y obtener inferencias desde FastAPI.

Esta arquitectura cubre el ciclo completo de MLOps: ingestión y orquestación → entrenamiento y registro de modelos → almacenamiento de artefactos → despliegue del modelo → consumo por usuario final.

---

## Estructura del Proyecto

MLOPS_Proyecto3/
├── airflow/ # Contiene los DAGs
│ └── dags/
├── fastapi/ # Servicio de inferencia
│ └── main.py
├── streamlit/ # Interfaz de usuario
│ └── app.py
├── k8s/ # Manifiestos de Kubernetes
│ ├── 25 archivos .yaml (uno por componente)
├── Makefile # Automatiza despliegue y limpieza


---

## Servicios Implementados

### 1. Airflow
- Webserver, Scheduler, Worker, Triggerer
- Conectado a PostgreSQL (`postgres-airflow`)
- Usa Redis como broker (`CeleryExecutor`)
- Ejecuta DAGs para ingestión, procesamiento y entrenamiento

### 2. PostgreSQL (x3 instancias)
- **postgres-airflow**: almacena metadatos de Airflow
- **postgres-mlflow**: almacena runs, métricas y modelos registrados en MLflow
- **postgres-data**: base de datos con datos crudos o preprocesados (por ejemplo, covertype)

### 3. MinIO
- Servicio tipo S3 que actúa como `artifact store` para MLflow

### 4. MLflow Server
- Tracking de experimentos, runs, parámetros, métricas y modelos
- Conectado a PostgreSQL (`postgres-mlflow`) y MinIO

### 5. FastAPI
- Exposición de modelos en stage "Production" desde MLflow
- Endpoint REST `/predict` para hacer inferencias

### 6. Streamlit
- Interfaz interactiva que se comunica con FastAPI para mostrar resultados al usuario
- Expuesta en el puerto 8503

---

## Pasos para la Ejecución

### 1. Habilitar servicios en MicroK8s

```bash
microk8s enable dns registry storage
```

### 2. Aplicar los manifiestos en orden
# Paso 1: Configuración común
```bash
microk8s kubectl apply -f k8s/airflow-configmap.yaml
```
# Paso 2: Bases de datos
```bash
microk8s kubectl apply -f k8s/postgres-airflow-pvc.yaml
microk8s kubectl apply -f k8s/postgres-airflow-deployment.yaml
microk8s kubectl apply -f k8s/postgres-airflow-service.yaml
microk8s kubectl apply -f k8s/postgres-mlflow-pvc.yaml
microk8s kubectl apply -f k8s/postgres-mlflow-deployment.yaml
microk8s kubectl apply -f k8s/postgres-mlflow-service.yaml
microk8s kubectl apply -f k8s/postgres-data-pvc.yaml
microk8s kubectl apply -f k8s/postgres-data-deployment.yaml
microk8s kubectl apply -f k8s/postgres-data-service.yaml
```
# Paso 3: Redis
```bash
microk8s kubectl apply -f k8s/redis-deployment.yaml
microk8s kubectl apply -f k8s/redis-service.yaml
```
# Paso 4: MinIO
```bash
microk8s kubectl apply -f k8s/minio-pvc.yaml
microk8s kubectl apply -f k8s/minio-deployment.yaml
microk8s kubectl apply -f k8s/minio-service.yaml
```
# Paso 5: MLflow
```bash
microk8s kubectl apply -f k8s/mlflow-deployment.yaml
microk8s kubectl apply -f k8s/mlflow-service.yaml
```
# Paso 6: Airflow
```bash
microk8s kubectl apply -f k8s/airflow-webserver.yaml
microk8s kubectl apply -f k8s/airflow-scheduler.yaml
microk8s kubectl apply -f k8s/airflow-worker.yaml
microk8s kubectl apply -f k8s/airflow-triggerer.yaml
```
# Paso 7: FastAPI y Streamlit
```bash
microk8s kubectl apply -f k8s/fastapi-deployment.yaml
microk8s kubectl apply -f k8s/fastapi-service.yaml
microk8s kubectl apply -f k8s/streamlit-deployment.yaml
microk8s kubectl apply -f k8s/streamlit-service.yaml
```

### 3. Puertos y Direcciones de Acceso
```bash
microk8s kubectl get svc
```




