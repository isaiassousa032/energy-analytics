# Requisitos

Requisitos do Energy Analytics v1.0. Este documento liga as perguntas de negócio aos dados e às métricas. As definições das métricas ficam em [`metrics_dictionary.md`](metrics_dictionary.md) e os achados das fontes em [`data_sources.md`](data_sources.md); aqui só se aponta para eles. O plano de fases está em [`planning.md`](planning.md).

## 1. Objetivo e escopo

**Objetivo:** responder a perguntas sobre demanda, clima versus demanda e geração por fonte no setor elétrico brasileiro, com dados públicos do ONS e do Open-Meteo, modelagem dimensional, testes dbt e um dashboard no Power BI.

**Dentro do escopo (v1.0)**
- Granularidade diária, por subsistema (SE, S, NE e N) e para o SIN.
- Carga e geração do ONS de 2000 a 2026 no Bronze e no Silver; **janela de análise do Gold e do dashboard: 2019-01-01 em diante**.
- Clima: uma cidade por subsistema (São Paulo, Curitiba, Fortaleza e Manaus), temperatura média e precipitação diárias, modelo `era5_seamless`.
- Métricas M01 a M12 (aprovadas em 2026-11-20).

**Fora do escopo (v1.0)**
- Granularidade horária e as métricas M13 a M15.
- Mais de uma cidade por subsistema e pesos entre cidades.
- Geração distribuída (o dicionário do ONS não a menciona; tratada como não incluída).
- Airflow, Docker Compose, PySpark, Kafka e previsão de demanda.

## 2. Perguntas de negócio, dados e métricas

| Pergunta | Métricas | Dataset |
|---|---|---|
| D1. Como a demanda evolui ao longo do tempo? | M01, M02 | `carga_energia_di` |
| D2. Quais são os períodos de maior demanda? | M03 | `carga_energia_di` |
| D3. Como os subsistemas se comportam? | M01, M04 | `carga_energia_di` |
| C1. Existe associação entre temperatura e demanda? | M05, M06, M07 | `carga_energia_di` e Open-Meteo |
| C2. Como essa relação varia por região (subsistema)? | M07 por subsistema | `carga_energia_di` e Open-Meteo |
| C3. Quais períodos apresentam comportamentos atípicos? | M08 | `carga_energia_di` |
| G1. Como a geração varia por fonte e por subsistema? | M09, M10 | `balanco_energia_subsistema_ho` |
| G2. Como a geração se relaciona com a demanda? | M11, M12 | `balanco_energia_subsistema_ho` |

## 3. Requisitos funcionais

| ID | Requisito | Perguntas |
|---|---|---|
| RF-01 | Carga média diária por subsistema e para o SIN, com variação anual e participação no SIN (M01, M02, M04). | D1, D3 |
| RF-02 | Ranking dos dias e meses de maior demanda (M03). | D2 |
| RF-03 | Temperatura média diária e graus-dia de resfriamento por subsistema, a partir da cidade escolhida (M05, M06). | C1 |
| RF-04 | Correlação entre carga e temperatura por subsistema, com janela anual (M07). | C1, C2 |
| RF-05 | Sinalização de dia atípico por z-score (M08). | C3 |
| RF-06 | Geração diária por fonte (hidráulica, térmica, eólica e solar) e participação de cada fonte (M09, M10). | G1 |
| RF-07 | Cobertura da carga pela geração e saldo de intercâmbio (positivo = exportação) (M11, M12). | G2 |
| RF-08 | Todas as métricas calculadas uma única vez, na camada Gold. O Power BI só consome, sem recalcular. | todas |
| RF-09 | Dashboard abre na janela de 2019 em diante e permite recortes por dia, mês, ano e subsistema. | todas |

## 4. Requisitos de dados

| ID | Requisito |
|---|---|
| RD-01 | Bronze preserva o dado original, todo como texto, com metadados de carga. Silver converte tipos com `try_cast` e `nullif`. |
| RD-02 | Juntar datasets sempre pelo código do subsistema (com `trim`), nunca pelo nome. |
| RD-03 | Excluir a linha `SIN` do balanço ao agregar os subsistemas. |
| RD-04 | Tratar os defeitos conhecidos do ONS: linha espúria de 2013-02-02, três dias sem dado (2013-12-01, 2014-02-01 e 2015-04-09) e valores que violam o dicionário (anular e sinalizar). |
| RD-05 | Dias de 23 horas (último em 2018-11-04) ficam fora da janela padrão. Não converter horários para UTC: agregar por dia local. |
| RD-06 | Clima por requisições de 1 ano por cidade, com pausa e retry. O ERA5 tem 7 dias de atraso medidos: descartar os `null` da ponta e reprocessar a janela final a cada execução. |
| RD-07 | Cargas idempotentes: reprocessar um período substitui a partição, sem duplicar. |
| RD-08 | Cobertura mínima para considerar um dia válido: a definir na Fase 02. |

## 5. Requisitos não funcionais

| ID | Categoria | Requisito |
|---|---|---|
| RNF-01 | Custo | Warehouse X-Small com auto-suspend de 60 s e resource monitor, na edição Enterprise (us-west-2). Operações que consomem créditos são feitas com confirmação e poucos dados. |
| RNF-02 | Prazo | A conta trial do Snowflake termina por volta de 2027-02-04. O que depende dela deve estar pronto antes, e o fim do projeto exporta snapshots e documentação estática. |
| RNF-03 | Segurança | Segredos fora do Git. Credenciais do Snowflake só por variáveis `SNOWFLAKE_*`, com usuário de serviço de papel mínimo (`LOADER`, `TRANSFORMER`, `REPORTER`). |
| RNF-04 | Portabilidade | SQL portátil e código específico de warehouse isolado na camada de carga, para migrar para o Databricks. |
| RNF-05 | Reprodutibilidade | Um Codespace novo reproduz o ambiente. Dependências com versão fixada. |
| RNF-06 | Qualidade | Testes dbt em cada camada. Violações dos dicionários do ONS geram aviso, não falha. |
| RNF-07 | Limites externos | Open-Meteo gratuito: 600 chamadas por minuto e 10.000 por dia. A carga histórica das 4 cidades custa cerca de 560 chamadas. |
| RNF-08 | Licenças | Atribuição ao ONS (CC BY 4.0) e ao Open-Meteo (CC BY 4.0, uso não comercial) no README e no rodapé do dashboard. |
| RNF-09 | Convenções | Tabelas e colunas em inglês, snake_case. Documentação em português. Commits em Conventional Commits. |

## 6. Premissas e limitações

- Uma cidade não representa o subsistema inteiro. A temperatura da cidade é um proxy do clima do subsistema.
- Hipótese ainda não medida: Fortaleza e Manaus têm temperatura quase constante, então a correlação entre carga e temperatura tende a ser fraca no Nordeste e no Norte.
- Correlação não implica causalidade. Calendário (dia útil e feriado) e tendência de crescimento podem distorcer M07 e M08.
- O Open-Meteo traz reanálise (ERA5), não medições de estação.
- 2026 é um ano parcial: comparar períodos equivalentes.
- O plano gratuito do Open-Meteo não tem garantia de disponibilidade, e a API deu timeouts frequentes nos testes.
- Fora da janela de 2019 em diante, os resultados não têm garantia de qualidade (horário de verão, dias sem dado, mudanças de regime como o racionamento de 2001).

## 7. Critérios de aceite do MVP

- Cada pergunta (D1 a G2) tem ao menos uma visual no dashboard, alimentada só por tabelas do Gold.
- Todas as métricas M01 a M12 existem no Gold com o nome técnico do dicionário e passam nos testes definidos nele.
- Nenhuma métrica é calculada no Power BI.
- O dashboard mostra a atribuição ao ONS e ao Open-Meteo.
- `dbt build` roda do zero em um Codespace novo, e a documentação do dbt está gerada.
- Os requisitos RD-01 a RD-07 têm teste ou documentação que os comprove.

## 8. Pendências para a Fase 02

- Cobertura mínima para considerar um dia válido (RD-08).
- Calibração de `T_base` dos graus-dia de resfriamento (M06).
- Nomes finais de modelos e colunas do Gold (hoje provisórios no dicionário).
- Tratamento de fuso nas camadas Silver e Gold, caso a janela seja estendida para antes de 2019.
