# Learn.py (In development, unfinished)

**Final Class Project**  
**Course:** 2ºSMR  

Visit the platform here: [lt209.ddns.net:2000](http://lt209.ddns.net:2000)
---

## Project Description

**Learn.py** is an educational platform inspired by **Moodle** and **Google Classroom**, designed to facilitate the organization of classes, assignments, and communication between teachers and students.  

The system combines the best of both platforms, with a **modern and intuitive interface**, allowing simple management in both in-person and remote environments.  

It has been developed with a modular and scalable approach, using **Django** for the backend, **Svelte** for the frontend, and **SQLite** as the database.

---

## Technical Summary

| Component        | Technology Used                          |
|------------------|------------------------------------------|
| **Backend**       | Django (Python) + Django REST Framework  |
| **Frontend**      | Svelte                                   |
| **Database**      | SQLite                                   |
| **Server**        | Raspberry Pi (Debian, terminal version) |

---

## Project Objectives

- Develop a platform with **differentiated roles**: administrator, teacher, and student.  
- Implement a **class and assignment management system**, with file uploads, deadlines, and grading.  
- Integrate an **internal communication channel** and **real-time notifications**.  
- Optimize the system to run on a **Raspberry Pi with Debian**.

---

## Installation and Configuration

### Prerequisites

Make sure you have installed:
- **Python 3.x**
- **pip**
- **Node.js** and **npm**

---

### Create virtual environment

```bash
python -m venv venv
```

Activate the virtual environment:  
Windows  
```bash
venv\Scripts\activate
````
Linux  
```bash
source venv/bin/activate
```

## Install Python dependencies
```bash
pip install djangorestframework djangorestframework-simplejwt django-cors-headers pillow
````

## Start project
Windows:
```bash
start.bat
```
Linux:
```bash
chmod +x startLinux.sh
./startLinux.sh
```

This will start both servers

| Service   | Local URL                                      |
| ---------- | ---------------------------------------------- |
| **Django** | [http://localhost:8000](http://localhost:8000) |
| **Svelte** | [http://localhost:8001](http://localhost:8001) |

### Configuration

## Change backend IP in the frontend
In the file: Learn.py/Frontend/src/lib/config.ts  
edit the line:
```python
export const urlip = "http://localhost:8000/api/";
```

## Change frontend ports
On Windows (startWin.bat):
```bash
start cmd /k "cd frontend && npm run dev -- --host --port=[PORT]"
```
Linux (startLinux.bat):
```bash
cd frontend && npm run dev -- --host --port=[PORT]
```

## Configure CORS in Django
If you change the frontend port, you must update the allowed origins in:
Learn.py/backend/backend/setting/settings.py

Example:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]
```
