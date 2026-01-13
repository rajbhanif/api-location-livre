from datetime import date, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationRuleError
from app.repositories import pret_repo, book_repo
from app.models.pret import Pret

LOAN_DAYS_DEFAULT = 14
MAX_RENEWALS = 2


def list_prets_by_user(db: Session, user_id: int) -> List[Pret]:
    """Liste les prêts du membre."""
    return pret_repo.list_prets_by_user(db, user_id=user_id)


def create_pret(db: Session, user_id: int, book_id: int) -> Pret:
    """
    Créer un prêt pour un utilisateur :
    - Le livre doit exister
    - Il doit rester des copies disponibles
    - On décrémente les copies disponibles
    """
    book = book_repo.get_book(db, book_id)
    if not book:
        raise NotFoundError("Livre introuvable", code="book_not_found")

    if book.available_copies <= 0:
        raise ValidationRuleError(
            "Aucune copie disponible, réessayez plus tard",
            code="no_copies",
        )

    today = date.today()
    due_date = today + timedelta(days=LOAN_DAYS_DEFAULT)

    pret = pret_repo.create_pret(
        db,
        user_id=user_id,
        book_id=book_id,
        date_pret=today,
        date_retour=due_date,
        renouvellements=0,
    )

    # décrémenter les copies dispo
    book_repo.update_book(db, book.id, available_copies=book.available_copies - 1)

    return pret


def get_pret_or_404(db: Session, pret_id: int) -> Pret:
    pret = pret_repo.get_pret(db, pret_id)
    if not pret:
        raise NotFoundError("Prêt introuvable", code="pret_not_found")
    return pret


def return_pret(db: Session, pret_id: int) -> Pret:
    """
    Retourner un prêt :
    - on retrouve le prêt
    - on supprime le prêt
    - on incrémente les copies dispo du livre
    """
    pret = get_pret_or_404(db, pret_id)

    book = book_repo.get_book(db, pret.book_id)
    if not book:
        raise NotFoundError("Livre introuvable", code="book_not_found")

    deleted = pret_repo.delete_pret(db, pret_id)
    if not deleted:
        raise NotFoundError("Prêt introuvable", code="pret_not_found")

    book_repo.update_book(db, book.id, available_copies=book.available_copies + 1)

    return pret


def renew_pret(db: Session, pret_id: int) -> Pret:
    """
    Renouveler un prêt s'il n'a pas dépassé le maximum autorisé.
    """
    pret = get_pret_or_404(db, pret_id)

    if pret.renouvellements >= MAX_RENEWALS:
        raise ValidationRuleError(
            "Nombre maximal de renouvellements atteint",
            code="max_renewals_reached",
        )

    pret.date_retour = pret.date_retour + timedelta(days=LOAN_DAYS_DEFAULT)
    pret.renouvellements += 1

    return pret_repo.update_pret(db, pret)
