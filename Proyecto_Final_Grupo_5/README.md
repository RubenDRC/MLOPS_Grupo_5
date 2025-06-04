# 🚀 Proyecto Final – MLOps - **Grupo 5**

## 🧩 Descripción General
Este proyecto implementa un pipeline de MLOps que entrena modelos con GitHub Actions, construye imágenes Docker y los despliega en un clúster Kubernetes con MicroK8s. La API (FastAPI) y el frontend (Streamlit) consultan modelos desde MLflow y están desplegados en dos máquinas virtuales, con monitoreo vía Prometheus y Grafana.

---
## 🎯 Objetivo

Implementar un sistema de MLOps completo que abarque:

- Recolección y procesamiento automatizado de datos mediante **Airflow**.
- Entrenamiento y reentrenamiento continuo de modelos con control de versiones usando **MLflow**.
- Registro y versionamiento de modelos, seleccionando automáticamente el mejor para producción.
- Exposición del modelo de producción a través de una **API FastAPI** conectada a MLflow.
- Interfaz gráfica desarrollada en **Streamlit** para la inferencia.
- Observabilidad mediante **Prometheus** y **Grafana**.
- Automatización de builds y publicación de imágenes con **GitHub Actions**.
- Despliegue de todos los servicios sobre **Kubernetes**, orquestado automáticamente mediante **Argo CD**.

---

## ⚙️ Tecnologías Utilizadas

- **Airflow** para orquestación del pipeline de datos y entrenamiento.
- **MLflow** para el seguimiento de experimentos, versionado y registro del mejor modelo.
- **PostgreSQL**  Una instancia para la metadata de Airflow, otra para almacenar datos procesados y otra para MLflow (experimentos, métricas).
- **Redis** como sistema de caché y soporte en la comunicación de servicios.
- **FastAPI** para servir el modelo de producción expuesto desde MLflow.
- **Streamlit** como interfaz de usuario para realizar inferencia y visualización de explicabilidad.
- **Prometheus** y **Grafana** para monitoreo y visualización.
- **GitHub Actions** para integración y entrega continua (CI/CD).
- **Docker** para contenerización de algunos servicios.
- **Kubernetes** para despliegue orquestado de microservicios.
- **Argo CD** para GitOps y sincronización automática desde el repositorio.

---

## 📂 Estructura del desarrollo:

```
MLOps_Grupo_5/
├──.github/workflows/ci-cd.yml
├── Proyecto_Final_Grupo_5/
│   ├── airflow/
│      ├── dags/
│          ├── Config_MLFlow.py
│          ├── Drop_And_Create_Table.py
│          ├── Load_Data.py
│          ├── Preprocess_Data.py
│          └──  Train_Data.py
│      └── requirements.txt
│   ├── fastapi/
│      ├── main.py  
│      ├── Dockerfile
│      └── requirements.txt
│   ├── loadtester/ 
│      ├── main.py
│      ├── Dockerfile
│      └── requirements.txt
│   ├── manifests/ # manifiestos K8s + kustomization
│      ├── airflow
│      ├── api-service.yaml
│      ├── argocd
│      ├── fastapi
│      ├── grafana
│      ├── loadtester
│      ├── minio
│      ├── mlflow
│      ├── postgres-airflow
│      ├── postgres-data
│      ├── postgres-mlflow
│      ├── prometheus
│      ├── redis
│      ├── streamlit
│      └── kustomization.yaml
│   ├── mlflow/ 
│      └── requirements.txt
│   ├── streamlit/ 
│      ├── app.py
│      ├── Dockerfile
│      └── requirements.txt
└── README.md   
```

---

**Si desea ver la prueba y despliegue del sistema,** puede verlo en el siguiente video: https://www.youtube.com/watch?v=bD0nJ31p1rw

---

## Pasos para la Ejecución

#### 1: FastAPI, Streamlit y loadtester
```bash
microk8s kubectl apply -f manifest/fastapi/fastapi-deployment.yaml
microk8s kubectl apply -f manifest/fastapi/fastapi-service.yaml
microk8s kubectl apply -f manifest/fastapi/kustomization.yaml

microk8s kubectl apply -f manifest/streamlit/streamlit-deployment.yaml
microk8s kubectl apply -f manifest/streamlit/streamlit-service.yaml
microk8s kubectl apply -f manifest/streamlit/kustomization.yaml

microk8s kubectl apply -f manifest/loadtester/loadtester-deployment.yaml
microk8s kubectl apply -f manifest/loadtester/kustomization.yaml
```
---
#### 2: Observabilidad
```bash
microk8s kubectl apply -f manifests/grafana/grafana-datasource.yaml
microk8s kubectl apply -f manifests/grafana/grafana-deployment.yaml
microk8s kubectl apply -f manifests/grafana/grafana-service.yaml
microk8s kubectl apply -f manifests/grafana/grafana-pvc.yaml
microk8s kubectl apply -f manifests/grafana/kustomization.yaml

microk8s kubectl apply -f manifests/prometheus/prometheus-configmap.yaml
microk8s kubectl apply -f manifests/prometheus/prometheus-deployment.yaml
microk8s kubectl apply -f manifests/prometheus/prometheus-service.yaml
microk8s kubectl apply -f manifests/prometheus/prometheus-pvc.yaml
microk8s kubectl apply -f manifests/prometheus/kustomization.yaml
```
---
#### 3. Argo
```bash
microk8s kubectl apply -f manifests/argo/app.yaml
microk8s kubectl apply -f manifests/argo/install-argocd.yaml
microk8s kubectl apply -f manifests/argo/kustomization.yaml
```

---
#### 4. Orquestación y registro de experimentos
```bash
microk8s kubectl apply -f manifests/airflow/airflow-configmap.yaml
microk8s kubectl apply -f manifests/airflow/airflow-scheduler.yaml
microk8s kubectl apply -f manifests/airflow/airflow-triggerer.yaml
microk8s kubectl apply -f manifests/airflow/airflow-webserver-service.yaml
microk8s kubectl apply -f manifests/airflow/airflow-webserver.yaml
microk8s kubectl apply -f manifests/airflow/airflow-worker.yaml
microk8s kubectl apply -f manifests/airflow/kustomization.yaml

microk8s kubectl apply -f manifests/mlflow/mlflow-deployment.yaml
microk8s kubectl apply -f manifests/mlflow/mlflow-service.yaml
microk8s kubectl apply -f manifests/mlflow/kustomization.yaml

microk8s kubectl apply -f manifests/minio/minio-deployment.yaml
microk8s kubectl apply -f manifests/minio/minio-service.yaml
microk8s kubectl apply -f manifests/minio/minio-secret.yaml
microk8s kubectl apply -f manifests/minio/minio-pvc.yaml
microk8s kubectl apply -f manifests/minio/kustomization.yaml
```
---
#### 5. Bases de datos
```bash
microk8s kubectl apply -f manifests/postgres-airflow/postgres-airflow-deployment.yaml
microk8s kubectl apply -f manifests/postgres-airflow/postgres-airflow-service.yaml
microk8s kubectl apply -f manifests/postgres-airflow/postgres-airflow-pvc.yaml
microk8s kubectl apply -f manifests/postgres-airflow/kustomization.yaml

microk8s kubectl apply -f manifests/postgres-data/postgres-data-deployment.yaml
microk8s kubectl apply -f manifests/postgres-data/postgres-data-service.yaml
microk8s kubectl apply -f manifests/postgres-data/postgres-data-pvc.yaml
microk8s kubectl apply -f manifests/postgres-data/kustomization.yaml

microk8s kubectl apply -f manifests/postgres-mlflow/postgres-mlflow-deployment.yaml
microk8s kubectl apply -f manifests/postgres-mlflow/postgres-mlflow-service.yaml
microk8s kubectl apply -f manifests/postgres-mlflow/postgres-mlflow-pvc.yaml
microk8s kubectl apply -f manifests/postgres-mlflow/kustomization.yaml

microk8s kubectl apply -f manifests/redis/redis-deployment.yaml
microk8s kubectl apply -f manifests/redis/redis-service.yaml
microk8s kubectl apply -f manifests/redis/kustomization.yaml
```
---
#### 6. Verificar despliegue
```bash
microk8s kubectl get pods -n mlops-final
microk8s kubectl get svc -n mlops-final
```
---
#### 7· Acceso a los servicios: Segun los puertos indicados en el desarrollo acceder a los servicios (validar con el video).
---
#### 8. Credenciales de las máquinas virtuales

- **Usuario escritorio remoto:** estudiante
-**Contraseña:** 4Silvia+1974
-**Dirección IP:** 10.43.101.195
-**Puerto:** 3389
-**Protocolo:** RDP
-**Sistema Operativo** Ubuntu 22.04.5 LTS ( Jammy)

- **Usuario escritorio remoto:** estudiante
-**Contraseña:** 4Lopez/19418
-**Dirección IP:** 10.43.101.188
-**Puerto:** 3389
-**Protocolo:** RDP
-**Sistema Operativo** Ubuntu 22.04.5 LTS ( Jammy)

---

