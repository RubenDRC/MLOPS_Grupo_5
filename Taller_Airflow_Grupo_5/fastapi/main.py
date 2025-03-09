# fastapi/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
import pandas as pd

app = FastAPI(
    title="Penguin Classifier API",
    description="API que permite cargar modelos de ML para clasificar pingüinos.",
    version="2.0"
)

class PenguinFeatures(BaseModel):
    island: str
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    sex: str

# Diccionario global de modelos
models = {}

def load_models():
    global models
    model_directory = "/app/models"  # Montado con volumen

    if not os.path.exists(model_directory):
        print(f"Directorio de modelos no encontrado: {model_directory}")
        return

    models.clear()
    for model_file in os.listdir(model_directory):
        if model_file.endswith(".pkl"):
            model_path = os.path.join(model_directory, model_file)
            model_name = model_file.replace(".pkl", "")
            print(f"Cargando modelo: {model_name} desde {model_path}")
            try:
                models[model_name] = joblib.load(model_path)
            except Exception as e:
                print(f"Error al cargar el modelo {model_name}: {e}")

@app.on_event("startup")
def startup_event():
    # Se llama cuando inicia la app
    load_models()

@app.post("/refresh")
def refresh_models():
    load_models()
    return {"message": "Modelos recargados", "available_models": list(models.keys())}

@app.get("/")
def read_root():
    return {
        "message": "¡Bienvenido a la Penguin Classifier API!",
        "docs": "Visita /docs para la documentación interactiva.",
        "models_endpoint": "Visita /models para ver los modelos disponibles."
    }

@app.get("/models")
def list_models():
    return {"available_models": list(models.keys())}

@app.post("/predict")
def predict_species(data: PenguinFeatures, model_name: str):
    if model_name not in models:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"El modelo '{model_name}' no está disponible.",
                "available_models": list(models.keys())
            }
        )

    chosen_model = models[model_name]
    input_df = pd.DataFrame([{
        "island": data.island,
        "culmen_length_mm": data.culmen_length_mm,
        "culmen_depth_mm": data.culmen_depth_mm,
        "flipper_length_mm": data.flipper_length_mm,
        "body_mass_g": data.body_mass_g,
        "sex": data.sex
    }])

    try:
        prediction = chosen_model.predict(input_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la predicción: {e}")

    return {
        "model_used": model_name,
        "prediction": prediction[0]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8989, reload=True)
