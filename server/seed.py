from faker import Faker
from app import app
from models import db, User, Note
import random

fake = Faker()

def seed_database():
    with app.app_context():
        print("Clearing database...")
        Note.query.delete()
        User.query.delete()

        print("Creating users...")
        users = []
        # Create a test user
        test_user = User(username='test')
        test_user.password_hash = 'password'
        users.append(test_user)
        db.session.add(test_user)

        for _ in range(5):
            user = User(username=fake.user_name())
            user.password_hash = 'password123'
            users.append(user)
            db.session.add(user)
        
        db.session.commit()

        print("Creating notes...")
        for user in users:
            for _ in range(random.randint(5, 12)):
                note = Note(
                    title=fake.sentence(nb_words=4),
                    content=fake.paragraph(nb_sentences=3),
                    user=user
                )
                db.session.add(note)
        
        db.session.commit()
        print("Done seeding!")

if __name__ == '__main__':
    seed_database()
