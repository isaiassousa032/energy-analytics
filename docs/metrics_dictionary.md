# Dicionário de métricas

Definições oficiais dos indicadores do Energy Analytics. Cada métrica é definida **uma vez**, na camada Gold (dbt), e consumida pelo Power BI sem recálculo. Qualquer mudança de fórmula começa neste documento, no mesmo pull request que altera o modelo.

> **Status:** as métricas do MVP (M01 a M12) estão **Aprovadas** desde 2026-11-20, depois da exploração do ONS e do Open-Meteo (veja `data_sources.md`). M13 a M15 continuam como **Proposta**, porque ficam para depois da v1.0. Os modelos e colunas citados são provisórios e serão fechados na Fase 02.

## 1. Convenções

- **Granularidade padrão:** dia × subsistema. Recortes de tempo: dia, mês e ano. Granularidade horária fica para depois da v1.0.
- **Subsistemas:** SE/CO (Sudeste/Centro-Oeste), S (Sul), NE (Nordeste) e N (Norte). **SIN** é o Sistema Interligado Nacional, a soma dos quatro. Os códigos exatos virão do dicionário de cada dataset do ONS.
- **Região** nas perguntas de negócio significa subsistema.
- **Período:** os dados do ONS vão de 2000 a 2026, e a janela de análise padrão do Gold e do dashboard é de 2019-01-01 em diante (decidida em 2026-11-20; a carga no Bronze e no Silver é de 2000 a 2026). Os horários do ONS estão em horário local de Brasília, com horário de verão até 2018: o dia em que ele começa tem 23 horas. O tratamento de fuso nas camadas Silver e Gold será definido na Fase 02.
- **Unidades:** MWmed (megawatt médio; confirmado nos dicionários oficiais do ONS), MW, °C, % e adimensional.
- **Nomes técnicos:** inglês, snake_case. Nomes das medidas do Power BI: português.
- **Valores ausentes:** nos arquivos antigos do ONS vêm como texto vazio. No Silver viram NULL e não são imputados no Gold: a métrica fica nula, e a regra de cobertura mínima de cada dia será definida na Fase 02.
- **Status possíveis:** Proposta, Aprovada, Implementada, Descontinuada.

## 2. Índice

| ID | Nome técnico | Métrica | Unidade | Fonte | Responde | Prioridade | Status |
|---|---|---|---|---|---|---|---|
| M01 | `avg_load_mwmed` | Carga média diária | MWmed | Carga diária | D1, D3 | MVP | Aprovada |
| M02 | `load_yoy_change_pct` | Variação anual da carga | % | Carga diária | D1 | MVP | Aprovada |
| M03 | `load_rank_day`, `load_rank_month` | Ranking de maior demanda | posição | Carga diária | D2 | MVP | Aprovada |
| M04 | `load_share_sin_pct` | Participação do subsistema na carga do SIN | % | Carga diária | D3 | MVP | Aprovada |
| M05 | `avg_temp_c` | Temperatura média por subsistema | °C | Open-Meteo e cidade por subsistema | C1, C2 | MVP | Aprovada |
| M06 | `cooling_degree_days` | Graus-dia de resfriamento | °C·dia | Open-Meteo e cidade por subsistema | C1 | MVP | Aprovada |
| M07 | `load_temp_correlation` | Correlação carga × temperatura | −1 a 1 | Carga e clima | C1, C2 | MVP | Aprovada |
| M08 | `load_zscore`, `is_atypical_day` | Dia atípico | z-score e sinalizador | Carga diária | C3 | MVP | Aprovada |
| M09 | `generation_mwmed` | Geração por fonte | MWmed | Balanço de energia | G1 | MVP | Aprovada |
| M10 | `generation_share_pct` | Participação por fonte | % | Balanço de energia | G1 | MVP | Aprovada |
| M11 | `generation_to_load_ratio_pct` | Cobertura da carga pela geração | % | Balanço de energia | G2 | MVP | Aprovada |
| M12 | `net_export_mwmed` | Saldo de intercâmbio (positivo = exportação) | MWmed | Balanço de energia | G2 | MVP | Aprovada |
| M13 | `peak_load_mw` | Pico de carga | MW | Balanço de energia (carga horária) | D2 | Depois | Proposta |
| M14 | `load_factor_pct` | Fator de carga | % | Balanço de energia (carga horária) | D2 | Depois | Proposta |
| M15 | `load_temp_sensitivity` | Sensibilidade da carga à temperatura | MWmed por °C·dia | Carga e clima | C2 | Depois | Proposta |

## 3. Perguntas de negócio e métricas

| Pergunta | Métricas |
|---|---|
| D1. Como a demanda evolui ao longo do tempo? | M01, M02 |
| D2. Quais são os períodos de maior demanda? | M03 (MVP); M13 e M14 (depois) |
| D3. Como os subsistemas se comportam? | M01, M04 |
| C1. Existe associação entre temperatura e demanda? | M05, M06, M07 |
| C2. Como essa relação varia por região? | M07 por subsistema; M15 (depois) |
| C3. Quais períodos apresentam comportamentos atípicos? | M08 |
| G1. Como a geração varia por fonte e por subsistema? | M09, M10 |
| G2. Como a geração se relaciona com a demanda? | M11, M12 |

## 4. Definições

### M01 — Carga média diária

| Campo | Definição |
|---|---|
| Nome técnico | `avg_load_mwmed` |
| Descrição | Carga de energia média do subsistema no dia. |
| Fórmula | Valor diário de carga do subsistema. Para mês ou ano: média simples dos valores diários do período. Para o SIN: soma dos quatro subsistemas no dia. |
| Unidade | MWmed |
| Granularidade | dia × subsistema |
| Fonte | Carga de energia diária (ONS) |
| Responde | D1, D3 |
| Modelo (proposto) | `fct_load_daily` |
| Medida no Power BI | Carga Média |
| Testes | `not_null`, valor maior que zero, chave única (data, subsistema). São as regras do dicionário oficial do ONS, e os três dias sem dado são exceção conhecida |
| Observações | O valor diário coincide com a média horária da carga do balanço, exceto no dia de início do horário de verão em 2001 a 2012 e em 2018, quando fica cerca de 4,2% menor (provavelmente por dividir por 24 horas em um dia de 23). Três dias não têm dado para nenhum subsistema (2013-12-01, 2014-02-01 e 2015-04-09) e há uma linha espúria (S, 2013-02-02 00:00:01); ambos devem ser filtrados no Silver. O dicionário do ONS não permite carga nula, zero ou negativa, então essas linhas são defeitos. |

### M02 — Variação anual da carga

| Campo | Definição |
|---|---|
| Nome técnico | `load_yoy_change_pct` |
| Descrição | Variação percentual da carga média em relação ao mesmo período do ano anterior. |
| Fórmula | (carga média do período − carga média do mesmo período do ano anterior) ÷ carga média do ano anterior × 100 |
| Unidade | % |
| Granularidade | mês × subsistema e ano × subsistema |
| Fonte | Carga de energia diária (ONS) |
| Responde | D1 |
| Modelo (proposto) | `fct_load_daily` (agregações mensal e anual) |
| Medida no Power BI | Variação Anual da Carga |
| Testes | nulo quando não há período anterior; valor entre −50 e 50 como alerta |
| Observações | Com histórico a partir de 2020, a variação só existe de 2021 em diante. Para ter 2020 contra 2019, carregue 2019 como ano-base. Comparar períodos equivalentes (mesmos dias) quando o período atual for incompleto. |

### M03 — Ranking de maior demanda

| Campo | Definição |
|---|---|
| Nome técnico | `load_rank_day` e `load_rank_month` |
| Descrição | Posição do dia (ou do mês) na ordem decrescente de carga média, dentro do subsistema. |
| Fórmula | posição = classificação por `avg_load_mwmed` decrescente, particionada por subsistema (dias) ou pela carga média mensal (meses). |
| Unidade | posição (inteiro) |
| Granularidade | dia × subsistema e mês × subsistema |
| Fonte | Carga de energia diária (ONS) |
| Responde | D2 |
| Modelo (proposto) | `fct_load_daily` |
| Medida no Power BI | Ranking de Demanda |
| Testes | posição maior ou igual a 1 |
| Observações | Os filtros de "Top N" ficam no Power BI. Empates recebem a mesma posição. |

### M04 — Participação do subsistema na carga do SIN

| Campo | Definição |
|---|---|
| Nome técnico | `load_share_sin_pct` |
| Descrição | Fatia da carga do SIN que cabe a cada subsistema. |
| Fórmula | carga do subsistema no dia ÷ soma da carga dos quatro subsistemas no dia × 100 |
| Unidade | % |
| Granularidade | dia × subsistema |
| Fonte | Carga de energia diária (ONS) |
| Responde | D3 |
| Modelo (proposto) | `fct_load_daily` |
| Medida no Power BI | Participação no SIN |
| Testes | a soma por dia é 100 (tolerância de 0,01); valor entre 0 e 100 |
| Observações | Exige os quatro subsistemas presentes no dia; caso contrário, a métrica fica nula. |

### M05 — Temperatura média por subsistema

| Campo | Definição |
|---|---|
| Nome técnico | `avg_temp_c` |
| Descrição | Temperatura média diária do subsistema, medida na cidade escolhida como representativa (uma por subsistema na v1.0). |
| Fórmula | `temperature_2m_mean` da cidade do subsistema no dia (média diária da temperatura a 2 m, calculada pela API). Cidades: São Paulo (SE), Curitiba (S), Fortaleza (NE) e Manaus (N). Se houver mais de uma cidade no futuro: Σ (peso × temperatura da cidade), com Σ pesos = 1. |
| Unidade | °C |
| Granularidade | dia × subsistema |
| Fonte | Open-Meteo (API de histórico) e seed de cidade por subsistema |
| Responde | C1, C2 |
| Modelo (proposto) | `fct_weather_daily` e `mart_load_vs_temperature` |
| Medida no Power BI | Temperatura Média |
| Testes | exatamente uma cidade por subsistema (ou soma dos pesos igual a 1, se houver várias); faixa plausível (−5 a 50 °C); sem dias faltantes na janela (os dias finais do ERA5 vêm nulos pela defasagem de 7 dias) |
| Observações | Cidades decididas em 2026-11-20. Uma cidade não representa o subsistema inteiro: é uma limitação conhecida. Os dados do Open-Meteo são reanálise (ERA5), não medições de estação. |

### M06 — Graus-dia de resfriamento

| Campo | Definição |
|---|---|
| Nome técnico | `cooling_degree_days` |
| Descrição | Medida de calor acima de uma temperatura-base, usada para explicar a carga de refrigeração. |
| Fórmula | max(0, temperatura média do dia − T_base). Para períodos: soma dos valores diários. |
| Unidade | °C·dia |
| Granularidade | dia × subsistema |
| Fonte | Open-Meteo (API de histórico) e seed de cidade por subsistema |
| Responde | C1 |
| Modelo (proposto) | `mart_load_vs_temperature` |
| Medida no Power BI | Graus-Dia de Resfriamento |
| Testes | maior ou igual a zero |
| Observações | `T_base` é um parâmetro do dbt (variável). Valor inicial: 24 °C. Calibrar pelos dados (testar valores próximos, como 22 a 26 °C, e escolher o que melhor explica a carga) e registrar a escolha aqui. |

### M07 — Correlação carga × temperatura

| Campo | Definição |
|---|---|
| Nome técnico | `load_temp_correlation` |
| Descrição | Intensidade da associação linear entre a carga e a temperatura média diárias. |
| Fórmula | correlação de Pearson entre `avg_load_mwmed` e `avg_temp_c` nas observações diárias da janela. |
| Unidade | adimensional (−1 a 1) |
| Granularidade | ano × subsistema (e período completo × subsistema) |
| Fonte | Carga de energia diária (ONS) e Open-Meteo |
| Responde | C1, C2 |
| Modelo (proposto) | modelo de estatísticas derivado de `mart_load_vs_temperature` |
| Medida no Power BI | Correlação Carga × Temperatura |
| Testes | valor entre −1 e 1; mínimo de observações por janela |
| Observações | Correlação não implica causalidade. Efeitos de calendário (dia útil, feriado) e tendência podem distorcer: comparar também com os graus-dia (M06). A janela anual é o padrão por ter observações suficientes. |

### M08 — Dia atípico

| Campo | Definição |
|---|---|
| Nome técnico | `load_zscore` e `is_atypical_day` |
| Descrição | Indica dias em que a carga fugiu do esperado para aquele mês e dia da semana. |
| Fórmula | esperado = média de `avg_load_mwmed` nos dias com o mesmo subsistema, mês e dia da semana; z = (carga do dia − esperado) ÷ desvio padrão do grupo; `is_atypical_day` = valor absoluto de z maior que 2. |
| Unidade | z-score (adimensional) e sinalizador (verdadeiro ou falso) |
| Granularidade | dia × subsistema |
| Fonte | Carga de energia diária (ONS) |
| Responde | C3 |
| Modelo (proposto) | `fct_load_daily` ou modelo de anomalias |
| Medida no Power BI | Dias Atípicos |
| Testes | `load_zscore` nulo quando o desvio padrão é zero ou há poucas observações |
| Observações | Versão simples para o MVP, sem modelo estatístico. Feriados e o efeito de 2020 serão sinalizados naturalmente, e a tendência de crescimento pode inflar os extremos. Refinar depois (por exemplo, esperado por ano). Trate antes do cálculo os dias de início do horário de verão (carga até 4,2% menor) e os três dias sem dado. |

### M09 — Geração por fonte

| Campo | Definição |
|---|---|
| Nome técnico | `generation_mwmed` |
| Descrição | Geração média diária de cada fonte em cada subsistema. |
| Fórmula | média das leituras horárias de geração da fonte no dia. Fontes: hidráulica, térmica, eólica e solar. |
| Unidade | MWmed |
| Granularidade | dia × subsistema × fonte |
| Fonte | Balanço de energia nos subsistemas (ONS) |
| Responde | G1 |
| Modelo (proposto) | `fct_generation_daily` |
| Medida no Power BI | Geração por Fonte |
| Testes | `not_null` nas linhas dos subsistemas (o dicionário permite nulo, mas não ocorre neles); maior ou igual a zero (regra do dicionário; aviso, pois há poucos negativos); fonte dentro dos valores aceitos |
| Observações | Nas linhas dos quatro subsistemas a geração por fonte não tem valores ausentes (eólica e solar existem desde o início, provavelmente como zero antes de entrarem em operação). Os ausentes estão só na linha `SIN` (eólica até 2005 e parte de 2006; solar até 2015). Use as linhas dos subsistemas e calcule o SIN por soma. O dicionário descreve a oferta como a geração das usinas das quatro fontes e não menciona geração distribuída: tratar como não incluída. |

### M10 — Participação por fonte

| Campo | Definição |
|---|---|
| Nome técnico | `generation_share_pct` |
| Descrição | Fatia de cada fonte na geração total do subsistema. |
| Fórmula | `generation_mwmed` da fonte ÷ soma de `generation_mwmed` de todas as fontes no mesmo dia e subsistema × 100 |
| Unidade | % |
| Granularidade | dia × subsistema × fonte |
| Fonte | Balanço de energia nos subsistemas (ONS) |
| Responde | G1 |
| Modelo (proposto) | `fct_generation_daily` |
| Medida no Power BI | Participação por Fonte |
| Testes | a soma das fontes por dia e subsistema é 100 (tolerância de 0,01) |
| Observações | Para períodos longos, calcular a participação sobre a soma do período, e não a média das participações diárias. |

### M11 — Cobertura da carga pela geração

| Campo | Definição |
|---|---|
| Nome técnico | `generation_to_load_ratio_pct` |
| Descrição | Quanto da carga do subsistema é atendido pela geração do próprio subsistema. |
| Fórmula | geração total do subsistema ÷ carga do subsistema × 100 |
| Unidade | % |
| Granularidade | dia × subsistema |
| Fonte | Balanço de energia nos subsistemas (ONS) |
| Responde | G2 |
| Modelo (proposto) | `fct_generation_daily` com a carga do balanço |
| Medida no Power BI | Cobertura da Carga |
| Testes | maior que zero; alerta para valores fora de 20 a 300 |
| Observações | Usar a carga do próprio dataset de balanço. A reconciliação com a carga diária (M01) foi feita e as duas coincidem, exceto no dia de início do horário de verão. Em algumas horas isoladas de 2013 a 2018 a carga e o intercâmbio estão ausentes mesmo com geração presente: nesses casos a razão fica nula. |

### M12 — Saldo de intercâmbio

| Campo | Definição |
|---|---|
| Nome técnico | `net_export_mwmed` |
| Descrição | Energia trocada pelo subsistema com os demais: positivo exporta, negativo importa. |
| Fórmula | valor oficial da coluna `val_intercambio` do balanço. Positivo indica exportação líquida (o subsistema envia energia); negativo, importação líquida. |
| Unidade | MWmed |
| Granularidade | dia × subsistema |
| Fonte | Balanço de energia nos subsistemas (ONS) |
| Responde | G2 |
| Modelo (proposto) | `fct_generation_daily` |
| Medida no Power BI | Saldo de Intercâmbio |
| Testes | alerta quando geração − carga − intercâmbio passa de um limite (a definir); a soma dos quatro igual ao intercâmbio do `SIN` (aviso); não exigir soma zero |
| Observações | Adota-se a coluna oficial (intercâmbio líquido em MWmed; não pode ser nulo, e zero e negativo são permitidos). O dicionário não define o sinal: a convenção positivo = exportação foi inferida dos dados. A relação geração − carga ≈ intercâmbio vale na média (resíduo médio próximo de zero na maioria dos subsistemas), mas há horas com resíduo grande. A soma dos quatro subsistemas coincide com o intercâmbio da linha `SIN` (em média cerca de +38 MW, e não zero; provavelmente a troca do sistema com o exterior). Não derive o saldo de carga − geração. |

### M13 — Pico de carga

| Campo | Definição |
|---|---|
| Nome técnico | `peak_load_mw` |
| Descrição | Maior carga horária do dia no subsistema. |
| Fórmula | máximo da carga horária no dia |
| Unidade | MW |
| Granularidade | dia × subsistema |
| Fonte | Balanço de energia nos subsistemas (ONS), carga horária |
| Responde | D2 |
| Modelo (proposto) | `fct_load_daily` |
| Medida no Power BI | Pico de Carga |
| Testes | maior que zero; maior ou igual à carga média do dia |
| Observações | Usa a carga horária do balanço (`val_carga`), o que dispensa o dataset de curva de carga. O dia de início do horário de verão tem 23 horas. Adiado para depois do MVP. |

### M14 — Fator de carga

| Campo | Definição |
|---|---|
| Nome técnico | `load_factor_pct` |
| Descrição | Quanto a carga média se aproxima do pico: quanto mais alto, mais plana a curva de carga. |
| Fórmula | carga média do período ÷ pico de carga do período × 100 |
| Unidade | % |
| Granularidade | dia × subsistema (e mês, e ano) |
| Fonte | Balanço de energia nos subsistemas (ONS), carga horária |
| Responde | D2 |
| Modelo (proposto) | `fct_load_daily` |
| Medida no Power BI | Fator de Carga |
| Testes | valor entre 0 e 100 |
| Observações | Depende de M13. Em períodos longos, usar o pico do período, e não a média dos picos diários. |

### M15 — Sensibilidade da carga à temperatura

| Campo | Definição |
|---|---|
| Nome técnico | `load_temp_sensitivity` |
| Descrição | Quantos MWmed a carga sobe a cada grau-dia de resfriamento adicional. |
| Fórmula | inclinação da regressão linear de `avg_load_mwmed` contra `cooling_degree_days`, por subsistema e janela. |
| Unidade | MWmed por °C·dia |
| Granularidade | ano × subsistema |
| Fonte | Carga de energia diária (ONS) e Open-Meteo |
| Responde | C2 |
| Modelo (proposto) | modelo de estatísticas derivado de `mart_load_vs_temperature` |
| Medida no Power BI | Sensibilidade à Temperatura |
| Testes | número mínimo de observações; sinal esperado positivo como alerta |
| Observações | Considerar apenas dias úteis, ou controlar o dia da semana, para não misturar efeitos de calendário. Adiado para depois do MVP. |

## 5. Pendências de validação (Fase 01)

**Resolvido na exploração do ONS** (detalhes em `data_sources.md`):

- Unidade: MWmed em todos os valores, confirmada nos dois dicionários oficiais (carga diária, versão 1.2, e balanço, versão 1.0). Os valores diários da carga coincidem com a média horária do balanço, exceto no início do horário de verão.
- Regras dos dicionários: na carga diária, nada pode ser nulo, zero ou negativo. No balanço, a geração pode ser nula ou zero, mas não negativa; a carga e o intercâmbio não podem ser nulos; o intercâmbio pode ser negativo.
- Códigos de subsistema: N, NE, S e SE, mais `SIN` no balanço. Em 2026 os códigos do balanço vêm com espaços à direita (o dicionário define 3 posições).
- Fontes do balanço: hidráulica, térmica, eólica e fotovoltaica, sem ausências nas linhas dos subsistemas. A coluna oficial de intercâmbio existe.
- A carga do `SIN` é a soma dos quatro subsistemas.
- Dias sem dado: 2013-12-01, 2014-02-01 e 2015-04-09, e horas isoladas de 2013 a 2018 sem carga e intercâmbio.

**Ainda em aberto:**

- Geração distribuída: o dicionário não a menciona; tratar como não incluída até haver confirmação.
- Decidir o tratamento dos valores que violam os dicionários (carga e intercâmbio nulos, gerações e carga negativas) e investigar os resíduos grandes entre geração, carga e intercâmbio.
- Definir a cobertura mínima para considerar um dia válido. O dia de 23 horas (último em 2018-11-04) fica fora da janela padrão de 2019 em diante; só precisa de tratamento se a janela for estendida.
- Calibrar `T_base`. Cidades decididas: uma por subsistema (São Paulo, Curitiba, Fortaleza e Manaus), sem pesos.
- Janela padrão da correlação (M07): anual, disponível para todos os anos; o dashboard abre em 2019 em diante.

## 6. Como adicionar ou alterar uma métrica

1. Abra uma issue descrevendo a métrica e a pergunta de negócio que ela responde.
2. Acrescente a definição neste documento, com todos os campos da tabela (nome técnico, descrição, fórmula, unidade, granularidade, fonte, pergunta, modelo, medida no Power BI, testes e observações).
3. Implemente a métrica no Gold (dbt), com os testes listados.
4. Atualize o índice e o mapa de perguntas.
5. Só então crie ou ajuste a medida no Power BI, referenciando a coluna do Gold.

## 7. Glossário

- **MWmed:** megawatt médio, energia média por unidade de tempo no período.
- **SIN:** Sistema Interligado Nacional.
- **Grain:** nível de detalhe de uma linha da tabela (por exemplo, dia × subsistema).
- **Graus-dia de resfriamento:** soma dos graus acima de uma temperatura-base, usada como medida de calor.
- **Correlação de Pearson:** medida de associação linear entre duas variáveis, de −1 a 1.
- **Z-score:** distância de um valor até a média, em desvios padrão.