#!/bin/bash

# Ruta donde está el script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuración
ARCHIVO="$SCRIPT_DIR/backend/backend/db.sqlite3"
CARPETA="$SCRIPT_DIR/backend/backend/media"
DESTINO="/backupLearn.py"

if [ "$EUID" -ne 0 ]; then
    echo "No eres administrador"
    exit 1
fi

# Crear carpeta backup si no existe
mkdir -p "$DESTINO"

# Fecha y hora
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")

# Nombre del backup
NOMBRE="backup_$FECHA.tar.gz"

# Crear backup
tar -czvf "$DESTINO/$NOMBRE" "$ARCHIVO" "$CARPETA"

echo "Backup creado en $DESTINO/$NOMBRE"
