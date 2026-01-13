from typing import Optional

from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.book import BookOut
from app.services import book_service
from app.utils.security import require_role

router = APIRouter(tags=["livres"])


class LivreCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    titre: str = Field(..., alias="titre")
    auteur: str = Field(..., alias="auteur")
    annee: int = Field(..., alias="annee")
    nombre_copies: int = Field(..., alias="nombreCopies")
    copies_disponibles: Optional[int] = Field(None, alias="copiesDisponibles")

    @field_validator("nombre_copies")
    @classmethod
    def total_pos(cls, v: int) -> int:
        if v < 1:
            raise ValueError("nombreCopies doit être >= 1")
        return v


class LivreUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    titre: Optional[str] = Field(None, alias="titre")
    auteur: Optional[str] = Field(None, alias="auteur")
    annee: Optional[int] = Field(None, alias="annee")
    nombre_copies: Optional[int] = Field(None, alias="nombreCopies")
    copies_disponibles: Optional[int] = Field(None, alias="copiesDisponibles")


# ========= LECTURE =========


@router.get(
    "/livres",
    response_model=list[BookOut],
    status_code=status.HTTP_200_OK,
)
def list_livres(db: Session = Depends(get_db)):
    """Lister tous les livres."""
    return book_service.list_all(db)


@router.get(
    "/livres/{livre_id}",
    response_model=BookOut,
    status_code=status.HTTP_200_OK,
)
def get_livre(livre_id: int, db: Session = Depends(get_db)):
    """Récupérer un livre par son ID."""
    b = book_service.get_one(db, livre_id)
    if not b:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return b


# ========= ADMIN – CRÉATION / MISE À JOUR / SUPPRESSION =========


@router.post(
    "/admin/livres",
    dependencies=[Depends(require_role("admin"))],
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_book(payload: LivreCreate, db: Session = Depends(get_db)):
    data_in = payload.model_dump(by_alias=True)

    data = {
        "title": data_in["titre"],
        "author": data_in["auteur"],
        "year": data_in["annee"],
        "total_copies": data_in["nombreCopies"],
        "available_copies": data_in.get("copiesDisponibles"),
    }

    if data["available_copies"] is None:
        data["available_copies"] = data["total_copies"]

    if data["available_copies"] > data["total_copies"]:
        raise HTTPException(
            status_code=400,
            detail="copiesDisponibles ne peut pas être supérieure à nombreCopies",
        )

    return book_service.admin_create(db, **data)


@router.put(
    "/admin/livres/{livre_id}",
    dependencies=[Depends(require_role("admin"))],
    response_model=BookOut,
    status_code=status.HTTP_200_OK,
)
def admin_update_book(
    livre_id: int,
    payload: LivreUpdate,
    db: Session = Depends(get_db),
):
    din = {k: v for k, v in payload.model_dump(by_alias=True).items() if v is not None}

    data: dict = {}
    if "titre" in din:
        data["title"] = din["titre"]
    if "auteur" in din:
        data["author"] = din["auteur"]
    if "annee" in din:
        data["year"] = din["annee"]
    if "nombreCopies" in din:
        data["total_copies"] = din["nombreCopies"]
    if "copiesDisponibles" in din:
        data["available_copies"] = din["copiesDisponibles"]

    if (
        "available_copies" in data
        and "total_copies" in data
        and data["available_copies"] > data["total_copies"]
    ):
        raise HTTPException(
            status_code=400,
            detail="copiesDisponibles ne peut pas être supérieure à nombreCopies",
        )

    b = book_service.admin_update(db, livre_id, **data)
    if not b:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return b


@router.delete(
    "/admin/livres/{livre_id}",
    dependencies=[Depends(require_role("admin"))],
    status_code=status.HTTP_200_OK,
)
def admin_delete_book(livre_id: int, db: Session = Depends(get_db)):
    ok, error = book_service.admin_delete(db, livre_id)

    if not ok:
        if error == "book_not_found":
            raise HTTPException(status_code=404, detail="Livre introuvable")
        if error == "book_has_loans":
            raise HTTPException(
                status_code=400,
                detail="Impossible de supprimer le livre : il a encore des prêts actifs.",
            )
        raise HTTPException(
            status_code=400,
            detail="Suppression du livre impossible.",
        )

    return {"deleted": livre_id}
