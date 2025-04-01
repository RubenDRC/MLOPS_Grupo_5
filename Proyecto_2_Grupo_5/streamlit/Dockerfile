# streamlit/Dockerfile
FROM python:3.9-slim

WORKDIR /app

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


