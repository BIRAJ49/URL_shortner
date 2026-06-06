# Django URL Shortener

A simple URL shortener built with Django. Users can create an account, shorten long URLs, manage their own links, and see how many times each short link has been used.

## Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Apply the database migrations:

```bash
python manage.py migrate
```

Start the Django server:

```bash
python manage.py runserver
```

## What the app does

- Users can register, log in, and log out.
- Logged-in users can create short URLs.
- Each user can only view, edit, and delete their own URLs.
- Short URLs redirect to the original long URL.
- The app tracks the number of clicks for each short URL.
- Created date and expiration date are shown for each URL.

## Extra features

- Custom short keys can be added while creating or editing a URL.
- Automatic short keys are generated using SHA-256.
- URLs can have an optional expiration time.
- QR codes are available for short URLs.

## Tests

Run the tests with:

```bash
python manage.py test
```
