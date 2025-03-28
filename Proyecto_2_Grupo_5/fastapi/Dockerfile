FROM python:3.9

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY requirements.txt .
COPY main.py .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto para la API
EXPOSE 8000

# Comando para ejecutar FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

