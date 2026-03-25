#!/bin/bash

# Configuración
ARCHIVO="/home/luquis/Documentos/GitHub/Learn.py/backend/backend/db.sqlite3"
CARPETA="/home/luquis/Documentos/GitHub/Learn.py/backend/backend/media"
DESTINO="/backupLearn.py"

if [ "$EUID" -ne 0 ]; then
    echo "No eres administrador"
    exit 1
fi

if [ ! -d "$DESTINO" ]; then
    mkdir "$DESTINO"
fi
# Fecha y hora
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")

# Nombre del backup
NOMBRE="backup_$FECHA.tar.gz"

# Crear backup
tar -czvf "$DESTINO/$NOMBRE" "$ARCHIVO" "$CARPETA"

echo "Backup creado en $DESTINO/$NOMBRE"