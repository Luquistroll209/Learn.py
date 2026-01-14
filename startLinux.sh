#!/bin/bash

# Servidor django en background
source env/bin/activate && cd backend/backend && python manage.py runserver &

# Servidor svelte en foreground
cd Frontend && npm run dev -- --host --port=8001
