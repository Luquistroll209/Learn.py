@echo off
REM Servidor django
start cmd /k ".\venv\Scripts\activate && cd .\backend\backend && python manage.py runserver"

REM Servidor svelte
start cmd /k "cd frontend && npm run dev -- --host --port=8001"
