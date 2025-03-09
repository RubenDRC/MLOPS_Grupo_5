# airflow/Dockerfile
FROM apache/airflow:2.7.0

# Cambiamos a usuario 'airflow'
USER airflow

# Agregamos ~/.local/bin al PATH
ENV PATH="/home/airflow/.local/bin:${PATH}"

# Instalamos paquetes extra que requieras
RUN pip install --no-cache-dir apache-airflow-providers-mysql mysql-connector-python


