# fastapi/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copiamos el archivo de requerimientos
COPY requirements.txt /app/requirements.txt

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el main.py
COPY main.py /app/main.py

# Exponemos el puerto 8989
EXPOSE 8989

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8989"]

