# Streamlit
import streamlit as st
import requests
import pandas as pd
from datetime import date

st.title("Predicción del Precio de Vivienda")

st.markdown("Usa un modelo MLflow para predecir el valor de una vivienda con base en sus características.")

with st.form("prediction_form"):
    model_name = st.text_input("Nombre del modelo en MLflow", "RandomForestModel_Move")

    inputs = {
        "brokered_by": str(st.number_input("ID del agente (brokered_by)", min_value=0.0, value=51868.0, step=1.0)),
        "status": st.selectbox("Estado de la vivienda", ["for_sale", "under_construction"]),
        "bed": st.number_input("Número de habitaciones (bed)", min_value=0, value=5),
        "bath": st.number_input("Número de baños (bath)", min_value=0, value=3),
        "acre_lot": st.number_input("Tamaño del lote en acres (acre_lot)", min_value=0.0, value=0.12),
        "street": str(st.number_input("ID de la calle (street)", min_value=0.0, value=1499905.0, step=1.0)),
        "city": st.text_input("Ciudad", "Enfield"),
        "state": st.text_input("Estado", "Connecticut"),
        "zip_code": str(st.number_input("Código postal (zip_code)", min_value=0.0, value=6082.0, step=1.0)),
        "house_size": st.number_input("Tamaño en pies cuadrados (house_size)", min_value=0, value=3117),
        "prev_sold_date": st.date_input("Fecha de última venta", value=date(2014, 7, 1)).isoformat()
    }

    submitted = st.form_submit_button("Predecir precio")

if submitted:
    st.info("Enviando solicitud al backend...")

    try:
        response = requests.post(
            url=f"http://10.43.101.188:30190/predict?model_name={model_name}",
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


