# Streamlit
import streamlit as st
import requests
import pandas as pd
from datetime import date

st.title("Predicción del Precio de Vivienda")

st.markdown("Usa un modelo MLflow para predecir el valor de una vivienda con base en sus características.")

with st.form("prediction_form"):
    model_name = st.text_input("Nombre del modelo en MLflow", "RandomForestModel")

    inputs = {
        "brokered_by": st.selectbox("Agente/Broker", ["RE/MAX", "Keller Williams", "Coldwell Banker", "Century 21", "Otro"]),
        "status": st.selectbox("Estado de la vivienda", ["for_sale", "under_construction"]),
        "bed": st.number_input("Número de habitaciones (bed)", min_value=0, value=3),
        "bath": st.number_input("Número de baños (bath)", min_value=0, value=2),
        "acre_lot": st.number_input("Tamaño del lote en acres (acre_lot)", min_value=0.0, value=0.25),
        "street": st.text_input("Calle", "123 Main St"),
        "city": st.text_input("Ciudad", "Springfield"),
        "state": st.text_input("Estado", "IL"),
        "zip_code": st.text_input("Código postal", "62704"),
        "house_size": st.number_input("Tamaño en pies cuadrados (house_size)", min_value=0, value=1500),
        "prev_sold_date": st.date_input("Fecha de última venta", value=date(2020, 1, 1)).isoformat()
    }

    submitted = st.form_submit_button("Predecir precio")

if submitted:
    st.info("Enviando solicitud al backend...")

    try:
        response = requests.post(
            url=f"http://10.43.101.195:30190/predict?model_name={model_name}",
            json=inputs
        )

        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicción de precio: ${result['prediccion'][0]:,.2f}")
            st.info(f"Modelo: {result['modelo']} (versión {result['version']})")
        else:
            st.error(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"No se pudo conectar al backend: {str(e)}")

