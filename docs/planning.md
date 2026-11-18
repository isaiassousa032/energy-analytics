# Planejamento do Energy Analytics v2

Versão condensada do planejamento (a original foi escrita fora do repositório). Fonte da verdade para fases, critérios de pronto, janela do trial e decisões em aberto. O estado atual fica em `project_status.md`.

## Objetivo e princípios
Plataforma analítica sobre o setor elétrico brasileiro que responde a três frentes: demanda, clima e demanda, e geração por fonte. Mostrar o ciclo completo de Analytics Engineering, do dado bruto ao insight.

- O dbt é o produto principal: camadas claras, testes, documentação e contratos de colunas.
- Métricas definidas uma vez, no Gold (`metrics_dictionary.md`), nunca no Power BI.
- Portabilidade: código específico de warehouse isolado, para migrar para o Databricks.
- Custo controlado: o trial do Snowflake é limitado; tudo é preparado antes e usado de forma deliberada.
- Reprodutível e seguro: dados e segredos fora do Git; um Codespace novo reproduz o ambiente.

## Perguntas de negócio
- **Demanda:** D1 evolução ao longo do tempo; D2 períodos de maior demanda; D3 comportamento dos subsistemas.
- **Clima e energia:** C1 associação entre temperatura e demanda; C2 como a relação varia por região (região = subsistema); C3 períodos atípicos.
- **Geração:** G1 geração por fonte e por subsistema; G2 relação entre geração e demanda.

## Arquitetura
Fontes (ONS e Open-Meteo) → Python (extração) → arquivos de aterrissagem locais → Python (`PUT` e `COPY INTO`) → BRONZE (texto + metadados) → dbt → SILVER (staging e intermediate) → dbt → GOLD (marts) → Power BI.

Objetos no Snowflake: database `ENERGY_ANALYTICS` com schemas `BRONZE`, `SILVER`, `GOLD` (o dev do dbt usa schemas pessoais); warehouse X-Small com auto-suspend de 60 s e resource monitor; papéis `LOADER`, `TRANSFORMER` e `REPORTER`; usuários de serviço com par de chaves. Scripts em `snowflake/`.

Portabilidade (Databricks): SQL padrão; funções específicas em macros `adapter.dispatch`; código de warehouse só em `ingestion/loaders/`; Bronze reconstruível a partir das fontes; targets do dbt por ambiente; Gold com nomes e tipos estáveis; evitar VARIANT e FLATTEN fora do staging. Databricks Free Edition: só serverless, um SQL warehouse 2X-Small, saída para a internet restrita, uso não comercial; validar a conexão de dbt e Power BI antes de migrar.

## Fases (cada uma com milestone e issues no GitHub)

### Fase 00: Fundação e limpeza
Tag `v0-airflow-duckdb`, limpar a `main`, novo devcontainer (Python 3.12, sem Compose), `requirements.txt`, `.gitignore` e `.env.example` (variáveis `SNOWFLAKE_*` sem valores), README, milestones e issues.
**Pronto quando:** Codespace novo sobe sem Docker Compose, `dbt --version` funciona e o repositório não tem nada de Airflow.

### Fase 01: Negócio e requisitos
Fechar indicadores e dicionário de métricas; explorar o ONS (feito); documentar datasets em `data_sources.md`; avaliar o Open-Meteo e escolher cidades por subsistema; definir granularidade (diária no MVP) e período; escrever `docs/requirements.md`.
**Pronto quando:** cada pergunta de negócio aponta para um dataset e para indicadores definidos.

### Fase 02: Arquitetura e modelagem
Diagrama (`docs/architecture.md`); modelo dimensional (`docs/data_model.md`): dimensões `dim_date`, `dim_subsystem`, `dim_energy_source`, `dim_location`; fatos `fct_load_daily`, `fct_generation_daily`, `fct_weather_daily`; mart `mart_load_vs_temperature`; seed de pesos cidade para subsistema; convenções; rascunho do SQL do Snowflake; materialização, carga idempotente, fuso e tratamento dos valores que violam os dicionários do ONS; testes por modelo.
**Pronto quando:** documentos existem e o grain de cada fato está claro.

### Fase 03: Ingestão com Python
Estrutura `ingestion/`; CLI por fonte com período como parâmetro; ONS do bucket público (Parquet, CSV como alternativa); Open-Meteo por cidade e ano; gravação em `data/landing/`; metadados e log; validações; fatia vertical (um mês, uma cidade) e depois o histórico completo.
**Pronto quando:** histórico completo em `data/landing/` e reexecutar não duplica nem altera arquivos.

### Fase 04: Snowflake, provisionamento e Bronze
Conferir região e edição da conta trial; executar o SQL de `snowflake/`; usuários de serviço (par de chaves) e segredos nos Codespaces secrets; `ingestion/loaders/snowflake.py`; tabela `bronze._load_log`; carregar a fatia e depois o histórico.
**Pronto quando:** Bronze reconcilia com os arquivos, recarregar não duplica e o consumo de créditos é acompanhado.

### Fase 05: dbt, Silver
Projeto `dbt/energy_analytics`, `profiles.yml` com `env_var()`, sources com frescor, staging, intermediate (clima por subsistema), testes e descrição de colunas.
**Pronto quando:** `dbt build` do Silver passa e a documentação cobre todos os modelos.

### Fase 06: dbt, Gold
Dimensões, fatos e marts por pergunta; indicadores do dicionário de métricas; exposures do Power BI; testes de negócio.
**Pronto quando:** `dbt build` completo passa e as três frentes são respondidas por SQL sobre o Gold.

### Fase 07: Power BI e insights
Conexão ao Snowflake com o papel `REPORTER` em modo Import; modelo estrela e medidas DAX; páginas (visão geral, demanda, clima e demanda, geração); PBIP em `powerbi/`; `docs/insights.md`. Rodapé com "Weather data by Open-Meteo.com".
**Pronto quando:** dashboard e insights respondem às perguntas de negócio.

### Fase 08: Automação, CI/CD e documentação
CI em PRs (SQLFluff, `dbt parse` e `compile`, sem consumir créditos); proteger a `main`; workflow agendado (ingestão e `dbt build`) só durante o trial; `dbt docs generate` e publicação; revisar a documentação.
**Pronto quando:** PR com erro não passa no CI e a documentação do dbt está publicada.

### Fase 09: Encerramento do trial e publicação
Decidir o destino (pagamento por uso, Databricks Free Edition ou congelar); exportar snapshots dos marts, dbt docs estático e PBIP com dados importados; README final; varredura de segredos no histórico; release `v1.0.0`; backlog da v2.
**Pronto quando:** o projeto continua demonstrável sem o Snowflake ativo.

## Janela do trial do Snowflake
Trial de 120 dias (oferta de parceiro), 84 dias restantes em 12/11/2026, fim por volta de 04/02/2027. Confira em Snowsight (Admin, Billing) o que acontece ao fim.

| Quando | Foco |
|---|---|
| 12 a 25 nov | Fases 00 e 01 |
| 26 nov a 9 dez | Fases 02 e 03; provisionar o Snowflake em paralelo |
| 10 a 23 dez | Fases 04 e 05 |
| 24 dez a 13 jan | Fase 06 (folga para as festas) |
| 14 a 27 jan | Fases 07 e 08 |
| 28 jan a 4 fev | Fase 09 (exportar, decidir e congelar) |

Cuidados: warehouse X-Small com auto-suspend curto e resource monitor; evitar recursos serverless e de IA; tudo que depende do Snowflake ativo (docs, exportações, snapshots) entra na janela.

## Decisões em aberto
- dbt 1.x ou v2: começar no 1.x e reavaliar depois da v1.0.
- Região e edição do Snowflake: já definidas pela conta; conferir.
- Método de carga (`PUT` e `COPY INTO` ou `write_pandas`): Fase 04.
- Modelos incrementais: Fase 06.
- Granularidade horária (M13 e M14): depois da v1.0.
- Fivetran (experimento com o Connector SDK) e Airflow: depois da v1.0.
- Publicação do dashboard (os dados são públicos): Fase 09.
