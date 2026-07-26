# F1 Fantasy League

A Flask web app for Formula 1 fantasy predictions, scoring, standings, and admin race evaluation.

## Features

- User registration and login
- Upcoming race dashboard
- Prediction create and update flow
- Points calculation and standings
- Admin dashboard with user editing
- Admin race management and evaluation
- Race, driver, constructor, and result data from the Jolpi Ergast API proxy

## Requirements

- Python 3.8 or newer
- pip
- SQLite for local development

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional environment variables:

```bash
SECRET_KEY=change-me
DATABASE_URL=sqlite:///f1_fantasy.db
JOLPI_ERGAST_API_BASE_URL=https://api.jolpi.ca/ergast/f1
```

## Database Setup

For a new local database, initialize tables and seed the default `admin` and `user` roles:

```bash
flask --app flask_app init-db
```

If you are using migrations instead, run:

```bash
flask --app flask_app db upgrade
flask --app flask_app init-db
```

## Running

Development:

```bash
flask --app flask_app run
```

You can also run the local entry point, which initializes the database before starting the server:

```bash
python app.py
```

Production example:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "flask_app:create_app()"
```

## API Integration

The app uses the Jolpi Ergast API proxy at `https://api.jolpi.ca/ergast/f1` by default. The integration fetches:

- Next race schedule
- Driver list
- Constructor standings
- Race results for evaluation

The API base URL can be overridden with `JOLPI_ERGAST_API_BASE_URL`.

## Testing

Run the smoke tests with:

```bash
.venv/bin/python -m pytest -q
```

The smoke suite covers registration, login, dashboard rendering, prediction create/update, admin access, race management, and idempotent race evaluation with mocked API responses.
