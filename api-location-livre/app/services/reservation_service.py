from sqlalchemy.orm import Session

from app.repositories import reservation_repo
from app.repositories.book_repo import get_book
from app.core.exceptions import NotFoundError


def create_reservation(db: Session, user_id: int, book_id: int):
    """
    Crée une réservation pour un utilisateur et un livre :
    - Le livre doit exister.
    """
    book = get_book(db, book_id)
    if not book:
        raise NotFoundError("Livre introuvable", code="book_not_found")

    return reservation_repo.create_reservation(
        db,
        user_id=user_id,
        book_id=book_id,
    )


def next_in_queue(db: Session, book_id: int):
    """
    Récupère et retire la prochaine réservation dans la file pour ce livre.
    """
    return reservation_repo.pop_next_reservation(db, book_id)


def list_queue(db: Session, book_id: int):
    """
    Liste les réservations pour un livre donné.
    """
    return reservation_repo.list_reservations(db, book_id)
