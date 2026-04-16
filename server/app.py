import os
from flask import Flask, request, session, make_response
from flask_restful import Api, Resource
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from models import db, User, Note

app = Flask(__name__)
# Using a fallback for development; in production this should be an env var
app.secret_key = os.environ.get('SECRET_KEY', 'default_dev_secret_key_12345')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

class Index(Resource):
    def get(self):
        return {"message": "Welcome to the Notes API Backend!"}, 200

class CheckSession(Resource):
    """
    Endpoint to check if the user is currently logged in based on their session.
    """
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            # Found a user_id in the session, let's grab the user object
            user = User.query.filter(User.id == user_id).first()
            if user:
                return user.to_dict(), 200
        
        # If no user or session, return a 401
        return {'error': 'Not authorized. Please log in.'}, 401

class Signup(Resource):
    """
    Handles new user registration.
    """
    def post(self):
        data = request.get_json()
        try:
            # Basic validation
            if not data.get('username') or not data.get('password'):
                return {'errors': ['Wait, we need both a username and a password.']}, 422
            
            if data.get('password') != data.get('password_confirmation'):
                return {'errors': ['Hmm, those passwords didn\'t match.']}, 422

            # Create the new user and set the password (setter handles hashing)
            new_user = User(username=data.get('username'))
            new_user.password_hash = data.get('password')
            
            db.session.add(new_user)
            db.session.commit()
            
            # Log them in automatically after signup
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
            
        except IntegrityError:
            # This happens if the username is already taken
            return {'errors': ['That username is already taken. Try another one?']}, 422
        except Exception as e:
            return {'errors': [str(e)]}, 422

class Login(Resource):
    """
    Authenticates an existing user.
    """
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Look up the user
        user = User.query.filter(User.username == username).first()
        
        # Check if user exists and password is correct
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
            
        return {'errors': ['That didn\'t work. Check your username or password.']}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error': '401 Unauthorized'}, 401

class Notes(Resource):
    """
    Handles listing a user's notes and creating new ones.
    """
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'You need to be logged in to see your notes.'}, 401
        
        # Default to page 1, 10 items per page
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Only fetch notes belonging to the current user
        pagination = Note.query.filter(Note.user_id == user_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'notes': [n.to_dict() for n in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        }, 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Wait, you\'re not logged in!'}, 401
        
        data = request.get_json()
        try:
            # Create a new note linked to the current user
            new_note = Note(
                title=data.get('title'),
                content=data.get('content'),
                user_id=user_id
            )
            db.session.add(new_note)
            db.session.commit()
            return new_note.to_dict(), 201
        except Exception as e:
            return {'errors': [str(e)]}, 422

class NoteByID(Resource):
    """
    Handles operations on a specific note (update and delete).
    """
    def patch(self, id):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized access.'}, 401
        
        # Ensure the note exists and belongs to the user
        target_note = Note.query.filter(Note.id == id, Note.user_id == user_id).first()
        if not target_note:
            return {'error': 'Note not found or you don\'t have access.'}, 404
        
        data = request.get_json()
        try:
            # Loop through the patch data and update fields
            for key, value in data.items():
                if hasattr(target_note, key):
                    setattr(target_note, key, value)
            
            db.session.commit()
            return target_note.to_dict(), 200
        except Exception as e:
            return {'errors': [str(e)]}, 422

    def delete(self, id):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized access.'}, 401
        
        # Again, check ownership
        target_note = Note.query.filter(Note.id == id, Note.user_id == user_id).first()
        if not target_note:
            return {'error': 'Note not found or already deleted.'}, 404
        
        db.session.delete(target_note)
        db.session.commit()
        return {}, 204

api.add_resource(Index, '/')
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Notes, '/notes')
api.add_resource(NoteByID, '/notes/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
