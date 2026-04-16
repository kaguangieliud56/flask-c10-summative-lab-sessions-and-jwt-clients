# Personal Notes API

This is the backend for a simple Notes application. I've built it using Flask and SQLAlchemy to help users keep track of their personal thoughts and tasks securely. It uses session-based authentication to make sure everyone's notes stay private.

## Key Features
- **User Accounts**: Sign up and log in securely.
- **Private Notes**: Your notes are yours only. Nobody else can see them.
- **Pagination**: The notes list is paginated so it doesn't slow down if you have tons of notes.
- **Secure Passwords**: I'm using Bcrypt for hashing, so passwords aren't stored in plain text.

## Setup & Running

1. **Get inside the server folder**:
   ```bash
   cd server
   ```
2. **Install what's needed**:
   ```bash
   pipenv install
   ```
3. **Setup the database**:
   ```bash
   pipenv run flask db init
   pipenv run flask db migrate -m "Initial setup"
   pipenv run flask db upgrade
   ```
4. **Seed it with some data**:
   ```bash
   pipenv run python seed.py
   ```
5. **Start the server**:
   ```bash
   pipenv run python app.py
   ```
   The API should be live at `http://localhost:5555`.

## API Routes

### Auth Stuff
- `POST /signup`: Register a new user.
- `POST /login`: Log in to your account.
- `DELETE /logout`: Log out.
- `GET /check_session`: See if you're still logged in.

### The Notes (Need to be logged in)
- `GET /notes`: List your notes. Supports `?page=1&per_page=5`.
- `POST /notes`: Create a new note.
- `PATCH /notes/<id>`: Edit a note by its ID.
- `DELETE /notes/<id>`: Get rid of a note.

## Challenges & Notes
- Implementing the custom password setter in the `User` model took a bit of trial and error to get the hashing right.
- Making sure the `Note` model correctly filtered by `user_id` in the API endpoints was key for security.
- Pagination was added to the `/notes` GET route to improve performance for users with many records.
