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


** Si desea ver la prueba y despliegue del sistema, ** puede verlo en el siguiente video: https://youtu.be/i4d9ynKVjt8 


