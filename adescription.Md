# Project Overview

## Summary
This repository implements a full-stack complaint tracking and user management application with a Python/Flask backend, a React + TypeScript frontend for the user login page, and HTML admin pages. It includes database schemas, migration scripts, utility tools, and Docker compose support for local development.

## Tech Stack
- Backend: Python, Flask, Flask-CORS
- Database: PostgreSQL (SQL files provided: `database.sql`, `database_pgadmin_safe.sql`, migration tracking)
- DB client: `psycopg2-binary` (used by connection scripts)
- HTTP client: `requests` (utility scripts)
- Frontend: React (Create React App) + TypeScript (`user-login-page`)
- Static frontend/admin: plain HTML/CSS/JS pages (`*.html` files in repo root)
- Containerization / orchestration: `docker-compose.yml`
- Scripting & utilities: Python scripts for tracking IDs, migrations, and officer management

## Languages
- Python (backend, scripts)
- SQL (database schema and migration files)
- JavaScript / TypeScript (React frontend)
- HTML / CSS (static admin and form pages)

## Key Dependencies (from `requirements.txt`)
- `flask`
- `flask-cors`
- `psycopg2-binary`
- `requests`

## Frontend Dependencies (from `user-login-page/package.json`)
- `react`, `react-dom`, `react-scripts`, `typescript`
- Type definitions: `@types/react`, `@types/react-dom`

## Connections and Integrations
- PostgreSQL database: SQL files and migration scripts suggest a Postgres DB used by the app.
- DB connection helper(s): `conn.py` and `connet.py` (note: there are two similarly-named files — one may be a typo/duplicate; inspect both before use).
- Admin interface: multiple static HTML admin pages (e.g., `admin_health.html`, `admin_police.html`, `admin_education.html`, `admin_transport.html`, `admin_electrical.html`).
- Docker Compose: `docker-compose.yml` for composing services locally.
- Scripts: `run_flask.bat`, `run_migration.py`, `serve_admin.py`, and various utilities under `tools/` (`list_officers.py`, `update_officers.py`).

## Main Functionalities
- User registration & login flows (static forms + React login page in `user-login-page`).
- Complaint tracking: `track_complaint.html` and utilities to generate/list tracking IDs (`generate_tracking_ids.py`, `list_tracking_ids.py`).
- Admin dashboards: several admin HTML pages for different departments.
- Database setup and migration helpers: SQL files and `run_migration.py` for managing schema changes and tracking migrations.
- Officer management utilities in `tools/` to list and update officer records.
- End-to-end tests: `test_end_to_end.py` and other testing-related docs (`QUICK_START_TESTING.md`).

## Notable Files and Purpose
- `conn.py` / `connet.py` — database connection helpers
- `db_manager.py` — DB management utilities
- `serve_admin.py` — serve or manage admin interfaces
- `generate_tracking_ids.py`, `list_tracking_ids.py` — tracking utilities
- `run_migration.py` — apply/track DB migrations
- `docker-compose.yml` — local multi-service configuration
- `user-login-page/` — React + TypeScript user login frontend

## Recommendations / Notes
- Review `connet.py` vs `conn.py` to confirm which is the intended DB connector and remove duplicates.
- Inspect `docker-compose.yml` and SQL files to configure Postgres credentials before running locally.
- Run the React frontend from `user-login-page` with `npm install` and `npm start` (or `run_react.bat` on Windows).

## Quick Start (local)
1. Create and configure a PostgreSQL instance (or use `docker-compose up`).
2. Install Python deps: `pip install -r requirements.txt`.
3. Run migrations: `python run_migration.py` (review script options).
4. Start backend: `run_flask.bat` or `python app.py` / `flask run` as appropriate.
5. Start frontend: open `user-login-page` and run `npm install` then `npm start` (or use `run_react.bat`).

---
Generated summary of repository structure, tech stack, and core functionality.
