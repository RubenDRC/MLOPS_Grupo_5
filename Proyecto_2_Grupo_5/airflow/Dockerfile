FROM apache/airflow:2.7.0

# Cambiar a usuario root para poder instalar paquetes
USER root

# Copiar archivo de requisitos
COPY requirements.txt /requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /requirements.txt

# Volver al usuario airflow
USER airflow

