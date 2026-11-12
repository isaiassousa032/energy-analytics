"""Explora o bucket público de dados abertos do ONS (sem credenciais).

Uso, a partir da raiz do repositório, no terminal do Codespace:

  # 1) lista as pastas (datasets), formatos e anos disponíveis
  docker compose exec -T airflow python - list < scripts/explore_ons.py

  # 2) perfil de um dataset: schema, linhas, período, nulos e valores distintos
  docker compose exec -T airflow python - profile NOME_DA_PASTA < scripts/explore_ons.py

Variável opcional: ONS_BASE (padrão: s3://ons-aws-prod-opendata/dataset).
"""

import difflib
import os
import re
import sys
from collections import defaultdict

import duckdb

BASE = os.environ.get("ONS_BASE", "s3://ons-aws-prod-opendata/dataset").rstrip("/")

con = duckdb.connect()
if BASE.startswith("s3://"):
    con.execute("SET extension_directory='/tmp/duckdb_extensions'")
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    con.execute("SET s3_region='sa-east-1'")  # acesso anônimo: bucket público


def list_files():
    rows = con.execute(f"SELECT file FROM glob('{BASE}/**')").fetchall()
    folders = defaultdict(list)
    for (path,) in rows:
        rel = path[len(BASE) + 1:]
        if "/" in rel:
            folders[rel.split("/", 1)[0]].append(path)
    return folders


def years_in(names):
    years = set()
    for name in names:
        years.update(re.findall(r"(?<!\d)((?:19|20)\d{2})(?!\d)", name))
    return years


def cmd_list():
    folders = list_files()
    print(f"{'pasta':46}{'arquivos':>9}  {'formatos':24}anos")
    for folder in sorted(folders):
        files = folders[folder]
        names = [f.rsplit("/", 1)[-1] for f in files]
        exts = defaultdict(int)
        for n in names:
            exts[n.rsplit(".", 1)[-1].lower() if "." in n else "?"] += 1
        fmt = ",".join(f"{k}:{v}" for k, v in sorted(exts.items()))
        yrs = years_in(names)
        span = f"{min(yrs)}-{max(yrs)}" if yrs else "-"
        print(f"{folder:46}{len(files):>9}  {fmt:24}{span}")
    print(f"\n{len(folders)} pastas em {BASE}")


def reader(files, kind):
    lst = ", ".join(f"'{f}'" for f in files)
    if kind == "parquet":
        return f"read_parquet([{lst}], union_by_name=true)"
    return f"read_csv([{lst}], all_varchar=true, union_by_name=true)"


def show(sql):
    con.sql(sql).show(max_width=220, max_rows=60)


def cmd_profile(dataset):
    folders = list_files()
    if dataset not in folders:
        close = difflib.get_close_matches(dataset, folders, n=5)
        print(f"Pasta '{dataset}' não encontrada. Parecidas: {close or 'nenhuma'}")
        print("Rode o comando 'list' para ver todas as pastas.")
        sys.exit(1)

    files = sorted(folders[dataset])
    parquet = [f for f in files if f.lower().endswith(".parquet")]
    csv = [f for f in files if f.lower().endswith(".csv")]
    kind, usable = ("parquet", parquet) if parquet else ("csv", csv)
    if not usable:
        print("Nenhum arquivo Parquet ou CSV nesta pasta. Arquivos:", files[:10])
        sys.exit(1)

    names = [f.rsplit("/", 1)[-1] for f in files]
    yrs = years_in(names)
    print(f"== {dataset} ==")
    print(f"arquivos: {len(files)} | usando {kind} ({len(usable)}) | anos nos nomes: "
          f"{min(yrs) + '-' + max(yrs) if yrs else '-'}")
    print(f"primeiro: {usable[0]}\núltimo:   {usable[-1]}")

    newest = reader([usable[-1]], kind)
    everything = reader(usable, kind) if kind == "parquet" else reader(sorted({usable[0], usable[-1]}), kind)

    print("\n-- schema (arquivo mais recente) --")
    show(f"DESCRIBE SELECT * FROM {newest}")
    schema = con.execute(f"DESCRIBE SELECT * FROM {newest}").fetchall()
    cols = [(r[0], r[1]) for r in schema]

    scope = "todos os arquivos" if kind == "parquet" else "primeiro e último CSV (amostra)"
    print(f"\n-- linhas ({scope}) --")
    show(f"SELECT count(*) AS linhas FROM {everything}")

    date_cols = [c for c, _ in cols
                 if c.lower().startswith(("din_", "dat_")) or re.search(r"data|date|instante", c.lower())]
    if date_cols:
        print(f"\n-- período ({scope}) --")
        parts = ", ".join(f'min("{c}")::VARCHAR AS "{c}_min", max("{c}")::VARCHAR AS "{c}_max"'
                          for c in date_cols)
        show(f"SELECT {parts} FROM {everything}")

    print("\n-- nulos por coluna (arquivo mais recente) --")
    parts = ", ".join(f'count(*) - count("{c}") AS "{c}"' for c, _ in cols)
    show(f"SELECT {parts} FROM {newest}")

    text_cols = [c for c, t in cols if t.upper().startswith("VARCHAR") and c not in date_cols]
    if text_cols:
        parts = ", ".join(f'count(DISTINCT "{c}") AS "{c}"' for c in text_cols)
        counts = con.execute(f"SELECT {parts} FROM {newest}").fetchone()
        print("\n-- valores distintos de colunas de texto com até 15 valores --")
        for c, n in zip(text_cols, counts):
            if n <= 15:
                vals = [r[0] for r in con.execute(
                    f'SELECT DISTINCT "{c}" FROM {newest} ORDER BY 1').fetchall()]
                print(f"{c} ({n}): {vals}")

    print("\n-- amostra (5 linhas do arquivo mais recente) --")
    show(f"SELECT * FROM {newest} LIMIT 5")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["list"]:
        cmd_list()
    elif args[:1] == ["profile"] and len(args) == 2:
        cmd_profile(args[1])
    else:
        print(__doc__)
        sys.exit(2)
