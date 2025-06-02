from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import mlflow
import mlflow.pyfunc
import pandas as pd
import os
import pickle
from mlflow.tracking import MlflowClient
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

# Configurar MLflow desde variables de entorno (o valor por defecto)
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))

# Inicializar FastAPI
app = FastAPI(
    title="API Predicciones Precio de Viviendas",
    description="Predicciones usando modelos registrados en MLflow",
    version="1.0"
)

# Métricas Prometheus
REQUEST_COUNT = Counter('predict_requests_total', 'Total de peticiones de predicción')
REQUEST_LATENCY = Histogram('predict_latency_seconds', 'Tiempo de latencia de predicción')

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de MLflow para predicción de precios", "docs": "/docs"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Schema de entrada actualizado
class PredictionInput(BaseModel):
    brokered_by: str = Field(..., alias="brokered_by")
    status: str = Field(..., alias="status")
    bed: int = Field(..., alias="bed")
    bath: int = Field(..., alias="bath")
    acre_lot: float = Field(..., alias="acre_lot")
    street: str = Field(..., alias="street")
    city: str = Field(..., alias="city")
    state: str = Field(..., alias="state")
    zip_code: str = Field(..., alias="zip_code")
    house_size: int = Field(..., alias="house_size")
    prev_sold_date: str = Field(..., alias="prev_sold_date")  # ISO date string

    class Config:
        allow_population_by_field_name = True

# Descargar artefacto desde MLflow
def descargar_artefacto(run_id: str, filename: str):
    client = MlflowClient()
    return client.download_artifacts(run_id, filename)

# Endpoint de predicción
@app.post("/predict")
def predecir(datos: PredictionInput, model_name: str):
    start_time = time.time()
    REQUEST_COUNT.inc()

    try:
        client = MlflowClient()
        versiones = client.get_latest_versions(model_name, stages=["Production"])
        if not versiones:
            raise HTTPException(status_code=404, detail=f"No hay versión 'Production' para el modelo '{model_name}'")

        run_id = versiones[0].run_id
        model_uri = f"models:/{model_name}/Production"
        model = mlflow.pyfunc.load_model(model_uri)

        # Descargar y cargar label_encoders.pkl
        encoders_path = descargar_artefacto(run_id, "label_encoders.pkl")
        with open(encoders_path, "rb") as f:
            label_encoders = pickle.load(f)

        # Preparar dataframe
        df = pd.DataFrame([datos.dict()])
        df['prev_sold_date'] = pd.to_datetime(df['prev_sold_date'], errors='coerce')
        df['prev_sold_year'] = df['prev_sold_date'].dt.year.fillna(0)
        df.drop(columns=['prev_sold_date'], inplace=True)

        # Codificar con LabelEncoders
        for col, le in label_encoders.items():
            df[col] = le.transform(df[col].astype(str))

        # Reordenar columnas
        expected_cols = model.metadata.get_input_schema().input_names()
        for col in expected_cols:
            if col not in df:
                df[col] = 0
        df = df[expected_cols]

        pred = model.predict(df)

        return {
            "modelo": model_name,
            "prediccion": pred.tolist(),
            "version": versiones[0].version
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /predict: {str(e)}")

    finally:
        REQUEST_LATENCY.observe(time.time() - start_time)

