# Gestion.2.0 Backend

Backend Django REST Framework genere depuis les pages et formulaires Angular de `Gestion.2.0_frontend`.

## Modules deduits du frontend

- Authentification et profil utilisateur
- Competitions CRUD
- Equipes CRUD
- Joueurs CRUD rattaches aux equipes
- Matchs CRUD, planification, scores, buts et cartons
- Classements recalcules depuis les matchs termines
- Notifications CRUD et marquage comme lues
- Journal d'audit en lecture

## Installation

```powershell
..\env\Scripts\python.exe -m pip install -r requirements.txt
..\env\Scripts\python.exe manage.py migrate
..\env\Scripts\python.exe manage.py seed_demo
..\env\Scripts\python.exe manage.py runserver
```
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
"""
API: `http://127.0.0.1:8000/api/`

## Auth

```http
POST /api/auth/login/
{
  "email": "admin@iusj.org",
  "motDePasse": "admin123"
}
```

La reponse contient `token`, `refresh` et `user`. Envoyer ensuite:

```http
Authorization: Bearer <token>
```
