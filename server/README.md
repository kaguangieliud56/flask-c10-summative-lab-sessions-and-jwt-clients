# Notes API Backend

This is a secure Flask API backend built for a productivity tool that allows users to track personal notes. It features session-based authentication and restricted access to ensure data privacy between users.

## Features
- Full Authentication (Signup, Login, Logout, Check Session)
- User-owned resource: **Notes**
- CRUD operations for Notes
- Pagination on Note index
- Secure password hashing with Bcrypt
- Session-based authorization

## Installation

1. Navigate to the `server` directory:
   ```bash
   cd server
   ```
2. Install dependencies using Pipenv:
   ```bash
   pipenv install
   ```
3. Initialize the database and run migrations:
   ```bash
   export FLASK_APP=app.py
   pipenv run flask db init
   pipenv run flask db migrate -m "Initial migration"
   pipenv run flask db upgrade
   ```
4. Seed the database with sample data:
   ```bash
   pipenv run python seed.py
   ```

## Running the Application

To start the Flask server:
```bash
pipenv run python app.py
```
The server will run on `http://localhost:5555`.

## API Endpoints

### Authentication
- `POST /signup`: Create a new user account.
- `POST /login`: Log in to an existing account.
- `DELETE /logout`: Log out of the current account.
- `GET /check_session`: Verify current login status and get user details.

### Notes (Protected)
- `GET /notes`: List all notes for the authenticated user (supports `page` and `per_page` query params).
- `POST /notes`: Create a new note.
- `PATCH /notes/<id>`: Update an existing note by ID.
- `DELETE /notes/<id>`: Delete a note by ID.

## Project Structure
- `app.py`: Main application entry point and routes.
- `models.py`: Database models (User, Note).
- `seed.py`: Database seeding script.
- `migrations/`: Database migrations managed by Flask-Migrate.
