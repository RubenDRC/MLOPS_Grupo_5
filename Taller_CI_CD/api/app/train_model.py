from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from prometheus_fastapi_instrumentator import Instrumentator

# Cargar modelo y codificador
model = joblib.load("app/model.pkl")
label_encoder = joblib.load("app/label_encoder.pkl")

app = FastAPI()

# Instrumentador de Prometheus
Instrumentator().instrument(app).expose(app)

# Esquema de entrada
class PenguinInput(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

@app.get("/")
def read_root():
    return {"message": "API de predicción de especie de pingüino"}

@app.post("/predict")
def predict_species(data: PenguinInput):
    features = np.array([[data.culmen_length_mm, data.culmen_depth_mm, data.flipper_length_mm, data.body_mass_g]])
    prediction = model.predict(features)
    species = label_encoder.inverse_transform(prediction)
    return {"species_prediction": species[0]}

