from faker import Faker
from random import randint
from server.config import create_app, db
from server.models import User, Note

fake = Faker()
app = create_app()

def run():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # users
        users = []
        for i in range(3):
            u = User(
                username=f"user{i+1}",
                image_url=f"https://picsum.photos/seed/{i+1}/200/200",
                bio=fake.sentence(),
            )
            u.password_hash = "password123"
            users.append(u)
            db.session.add(u)
        db.session.commit()

        # notes (2–4 each)
        for u in users:
            for _ in range(randint(2, 4)):
                n = Note(
                    title=fake.sentence(nb_words=4),
                    content=fake.paragraph(nb_sentences=3),
                    user_id=u.id,
                )
                db.session.add(n)
        db.session.commit()
        print("Seed complete ✅")

if __name__ == "__main__":
    run()
