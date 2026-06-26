# BackEndIng

Backend service for the **Legal Catalog System** (LegalFileManager).
Built with Django 5 + Django REST Framework + SimpleJWT.

> **Important — full deployment**: this backend is only one half of the system.
> A working environment also requires the frontend project:
> [https://github.com/AymanElS4/FrontEndIngT3.git](https://github.com/AymanElS4/FrontEndIngT3.git).
> The backend exposes the REST API; the frontend consumes it. Both must be running
> (locally or in their respective hosts) for the system to be usable end-to-end.

## Requirements

- Python 3.11 or higher
- pip
- virtualenv (recommended)

## Installation

1. Open a terminal in the backend folder.

2. Create and activate a virtual environment (optional but recommended):

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux (bash, zsh):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the backend

Start the backend in development mode:

1. Move into the Django project:
   ```bash
   cd lfilemanager
   ```

2. Apply migrations (first run only):
   ```bash
   python manage.py migrate
   ```

3. (Optional) Populate the database with seed data:
   ```bash
   python seed_data.py
   ```

4. Start the development server:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```

The backend will be available at:

- http://127.0.0.1:8000/

## Useful commands

Run Django checks:
```bash
python manage.py check
```

Create migrations after editing models:
```bash
python manage.py makemigrations
```

Apply migrations:
```bash
python manage.py migrate
```

Run the test suite (the project uses **pytest**, configured in `lfilemanager/pytest.ini`):
```bash
pytest
```

Create a superuser to access the Django Admin panel at `/admin`:
```bash
python manage.py createsuperuser
```

## Environment variables

For local development the default settings work out of the box (SQLite, `DEBUG=True`).
For deployment to a production environment (Vercel + Render) the following variables
must be configured: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`,
`CORS_ALLOWED_ORIGINS`, `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`,
and `GAS_WEBHOOK_URL`.


## Project structure

```
BackEndIng/
├── requirements.txt
└── lfilemanager/
    ├── manage.py
    ├── pytest.ini
    ├── seed_data.py
    ├── lfilemanager/        # Django core (settings, urls, wsgi)
    └── client/              # Main Django app
        ├── views.py
        ├── urls.py
        ├── gas_storage.py   # Custom Storage backend → Google Drive via GAS
        ├── models/          # Domain entities (caso, documento, codigo_legal, ...)
        ├── serializers/
        └── tests/
```
