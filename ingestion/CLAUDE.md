# ingestion/: regras específicas

- Estrutura prevista: `sources/` (ONS e Open-Meteo), `loaders/` (código específico de warehouse, hoje só Snowflake) e `utils/` (HTTP com retry e backoff, caminhos, log).
- Aterrissagem local em `data/landing/<fonte>/<dataset>/ano=AAAA/mes=MM/` (fora do Git). A carga no Snowflake faz `PUT` no stage e `COPY INTO` o schema `BRONZE`.
- Bronze preserva o dado original: **todas as colunas como texto** mais metadados `_ingested_at`, `_source_file` e `_batch_id`. Conversão de tipos só no dbt (staging).
- Idempotência: reprocessar um período substitui a partição, nunca duplica. Registre cada carga em `bronze._load_log`.
- Falhe de forma explícita: valide schema esperado e linhas maiores que zero em cada extração.
- ONS: prefira Parquet e use CSV nos meses sem Parquet (o tipo das colunas muda entre anos, e ausências vêm como texto vazio). Veja `docs/data_sources.md`.
- Open-Meteo: requisições de 1 ano por cidade, pausa entre elas (cerca de 3 s), tratamento de 429, e cache local. O ERA5 tem 5 dias de atraso: nunca peça os últimos 5 dias com `models=era5`.
- Código específico de warehouse fica só em `loaders/`, atrás de uma interface comum (para migrar para Databricks).
- Credenciais só por variáveis de ambiente. Nunca grave segredos em arquivos.
