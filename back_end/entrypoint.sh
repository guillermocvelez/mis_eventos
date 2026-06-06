#!/bin/bash
set -e

echo "Aplicando migraciones..."
alembic upgrade head

echo "Iniciando servidor..."
fastapi run app/main.py --host 0.0.0.0 --port 8000