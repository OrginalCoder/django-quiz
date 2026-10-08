# Django Quiz Platformasi — Render.com Deploy Qo'llanmasi (SQLite)

Zamonaviy, xavfsiz va to'liq interaktiv Django Quiz platformasi. Ushbu loyihada real vaqt rejimida PvP janglar, haftalik turnirlar, Google OAuth orqali autentifikatsiya, AI tahlili, geymifikatsiya nishonlari va anti-cheat tizimlari mujassamlashgan.

Ma'lumotlar bazasi sifatida **SQLite (`db.sqlite3`)** ishlatiladi — alohida tashqi baza (PostgreSQL) ochish shart emas!

---

## Mundarija
1. [Loyiha xususiyatlari](#loyiha-xususiyatlari)
2. [Render.com ga Deploy qilish (Qadamma-qadam)](#rendercom-ga-deploy-qilish-qadamma-qadam)
   - [1-qadam: Loyihani GitHub-ga yuklash](#1-qadam-loyihani-github-ga-yuklash)
   - [2-qadam: Render-da Web Service yaratish](#2-qadam-render-da-web-service-yaratish)
   - [3-qadam: Muhit o'zgaruvchilarini (Environment Variables) sozlash](#3-qadam-muhit-ozgaruvchilarini-environment-variables-sozlash)
   - [4-qadam: Google Cloud Console da Redirect URI ni qo'shish](#4-qadam-google-cloud-console-da-redirect-uri-ni-qoshish)
   - [5-qadam: Admin (Superuser) hisobiga kirish](#5-qadam-admin-superuser-hisobiga-kirish)
3. [Mahalliy kompyuterda (Local) ishga tushirish](#mahalliy-kompyuterda-local-ishga-tushirish)

---

## Loyiha xususiyatlari

- **Ma'lumotlar bazasi:** SQLite (`db.sqlite3`) — har qanday ortiqcha sozlamalarsiz to'g'ridan-to'g'ri ishlaydi.
- **Avtomatik Admin Yaratish:** `build.sh` orqali admin foydalanuvchisi avtomatik yaratiladi va paroli saqlanadi.
- **Google OAuth:** django-allauth orqali bir bosqichli Google orqali tezkor kirish va ro'yxatdan o'tish.
- **Anti-Cheat Himoyasi:** Test paytida nusxa olish, sichqonchaning o'ng tugmasi, matn belgilash, F12 / DevTools, skrinshot harakatlari va ko'p barmoqli teginishlar cheklangan.
- **PvP Battle & Turnirlar:** Foydalanuvchilar o'rtasida real vaqtda raqobat va haftalik mukofotli sovrinli turnirlar.
- **Geymifikatsiya:** Foydalanuvchi darajalari, XP, yutuq nishonlari (Badges) va xatolar ustida ishlash bo'limi.
- **Production-ready:** WhiteNoise orqali statik fayllar optimizatsiyasi va Gunicorn serveri bilan sozlangan.

---

## Render.com ga Deploy qilish (Qadamma-qadam)

### 1-qadam: Loyihani GitHub-ga yuklash

Agar loyihangiz hali GitHub-da bo'lmasa, terminalda quyidagi buyruqlarni ketma-ket bajaring:

```bash
git init
git add .
git commit -m "Render deploy tayyorgarligi"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

*(Eslatma: `.env` fayli `.gitignore` orqali himoyalangan va GitHub-ga yuklanmaydi).*

---

### 2-qadam: Render-da Web Service yaratish

1. [Render.com](https://render.com) saytiga kiring va profilingizni oching.
2. Dashboard-da **New +** tugmasini bosing va **Web Service** ni tanlang.
3. **Build and deploy from a Git repository** ni tanlab, GitHub-dagi loyiha repozitoriyangizni ulang.
4. Asosiy parametrlarni quyidagicha to'ldiring:
   - **Name:** `quiz-app` (bu sizning domen nomingiz bo'ladi, masalan: `quiz-app.onrender.com`)
   - **Region:** Frankfurt (yoki o'zingizga yaqin hudud)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`
   - **Plan:** Free

---

### 3-qadam: Muhit o'zgaruvchilarini (Environment Variables) sozlash

O'sha Web Service sahifasidagi **Environment Variables** bo'limiga o'ting va quyidagi o'zgaruvchilarni kiriting:

| O'zgaruvchi nomi | Standart qiymat | Tavsif |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.14.3` (yoki `3.12.0`) | Python versiyasi |
| `SECRET_KEY` | Tasodifiy uzun maxfiy satr | Django xavfsizlik kaliti |
| `DEBUG` | `False` | Production rejimi |
| `DJANGO_SUPERUSER_USERNAME` | `admin` | Admin panel login nomi |
| `DJANGO_SUPERUSER_PASSWORD` | `admin123` (yoki xohlagan kuchli parolingiz) | Admin panel paroli |
| `DJANGO_SUPERUSER_EMAIL` | `admin@quiz.uz` | Admin elektron pochtasi |
| `GOOGLE_CLIENT_ID` | Google Cloud Console Client ID | Google orqali kirish uchun |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console Client Secret | Google OAuth maxfiy kaliti |
| `GEMINI_API_KEY` | Gemini API kalitingiz | AI tavsiyalari va savollar tahlili uchun |

Sozlamalarni kiritgach, **Create Web Service** (yoki **Save Changes**) tugmasini bosing.

Render avtomatik tarzda:
- `requirements.txt` dagi barcha kerakli kutubxonalarni o'rnatadi
- Statik fayllarni `collectstatic` orqali to'playdi
- `python manage.py migrate` orqali SQLite (`db.sqlite3`) bazasini va barcha jadvallarni shakllantiradi
- `python manage.py seed_data` orqali test toifalarini va savollarni avtomatik yuklaydi
- `python manage.py create_admin` orqali admin login va parolini avtomatik yaratib, saqlab ketadi
- `gunicorn` orqali saytni ishga tushiradi

---

### 4-qadam: Google Cloud Console da Redirect URI ni qo'shish

Render sizga tayyor veb-sayt domenini taqdim etadi (masalan: `https://quiz-app.onrender.com`).
Google orqali kirish to'g'ri ishlashi uchun:

1. [Google Cloud Console](https://console.cloud.google.com/) sahifasiga kiring.
2. **APIs & Services** > **Credentials** bo'limiga o'ting.
3. OAuth 2.0 Client ID sozlamasini tahrirlash uchun qalamcha belgisini bosing.
4. **Authorized JavaScript origins** ga Render domeningizni qo'shing:
   - `https://quiz-app.onrender.com`
5. **Authorized redirect URIs** ga ushbu manzilni qo'shing:
   - `https://quiz-app.onrender.com/accounts/google/login/callback/`
6. **Save** tugmasini bosing.

Endi Render saytingizda Google hisobi orqali kirish to'liq ishlaydi!

---

### 5-qadam: Admin (Superuser) hisobiga kirish

Admin foydalanuvchisi deploy jarayonida (`build.sh`) avtomatik yaratiladi!
Sayt tayyor bo'lgach:

1. Brauzerda quyidagi manzilni oching:
   `https://quiz-app.onrender.com/admin/`
2. Kirish ma'lumotlari:
   - **Login:** `admin` (yoki `DJANGO_SUPERUSER_USERNAME` da kiritgan nomingiz)
   - **Parol:** `admin123` (yoki `DJANGO_SUPERUSER_PASSWORD` da kiritgan parolingiz)

Agar parolni keyinchalik o'zgartirmoqchi bo'lsangiz, Render Environment Variables bo'limida yangi parol yozib, qayta deploy qilishingiz kifoya.

---

## Mahalliy kompyuterda (Local) ishga tushirish

```bash
python -m venv .venv
source .venv/bin/activate  # Windows uchun: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py create_admin
python manage.py runserver
```

Sayt manzili: `http://127.0.0.1:8000/`
Admin panel: `http://127.0.0.1:8000/admin/` (Login: `admin`, Parol: `admin123`)
