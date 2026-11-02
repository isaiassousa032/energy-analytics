#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python .devcontainer/setup.py

# O daemon Docker pode ainda estar inicializando ao retomar o devcontainer.
for attempt in {1..30}; do
  if docker info >/dev/null 2>&1; then
    break
  fi
  if [ "$attempt" -eq 30 ]; then
    echo "Docker indisponível. Consulte os logs do devcontainer e execute bash .devcontainer/start.sh novamente." >&2
    exit 1
  fi
  sleep 2
done

# Ao retomar o Codespace podem sobrar containers com estado inconsistente.
# Os dados ficam em bind mounts (.local/, data/, warehouse/), então recriar é seguro.
docker compose down --remove-orphans >/dev/null 2>&1 || true

docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 300

# DuckDB aceita um escritor por vez: tasks que gravam no warehouse usam esta pool.
docker compose exec -T airflow airflow pools set duckdb 1 "Escrita serializada no DuckDB" \
  || echo "Aviso: não foi possível criar a pool 'duckdb'. Rode o comando manualmente." >&2

echo "Airflow iniciado. Abra a porta 8080 na aba Ports e mantenha a visibilidade Private."
