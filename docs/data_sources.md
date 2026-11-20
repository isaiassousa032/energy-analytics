# Fontes de dados

Registro das fontes do Energy Analytics: o que cada dataset contém, como acessar, o que a exploração encontrou e como cada achado será tratado. Este documento acompanha o `metrics_dictionary.md`.

> **Status:** ONS explorado em novembro de 2026 com `scripts/explore_ons.py` (checks 0 a 14). O Open-Meteo foi levantado pela documentação; falta rodar o script de exploração.

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

**Dicionário oficial (versão 1.2, de 01/05/2023):** todos os campos são obrigatórios (não permitem nulo) e a carga não pode ser zero nem negativa. `id_subsistema` tem 3 posições, `nom_subsistema` tem 60, `din_instante` segue o formato `YYYY-MM-DD HH:MM:SS` e `val_cargaenergiamwmed` é FLOAT, em MWmed.

**Contrato segundo o dicionário de dados do ONS** (versão 1.2, de 01/05/2023):

| Coluna | Tipo oficial | Formato | Permite nulo | Permite zero | Permite negativo |
|---|---|---|---|---|---|
| `id_subsistema` | texto | 3 posições | não | — | — |
| `nom_subsistema` | texto | 60 posições | não | — | — |
| `din_instante` | datetime | AAAA-MM-DD HH:MM:SS | não | — | — |
| `val_cargaenergiamwmed` | float | — | não | não | não |

O dicionário confirma a unidade (MWmed) e define que a carga não pode ser nula, zero nem negativa. As 13 linhas sem valor encontradas na exploração violam esse contrato: são defeitos dos dados, e não ausências válidas. O tipo oficial é número (float), o que reforça converter os arquivos antigos, publicados como texto.

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

**Contrato segundo o dicionário de dados do ONS** (versão 1.0, de 02/05/2023):

| Coluna | Tipo oficial | Formato | Permite nulo | Permite zero | Permite negativo |
|---|---|---|---|---|---|
| `id_subsistema` | texto | 3 posições | não | — | — |
| `nom_subsistema` | texto | 20 posições | não | — | — |
| `din_instante` | datetime | AAAA-MM-DD HH:MM:SS | não | — | — |
| `val_gerhidraulica`, `val_gertermica`, `val_gereolica`, `val_gersolar` | float | — | sim | sim | não |
| `val_carga` | float | — | não | sim | não |
| `val_intercambio` | float | — | não | sim | sim |

Todas as colunas de valor estão em MWmed. A oferta é a geração das usinas hidráulicas, térmicas, eólicas e fotovoltaicas, e o intercâmbio é líquido. O dicionário não define o sinal do intercâmbio e não menciona a linha `SIN` nem a geração distribuída.

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
| 3 | Nas linhas dos quatro subsistemas, a geração por fonte nunca está ausente. Os ausentes de geração (hidráulica 48, térmica 72, eólica 54.738, solar 136.041) estão só na linha `SIN`: eólica até 2005 e parte de 2006, solar até 2015. O dicionário permite geração nula | checks 13 e 13b | usar as linhas dos subsistemas e calcular o SIN por soma |
| 4 | Carga e intercâmbio ausentes em 331 linhas do balanço, em horas isoladas e em dias sem dado entre 2013 e 2018 (120 linhas em 2013, 100 em 2014 e em 2015, 3 a 4 por ano de 2016 a 2018). Violam o dicionário, que não permite carga ou intercâmbio nulos | checks 13 e 13b | manter nulo; teste de completude como aviso |
| 5 | Na carga diária, três dias sem dado para os quatro subsistemas (2013-12-01, 2014-02-01 e 2015-04-09) e uma linha espúria (S, 2013-02-02 00:00:01, sem valor). Violam o dicionário do ONS, que não permite carga nula | checks 2b e 14 | filtrar linhas sem valor; depois disso cada subsistema tem 9.814 linhas, três delas sem valor |
| 6 | Códigos de subsistema com espaços à direita no balanço de 2026 (`N  `, `NE `), provavelmente refletindo o formato de 3 posições do dicionário | check 3 | `trim` no staging; juntar os datasets sempre pelo código, nunca pelo nome (a caixa difere entre eles) |
| 7 | Os horários são locais, com horário de verão. 14 horas ficam totalmente ausentes, todas às 00:00 do início do horário de verão (2000 a 2013), e esses dias têm 23 linhas. De 2014 a 2018 só 1 das 5 séries tem 23 linhas nesse dia | checks 4b e 5b | manter o timestamp local e derivar `reference_date`; não converter para UTC; agregar por dia; documentar o dia de 23 horas |
| 8 | Lacunas parciais: 25 linhas faltantes em 2014 e em 2015 e 1 em cada ano de 2016 a 2018; o Norte tem cerca de 48 linhas a menos que os demais | check 5 | teste de completude como aviso |
| 9 | Carga diária e média horária da carga do balanço coincidem, exceto no dia de início do horário de verão em 2001 a 2012 e em 2018, quando a diária fica cerca de 4,2% menor (provavelmente por dividir por 24 em um dia de 23 horas; máximo de cerca de 1.300 MW) | check 6 | usar a carga diária no M01 e a do balanço nas razões com geração; teste de reconciliação com tolerância; tratar esses dias no M08 |
| 10 | A carga da linha `SIN` é a soma dos quatro subsistemas (diferença média de 0,002 MW). O intercâmbio do `SIN` também (diferença média de 0,135 MW, com máximo de 1.551 MW) | check 12 | calcular o SIN por soma e usar a linha `SIN` só como validação |
| 11 | Intercâmbio líquido: o dicionário não define o sinal; pelos dados, positivo = exportação (média: N +1.723 MW, NE +146, S −955, SE −877). A soma dos quatro não é zero: coincide com o intercâmbio do `SIN` (cerca de +38 MW em média, provavelmente a troca com o exterior). Geração − carga − intercâmbio é próximo de zero na média, mas há horas com resíduo grande | checks 7 e 8 | usar a coluna oficial `val_intercambio` (M12); teste de resíduo como aviso |
| 12 | Valores suspeitos: 1 carga não positiva (zero é permitido no balanço, negativo não), 2 gerações térmicas negativas, 27 eólicas negativas e 1 solar negativa. Gerações e carga negativas violam o dicionário | check 9 | anular (NULL) e sinalizar os negativos; teste com aviso |
| 13 | Carga diária, contrato oficial × observado: os 13 valores ausentes violam a regra de não permitir nulo; o código de 3 posições explica os espaços de 2026 (os arquivos antigos foram gravados sem eles); o tipo FLOAT contradiz as colunas em texto até 2021 | dicionário oficial e checks 0, 3 e 14 | tratar como defeito de origem: filtrar no Silver e documentar. Os testes `not_null` e maior que zero seguem o dicionário oficial, com os três dias sem dado como exceção conhecida |
| 14 | O dicionário limita `nom_subsistema` do balanço a 20 posições, mas o nome do SIN (`SISTEMA INTERLIGADO NACIONAL`) tem 28 caracteres; a caixa dos nomes difere entre os datasets | profile e dicionário | usar o código; o nome vem de uma dimensão própria |

## 2. Open-Meteo

Levantamento pela documentação oficial (novembro de 2026). O que depende de medição será confirmado com `scripts/explore_open_meteo.py`.

- **API:** Historical Weather API, `https://archive-api.open-meteo.com/v1/archive`, sem chave.
- **Dados:** reanálise. ERA5 (0,25°, cerca de 25 km, de 1940), ERA5-Land (0,1°, cerca de 11 km, de 1950), ERA5-Seamless, IFS e outros. O padrão (`best_match`) combina IFS, ERA5 e ERA5-Land. Para séries longas e consistentes, a documentação recomenda ERA5 ou ERA5-Land. A precipitação não existe no ERA5-Land. O ERA5 é atualizado diariamente, com 5 dias de atraso.
- **Variáveis de interesse:** diárias `temperature_2m_mean`, `temperature_2m_max`, `temperature_2m_min` e `precipitation_sum` (as diárias exigem `timezone`); horárias, como `temperature_2m`.
- **Fuso:** `timezone=America/Sao_Paulo` usa o deslocamento do momento da requisição em todo o período e ignora mudanças de horário de verão. Para horas que respeitam o horário de verão, pedir `timeformat=unixtime` e converter. As fronteiras diárias seguem o deslocamento fixo, o que não afeta médias diárias de forma relevante.
- **Grade:** os valores são da célula da grade, que pode ficar a alguns quilômetros do ponto pedido; a altitude vem de um modelo de 90 m.
- **Limites do plano gratuito (uso não comercial, sem garantia de disponibilidade):** 600 chamadas por minuto, 5.000 por hora, 10.000 por dia e 300.000 por mês. Uma chamada cobre até 14 dias e 10 variáveis; acima disso a contagem é fracionada.
- **Estimativa da carga histórica (custo medido, ver resultados):** 11 cidades candidatas × 2000 até hoje × 2 variáveis diárias custam cerca de 1.540 chamadas (15% do limite diário), em requisições de 1 ano por cidade (cerca de 5,2 chamadas cada) e com pausa entre elas. A atualização incremental custa cerca de 11 chamadas por execução.
- **Licença e atribuição:** dados sob CC BY 4.0. É obrigatório um link para o Open-Meteo junto de qualquer exibição dos dados (por exemplo, no rodapé do dashboard: "Weather data by Open-Meteo.com"), além de indicar as alterações feitas. As reanálises vêm do Copernicus Climate Change Service (C3S). O plano gratuito é só para uso não comercial, o que cobre um projeto de portfólio.
**Resultados da exploração (`check`, `cities`, `tz` e `recency` rodados em 18 e 19 de novembro de 2026):**

- Os cabeçalhos da resposta confirmam o limite de 600 chamadas por janela de 60 s e o custo de 1,0 para 14 dias com até 10 variáveis.
- Unidades: temperatura em °C e precipitação em mm. Em 14 dias vieram 336 pontos horários, sem nulos.
- Grade de São Paulo (ponto pedido: -23,5505 e -46,6333): o ERA5 usa a célula -23,500 e -46,750 (13,2 km); o ERA5-Land e o ERA5-Seamless, a célula -23,600 e -46,600 (6,5 km); o padrão (`best_match`), -23,515 e -46,611 (4,6 km). A altitude da célula é 758 m em todos.
- Comparação para São Paulo em 2023 (365 dias):

| Modelo | Temperatura média | Precipitação total | Nulos de precipitação | Dif. média de temperatura vs ERA5 |
|---|---|---|---|---|
| padrão (`best_match`) | 19,77 °C | 1.338,7 mm | 0 | 0,975 °C |
| `era5` | 20,72 °C | 1.226,3 mm | 0 | referência |
| `era5_land` | 20,23 °C | sem dado | 365 | 0,625 °C |
| `era5_seamless` | 20,23 °C | 1.226,3 mm | 0 | 0,625 °C |

- Leitura: o `era5_seamless` combina a temperatura do ERA5-Land (grade de 0,1°) com a precipitação do ERA5, sem nulos e sem trocar de modelo ao longo do tempo. Os modelos diferem de 0,6 a 1,0 °C na média anual, então é preciso escolher um e mantê-lo em toda a série.
- Cidades, `era5_seamless` (2023-01-01 a 2023-01-14): as células ficam de 2,0 a 10,9 km do ponto pedido e a altitude é coerente com a cidade. Com o ERA5 puro (0,25°) as três primeiras cidades ficavam de 11 a 19 km.

| Sub | Cidade | Célula usada | Dist. (km) | Alt. (m) | T média (°C) |
|---|---|---|---|---|---|
| SE | São Paulo | -23,600, -46,600 | 6,5 | 758 | 20,59 |
| SE | Rio de Janeiro | -22,900, -43,100 | 7,5 | 12 | 25,02 |
| SE | Belo Horizonte | -19,900, -43,900 | 4,1 | 843 | 21,11 |
| SE | Brasília | -15,800, -47,900 | 2,0 | 1.092 | 21,22 |
| S | Porto Alegre | -30,000, -51,200 | 4,2 | 15 | 25,24 |
| S | Curitiba | -25,400, -49,300 | 4,1 | 920 | 19,10 |
| NE | Salvador | -13,000, -38,600 | 10,9 | 39 | 25,92 |
| NE | Fortaleza | -3,800, -38,500 | 8,1 | 21 | 27,14 |
| NE | Recife | -8,000, -34,900 | 5,9 | 3 | 27,16 |
| N | Manaus | -3,100, -60,000 | 3,2 | 47 | 25,69 |
| N | Belém | -1,500, -48,500 | 5,0 | 19 | 26,76 |

- **Estabilidade da API:** houve `ReadTimeout` (90 s) em várias chamadas, inclusive 3 tentativas seguidas em Manaus numa execução (a cidade respondeu depois, numa chamada isolada). A ingestão precisa de retry com espera crescente e não deve assumir resposta rápida.
- **Defasagem real:** em 2026-11-19, o `era5` e o `era5_seamless` terminaram em 2026-11-12, ou seja, 7 dias de defasagem (a documentação diz 5). Os dias seguintes vêm como `null` (7 nulos na janela), então a carga deve descartar nulos da ponta e reprocessar a janela final. O padrão (`best_match`) não tem defasagem, mas muda de modelo.
- **Fuso e horário de verão:** com `timezone=America/Sao_Paulo` no modo ISO, a API devolve 24 horas em todos os dias, inclusive em 2018-11-04, enquanto o ONS tem 23 linhas nesse dia. A série horária usa deslocamento fixo de -3 h (`utc_offset_seconds = -10800`). Como o MVP é diário e junta por data, não há problema.
- **Custo medido:** uma requisição de 1 ano com 2 variáveis diárias custou 5,214 chamadas (`X-RateLimit-Cost`), que é 365/14 × 2/10. Dias e variáveis escalam juntos, e o piso de 1 chamada vale só para a requisição inteira. O `cost` do script estimava cerca de 5 vezes mais por multiplicar um piso de 1 em cada fator, e foi corrigido.

**Proposta provisória:** modelo `era5_seamless`, variáveis diárias (temperatura média e precipitação), `timezone=America/Sao_Paulo`, requisições de 1 ano por cidade com pausa, e ingestão incremental que descarte nulos da ponta e reprocesse os últimos dias (defasagem de 7 dias, não 5).

## 3. Decisões e propostas (item 5 da Fase 01)

- **Histórico:** carregar de 2000 até hoje no Bronze. O volume é pequeno e o custo, trivial.
- **Granularidade do MVP:** diária por subsistema. As métricas horárias (M13 e M14) ficam para depois.
- **Janela de análise (decidida em 2026-11-20):** de 2019-01-01 até o último dia com clima disponível (cerca de 7 dias antes de hoje). A carga no Bronze e no Silver continua de 2000 a 2026; a janela vale para o Gold e para o dashboard. Motivos: (1) o último dia de 23 horas é 2018-11-04, então a janela não tem esse problema; (2) permite a variação anual de 2020 contra 2019 (M04) e inclui o efeito de 2020 e a crise hídrica de 2021 como candidatos a dia atípico; (3) os três dias sem dado e a linha espúria ficam em 2013 a 2015, fora da janela; (4) a relação entre carga e temperatura muda ao longo do tempo (racionamento de 2001), e uma janela de 26 anos misturaria regimes. O M07 usa janela anual e fica disponível para todos os anos. 2026 é parcial: comparar períodos equivalentes. O racionamento de 2001 pode virar um estudo de caso à parte, só com carga.
- **Cidades (decidido em 2026-11-20):** uma por subsistema, para começar: São Paulo (SE), Curitiba (S), Fortaleza (NE) e Manaus (N). Sem pesos por subsistema, porque cada cidade é o proxy do clima do seu subsistema; a ampliação fica para depois da primeira análise. Limitação a registrar nos requisitos: uma cidade não representa um subsistema inteiro. Hipótese ainda não medida: Fortaleza e Manaus têm temperatura quase constante, então a correlação carga × temperatura tende a ser fraca nelas.
- **Modelo do Open-Meteo:** `era5_seamless`, com temperatura média e precipitação diárias e `timezone=America/Sao_Paulo`.
- **Snowflake:** região AWS us-west-2 (Oregon), edição Enterprise (consome mais crédito por hora de warehouse que a Standard: manter o resource monitor e o auto-suspend de 60 s).
- **dbt:** a v1.0 do projeto usa dbt 1.x.

## 4. Pendências

- Geração distribuída: o dicionário não a menciona; tratar como não incluída até haver confirmação.
- Decidir o tratamento dos valores que violam os dicionários (achados 4, 5 e 12) e investigar os resíduos grandes (achado 11).
- Open-Meteo: verificar se os valores dos últimos dias do ERA5 são revisados depois (afeta a janela de reprocessamento).

## 5. Atribuição

Dados de energia: ONS, Operador Nacional do Sistema Elétrico, licença CC BY 4.0.