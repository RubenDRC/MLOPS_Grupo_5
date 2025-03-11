# Creación de la API con FastAPI

# ------------------------------------------------------------------------------ 
# Importaciones necesarias
# ------------------------------------------------------------------------------ 
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
import uvicorn
import pandas as pd
from typing import Optional

# ------------------------------------------------------------------------------ 
# 1. Creación de la app
# ------------------------------------------------------------------------------ 
app = FastAPI(
    title="Penguin Classifier API",
    description="API que permite cargar modelos de ML para clasificar pingüinos.",
    version="2.0"
)

# ------------------------------------------------------------------------------ 
# 2. Definimos el esquema de datos de entrada con Pydantic 
# ------------------------------------------------------------------------------ 
class PenguinFeatures(BaseModel):
    island: str
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    sex: str

# ------------------------------------------------------------------------------ 
# 3. Variables globales para almacenar los modelos 
# ------------------------------------------------------------------------------ 
models = {}



# ------------------------------------------------------------------------------ 
# 5. Endpoint raíz ("/") -> Evita 404 al acceder a la raíz
# ------------------------------------------------------------------------------ 
@app.get("/")
def read_root():
    """
    Mensaje de bienvenida al acceder a la raíz.
    """
    return {
        "message": "¡Bienvenido a la Penguin Classifier API!",
        "docs": "Visita /docs para la documentación interactiva.",
        "models_endpoint": "Visita /models para ver los modelos disponibles."
    }


# 4. Endpoint para cargar los modelos manualmente
@app.get("/load_models")
def load_models_manually():
    """
    Carga los modelos en memoria manualmente cuando se hace una solicitud GET.
    """
    global models
    model_directory = "/models"  # Ruta donde los modelos .pkl están montados

    # Verificar que el directorio exista
    if not os.path.exists(model_directory):
        return {"error": f"Directorio de modelos no encontrado: {model_directory}"}
    
    # Buscar todos los archivos .pkl en el directorio 'models'
    for model_file in os.listdir(model_directory):
        if model_file.endswith(".pkl"):
            model_path = os.path.join(model_directory, model_file)
            model_name = model_file.replace(".pkl", "")  # Nombre del modelo (sin extensión)
            print(f"Cargando modelo: {model_name} desde {model_path}")
            models[model_name] = joblib.load(model_path)

    return {"message": "Modelos cargados correctamente.", "models_loaded": list(models.keys())}
    
# ------------------------------------------------------------------------------ 
# 6. Endpoint para listar los modelos disponibles ("/models")
# ------------------------------------------------------------------------------ 
@app.get("/models")
def list_models():
    """
    Retorna la lista de modelos disponibles 
    para que el usuario sepa qué nombres puede usar.
    """
    return {"available_models": list(models.keys())}

# ------------------------------------------------------------------------------ 
# 7. Endpoint de predicción ("/predict")
# ------------------------------------------------------------------------------ 
@app.post("/predict")
def predict_species(
    data: PenguinFeatures, 
    model_name: str
):
    """
    Endpoint para predecir la especie de pingüino.

    - 'data': objeto JSON con los features (island, culmen_length_mm, etc.)
    - 'model_name': el nombre del modelo (uno de los modelos cargados)

    Ejemplo de llamada:
      POST /predict?model_name=Logistic regression
      {
        "island": "Biscoe",
        "culmen_length_mm": 50.0,
        "culmen_depth_mm": 18.5,
        "flipper_length_mm": 200.0,
        "body_mass_g": 4000.0,
        "sex": "MALE"
      }
    """
    # Verificar que el modelo solicitado está en 'models'
    if model_name not in models:
        return {
            "error": f"El modelo '{model_name}' no está disponible.",
            "available_models": list(models.keys())
        }

    chosen_model = models[model_name]

    # Convertir la data de entrada en un DataFrame
    input_df = pd.DataFrame([{
        "island": data.island,
        "culmen_length_mm": data.culmen_length_mm,
        "culmen_depth_mm": data.culmen_depth_mm,
        "flipper_length_mm": data.flipper_length_mm,
        "body_mass_g": data.body_mass_g,
        "sex": data.sex
    }])

    # Hacer la predicción
    prediction = chosen_model.predict(input_df)

    # Retornar la predicción
    return {
        "model_used": model_name,
        "prediction": prediction[0]  # Devolver el valor de predicción
    }
