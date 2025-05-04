from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import mlflow.tracking
from mlflow.tracking import MlflowClient
import pandas as pd
import os
import pickle
import boto3
import tempfile

# Configurar MLflow y acceso a MinIO
os.environ["MLFLOW_TRACKING_URI"] = "http://10.43.101.195:5000"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://10.43.101.195:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "supersecret"
mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

# FastAPI app
app = FastAPI(
    title="MLflow Model API",
    description="API para predicciones usando modelos de MLflow",
    version="1.0"
)

# Input schema
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

# Función robusta para descargar artefactos
def descargar_artefacto(run_id: str, filename: str):
    from mlflow.artifacts import download_artifacts
    try:
        uri = f"runs:/{run_id}/artifacts/{filename}"
        print(f"[MLflow] Descargando {filename} desde: {uri}")
        return download_artifacts(uri)
    except Exception as e:
        print(f"[MLflow] Falló la descarga: {e}")
        print(f"[Boto3] Intentando descargar desde MinIO...")
        key = f"artifacts/1/{run_id}/artifacts/{filename}"  # experiment_id = 1
        s3 = boto3.client(
            "s3",
            endpoint_url="http://10.43.101.195:9000",
            aws_access_key_id="admin",
            aws_secret_access_key="supersecret"
        )
        temp_path = tempfile.NamedTemporaryFile(delete=False).name
        s3.download_file("mlflows3", key, temp_path)
        print(f"[Boto3] Descargado exitosamente en: {temp_path}")
        return temp_path

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la API de MLflow!", "docs": "/docs"}

@app.get("/models")
def list_models():
    client = MlflowClient()
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
    try:
        client = MlflowClient()
        versions = client.get_latest_versions(model_name, stages=["Production"])
        if not versions:
            raise HTTPException(status_code=404, detail=f"No hay versión 'Production' del modelo '{model_name}'")

        model_version = versions[0].version
        run_id = versions[0].run_id
        model_uri = f"models:/{model_name}/{model_version}"


        model = mlflow.pyfunc.load_model(model_uri)

        # Descargar y cargar los LabelEncoders
        encoders_path = descargar_artefacto(run_id, "label_encoders.pkl")
        with open(encoders_path, "rb") as f:
            label_encoders = pickle.load(f)

        # Crear el DataFrame de entrada
        input_df = pd.DataFrame([input_data.dict()])

        # Aplicar LabelEncoder a las columnas categóricas
        for col, encoder in label_encoders.items():
            input_df[col] = encoder.transform(input_df[col])

        # Verificar las columnas esperadas por el modelo
        schema = model.metadata.get_input_schema()
        if schema is None:
            expected_columns = input_df.columns.tolist()
        else:
            expected_columns = schema.input_names()

        for col in expected_columns:
            if col not in input_df:
                input_df[col] = 0  # Completar con ceros si falta alguna columna
        input_df = input_df[expected_columns]  # Reordenar columnas

        # Realizar predicción
        prediction = model.predict(input_df)

        # Intentar decodificar el target si hay un LabelEncoder para Y
        try:
            label_encoder_path = descargar_artefacto(run_id, "label_encoder_y.pkl")
            with open(label_encoder_path, "rb") as f:
                label_encoder_y = pickle.load(f)
            prediction = label_encoder_y.inverse_transform(prediction)
        except Exception as e:
            print(f"[WARNING] No se pudo decodificar el target: {e}")

        return {
            "model_used": model_name,
            "version": model_version,
            "prediction": prediction.tolist()
        }

    except Exception as e:
        print(f"[ERROR] Fallo en /predict: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


