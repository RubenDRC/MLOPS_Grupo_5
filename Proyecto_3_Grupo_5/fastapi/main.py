from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
import mlflow
import mlflow.pyfunc
import pandas as pd
import os
import pickle
from mlflow.tracking import MlflowClient

# Configurar MLflow con variables de entorno desde Kubernetes
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://10.152.183.196:5000"))

app = FastAPI(
    title="API Predicciones Diabetes",
    description="Predicciones usando modelos registrados en MLflow",
    version="1.0"
)

# Schema de entrada

class PredictionInput(BaseModel):
    race: str = Field(..., alias="race")
    gender: str = Field(..., alias="gender")
    age: str = Field(..., alias="age")
    weight: str = Field(..., alias="weight")
    admission_type_id: str = Field(..., alias="admission_type_id")
    discharge_disposition_id: str = Field(..., alias="discharge_disposition_id")
    admission_source_id: str = Field(..., alias="admission_source_id")
    time_in_hospital: str = Field(..., alias="time_in_hospital")
    payer_code: str = Field(..., alias="payer_code")
    medical_specialty: str = Field(..., alias="medical_specialty")
    num_lab_procedures: str = Field(..., alias="num_lab_procedures")
    num_procedures: str = Field(..., alias="num_procedures")
    num_medications: str = Field(..., alias="num_medications")
    number_outpatient: str = Field(..., alias="number_outpatient")
    number_emergency: str = Field(..., alias="number_emergency")
    number_inpatient: str = Field(..., alias="number_inpatient")
    diag_1: str = Field(..., alias="diag_1")
    diag_2: str = Field(..., alias="diag_2")
    diag_3: str = Field(..., alias="diag_3")
    number_diagnoses: str = Field(..., alias="number_diagnoses")
    max_glu_serum: str = Field(..., alias="max_glu_serum")
    a1cresult: str = Field(..., alias="a1cresult")
    metformin: str = Field(..., alias="metformin")
    repaglinide: str = Field(..., alias="repaglinide")
    nateglinide: str = Field(..., alias="nateglinide")
    chlorpropamide: str = Field(..., alias="chlorpropamide")
    glimepiride: str = Field(..., alias="glimepiride")
    acetohexamide: str = Field(..., alias="acetohexamide")
    glipizide: str = Field(..., alias="glipizide")
    glyburide: str = Field(..., alias="glyburide")
    tolbutamide: str = Field(..., alias="tolbutamide")
    pioglitazone: str = Field(..., alias="pioglitazone")
    rosiglitazone: str = Field(..., alias="rosiglitazone")
    acarbose: str = Field(..., alias="acarbose")
    miglitol: str = Field(..., alias="miglitol")
    troglitazone: str = Field(..., alias="troglitazone")
    tolazamide: str = Field(..., alias="tolazamide")
    examide: str = Field(..., alias="examide")
    citoglipton: str = Field(..., alias="citoglipton")
    insulin: str = Field(..., alias="insulin")
    glyburide_metformin: str = Field(..., alias="glyburide_metformin")
    glipizide_metformin: str = Field(..., alias="glipizide_metformin")
    glimepiride_pioglitazone: str = Field(..., alias="glimepiride_pioglitazone")
    metformin_rosiglitazone: str = Field(..., alias="metformin_rosiglitazone")
    metformin_pioglitazone: str = Field(..., alias="metformin_pioglitazone")
    change: str = Field(..., alias="change")
    diabetesmed: str = Field(..., alias="diabetesmed")

    class Config:
        allow_population_by_field_name = True

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de MLflow para Diabetes", "docs": "/docs"}

# ✅ Descargar artefacto directamente desde el run usando MLflowClient
def descargar_artefacto(run_id: str, filename: str):
    client = MlflowClient()
    return client.download_artifacts(run_id, filename)

@app.post("/predict")
def predecir(datos: PredictionInput, model_name: str):
    try:
        client = MlflowClient()
        versiones = client.get_latest_versions(model_name, stages=["Production"])
        if not versiones:
            raise HTTPException(status_code=404, detail=f"No hay versión 'Production' para el modelo '{model_name}'")

        run_id = versiones[0].run_id
        model_uri = f"models:/{model_name}/Production"
        model = mlflow.pyfunc.load_model(model_uri)

        encoders_path = descargar_artefacto(run_id, "label_encoders.pkl")
        with open(encoders_path, "rb") as f:
            label_encoders = pickle.load(f)

        df = pd.DataFrame([datos.dict()])
        for col, le in label_encoders.items():
            df[col] = le.transform(df[col])

        schema = model.metadata.get_input_schema()
        expected_cols = schema.input_names() if schema else df.columns.tolist()
        for col in expected_cols:
            if col not in df:
                df[col] = 0
        df = df[expected_cols]

        pred = model.predict(df)

        try:
            y_enc_path = descargar_artefacto(run_id, "label_encoder_y.pkl")
            with open(y_enc_path, "rb") as f:
                le_y = pickle.load(f)
            pred = le_y.inverse_transform(pred)
        except:
            pass

        return {
            "modelo": model_name,
            "prediccion": pred.tolist(),
            "version": versiones[0].version
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en /predict: {str(e)}")

