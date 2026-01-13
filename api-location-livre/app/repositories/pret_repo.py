from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.pret import Pret


def create_pret(db: Session, **data) -> Pret:
    """
    Crée un prêt à partir des champs passés en kwargs.
    Champs attendus : user_id, book_id, date_pret, date_retour, renouvellements.
    """
    pret = Pret(**data)
    db.add(pret)
    db.commit()
    db.refresh(pret)
    return pret


def get_pret(db: Session, pret_id: int) -> Optional[Pret]:
    """
    Récupère un prêt par son id ou None s'il n'existe pas.
    """
    return db.get(Pret, pret_id)


def list_prets_by_user(db: Session, user_id: int) -> List[Pret]:
    """
    Retourne la liste des prêts d'un utilisateur (liste éventuellement vide).
    """
    return (
        db.query(Pret)
        .filter(Pret.user_id == user_id)
        .all()
    )


def update_pret(db: Session, pret: Pret) -> Pret:
    """
    Persiste les modifications faites sur un objet Pret déjà chargé.
    """
    db.add(pret)
    db.commit()
    db.refresh(pret)
    return pret


def delete_pret(db: Session, pret_id: int) -> bool:
    """
    Supprime un prêt. Retourne True si supprimé, False s'il n'existait pas.
    """
    pret = db.get(Pret, pret_id)
    if not pret:
        return False
    db.delete(pret)
    db.commit()
    return True


def list_overdue_prets_for_user(db: Session, user_id: int, today: date) -> List[Pret]:
    """
    Liste les prêts en retard pour un utilisateur donné à la date fournie.
    """
    return (
        db.query(Pret)
        .filter(
            Pret.user_id == user_id,
            Pret.date_retour < today,
        )
        .all()
    )


def count_active_prets_for_book(db: Session, book_id: int) -> int:
    """
    Retourne le nombre de prêts associés à un livre.
    À adapter si tu as une notion de prêt 'actif' (non retourné).
    """
    return db.query(Pret).filter(Pret.book_id == book_id).count()
