# Usa Python 3.10 como imagen base
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia y actualiza las dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia los archivos de la aplicación
COPY main.py .
COPY data ./data
COPY models ./models

# Exponer el puerto de la API
EXPOSE 8000

# Ejecutar la API con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]