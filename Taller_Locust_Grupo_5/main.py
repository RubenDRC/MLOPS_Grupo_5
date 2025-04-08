# Creación de la API con FastAPI

# ------------------------------------------------------------------------------
# Importaciones necesarias
# ------------------------------------------------------------------------------
from fastapi import FastAPI, Response
from pydantic import BaseModel
from enum import Enum
import joblib
import pandas as pd
import uvicorn
from typing import Optional
from fastapi.responses import FileResponse

# ------------------------------------------------------------------------------
# 1. Definimos un Enum para el parámetro `model_name`
#    Esto creará un "combo box" con estas 3 opciones en la documentación de Swagger
# ------------------------------------------------------------------------------
class ModelName(str, Enum):
    random_forests = "Random forests"
    logistic_regression = "Logistic regression"
    support_vector_machine = "Support vector machine"

# ------------------------------------------------------------------------------
# 2. Creación de la app
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Penguin Classifier API",
    description="API que permite seleccionar entre 3 modelos de ML (RandomForest, LR, SVM) para clasificar pingüinos.",
    version="1.0"
)

# ------------------------------------------------------------------------------
# 3. Definimos el esquema de datos de entrada con Pydantic
# ------------------------------------------------------------------------------
class PenguinFeatures(BaseModel):
    island: str
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    sex: str

# ------------------------------------------------------------------------------
# 4. Variables globales para almacenar los modelos
# ------------------------------------------------------------------------------
models = {}

# ------------------------------------------------------------------------------
# 5. Evento de inicio (startup) para cargar los modelos en memoria
# ------------------------------------------------------------------------------
@app.on_event("startup")
def load_models():
    """
    Carga los 3 modelos entrenados y guardados como .pkl 
    y los asigna al diccionario global 'models'.
    """
    global models
    models["Random forests"] = joblib.load("models/model_rf.pkl")          # RandomForest
    models["Logistic regression"] = joblib.load("models/model_lr.pkl")     # LogisticRegression
    models["Support vector machine"] = joblib.load("models/model_svm.pkl") # SVM

# ------------------------------------------------------------------------------
# 6. Endpoint raíz ("/") -> Evita 404 al acceder a la raíz
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

# ------------------------------------------------------------------------------
# 7. Endpoint para servir un favicon (opcional)
#    Si no tienes favicon.ico, lo dejamos con status 204.
# ------------------------------------------------------------------------------
@app.get("/favicon.ico")
def read_favicon():
    # OPCIÓN 1: si tienes un archivo "favicon.ico" en la misma carpeta, retorna:
    # return FileResponse("favicon.ico")
    #
    # OPCIÓN 2: responder sin contenido (status 204) para evitar 404.
    return Response(status_code=204)

# ------------------------------------------------------------------------------
# 8. Endpoint para listar los modelos disponibles ("/models")
# ------------------------------------------------------------------------------
@app.get("/models")
def list_models():
    """
    Retorna la lista de modelos disponibles, 
    para que el usuario sepa qué nombres puede usar.
    """
    return {"available_models": list(models.keys())}

# ------------------------------------------------------------------------------
# 9. Endpoint de predicción ("/predict")
#    El parámetro model_name ahora es un Enum: ModelName
#    para que aparezca un combo con (Random forests, Logistic regression, Support vector machine)
# ------------------------------------------------------------------------------
@app.post("/predict")
def predict_species(
    data: PenguinFeatures, 
    model_name: ModelName = ModelName.random_forests
):
    """
    Endpoint para predecir la especie de pingüino.

    - 'data': objeto JSON con los features (island, culmen_length_mm, etc.)
    - 'model_name': enum con 3 opciones:
          Random forests, Logistic regression, Support vector machine

    Ejemplo de llamada (usando 'Logistic regression'):
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
    # 1) Recuperar la cadena real del enum
    chosen_model_key = model_name.value

    # 2) Verificar que el modelo solicitado está en 'models'
    if chosen_model_key not in models:
        return {
            "error": f"El modelo '{chosen_model_key}' no está disponible.",
            "available_models": list(models.keys())
        }

    chosen_model = models[chosen_model_key]

    # 3) Convertir la data de entrada en un DataFrame
    input_df = pd.DataFrame([{
        "island": data.island,
        "culmen_length_mm": data.culmen_length_mm,
        "culmen_depth_mm": data.culmen_depth_mm,
        "flipper_length_mm": data.flipper_length_mm,
        "body_mass_g": data.body_mass_g,
        "sex": data.sex
    }])

    # 4) Hacer la predicción
    prediction = chosen_model.predict(input_df)

    # 5) Retornar la predicción
    return {
        "model_used": chosen_model_key,
        "prediction": prediction[0]
    }

# ------------------------------------------------------------------------------
# 10. Iniciar la aplicación en el puerto 8989 (opcional si lanzas con uvicorn)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8989)
