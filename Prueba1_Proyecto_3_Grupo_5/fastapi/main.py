# main.py  –  API de inferencia para Proyecto 3 (Diabetes Readmission)
# ────────────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
import os, tempfile, pickle, boto3
from mlflow.artifacts import download_artifacts

# ──────────── Config MLflow + MinIO (DNS internos de K8s) ───────────
os.environ["MLFLOW_TRACKING_URI"]     = "http://mlflow:5000"
os.environ["MLFLOW_S3_ENDPOINT_URL"]  = "http://minio:9000"
os.environ["AWS_ACCESS_KEY_ID"]       = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"]   = "supersecret"
mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

MINIO_BUCKET = "mlflows3"   # nombre usado por el Helm chart MLflow‑S3

# ────────────────────────── FastAPI app ─────────────────────────────
app = FastAPI(
    title="API – RandomForest Diabetes Readmission",
    version="1.0",
    description=(
        "Devuelve la probabilidad de re‑ingreso (<30 días) para pacientes "
        "diabéticos. Consume el modelo en stage **Production** del "
        "experimento `Proyecto_3_Diabetes_Readmission`."
    )
)

class PredictPayload(BaseModel):
    """
    JSON libre — solo envía las columnas que quieras.
    Todas las columnas que espere el modelo y no estén en la petición
    se rellenarán con 0 (o cadena vacía); categorías serán codificadas
    vía LabelEncoder si existe en encoders.pkl.
    """
    data: Dict[str, Any] = Field(..., example={
        "age": "[60-70)",
        "race": "Caucasian",
        "gender": "Female",
        "time_in_hospital": 5,
        "num_lab_procedures": 45,
        "num_medications": 13,
        "insulin": "Up",
        "change_flag": "Yes",
        "diabetesMed": "Yes"
    })

# ──────────────────── utilidades de artefactos ──────────────────────
def _download_artifact(run_id: str, filename: str) -> str:
    """
    Descarga un artefacto de MLflow; si falla, recurre a MinIO.
    Devuelve la ruta local del archivo temporal.
    """
    try:
        uri = f"runs:/{run_id}/{filename}"
        return download_artifacts(uri)
    except Exception:
        # fallback MinIO
        s3 = boto3.client(
            "s3",
            endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"],
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
        )
        tmp = tempfile.NamedTemporaryFile(delete=False).name
        key = f"artifacts/1/{run_id}/artifacts/{filename}"  # experiment_id=1
        s3.download_file(MINIO_BUCKET, key, tmp)
        return tmp

def _get_production_model(model_name: str):
    client = MlflowClient()
    vers = client.get_latest_versions(model_name, stages=["Production"])
    if not vers:
        raise HTTPException(status_code=404,
                            detail=f"No hay versión Production para '{model_name}'")
    v = vers[0]
    model = mlflow.pyfunc.load_model(f"models:/{model_name}/{v.version}")
    return model, v.run_id, v.version

# ─────────────────────────── Endpoints ──────────────────────────────
@app.get("/")
def root():
    return {"msg": "Bienvenido – consulte /docs para la interfaz OpenAPI"}

@app.get("/models")
def available_models():
    client = MlflowClient()
    listado = []
    for m in client.search_registered_models():
        for v in m.latest_versions:
            listado.append({"name": m.name, "version": v.version,
                            "stage": v.current_stage})
    return listado

@app.post("/predict")
def predict(payload: PredictPayload, model_name: str = "RandomForest_Diabetes"):
    try:
        # 1) cargar modelo Production
        model, run_id, version = _get_production_model(model_name)

        # 2) encoders
        enc_path = _download_artifact(run_id, "encoders.pkl")
        with open(enc_path, "rb") as f:
            encoders = pickle.load(f)

        # 3) preparar dataframe
        df = pd.DataFrame([payload.data])
        for col, le in encoders.items():
            if col in df:
                df[col] = le.transform(df[col].astype(str))
            else:
                # columna faltante → cero
                df[col] = 0

        # rellenar resto de columnas inexistentes
        expected = model.metadata.get_input_schema().input_names()
        for col in expected:
            if col not in df:
                df[col] = 0
        df = df[expected]

        # 4) predecir
        preds = model.predict(df)

        # 5) intentar decodificar y probabilidad
        out = preds.tolist()
        try:
            le_y_path = _download_artifact(run_id, "label_encoder_y.pkl")
            with open(le_y_path, "rb") as f:
                le_y = pickle.load(f)
            out = le_y.inverse_transform(preds).tolist()
        except Exception:
            pass

        return {"model": model_name, "version": version, "prediction": out}

    except HTTPException as e:
        raise e
    except Exception as e:
        print("[ERROR]", e)
        raise HTTPException(status_code=500, detail=str(e))
