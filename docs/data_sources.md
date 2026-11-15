# Fontes de dados

Registro das fontes do Energy Analytics: o que cada dataset contém, como acessar, o que a exploração encontrou e como cada achado será tratado. Este documento acompanha o `metrics_dictionary.md`.

> **Status:** ONS explorado em novembro de 2026 com `scripts/explore_ons.py` (checks 0 a 14). O Open-Meteo ainda será avaliado (próximo passo da Fase 01).

## 1. ONS (Operador Nacional do Sistema Elétrico)

- **Portal:** Portal de Dados Abertos do ONS (dados.ons.org.br).
- **Acesso:** bucket público da AWS `s3://ons-aws-prod-opendata/dataset/<pasta>/`, região `sa-east-1`, sem credenciais.
- **Licença:** CC BY 4.0 (exige atribuição).
- **Catálogo:** 96 pastas. Cada uma traz arquivos por ano ou mês em CSV, XLSX e (na maioria) Parquet, além de um JSON e um PDF com o dicionário de dados.
- **Atualização:** na exploração, os dados iam até 13/11/2026. A frequência exata será confirmada.

### 1.1 Datasets do MVP

#### `carga_energia_di` — carga de energia diária

| Item | Detalhe |
|---|---|
| Arquivos | `CARGA_ENERGIA_<ANO>.parquet`, 27 arquivos (2000 a 2026) |
| Granularidade | dia × subsistema |
| Volume | 39.257 linhas (4 subsistemas × 9.814 dias, mais 1 linha espúria) |
| Período | 2000-01-01 a 2026-11-13 |
| Usada em | M01 a M04 e M08 |

| Coluna | Tipo | Descrição |
|---|---|---|
| `id_subsistema` | texto | N, NE, S ou SE |
| `nom_subsistema` | texto | Norte, Nordeste, Sul ou Sudeste/Centro-Oeste |
| `din_instante` | timestamp | dia, à meia-noite |
| `val_cargaenergiamwmed` | número (texto em 2000 a 2021) | carga média do dia, em MWmed |

#### `balanco_energia_subsistema_ho` — balanço de energia nos subsistemas

| Item | Detalhe |
|---|---|
| Arquivos | `BALANCO_ENERGIA_SUBSISTEMA_<ANO>.parquet`, 27 arquivos (2000 a 2026) |
| Granularidade | hora × subsistema (mais a linha `SIN`) |
| Volume | 1.177.557 linhas (o esperado sem lacunas seria 1.177.680) |
| Período | 2000-01-01 00:00 a 2026-11-13 23:00 |
| Usada em | M09 a M12 e, depois do MVP, M13 e M14 |

| Coluna | Tipo | Descrição |
|---|---|---|
| `id_subsistema` | texto | N, NE, S, SE e SIN (com espaços à direita em 2026) |
| `nom_subsistema` | texto | nomes em caixa alta (NORTE, NORDESTE, SUL, SUDESTE/CENTRO-OESTE, SISTEMA INTERLIGADO NACIONAL) |
| `din_instante` | timestamp | hora cheia, em horário local |
| `val_gerhidraulica`, `val_gertermica`, `val_gereolica`, `val_gersolar` | número (texto em 2000 a 2022) | geração por fonte |
| `val_carga` | número (texto em 2000 a 2022) | carga horária |
| `val_intercambio` | número (texto em 2000 a 2022) | intercâmbio do subsistema; positivo = exportação |

As unidades do balanço serão conferidas no dicionário PDF da pasta (esperado: MWmed, potência média na hora).

### 1.2 Datasets avaliados

| Pasta | Decisão | Motivo |
|---|---|---|
| `carga_energia_di` | MVP | carga diária oficial por subsistema |
| `balanco_energia_subsistema_ho` | MVP | geração por fonte, carga horária e intercâmbio |
| `curva-carga-ho` | Dispensado | a carga horária já vem no balanço |
| `ear_subsistema_di` e `ena_subsistema_di` | Opcional, depois | contexto hidrológico (energia armazenada e afluente) para explicar a geração hidráulica; ainda não perfilados |
| `intercambio_nacional_ho` | Adiado | o intercâmbio por subsistema já vem no balanço |
| `fator_capacidade_2_di` | Adiado | fora do escopo do MVP |

### 1.3 Achados da exploração e tratamento

| # | Achado | Evidência | Tratamento |
|---|---|---|---|
| 1 | Tipos mudam entre os anos: os valores numéricos são texto até 2021 (carga diária) e até 2022 (balanço) e número depois | schema por arquivo (check 0) | Bronze preserva tudo como texto; o Silver converte com `try_cast` |
| 2 | Valores ausentes vêm como texto vazio nos arquivos antigos | checks 10, 11 e 13b | Silver: `nullif` e `try_cast`, sem imputar zero |
| 3 | Nas linhas dos quatro subsistemas, a geração por fonte nunca está ausente. Os ausentes de geração (hidráulica 48, térmica 72, eólica 54.738, solar 136.041) estão só na linha `SIN`: eólica até 2005 e parte de 2006, solar até 2015 | checks 13 e 13b | usar as linhas dos subsistemas e calcular o SIN por soma |
| 4 | Carga e intercâmbio ausentes em 331 linhas do balanço, em horas isoladas e em dias sem dado entre 2013 e 2018 (120 linhas em 2013, 100 em 2014 e em 2015, 3 a 4 por ano de 2016 a 2018) | checks 13 e 13b | manter nulo; teste de completude como aviso |
| 5 | Na carga diária, três dias sem dado para os quatro subsistemas (2013-12-01, 2014-02-01 e 2015-04-09) e uma linha espúria (S, 2013-02-02 00:00:01, sem valor) | checks 2b e 14 | filtrar linhas sem valor; depois disso cada subsistema tem 9.814 linhas, três delas sem valor |
| 6 | Códigos de subsistema com espaços à direita no arquivo de 2026 (`N  `, `NE `) | check 3 | `trim` no staging; juntar os datasets sempre pelo código, nunca pelo nome (a caixa difere entre eles) |
| 7 | Os horários são locais, com horário de verão. 14 horas ficam totalmente ausentes, todas às 00:00 do início do horário de verão (2000 a 2013), e esses dias têm 23 linhas. De 2014 a 2018 só 1 das 5 séries tem 23 linhas nesse dia | checks 4b e 5b | manter o timestamp local e derivar `reference_date`; não converter para UTC; agregar por dia; documentar o dia de 23 horas |
| 8 | Lacunas parciais: 25 linhas faltantes em 2014 e em 2015 e 1 em cada ano de 2016 a 2018; o Norte tem cerca de 48 linhas a menos que os demais | check 5 | teste de completude como aviso |
| 9 | Carga diária e média horária da carga do balanço coincidem, exceto no dia de início do horário de verão em 2001 a 2012 e em 2018, quando a diária fica cerca de 4,2% menor (provavelmente por dividir por 24 em um dia de 23 horas; máximo de cerca de 1.300 MW) | check 6 | usar a carga diária no M01 e a do balanço nas razões com geração; teste de reconciliação com tolerância; tratar esses dias no M08 |
| 10 | A carga da linha `SIN` é a soma dos quatro subsistemas (diferença média de 0,002 MW). O intercâmbio do `SIN` também (diferença média de 0,135 MW, com máximo de 1.551 MW) | check 12 | calcular o SIN por soma e usar a linha `SIN` só como validação |
| 11 | Intercâmbio: positivo = exportação (média: N +1.723 MW, NE +146, S −955, SE −877). A soma dos quatro não é zero: coincide com o intercâmbio do `SIN` (cerca de +38 MW em média, provavelmente a troca com o exterior). Geração − carga − intercâmbio é próximo de zero na média, mas há horas com resíduo grande | checks 7 e 8 | usar a coluna oficial `val_intercambio` (M12); teste de resíduo como aviso |
| 12 | Valores suspeitos: 1 carga não positiva, 2 gerações térmicas negativas, 27 eólicas negativas e 1 solar negativa | check 9 | investigar e decidir entre manter, anular ou sinalizar |

## 2. Open-Meteo

A avaliar (item 4 da Fase 01): variáveis (temperatura a 2 m e precipitação), cidades por subsistema, fuso horário, custo ponderado das chamadas conforme o período e os limites do plano gratuito.

## 3. Decisões e propostas (item 5 da Fase 01)

- **Histórico:** carregar de 2000 até hoje no Bronze. O volume é pequeno e o custo, trivial.
- **Granularidade do MVP:** diária por subsistema. As métricas horárias (M13 e M14) ficam para depois.
- **Janela de análise:** a definir após avaliar o Open-Meteo. Períodos como o racionamento de 2001, o efeito de 2020 e a crise hídrica de 2021 são candidatos a exemplos de comportamento atípico.

## 4. Pendências

- Conferir o dicionário PDF do ONS (unidades e definições do balanço, inclusive geração distribuída).
- Investigar os valores suspeitos (achado 12) e os resíduos grandes (achado 11).
- Avaliar o Open-Meteo e preencher a seção 2.

## 5. Atribuição

Dados de energia: ONS, Operador Nacional do Sistema Elétrico, licença CC BY 4.0.
