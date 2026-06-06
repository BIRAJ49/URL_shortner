# Django URL Shortener

A small Django web application for creating and managing short URLs.

## Features

- User registration, login, and logout
- Authenticated URL creation and management
- Automatic base62 short key generation
- Optional custom short keys
- Short URL redirects
- Per-link click counts
- Creation and expiration timestamps
- Edit and delete actions for owned URLs
- QR code generation for each short URL
- Responsive Django-template UI

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Tests

```bash
python manage.py test
```

## Notes

- The app uses SQLite by default for local development.
- QR code generation uses the `qrcode` package with Pillow support.
- Expired links return HTTP `410 Gone` and do not increment click counts.
