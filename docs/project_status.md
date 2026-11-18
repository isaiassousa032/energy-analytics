# Estado do projeto

Atualize este arquivo ao fim de cada tarefa. Última atualização: 17 de novembro de 2026.

## Onde estamos
- **Fase 00 (fundação):** tag `v0-airflow-duckdb` criada, `main` limpa com histórico preservado, novo devcontainer e `requirements.txt` criados, rebuild do Codespace validado. A confirmar: `.gitignore` e `.env.example` atualizados, porta 8080 do devcontainer (encaminhamento automático), versões fixadas, arquivo `LICENSE`, README e milestones e issues das fases 00 a 09 criados no GitHub.
- **Fase 01 (negócio e requisitos):**
  - feito: indicadores e `docs/metrics_dictionary.md` (M01 a M15, status Proposta); exploração do ONS concluída com `scripts/explore_ons.py` (checks 0 a 14) e dicionários PDF do ONS conferidos; `docs/data_sources.md` com os achados.
  - em andamento: avaliação do Open-Meteo. O script `scripts/explore_open_meteo.py` foi criado, mas ainda **não foi executado** no ambiente real.
  - falta: escolher modelo e cidades do Open-Meteo; decidir granularidade e período (item 5); escrever `docs/requirements.md` (item 6).

## Próximos passos (em ordem)
1. Rodar `python scripts/explore_open_meteo.py check` e registrar o resultado em `docs/data_sources.md` (seção 2).
2. Escolher cidades e pesos por subsistema, o modelo (proposta: `era5`) e a janela de análise.
3. Escrever `docs/requirements.md` e aprovar o dicionário de métricas (trocar o status de Proposta para Aprovada).
4. Fechar a Fase 00 pendente (itens "a confirmar" acima) e abrir a Fase 02.

## Decisões já tomadas
- Foco em Analytics Engineering. Sem Airflow nesta versão. Docker Compose removido.
- Snowflake (trial) como warehouse, com possível migração futura para o Databricks. dbt Core 1.x. Power BI para consumo.
- Carregar o histórico completo do ONS (2000 em diante) no Bronze; granularidade diária no MVP.
- Datasets do MVP: `carga_energia_di` e `balanco_energia_subsistema_ho`. Intercâmbio oficial (`val_intercambio`, positivo = exportação) em vez de derivado.
- Valores que violam os dicionários do ONS: anular (NULL) e sinalizar, com testes em severidade de aviso.

## Em aberto
- Tratamento do dia de 23 horas (horário de verão) nas métricas diárias e no dia atípico (M08).
- Cobertura mínima para considerar um dia válido.
- Geração distribuída não é mencionada nos dicionários do ONS: tratar como não incluída.
- Calibração de `T_base` (graus-dia de resfriamento) e janela padrão da correlação (M07).

## Registro de sessões
Uma linha por sessão: data, o que foi feito, o que ficou pendente.

- 2026-11-17: contexto do projeto preparado para o Claude Code (`CLAUDE.md`, `docs/planning.md`, este arquivo).
