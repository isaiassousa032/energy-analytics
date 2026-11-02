"""DAG de teste do ambiente: confere dbt, DuckDB, volumes e a pool 'duckdb'."""

from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task


@dag(
    dag_id="smoke_test",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["infra"],
)
def smoke_test():
    dbt_version = BashOperator(
        task_id="dbt_version",
        bash_command="$DBT_BIN --version",
    )

    @task(pool="duckdb")
    def check_duckdb():
        from pathlib import Path

        import duckdb

        db_path = Path("/opt/airflow/project/warehouse/_smoke_test.duckdb")
        con = duckdb.connect(str(db_path))
        try:
            con.execute("create or replace table t as select 42 as answer")
            answer = con.execute("select answer from t").fetchone()[0]
        finally:
            con.close()
            db_path.unlink(missing_ok=True)
            Path(str(db_path) + ".wal").unlink(missing_ok=True)
        assert answer == 42
        return f"duckdb {duckdb.__version__} ok"

    dbt_version >> check_duckdb()


smoke_test()
