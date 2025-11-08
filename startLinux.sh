#!/bin/bash

# Servidor django en background
source venv/bin/activate && cd backend/backend && python manage.py runserver &

# Servidor svelte en foreground
cd frontend && npm run dev -- --host --port=8001