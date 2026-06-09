# Karatina Dental Clinic — Web Based Appointment System

**BSc IT Final Year Project — Karatina University, 2026**

A web-based online clinic appointment booking and scheduling system
developed using Python 3 and the Django framework.

---

## Quick Start (5 Steps)

### Step 1 — Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4 — Load sample data (doctors, patients, slots)
```bash
python manage.py populate_data
```

### Step 5 — Start the server
```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000**

---

## Login Credentials

| Role          | Username       | Password     |
|---------------|----------------|--------------|
| Admin         | admin          | admin1234    |
| Patient 1     | mary.wanjiku   | patient1234  |
| Patient 2     | john.mwangi    | patient1234  |
| Patient 3     | grace.njeri    | patient1234  |

---

## System URLs

| URL                         | Description              |
|-----------------------------|--------------------------|
| /                           | Home / Landing page      |
| /book/                      | Book appointment         |
| /mine/                      | My appointments          |
| /contact/                   | Contact page             |
| /dashboard/                 | Admin dashboard          |
| /accounts/login/            | Patient login            |
| /accounts/register/         | Patient registration     |
| /admin/                     | Django admin panel       |

---

## Technology Stack

- **Backend:** Python 3, Django 4.x
- **Database:** SQLite (development)
- **Frontend:** HTML5, CSS3, Bootstrap 5
- **Icons:** Font Awesome 6.4
- **Version Control:** Git

---

## Project Structure

```
karatina_dental/
├── manage.py
├── requirements.txt
├── README.md
├── clinic_system/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # Auth app
│   ├── views.py
│   └── urls.py
├── appointments/           # Core app
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── urls.py
│   └── management/commands/populate_data.py
├── templates/              # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── contact.html
│   ├── accounts/
│   └── appointments/
└── static/css/style.css    # Single stylesheet
```

---
