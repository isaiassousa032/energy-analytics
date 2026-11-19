# Energy Analytics: contexto para o Claude Code

## O que é o projeto
Projeto de portfólio de **Analytics Engineering** sobre o setor elétrico brasileiro. Integra dados públicos do ONS (carga e geração de energia) com clima do Open-Meteo para responder perguntas de demanda, clima versus demanda e geração por fonte, com modelagem dimensional, testes dbt e dashboard no Power BI. O autor está desenvolvendo habilidades de Analytics Engineering: explique decisões de forma breve e objetiva, em português.

## Estado atual (detalhes em `docs/project_status.md`)
- O projeto foi recomeçado em novembro de 2026. A versão anterior (Airflow, DuckDB e Docker Compose) está na tag `v0-airflow-duckdb`.
- Fase 00 (fundação e ambiente) em fechamento. Fase 01 (negócio e requisitos) em andamento: indicadores, dicionário de métricas e exploração do ONS prontos; Open-Meteo, granularidade, período e `docs/requirements.md` pendentes.
- A conta trial do Snowflake já existe e termina por volta de 2027-02-04. O calendário das fases está em `docs/planning.md`.

## Stack e decisões fixas
- Ingestão em Python 3.12. Warehouse: Snowflake (trial), com migração futura possível para Databricks, então mantenha o SQL portátil. dbt Core 1.x com dbt-snowflake (não usar dbt v2 por ora). Power BI Desktop para o consumo. Desenvolvimento em GitHub Codespaces com devcontainer.
- Fora desta versão: Airflow, Docker Compose, DuckDB no projeto (só em scripts de exploração locais, instalado à mão e fora do `requirements.txt`), PySpark, Kafka, pytest e Ruff.
- Arquitetura medalhão no Snowflake: database `ENERGY_ANALYTICS` com schemas `BRONZE` (Python carrega tudo como texto, mais metadados), `SILVER` (dbt: staging e intermediate) e `GOLD` (dbt: marts). Papéis `LOADER`, `TRANSFORMER` e `REPORTER`. Warehouse X-Small com auto-suspend de 60 s e resource monitor.

## Convenções
- Commits em inglês, no padrão Conventional Commits (`feat`, `fix`, `docs`, `chore`, `refactor`, `ci`), com escopo quando fizer sentido: `feat(ingestion): add ONS daily load extractor`.
- Uma branch curta por tarefa (`feat/...`, `docs/...`, `fix/...`, `chore/...`), pull request e squash merge na `main`. Não commite direto na `main` sem o autor pedir.
- Tabelas e colunas em inglês, snake_case. Documentação em português.
- dbt: `stg_<fonte>__<entidade>`, `int_<descrição>`, `dim_`, `fct_`, `mart_`. Staging como view, intermediate como view ou ephemeral, marts como tabela.
- As métricas são definidas uma vez, no Gold, conforme `docs/metrics_dictionary.md`. O Power BI só consome.
- Dependências com versão fixada (`==`). Peça aprovação antes de adicionar uma nova.

## Segurança e custo (importante)
- Nunca leia, imprima ou commite segredos: `.env`, chaves `.p8` e `.pem`, tokens. As credenciais do Snowflake vêm só de variáveis de ambiente `SNOWFLAKE_*`. Use usuário de serviço com papel mínimo, nunca `ACCOUNTADMIN` no dia a dia.
- `data/`, `.duckdb` e `.parquet` não vão para o Git.
- Antes de rodar algo que consome créditos do Snowflake (`dbt build` ou `run`, cargas, DDL em massa), explique o que vai rodar e peça confirmação. Use `--select` e poucos dados.
- Open-Meteo: limite gratuito de 600 chamadas por minuto, 5.000 por hora e 10.000 por dia. Requisições de 1 ano por cidade, com pausa, sem loops soltos. Uso não comercial e atribuição obrigatória.
- Operações destrutivas de git (force push, reset --hard) só com pedido explícito.

## Fontes de dados (resumo; achados completos em `docs/data_sources.md`)
- **ONS:** bucket público `s3://ons-aws-prod-opendata/dataset/<pasta>/` (região sa-east-1, sem credenciais), CC BY 4.0. MVP: `carga_energia_di` (dia por subsistema) e `balanco_energia_subsistema_ho` (hora por subsistema, mais a linha `SIN`; geração hidráulica, térmica, eólica e solar, carga e intercâmbio). Dados de 2000 a 2026.
- **Pegadinhas que o código precisa tratar:**
  - valores numéricos como texto até 2021 (carga diária) e 2022 (balanço), e texto vazio no lugar de nulo: use `nullif` e `try_cast`;
  - códigos de subsistema com espaços à direita em 2026: use `trim`, e junte datasets sempre pelo código, nunca pelo nome;
  - a linha `SIN` do balanço é a soma dos quatro subsistemas: exclua ao agregar;
  - uma linha espúria (S, 2013-02-02 00:00:01) e três dias sem dado (2013-12-01, 2014-02-01, 2015-04-09);
  - horários locais com horário de verão (dias de 23 horas até 2018): não converta para UTC, agregue por dia;
  - intercâmbio: positivo = exportação (inferido dos dados).
- **Open-Meteo:** Historical Weather API (`archive-api.open-meteo.com/v1/archive`). Proposta: `models=era5_seamless`, variáveis diárias `temperature_2m_mean` e `precipitation_sum`, `timezone=America/Sao_Paulo`. O ERA5 tem 5 dias de atraso. Cidades candidatas: SE (São Paulo, Rio de Janeiro, Belo Horizonte, Brasília), S (Porto Alegre, Curitiba), NE (Salvador, Fortaleza, Recife), N (Manaus, Belém). A escolha final está pendente.

## Comandos úteis
- ONS: `python scripts/explore_ons.py list`, `profile PASTA` ou `check` (precisa de `pip install duckdb`, só local).
- Open-Meteo: `python scripts/explore_open_meteo.py check`.
- GitHub: `gh issue list --milestone "Fase 01 — Negócio e requisitos"`. Os milestones e as issues das fases 00 a 09 já existem.
- dbt, quando existir o projeto: `dbt build --select <modelo>+` dentro de `dbt/energy_analytics`.

## Onde está o resto (leia sob demanda, não carregue tudo)
- `docs/planning.md`: plano completo (fases, critérios de pronto, janela do trial, decisões em aberto).
- `docs/project_status.md`: estado atual e próximos passos. Atualize ao fim de cada tarefa.
- `docs/metrics_dictionary.md`: métricas M01 a M15 (fonte da verdade).
- `docs/data_sources.md`: fontes, contratos dos dicionários do ONS e achados.
- As subpastas `ingestion/` e `dbt/` têm seu próprio `CLAUDE.md`, carregado quando você trabalha nelas.

## Como trabalhar com o autor
- Responda em português e seja objetivo. Para tarefas grandes, proponha um plano curto antes de editar.
- Uma tarefa corresponde a uma issue e a uma branch pequena. Ao terminar: atualize `docs/project_status.md` e sugira o commit e o pull request.
- Se algo for ambíguo ou arriscado (custo, segurança, mudança de arquitetura), pergunte antes.
