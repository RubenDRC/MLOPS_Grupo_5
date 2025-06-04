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

# URI fija de MLflow
mlflow.set_tracking_uri("http://10.43.101.195:30958")

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
    return {"message": "Bienvenido a la API de MLflow para predicción de precios V2", "docs": "/docs"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Esquema de entrada
class PredictionInput(BaseModel):
    brokered_by: str
    status: str
    bed: int
    bath: int
    acre_lot: float
    street: str
    city: str
    state: str
    zip_code: str
    house_size: int
    prev_sold_date: str  # ISO date string

# Descargar artefactos
def descargar_artefacto(run_id: str, filename: str):
    client = MlflowClient()
    return client.download_artifacts(run_id, filename)

@app.post("/predict")
def predecir(datos: PredictionInput, model_name: str):
    start_time = time.time()
    REQUEST_COUNT.inc()

    try:
        # Obtener modelo y artefactos
        client = MlflowClient()
        versiones = client.get_latest_versions(model_name, stages=["Production"])
        if not versiones:
            raise HTTPException(status_code=404, detail=f"No hay versión 'Production' para el modelo '{model_name}'")

        run_id = versiones[0].run_id
        model_uri = f"models:/{model_name}/Production"
        model = mlflow.pyfunc.load_model(model_uri)

        # Cargar encoders
        encoders_path = descargar_artefacto(run_id, "label_encoders.pkl")
        with open(encoders_path, "rb") as f:
            label_encoders = pickle.load(f)

        # Preparar DataFrame
        df = pd.DataFrame([datos.dict()])
        df['prev_sold_date'] = pd.to_datetime(df['prev_sold_date'], errors='coerce')
        df['prev_sold_year'] = df['prev_sold_date'].dt.year.fillna(0)
        df.drop(columns=['prev_sold_date'], inplace=True)

        # Codificar categóricas
        for col, le in label_encoders.items():
            if col in df.columns:
                df[col] = le.transform(df[col].astype(str))
            else:
                df[col] = 0

        # Obtener columnas esperadas desde la firma
        input_schema = model.metadata.get_input_schema()
        expected_cols = [field.name for field in input_schema.inputs]

        # Asegurar presencia y orden de columnas
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0
        df = df[expected_cols]

        # Predicción
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
