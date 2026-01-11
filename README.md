# Learn.py (En proceso de creación sin terminar)

**Autor:** Lucas Karlsson López  
**Curso:** 2ºSMR  

---

## Descripción del Proyecto

**Learn.py** es una plataforma educativa inspirada en **Moodle** y **Google Classroom**, diseñada para facilitar la organización de clases, tareas y la comunicación entre docentes y estudiantes.  

El sistema combina lo mejor de ambas plataformas, con una **interfaz moderna e intuitiva**, permitiendo una gestión sencilla tanto en entornos presenciales como a distancia.  

Se ha desarrollado con un enfoque modular y escalable, usando **Django** para el backend, **Svelte** para el frontend y **SQLite** como base de datos.

---

## Resumen Técnico

| Componente        | Tecnología Utilizada                     |
|-------------------|------------------------------------------|
| **Backend**       | Django (Python) + Django REST Framework  |
| **Frontend**      | Svelte                                   |
| **Base de Datos** | SQLite                                   |
| **Servidor**      | Raspberry Pi (Debian, versión terminal)  |
| **Autenticación** | OAuth2 (Google)                          |

---

## Objetivos del Proyecto

- Desarrollar una plataforma con **roles diferenciados**: administrador, docente y estudiante.  
- Implementar un **sistema de gestión de clases y tareas**, con subida de archivos, fechas límite y calificación.  
- Integrar un **canal de comunicación interna** y **notificaciones en tiempo real**.  
- Optimizar el sistema para ejecutarse en una **Raspberry Pi con Debian**.

---

## Instalación y Configuración

### Requisitos previos

Asegúrate de tener instalados:
- **Python 3.x**
- **pip**
- **Node.js** y **npm**

---

### Crear entorno virtual

```bash
python -m venv venv
```

Activar el entorno virtual:
Windows	
```bash
venv\Scripts\activate
````
Linux
```bash
source venv/bin/activate
```
## Instalar dependencias de Python
```bash
pip install djangorestframework djangorestframework-simplejwt django-cors-headers pillow
````
## Iniciar proyecto
Windows:
```bash
start.bat
```
Linux:
```bash
chmod +x startLinux.sh
./startLinux.sh

```
Esto iniciara ambos servidores
| Servicio   | URL Local                                      |
| ---------- | ---------------------------------------------- |
| **Django** | [http://localhost:8000](http://localhost:8000) |
| **Svelte** | [http://localhost:8001](http://localhost:8001) |

### Configuración
## Cambiar la IP del backend en el frontend
En la archivo: Learn.py/Frontend/src/lib/config.ts
editas la linea:
```python
export const urlip = "http://localhost:8000/api/";
```

## Cambiar los puertos del frontend
En Windows (startWin.bat):
```bash
start cmd /k "cd frontend && npm run dev -- --host --port=[PUERTO]"
```
Linux (startLinux.bat):
```bash
cd frontend && npm run dev -- --host --port=[PUERTO]
```

## Configurar CORS en Django
Si modificas el puerto del frontend, debes actualizar los orígenes permitidos en:
Learn.py/backend/backend/setting/settings.py

Ejemplo:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]
```
