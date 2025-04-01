# Usa una imagen base de Python
FROM python:3.10

# Configurar el directorio de trabajo
WORKDIR /app

# Instalar UV
RUN pip install --no-cache-dir --upgrade pip && pip install uv

# Copiar el archivo de dependencias
COPY pyproject.toml ./

# Instalar dependencias del proyecto con UV
RUN uv pip install --system --deps pyproject.toml

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto 8888
EXPOSE 8888

# Comando para iniciar FastAPI con Uvicorn usando UV
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888", "--reload"]
