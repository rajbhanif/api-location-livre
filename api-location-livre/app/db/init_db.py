from app.db.session import Base, engine, SessionLocal
from app.models.book import Book
from app.models.user import User
from app.utils.security import hash_password

def init_db():
    Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    if not db.query(Book).first():
        db.add_all([
            Book(title="L’Alchimiste", author="Paulo Coelho", year=1988, total_copies=3, available_copies=3),
            Book(title="1984", author="George Orwell", year=1949, total_copies=2, available_copies=2),
        ])
    if not db.query(User).first():
        db.add_all([
            User(email="admin@example.com", full_name="Admin", password_hash=hash_password("admin"), role="admin"),
            User(email="biblio@example.com", full_name="Biblio", password_hash=hash_password("biblio"), role="bibliothecaire"),
            User(email="membre@example.com", full_name="Membre", password_hash=hash_password("membre"), role="membre"),
        ])
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    seed()
    print("DB initialized & seeded")
