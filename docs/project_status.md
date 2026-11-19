# Estado do projeto

Atualize este arquivo ao fim de cada tarefa. Última atualização: 19 de novembro de 2026.

## Onde estamos
- **Fase 00 (fundação):** tag `v0-airflow-duckdb` criada, `main` limpa com histórico preservado, novo devcontainer e `requirements.txt` criados, rebuild do Codespace validado. A confirmar: `.gitignore` e `.env.example` atualizados, porta 8080 do devcontainer (encaminhamento automático), versões fixadas, arquivo `LICENSE`, README e milestones e issues das fases 00 a 09 criados no GitHub.
- **Fase 01 (negócio e requisitos):**
  - feito: indicadores e `docs/metrics_dictionary.md` (M01 a M15, status Proposta); exploração do ONS concluída com `scripts/explore_ons.py` (checks 0 a 14) e dicionários PDF do ONS conferidos; `docs/data_sources.md` com os achados.
  - Open-Meteo, exploração concluída (resultados em `docs/data_sources.md`, seção 2): `era5_seamless` é a proposta (sem nulos, sem trocar de modelo); as 11 cidades candidatas têm grade a 2 a 11 km e altitude coerente; defasagem real de 7 dias (não 5), com `null` nos dias finais; custo de 1 ano com 2 variáveis = 5,2 chamadas, então a carga histórica custa cerca de 1.540 chamadas (15% do limite diário); a API dá timeouts frequentes, então o retry é obrigatório.
  - falta: escolher cidades e pesos por subsistema e confirmar o modelo; decidir granularidade e período (item 5); escrever `docs/requirements.md` (item 6).

## Próximos passos (em ordem)
1. Escolher cidades e pesos por subsistema, confirmar o modelo (`era5_seamless`) e a janela de análise (seção 3 de `docs/data_sources.md`).
2. Verificar se os valores dos últimos dias do ERA5 são revisados depois (define a janela de reprocessamento).
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
- 2026-11-19: exploração do Open-Meteo executada (`check`, `cities`, `tz`, `recency`) e registrada em `docs/data_sources.md`; Manaus medida em chamada isolada; custo real medido e `cost` do script corrigido; README atualizado. Pendente: cidades e pesos, janela de análise, `docs/requirements.md`.
