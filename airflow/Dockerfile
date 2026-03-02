FROM apache/airflow:2.10.4-python3.11

USER root
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

USER airflow

ARG AIRFLOW_VERSION=2.10.4
ARG PYTHON_VERSION=3.11
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir \
    -r /tmp/requirements.txt \
    --constraint "${CONSTRAINT_URL}"