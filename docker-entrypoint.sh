#!/bin/bash

# Iniciar FastAPI en background
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
APP_PID=$!

# Esperar un momento para que la app se inicie
sleep 3

# Ejecutar script de inicialización del usuario
poetry run python init_user.py

# Mantener FastAPI en primer plano
wait $APP_PID 