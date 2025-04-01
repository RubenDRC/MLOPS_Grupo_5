# streamlit/Dockerfile
FROM python:3.9-slim
 
WORKDIR /app
 
ENV MLFLOW_TRACKING_URI=http://10.43.101.195:5000
ENV MLFLOW_S3_ENDPOINT_URL=http://10.43.101.195:9000
ENV AWS_ACCESS_KEY_ID=admin
ENV AWS_SECRET_ACCESS_KEY=supersecret
 
# Instala requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
 
# Copia la app de streamlit
COPY app.py .
 
# Expone el puerto 8503 para streamlit
EXPOSE 8503
 
# Comando de arranque
CMD ["streamlit", "run", "app.py", "--server.port=8503", "--server.address=0.0.0.0"]
CMD ["streamlit", "run", "app.py", "--server.port=8503", "--server.address=0.0.0.0"]


