# 🚀 Taller 6 – MLOps (CI/CD + GitOps) — **Grupo 5**

---

## 🎯 Objetivo
 
- Entrenar un modelo de ML automáticamente desde CI.
- Construir y publicar imágenes Docker.
- Desplegar la API, carga de pruebas y monitoreo usando Kubernetes.
- Automatizar el despliegue con Argo CD.
 
---
 
## ⚙️ Tecnologías Utilizadas
 
- **FastAPI** para la API.
- **Prometheus** para métricas.
- **Grafana** para visualización.
- **GitHub Actions** para CI/CD.
- **Docker** para empaquetado.
- **Kubernetes** para orquestación.
- **Argo CD** para GitOps.
 

---

## 📂 Estructura del desarrollo:

```
MLOps_Grupo_5/
├──.github/workflows/ci-cd.yml
├── Taller_CI_CD/
│   ├── api/ # código y modelo
│      ├── app/main.py  
│      ├── app/model.pkl # generado por train_model.py
│      ├── train_model.py
│      ├── Dockerfile
│      └── requirements.txt
│   ├── loadtester/ 
│      ├── main.py
│      ├── Dockerfile
│      └── requirements.txt
│   ├── manifests/ # manifiestos K8s + kustomization
│      ├── api-deployment.yaml
│      ├── api-service.yaml
│      ├── grafana-datasource.yaml
│      ├── grafana-deployment.yaml
│      ├── grafana-service.yaml
│      ├── prometheus-configmap.yaml
│      ├── prometheus-deployment-.yaml
│      ├── prometheus-service.yaml
│      ├── script-deployment.yaml
│      └── kustomization.yaml
│   ├── argo-cd/
│      ├── app.yaml           #
└── README.md   
```

---

**Si desea ver la prueba y despliegue del sistema,** puede verlo en el siguiente video: https://youtu.be/i4d9ynKVjt8 

---

## Pasos para la Ejecución

#### 1: FastAPI y loadtester
```bash
microk8s kubectl apply -f manifest/fastapi-deployment.yaml
microk8s kubectl apply -f manifest/fastapi-service.yaml
microk8s kubectl apply -f manifest/script-deployment.yaml
```

#### 2: Observabilidad
```bash
microk8s kubectl apply -f manifests/grafana-datasource.yaml
microk8s kubectl apply -f manifests/grafana-deployment.yaml
microk8s kubectl apply -f manifests/grafana-service.yaml
microk8s kubectl apply -f manifests/prometheus-configmap.yaml
microk8s kubectl apply -f manifests/prometheus-deployment.yaml
microk8s kubectl apply -f manifests/prometheus-service.yaml
```

### 3. Argo
```bash
microk8s kubectl apply -f argo-cd/app.yaml
```

### 4. Verificar despliegue
```bash
microk8s kubectl get pods
microk8s kubectl get svc
```
## 5 · Acceso a los servicios 
```bash
- FastAPI:  
kubectl port-forward svc/api 8000:8000 -n $NS &

- Prometheus:
kubectl port-forward svc/prometheus 9090:9090 -n $NS &

- Grafana:
kubectl port-forward svc/grafana 3000:3000 -n $NS &

- Argo CD:
kubectl port-forward svc/argocd-server 8080:443 -n argocd &
```





