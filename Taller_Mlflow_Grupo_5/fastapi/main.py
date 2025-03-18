from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pyfunc
import pandas as pd
import os
import pickle

# Configurar MLflow Tracking Server
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://10.43.101.195:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

app = FastAPI(
    title="MLflow Model API",
    description="API que permite hacer inferencias con modelos almacenados en MLflow",
    version="1.0"
)

class PredictionInput(BaseModel):
    island: str
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    sex: str

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la API de inferencia con MLflow!", "docs": "Visita /docs para la documentación."}

@app.get("/models")
def list_models():
    """Lista los modelos registrados en MLflow y sus versiones en 'Production'."""
    client = mlflow.tracking.MlflowClient()
    models = []
    for m in client.search_registered_models():
        for version in m.latest_versions:
            models.append({
                "name": m.name,
                "version": version.version,
                "stage": version.current_stage
            })
    return {"available_models": models}

@app.post("/predict")
def predict(input_data: PredictionInput, model_name: str):
    """Realiza una predicción usando la versión en 'Production' del modelo en MLflow."""
    client = mlflow.tracking.MlflowClient()
    
    # ** Obtener la versión en Production**
    versions = client.get_latest_versions(model_name, stages=["Production"])
    if not versions:
        raise HTTPException(status_code=404, detail=f"No hay una versión en 'Production' para el modelo '{model_name}'")
    
    model_version = versions[0].version
    model_uri = f"models:/{model_name}/{model_version}"
    run_id = versions[0].run_id  #  Obtener el `run_id` del experimento original

    # ** Cargar el modelo desde MLflow**
    try:
        model = mlflow.pyfunc.load_model(model_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar el modelo: {str(e)}")
    
    # ** Descargar el LabelEncoder desde el experimento (no el modelo)**
    label_encoder = None
    try:
        artifact_uri = f"runs:/{run_id}/artifacts/label_encoder.pkl"
        label_encoder_path = mlflow.artifacts.load_artifact(artifact_uri)
        with open(label_encoder_path, "rb") as f:
            label_encoder = pickle.load(f)
    except Exception:
        print("No se encontró el LabelEncoder, la predicción se devolverá en formato numérico.")

    # ** Convertir input en DataFrame**
    input_df = pd.DataFrame([input_data.dict()])
    
    # ** Realizar predicción**
    prediction = model.predict(input_df)
    
    # ** Decodificar el resultado si hay LabelEncoder**
    if label_encoder:
        prediction = label_encoder.inverse_transform(prediction)

    return {
        "model_used": model_name,
        "version": model_version,
        "prediction": prediction.tolist()
    }

