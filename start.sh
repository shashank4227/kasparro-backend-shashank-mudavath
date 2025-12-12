#!/bin/bash
set -e

echo "Initializing Database..."
python -c 'from core.database import init_db; init_db()'

echo "Starting ETL Pipeline in background..."
python main.py &

echo "Starting API Service..."
exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
