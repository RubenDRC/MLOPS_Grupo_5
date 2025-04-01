# streamlit/app.py
import streamlit as st
import requests
import pandas as pd

# ----------------------------------------------------------------------------

# El "service name" de Docker Compose es "fastapi", 
FASTAPI_URL = "http://fastapi:8000/predict"

MODEL_NAME = "RandomForestModel" 
# ----------------------------------------------------------------------------

st.title("Predicción de Cover Type - Proyecto MLOps")

st.markdown("""
Esta aplicación de Streamlit consume la **API de FastAPI** para realizar predicciones
sobre el tipo de cobertura forestal. 
""")

# Inputs para cada campo que requiere tu endpoint /predict:

Elevation = st.number_input("Elevation (int)", value=2500)
Aspect = st.number_input("Aspect (int)", value=45)
Slope = st.number_input("Slope (int)", value=10)
Horizontal_Distance_To_Hydrology = st.number_input("Horizontal_Distance_To_Hydrology", value=30)
Vertical_Distance_To_Hydrology = st.number_input("Vertical_Distance_To_Hydrology", value=10)
Horizontal_Distance_To_Roadways = st.number_input("Horizontal_Distance_To_Roadways", value=100)
Hillshade_9am = st.number_input("Hillshade_9am", value=220)
Hillshade_Noon = st.number_input("Hillshade_Noon", value=230)
Hillshade_3pm = st.number_input("Hillshade_3pm", value=120)
Horizontal_Distance_To_Fire_Points = st.number_input("Horizontal_Distance_To_Fire_Points", value=150)
Wilderness_Area = st.text_input("Wilderness_Area", value="Wilderness_Area_3")
Soil_Type = st.text_input("Soil_Type", value="Soil_11")

# Botón para predecir
if st.button("Predecir"):
    # payload para FastAPI
    input_data = {
        "Elevation": Elevation,
        "Aspect": Aspect,
        "Slope": Slope,
        "Horizontal_Distance_To_Hydrology": Horizontal_Distance_To_Hydrology,
        "Vertical_Distance_To_Hydrology": Vertical_Distance_To_Hydrology,
        "Horizontal_Distance_To_Roadways": Horizontal_Distance_To_Roadways,
        "Hillshade_9am": Hillshade_9am,
        "Hillshade_Noon": Hillshade_Noon,
        "Hillshade_3pm": Hillshade_3pm,
        "Horizontal_Distance_To_Fire_Points": Horizontal_Distance_To_Fire_Points,
        "Wilderness_Area": Wilderness_Area,
        "Soil_Type": Soil_Type
    }

    # URL con query param model_name=...
    url = f"{FASTAPI_URL}?model_name={MODEL_NAME}"

    try:
        # Envío POST
        response = requests.post(url, json=input_data)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicción: {result.get('prediction')}")
            st.write("Modelo utilizado:", result.get('model_used'), 
                     "\nVersión del modelo:", result.get('version'))
        else:
            st.error(f"Error {response.status_code}. {response.text}")
    except Exception as e:
        st.error(f"No se pudo conectar con la API. Detalles: {e}")
