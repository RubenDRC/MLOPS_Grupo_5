# Usa la imagen oficial de TensorFlow Extended (TFX)
FROM tensorflow/tfx:1.16.0

# Configurar el directorio de trabajo dentro del contenedor
WORKDIR /tfx

# Instalar herramientas necesarias
RUN pip install --upgrade pip uv setuptools wheel build

# Copiar el archivo de dependencias
COPY pyproject.toml /tfx/

# Crear entorno virtual con `uv`
RUN uv venv

# Asegurar que pip está instalado dentro del entorno virtual
RUN /tfx/.venv/bin/python -m ensurepip --default-pip
RUN /tfx/.venv/bin/pip install --upgrade pip setuptools wheel build

# Instalar dependencias dentro del entorno virtual
RUN /tfx/.venv/bin/pip install --no-build-isolation -e /tfx

# Exponer los puertos de Jupyter y TensorBoard
EXPOSE 8888 6006

# Asegurar que Jupyter Notebook inicie en la carpeta correcta
ENTRYPOINT ["/bin/bash", "-c", "cd /tfx/notebooks && exec jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root"]