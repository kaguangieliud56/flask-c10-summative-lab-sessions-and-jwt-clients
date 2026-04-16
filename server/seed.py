from faker import Faker
from app import app
from models import db, User, Note
import random

fake = Faker()

def seed_database():
    with app.app_context():
        print("--- Seeding Database ---")
        print("Clearing out old records...")
        Note.query.delete()
        User.query.delete()

        print("Generating some users...")
        users = []
        # Create a default test user for easy logging in
        test_user = User(username='test_user')
        test_user.password_hash = 'password123'
        users.append(test_user)
        db.session.add(test_user)

        # Add a few more random ones
        for i in range(4):
            new_user = User(username=fake.user_name())
            new_user.password_hash = 'secure_pass_99'
            users.append(new_user)
            db.session.add(new_user)
        
        print(f"Added {len(users)} users.")
        db.session.commit()

        print("Writing some random notes...")
        # A mix of realistic and fake notes
        note_titles = [
            "Project Ideas", "Grocery List", "Remember to call Mom",
            "Gym Routine", "Book Recommendations", "Vacation Planning",
            "Meeting Notes", "Birthday Gift Ideas", "Bug Fixes to-do"
        ]

        for user in users:
            # Each user gets a handful of notes
            for _ in range(random.randint(3, 8)):
                is_custom = random.random() > 0.5
                title = random.choice(note_titles) if is_custom else fake.sentence(nb_words=3)
                
                note = Note(
                    title=title,
                    content=fake.paragraph(nb_sentences=random.randint(2, 4)),
                    user=user
                )
                db.session.add(note)
        
        db.session.commit()
        print("Seed complete! Ready to rock.")

if __name__ == '__main__':
    seed_database()
