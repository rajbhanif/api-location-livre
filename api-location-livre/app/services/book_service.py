from sqlalchemy.orm import Session

from app.repositories.book_repo import (
    list_books,
    search_books,
    get_book,
    create_book,
    update_book,
    delete_book,
)
from app.repositories import pret_repo  


def list_all(db: Session):
    return list_books(db)


def search(db: Session, q: str):
    return search_books(db, q)


def get_one(db: Session, book_id: int):
    return get_book(db, book_id)


def admin_create(db: Session, **data):
    return create_book(db, **data)


def admin_update(db: Session, book_id: int, **data):
    return update_book(db, book_id, **data)


def admin_delete(db: Session, book_id: int):
    """
    Returns a tuple: (success: bool, error: str or None)

    error can be:
      - "book_not_found"
      - "book_has_loans"
    """

    book = get_book(db, book_id)
    if not book:
        return False, "book_not_found"

    active_loans_count = pret_repo.count_active_prets_for_book(db, book_id)
    if active_loans_count > 0:
        return False, "book_has_loans"

    delete_book(db, book_id)
    return True, None
