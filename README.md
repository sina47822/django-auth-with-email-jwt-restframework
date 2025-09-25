# Django + DRF + JWT (HttpOnly Cookie) + PostgreSQL — User Authentication API

A simple user authentication API built with **Django**, **Django REST Framework**, and **JWT**.  
The JWT token is stored in an **HttpOnly cookie** for security. The project uses **PostgreSQL** as the database and a custom `User` model extending `AbstractUser`.

---

## ✨ Features
- User registration (`/api/register/`)
- Login with JWT (HttpOnly cookie) (`/api/login/`)
- Get authenticated user details (`/api/user/`)
- Logout and delete JWT cookie (`/api/logout/`)
- Custom user model with email-based login

---

## 🛠 Tech Stack
- Python 3.11+ (recommended)
- Django 5.x
- Django REST Framework
- PyJWT
- PostgreSQL 13+

---

## 📂 Project Structure

```plaintext
core/
│── core/
│   └── urls.py
│
└── accounts/
    ├── models.py
    ├── serializers.py
    ├── views.py
    └── urls.py
```

---

## ⚙️ Setup & Installation

Requirements
- PostgreSQL installed and database created
- `.env` file with `SECRET_KEY` and DB credentials

Example `.env`:
``` #env
SECRET_KEY=replace-with-strong-secret
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Configure PostgreSQL `(settings.py)`
```
import os
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv("DB_NAME"),
    "USER": os.getenv("DB_USER"),
    "PASSWORD": os.getenv("DB_PASSWORD"),
    "HOST": os.getenv("DB_HOST", "127.0.0.1"),
    "PORT": os.getenv("DB_PORT", "5432"),
  }
}
```
Since a custom user model is used:
```
AUTH_USER_MODEL = "accounts.User"
```
# 🚀 Local Setup
```
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
# Or:
# pip install django djangorestframework pyjwt psycopg2-binary python-dotenv

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create admin user (optional)
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver
```

# 🔐 Authentication & JWT

- On login, a JWT is generated with:
-- exp: 60 minutes
-- iat: issued at
-- id: user ID
- Token is stored in an HttpOnly cookie (jwt).
- On /api/user/, token is decoded and validated.
- On logout, the cookie is deleted.
# Production Security Notes
- Always enable Secure=True (HTTPS only)
- Use SameSite="Lax" or "Strict"
- Set DEBUG=False and a strong SECRET_KEY
## Example secure cookie:

```
response.set_cookie(
    key="jwt",
    value=token,
    httponly=True,
    secure=True,
    samesite="Lax",
    max_age=60*60
)
```
# 📚 API Endpoints
| Method | Path             | Description                 | Auth Required |
| ------ | ---------------- | --------------------------- | ------------- |
| POST   | `/api/register/` | Register new user           | ❌             |
| POST   | `/api/login/`    | Login, set JWT cookie       | ❌             |
| GET    | `/api/user/`     | Get authenticated user info | ✅             |
| POST   | `/api/logout/`   | Logout and clear JWT cookie | ✅             |

---

# 🧪 Quick Test with cURL
Register
```
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","password":"Password123"}'
```
Login
```
curl -i -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Password123"}' \
  -c cookies.txt
```
Get User Info
```
curl -X GET http://127.0.0.1:8000/api/user/ -b cookies.txt
```
Logout
```
curl -X POST http://127.0.0.1:8000/api/logout/ -b cookies.txt
```

---

📦 .gitignore Example
```
.venv/
__pycache__/
*.pyc
*.sqlite3
.env
.idea/
.vscode/
```

# ✅ License
MIT (or add your preferred license)

---

# 🤝 Contributions
Pull requests and issues are welcome


