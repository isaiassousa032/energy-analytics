# Imagem do Airflow do Energy Analytics (não confundir com .devcontainer/Dockerfile,
# que prepara apenas o Codespace). Contexto de build: raiz do repositório.
FROM apache/airflow:3.3.2-python3.12

ARG AIRFLOW_VERSION=3.3.2

USER airflow

# 1) Bibliotecas de ingestão no ambiente do Airflow.
#    "apache-airflow==" evita que o pip altere a versão do Airflow.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /tmp/requirements.txt

# 2) dbt em virtualenv separado: evita conflito de dependências com o Airflow.
#    Nas DAGs, chame o binário via variável DBT_BIN (BashOperator).
COPY requirements-dbt.txt /tmp/requirements-dbt.txt
RUN PIP_USER=false python -m venv /home/airflow/dbt-venv \
    && PIP_USER=false /home/airflow/dbt-venv/bin/pip install --no-cache-dir -r /tmp/requirements-dbt.txt \
    && chmod -R g=u /home/airflow/dbt-venv
