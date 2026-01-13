from sqlalchemy.orm import Session
from app.models.reservation import Reservation

def create_reservation(db: Session, **data) -> Reservation:
    r = Reservation(**data)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def pop_next_reservation(db: Session, book_id: int):
    r = db.query(Reservation).filter(Reservation.book_id==book_id).order_by(Reservation.created_at.asc()).first()
    if r:
        db.delete(r)
        db.commit()
        return r
    return None

def list_reservations(db: Session, book_id: int):
    return db.query(Reservation).filter(Reservation.book_id==book_id).order_by(Reservation.created_at.asc()).all()
