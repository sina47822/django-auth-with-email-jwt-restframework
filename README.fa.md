# جنگو + DRF + JWT (کوکی HttpOnly) + PostgreSQL — احراز هویت کاربر

[🇬🇧 Read in English](./README.md)


یک API ساده برای مدیریت کاربران با استفاده از **Django**، **Django REST Framework** و **JWT**.  
توکن JWT در یک **کوکی HttpOnly** ذخیره می‌شود تا امنیت بیشتری داشته باشد. دیتابیس پروژه **PostgreSQL** است و از یک مدل کاربر سفارشی بر پایه `AbstractUser` استفاده شده است.

---

## ✨ امکانات
- ثبت‌نام کاربر جدید (`/api/register/`)
- ورود با JWT (ذخیره در کوکی HttpOnly) (`/api/login/`)
- دریافت اطلاعات کاربر احراز هویت شده (`/api/user/`)
- خروج و حذف کوکی JWT (`/api/logout/`)
- مدل کاربر سفارشی با ورود بر اساس ایمیل

---

## 🛠 تکنولوژی‌ها
- Python 3.11+ (پیشنهادی)
- Django 5.x
- Django REST Framework
- PyJWT
- PostgreSQL 13+

---

## 📂 ساختار پروژه

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

## ⚙️ نصب و راه‌اندازی

پیش‌نیازها
- نصب PostgreSQL و ایجاد دیتابیس
- ایجاد فایل `.env` شامل `SECRET_KEY` و اطلاعات دیتابیس

نمونه فایل `.env`:
```
SECRET_KEY=replace-with-strong-secret
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

تنظیمات PostgreSQL در `(settings.py)`
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
استفاده از مدل کاربر سفارشی
```
AUTH_USER_MODEL = "accounts.User"
```
# 🚀 اجرای لوکال
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

# 🔐 احراز هویت و

- هنگام ورود، یک توکن JWT تولید می‌شود با مقادیر زیر:
-- `(exp)` : زمان انقضا (۶۰ دقیقه)
-- `(iat)` : زمان انقضا (۶۰ دقیقه)
-- `(id)` : شناسه کاربر
- توکن در یک کوکی HttpOnly ذخیره می‌شود `(jwt)`.
- در اندپوینت /api/user/، توکن دیکود و اعتبارسنجی می‌شود.
- در اندپوینت خروج، کوکی حذف می‌شود.
# نکات امنیتی در محیط Production
- حتماً `(Secure=True)` (HTTPS فقط روی)
- استفاده از `(SameSite="Lax")` یا `("Strict")`
- تنظیم `(DEBUG=False)` و استفاده از `(SECRET_KEY)` قوی
نمونه ست کردن کوکی امن:

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
# 📚 اندپوینت‌ها
| Method | Path             | Description                 | Auth Required |
| ------ | ---------------- | --------------------------- | ------------- |
| POST   | `/api/register/` | Register new user           | ❌             |
| POST   | `/api/login/`    | Login, set JWT cookie       | ❌             |
| GET    | `/api/user/`     | Get authenticated user info | ✅             |
| POST   | `/api/logout/`   | Logout and clear JWT cookie | ✅             |

---

# 🧪 تست سریع با cURL
ثبت‌نام
```
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com","password":"Password123"}'
```
ورود
```
curl -i -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Password123"}' \
  -c cookies.txt
```
دریافت اطلاعات کاربر
```
curl -X GET http://127.0.0.1:8000/api/user/ -b cookies.txt
```
خروج
```
curl -X POST http://127.0.0.1:8000/api/logout/ -b cookies.txt
```

---

# 📦 فایل .gitignore پیشنهادی
```
.venv/
__pycache__/
*.pyc
*.sqlite3
.env
.idea/
.vscode/
```

# ✅ مجوز
MIT (یا هر مجوز دلخواه دیگر)

---

# 🤝 مشارکت
هرگونه Pull Request و Issue پذیرفته می‌شود.


