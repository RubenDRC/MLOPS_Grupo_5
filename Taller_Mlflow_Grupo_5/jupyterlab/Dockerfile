# Usa la imagen base de Python 3.9
FROM python:3.9

# Definir argumentos para MinIO (S3) y MySQL
ARG MLFLOW_S3_ENDPOINT_URL=http://10.43.101.195:9000
ARG AWS_ACCESS_KEY_ID=admin
ARG AWS_SECRET_ACCESS_KEY=admingrupo5

# Configurar variables de entorno
ENV MLFLOW_S3_ENDPOINT_URL=$MLFLOW_S3_ENDPOINT_URL
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

# Crear directorio de trabajo
WORKDIR /work

# Instalar cliente de MySQL y herramientas necesarias
RUN apt-get update && apt-get install -y \
    default-mysql-client && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivos al contenedor
COPY . .

# Instalar Jupyter, MLflow y dependencias necesarias
RUN pip install --no-cache-dir jupyterlab==3.6.1 jupyter==1.0.0 && \
    pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8888 para JupyterLab
EXPOSE 8888

# Comando de inicio
ENTRYPOINT ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root"]
