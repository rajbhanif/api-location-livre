from sqlalchemy.orm import Session
from app.models.book import Book

def list_books(db: Session):
    return db.query(Book).all()

def search_books(db: Session, q: str):
    ql = f"%{q.lower()}%"
    return db.query(Book).filter((Book.title.ilike(ql)) | (Book.author.ilike(ql))).all()

def get_book(db: Session, book_id: int):
    return db.query(Book).get(book_id)

def create_book(db: Session, **data):
    b = Book(**data)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

def update_book(db: Session, book_id: int, **data):
    b = db.query(Book).get(book_id)
    if not b:
        return None
    for k,v in data.items():
        setattr(b, k, v)
    db.commit()
    db.refresh(b)
    return b

def delete_book(db: Session, book_id: int):
    b = db.query(Book).get(book_id)
    if not b: return False
    db.delete(b)
    db.commit()
    return True
