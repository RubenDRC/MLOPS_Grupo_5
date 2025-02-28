# Usa la imagen oficial de TensorFlow Extended (TFX)
FROM tensorflow/tfx:1.16.0

# Configurar el directorio de trabajo dentro del contenedor
WORKDIR /tfx

# Instalar `uv`
RUN pip install uv

# Copiar el archivo de dependencias
COPY pyproject.toml /tfx/

# Instalar dependencias con `uv`
RUN uv venv && \
    uv pip install -e /tfx

# Exponer los puertos de Jupyter y TensorBoard
EXPOSE 8888 6006

# Definir el comando de inicio con el entorno virtual de `uv`
CMD ["/tfx/.venv/bin/jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]