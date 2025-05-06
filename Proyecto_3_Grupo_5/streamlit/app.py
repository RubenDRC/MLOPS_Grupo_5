# app.py
# ---------------------------------------------------------------
# UI sencilla que consume la API FastAPI (fastapi‑service:8000)
# y muestra la predicción de re‑ingreso (<30 días) de pacientes
# diabéticos.  Adaptado a Proyecto 3 – K8s / MinIO / MLflow.
# ---------------------------------------------------------------
import os, requests, json
import pandas as pd
import streamlit as st

# ─────────────── Configuración ────────────────
API_HOST = os.getenv("FASTAPI_ENDPOINT", "http://fastapi-service:8000")

# ──────────────── utilidades ──────────────────
@st.cache_data(show_spinner=False, ttl=3600)
def get_models():
    try:
        r = requests.get(f"{API_HOST}/models", timeout=3)
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception:
        return pd.DataFrame()

def send_prediction(payload: dict, model: str):
    r = requests.post(
        f"{API_HOST}/predict?model_name={model}",
        json={"data": payload},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

# ────────────────── UI ─────────────────────────
st.title("🩺 Readmisión de Pacientes Diabéticos (<30 días)")
st.markdown(
    "Esta app consulta el modelo **RandomForest_Diabetes** "
    "registrado en MLflow (stage *Production*) mediante la API FastAPI."
)

# ---------- Panel lateral ----------
with st.sidebar:
    st.header("ℹ️  Modelo disponible")
    models_df = get_models()
    if not models_df.empty:
        production = models_df[models_df["stage"] == "Production"]
        model_name = st.selectbox(
            "Selecciona modelo",
            production["name"].unique(),
            index=0 if "RandomForest_Diabetes" in production["name"].values else 0
        )
        st.caption(f"Versión Production actual: {production.iloc[0]['version']}")
    else:
        st.error("No se pudo obtener la lista de modelos.")
        st.stop()

# ---------- Formulario de entrada ----------
st.header("📋 Formulario (variables principales)")

cols = st.columns(3)
age          = cols[0].selectbox("Edad", ["[0-10)","[10-20)","[20-30)","[30-40)","[40-50)","[50-60)","[60-70)","[70-80)","[80-90)","[90-100)"])
gender       = cols[1].selectbox("Género", ["Male","Female","Unknown/Invalid"])
time_hosp    = cols[2].number_input("Días en hospital", 1, 14, 3)

num_labs     = st.number_input("Número procedimientos de lab", 0, 132, 45)
num_meds     = st.number_input("Número de medicamentos", 1, 81, 13)
insulin      = st.selectbox("Insulina", ["No","Up","Down","Steady"])
change_flag  = st.selectbox("¿Cambio de medicación?", ["No","Ch"])
diabetes_med = st.selectbox("¿Recibió medicamentos para diabetes?", ["No","Yes"])

submit = st.button("🔮 Predecir")

# ---------- Predicción ----------
if submit:
    with st.spinner("Consultando modelo…"):
        payload = {
            "age": age,
            "gender": gender,
            "time_in_hospital": time_hosp,
            "num_lab_procedures": num_labs,
            "num_medications": num_meds,
            "insulin": insulin,
            "change_flag": change_flag,
            "diabetesMed": diabetes_med
        }
        try:
            result = send_prediction(payload, model_name)
            st.success(f"Predicción: **{result['prediction'][0]}** "
                       f"(modelo v{result['version']})")
        except requests.HTTPError as err:
            st.error(f"API error: {err.response.text}")
        except Exception as e:
            st.error(f"Error inesperado: {e}")

st.divider()
st.caption("Proyecto 3 – MLOps (2025) ·  Grupo 5")
