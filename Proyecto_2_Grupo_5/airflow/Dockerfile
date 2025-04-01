FROM apache/airflow:2.7.0

COPY requirements.txt /
COPY dags /opt/airflow/dags

USER airflow

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /requirements.txt

