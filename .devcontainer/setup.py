"""Prepara arquivos locais sem iniciar serviços ou substituir segredos existentes."""

import base64
import os
from pathlib import Path
import secrets

root = Path(__file__).resolve().parent.parent
for directory in (
    "dags",
    "plugins",
    "ingestion",
    "dbt",
    "data/bronze/ons",
    "data/bronze/open_meteo",
    "warehouse",
    ".local/airflow",
):
    (root / directory).mkdir(parents=True, exist_ok=True)

env = root / ".env"
if not env.exists():
    content = (root / ".env.example").read_text(encoding="utf-8")
    replacements = {
        "AIRFLOW_UID=50000": f"AIRFLOW_UID={os.getuid() if hasattr(os, 'getuid') else 50000}",
        "CHANGE_ME_POSTGRES": secrets.token_hex(24),
        "CHANGE_ME_FERNET": base64.urlsafe_b64encode(os.urandom(32)).decode(),
        "CHANGE_ME_JWT": secrets.token_hex(32),
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    with env.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
    env.chmod(0o600)
    print(".env criado com segredos locais. Não o adicione ao Git.")
else:
    print(".env existente preservado.")
print("Para iniciar: docker compose up -d --build --wait --wait-timeout 300")
