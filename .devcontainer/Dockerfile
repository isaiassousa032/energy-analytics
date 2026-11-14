FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Alterna para root para ajustar repositórios do sistema
USER root

# Remove o repositório do Yarn da imagem base (chave GPG ausente/expirada)
# para evitar falhas no `apt-get update` executado pelas Dev Container Features.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

# Retorna ao usuário padrão não-privilegiado do container
USER vscode