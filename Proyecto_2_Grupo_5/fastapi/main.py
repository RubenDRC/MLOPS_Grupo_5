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

# Modelo de entrada adaptado al dataset Covertype
class PredictionInput(BaseModel):
    Elevation: int
    Aspect: int
    Slope: int
    Horizontal_Distance_To_Hydrology: int
    Vertical_Distance_To_Hydrology: int
    Horizontal_Distance_To_Roadways: int
    Hillshade_9am: int
    Hillshade_Noon: int
    Hillshade_3pm: int
    Horizontal_Distance_To_Fire_Points: int
    Wilderness_Area: str
    Soil_Type: str

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la API de inferencia con MLflow V2!", "docs": "Visita /docs para la documentación."}

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
    versions = client.get_latest_versions(model_name, stages=["Production"])
    if not versions:
        raise HTTPException(status_code=404, detail=f"No hay una versión en 'Production' para el modelo '{model_name}'")

    model_version = versions[0].version
    model_uri = f"models:/{model_name}/{model_version}"
    run_id = versions[0].run_id

    # Cargar el modelo desde MLflow
    try:
        model = mlflow.pyfunc.load_model(model_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar el modelo: {str(e)}")

    # Descargar codificadores (label_encoders.pkl)
    try:
        encoders_path = mlflow.artifacts.load_artifact(f"runs:/{run_id}/artifacts/label_encoders.pkl")
        with open(encoders_path, "rb") as f:
            label_encoders = pickle.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar los codificadores: {str(e)}")

    # Convertir entrada en DataFrame
    input_df = pd.DataFrame([input_data.dict()])

    # Aplicar codificación One-Hot con las columnas del entrenamiento
    for col, encoder in label_encoders.items():
        encoded = encoder.transform(input_df[[col]])
        ohe_df = pd.DataFrame(encoded.toarray(), columns=encoder.get_feature_names_out([col]))
        input_df = pd.concat([input_df.drop(columns=[col]), ohe_df], axis=1)

    # Ajustar columnas faltantes (por si algún valor no apareció en este input)
    expected_columns = model.metadata.get_input_schema().input_names()
    for col in expected_columns:
        if col not in input_df:
            input_df[col] = 0
    input_df = input_df[expected_columns]  # Reordenar

    # Hacer predicción
    prediction = model.predict(input_df)

    # Cargar LabelEncoder del target
    try:
        label_encoder_path = mlflow.artifacts.load_artifact(f"runs:/{run_id}/artifacts/label_encoder_y.pkl")
        with open(label_encoder_path, "rb") as f:
            label_encoder_y = pickle.load(f)
        prediction = label_encoder_y.inverse_transform(prediction)
    except Exception:
        pass  # Devolver como entero si no hay encoder

    return {
        "model_used": model_name,
        "version": model_version,
        "prediction": prediction.tolist()
    }

