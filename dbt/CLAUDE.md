# dbt/: regras específicas

- Projeto em `dbt/energy_analytics`. dbt Core 1.x com dbt-snowflake. O `profiles.yml` lê tudo por `env_var()`, com targets `dev` (schema pessoal) e `prod` (`SILVER` e `GOLD`).
- Camadas: `staging` (views), `intermediate` (view ou ephemeral, só quando ajudar a clareza) e `marts` (tabelas). Nomes: `stg_<fonte>__<entidade>`, `int_<descrição>`, `dim_`, `fct_`, `mart_`.
- Staging trata as pegadinhas do ONS: `nullif(trim(coluna), '')` e `try_cast` nos números, `trim` nos códigos de subsistema, filtro de linhas sem valor e da linha espúria, exclusão da linha `SIN` ao somar subsistemas, timestamps locais mantidos (derive `reference_date`, sem converter para UTC).
- Os testes seguem os dicionários do ONS (`docs/data_sources.md`): `not_null`, valor maior que zero, chave única. Use `severity: warn` nos casos de defeito conhecido de origem.
- As métricas vêm de `docs/metrics_dictionary.md` e são calculadas uma única vez, nos marts. Mantenha os nomes técnicos do dicionário.
- Portabilidade (Databricks): SQL padrão; funções específicas do Snowflake isoladas em macros com `adapter.dispatch`; evite VARIANT e FLATTEN fora do staging.
- Economia de créditos: sempre `--select` durante o desenvolvimento. Peça confirmação antes de `dbt build`, `run` ou `seed` completos.
- Todo modelo novo vem com descrição de colunas e testes no YAML, no mesmo pull request.
