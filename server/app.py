import os
from flask import Flask, request, session, make_response
from flask_restful import Api, Resource
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from models import db, User, Note

app = Flask(__name__)
app.secret_key = b'\x9d\x97\x8e\xe4\x9a\xfb\xba\x81\xfb\x1d\x01\x13\x82\x8e\x9c\x0b'
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
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if user:
                return user.to_dict(), 200
        return {'error': '401 Unauthorized'}, 401

class Signup(Resource):
    def post(self):
        json = request.get_json()
        try:
            if not json.get('username') or not json.get('password'):
                return {'errors': ['Username and password are required']}, 422
            
            if json.get('password') != json.get('password_confirmation'):
                return {'errors': ['Passwords do not match']}, 422

            user = User(username=json.get('username'))
            user.password_hash = json.get('password')
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            return {'errors': ['Username already exists']}, 422
        except Exception as e:
            return {'errors': [str(e)]}, 422

class Login(Resource):
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        
        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'errors': ['Invalid username or password']}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error': '401 Unauthorized'}, 401

class Notes(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': '401 Unauthorized'}, 401
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        notes_pagination = Note.query.filter(Note.user_id == user_id).paginate(page=page, per_page=per_page, error_out=False)
        notes = [note.to_dict() for note in notes_pagination.items]
        
        return {
            'notes': notes,
            'total': notes_pagination.total,
            'pages': notes_pagination.pages,
            'current_page': notes_pagination.page
        }, 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': '401 Unauthorized'}, 401
        
        json = request.get_json()
        try:
            note = Note(
                title=json.get('title'),
                content=json.get('content'),
                user_id=user_id
            )
            db.session.add(note)
            db.session.commit()
            return note.to_dict(), 201
        except Exception as e:
            return {'errors': [str(e)]}, 422

class NoteByID(Resource):
    def patch(self, id):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': '401 Unauthorized'}, 401
        
        note = Note.query.filter(Note.id == id, Note.user_id == user_id).first()
        if not note:
            return {'error': 'Note not found'}, 404
        
        json = request.get_json()
        try:
            for attr in json:
                setattr(note, attr, json.get(attr))
            db.session.commit()
            return note.to_dict(), 200
        except Exception as e:
            return {'errors': [str(e)]}, 422

    def delete(self, id):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': '401 Unauthorized'}, 401
        
        note = Note.query.filter(Note.id == id, Note.user_id == user_id).first()
        if not note:
            return {'error': 'Note not found'}, 404
        
        db.session.delete(note)
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
