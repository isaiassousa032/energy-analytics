FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

USER root
# Yarn não é usado neste ambiente. A fonte herdada tem uma chave GPG
# ausente e impede o apt-get update executado pela feature Docker.
# Removemos apenas essa fonte, sem desabilitar verificações de assinatura.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && rm -rf /var/lib/apt/lists/*

USER vscode