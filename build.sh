#!/usr/bin/env bash
# Script de build para o Render / CI
set -o errexit

pip install -r requirements.txt

# Executa migrações no banco de dados de produção
flask db upgrade
