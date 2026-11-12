# Pasta `carga_energia_di`

## schema (arquivo mais recente) --
┌───────────────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│      column_name      │ column_type │  null   │   key   │ default │  extra  │
│        varchar        │   varchar   │ varchar │ varchar │ varchar │ varchar │
├───────────────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ id_subsistema         │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ nom_subsistema        │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ din_instante          │ TIMESTAMP   │ YES     │ NULL    │ NULL    │ NULL    │
│ val_cargaenergiamwmed │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
└───────────────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘

arquivos: 83 | usando parquet (27) | anos nos nomes: 2000-2026
primeiro: s3://ons-aws-prod-opendata/dataset/carga_energia_di/CARGA_ENERGIA_2000.parquet
último:   s3://ons-aws-prod-opendata/dataset/carga_energia_di/CARGA_ENERGIA_2026.parquet

-- linhas (todos os arquivos) --
┌────────┐
│ linhas │
│ int64  │
├────────┤
│  39221 │
└────────┘


-- período (todos os arquivos) --
┌─────────────────────┬─────────────────────┐
│  din_instante_min   │  din_instante_max   │
│       varchar       │       varchar       │
├─────────────────────┼─────────────────────┤
│ 2000-01-01 00:00:00 │ 2026-11-04 00:00:00 │
└─────────────────────┴─────────────────────┘


-- nulos por coluna (arquivo mais recente) --
┌───────────────┬────────────────┬──────────────┬───────────────────────┐
│ id_subsistema │ nom_subsistema │ din_instante │ val_cargaenergiamwmed │
│     int64     │     int64      │    int64     │         int64         │
├───────────────┼────────────────┼──────────────┼───────────────────────┤
│             0 │              0 │            0 │                     0 │
└───────────────┴────────────────┴──────────────┴───────────────────────┘


-- valores distintos de colunas de texto com até 15 valores --
id_subsistema (4): ['N', 'NE', 'S', 'SE']
nom_subsistema (4): ['Nordeste', 'Norte', 'Sudeste/Centro-Oeste', 'Sul']

-- amostra (5 linhas do arquivo mais recente) --
┌───────────────┬──────────────────────┬─────────────────────┬───────────────────────┐
│ id_subsistema │    nom_subsistema    │    din_instante     │ val_cargaenergiamwmed │
│    varchar    │       varchar        │      timestamp      │        double         │
├───────────────┼──────────────────────┼─────────────────────┼───────────────────────┤
│ N             │ Norte                │ 2026-01-01 00:00:00 │     7649.438875000001 │
│ NE            │ Nordeste             │ 2026-01-01 00:00:00 │    12269.972583333334 │
│ S             │ Sul                  │ 2026-01-01 00:00:00 │    11203.195916666666 │
│ SE            │ Sudeste/Centro-Oeste │ 2026-01-01 00:00:00 │            40463.7935 │
│ N             │ Norte                │ 2026-01-02 00:00:00 │     8235.208333333334 │
└───────────────┴──────────────────────┴─────────────────────┴───────────────────────┘