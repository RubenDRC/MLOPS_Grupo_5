#Streamlit
import streamlit as st
import requests
import pandas as pd

st.title("Predicción de Reingreso por Diabetes")

st.markdown("Usa un modelo MLflow para predecir si un paciente será reingresado.")

with st.form("prediction_form"):
    model_name = st.text_input("Modelo MLflow", "RandomForestModel")

    inputs = {
        "race": st.selectbox("Raza", ["Caucasian", "AfricanAmerican", "Asian", "Hispanic", "Other"]),
        "gender": st.selectbox("Género", ["Male", "Female"]),
        "age": st.selectbox("Edad", ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]),
        "weight": st.text_input("Peso", "no aplica"),
        "admission_type_id": st.text_input("Tipo de admisión", "3"),
        "discharge_disposition_id": st.text_input("Tipo de egreso", "1"),
        "admission_source_id": st.text_input("Fuente de admisión", "1"),
        "time_in_hospital": st.text_input("Días hospitalizado", "2"),
        "payer_code": st.text_input("Código de pagador", "BC"),
        "medical_specialty": st.text_input("Especialidad médica", "Surgery-General"),
        "num_lab_procedures": st.text_input("Procedimientos lab.", "5"),
        "num_procedures": st.text_input("Procedimientos", "4"),
        "num_medications": st.text_input("Medicamentos", "11"),
        "number_outpatient": st.text_input("Visitas ambulatorias", "0"),
        "number_emergency": st.text_input("Emergencias", "0"),
        "number_inpatient": st.text_input("Internaciones", "0"),
        "diag_1": st.text_input("Diagnóstico 1", "196"),
        "diag_2": st.text_input("Diagnóstico 2", "199"),
        "diag_3": st.text_input("Diagnóstico 3", "250"),
        "number_diagnoses": st.text_input("Diagnósticos", "7"),
        "max_glu_serum": st.selectbox("Glucosa sérica máx.", ["None", "Norm", ">200", ">300", "no aplica"]),
        "a1cresult": st.selectbox("Resultado A1C", ["None", "Norm", ">7", ">8", "no aplica"]),
    }

    meds = [
        "metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
        "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
        "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide",
        "examide", "citoglipton", "insulin", "glyburide_metformin",
        "glipizide_metformin", "glimepiride_pioglitazone",
        "metformin_rosiglitazone", "metformin_pioglitazone"
    ]
    for med in meds:
        inputs[med] = st.selectbox(med, ["No", "Steady", "Up", "Down"], key=med)

    inputs["change"] = st.selectbox("¿Cambio?", ["No", "Ch"])
    inputs["diabetesmed"] = st.selectbox("¿Medicación diabetes?", ["Yes", "No"])

    submitted = st.form_submit_button("Predecir")

if submitted:
    st.info("Enviando solicitud...")
    response = requests.post(f"http://10.43.101.195:30190/predict?model_name={model_name}", json=inputs)
    if response.status_code == 200:
        result = response.json()
        st.success(f" Predicción: {result['prediccion'][0]}")
        st.info(f"Modelo: {result['modelo']} (versión {result['version']})")
    else:
        st.error(f" Error {response.status_code}: {response.text}")

