# Estado do projeto

Atualize este arquivo ao fim de cada tarefa. Última atualização: 20 de novembro de 2026.

## Onde estamos
- **Fase 00 (fundação):** concluída (confirmado pelo autor em 2026-11-20). Tag `v0-airflow-duckdb`, `main` limpa, novo devcontainer, `requirements.txt`, README e milestones e issues das fases 00 a 09.
- **Fase 01 (negócio e requisitos):**
  - feito: indicadores e `docs/metrics_dictionary.md` (M01 a M15, status Proposta); exploração do ONS concluída com `scripts/explore_ons.py` (checks 0 a 14) e dicionários PDF do ONS conferidos; `docs/data_sources.md` com os achados.
  - Open-Meteo, exploração concluída (resultados em `docs/data_sources.md`, seção 2): defasagem real de 7 dias (não 5), com `null` nos dias finais; custo de 1 ano com 2 variáveis = 5,2 chamadas (carga histórica de 4 cidades: cerca de 560 chamadas); a API dá timeouts frequentes, então o retry é obrigatório.
  - item 5 decidido (2026-11-20): granularidade diária por subsistema; modelo `era5_seamless`; uma cidade por subsistema (São Paulo, Curitiba, Fortaleza e Manaus), ampliando depois; janela de análise de 2019-01-01 em diante, com carga de 2000 a 2026 no Bronze e no Silver (seção 3 de `docs/data_sources.md`).
  - item 6 feito (2026-11-20): `docs/requirements.md` escrito (RF, RD e RNF, critérios de aceite do MVP); métricas M01 a M12 aprovadas (M13 a M15 seguem como Proposta, pois ficam para depois da v1.0).
  - falta: revisão do `docs/requirements.md` pelo autor e fechar a Fase 01.

## Próximos passos (em ordem)
1. Revisar `docs/requirements.md` e fechar a Fase 01 (milestone e issues).
2. Abrir a Fase 02 (arquitetura e modelagem): fechar as pendências da seção 8 do `docs/requirements.md` (cobertura mínima do dia, `T_base`, nomes do Gold).
3. Verificar se os valores dos últimos dias do ERA5 são revisados depois (define a janela de reprocessamento).

## Decisões já tomadas
- Foco em Analytics Engineering. Sem Airflow nesta versão. Docker Compose removido.
- Snowflake (trial) como warehouse, com possível migração futura para o Databricks. dbt Core 1.x. Power BI para consumo.
- Carregar o histórico completo do ONS (2000 em diante) no Bronze; granularidade diária no MVP.
- Janela de análise do Gold e do dashboard: 2019-01-01 em diante. Clima: `era5_seamless`, uma cidade por subsistema (São Paulo, Curitiba, Fortaleza e Manaus), sem pesos.
- Snowflake: região us-west-2 (Oregon), edição Enterprise. dbt 1.x na v1.0 do projeto.
- Datasets do MVP: `carga_energia_di` e `balanco_energia_subsistema_ho`. Intercâmbio oficial (`val_intercambio`, positivo = exportação) em vez de derivado.
- Valores que violam os dicionários do ONS: anular (NULL) e sinalizar, com testes em severidade de aviso.

## Em aberto
- Dia de 23 horas (horário de verão): fica fora da janela de 2019 em diante; só precisa de tratamento se a janela for estendida.
- Cobertura mínima para considerar um dia válido.
- Geração distribuída não é mencionada nos dicionários do ONS: tratar como não incluída.
- Calibração de `T_base` (graus-dia de resfriamento). A janela da correlação (M07) é anual.

## Registro de sessões
Uma linha por sessão: data, o que foi feito, o que ficou pendente.

- 2026-11-17: contexto do projeto preparado para o Claude Code (`CLAUDE.md`, `docs/planning.md`, este arquivo).
- 2026-11-19: exploração do Open-Meteo executada (`check`, `cities`, `tz`, `recency`) e registrada em `docs/data_sources.md`; Manaus medida em chamada isolada; custo real medido e `cost` do script corrigido; README atualizado. Pendente: cidades e pesos, janela de análise, `docs/requirements.md`.
- 2026-11-20: decisões do item 5 registradas (cidades, janela de 2019 em diante, modelo, granularidade, região e edição do Snowflake, dbt 1.x); Fase 00 marcada como concluída; "5 dias" corrigido para 7 nos `CLAUDE.md`. Pendente: `docs/requirements.md` e aprovação do dicionário de métricas.
- 2026-11-20 (2): `docs/requirements.md` escrito; M01 a M12 aprovadas; M05 e M06 ajustadas para uma cidade por subsistema (sem pesos). Pendente: revisão do autor e fechamento da Fase 01.
