from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict

from app.db.deps import get_db
from app.models.user import User
from app.schemas.pret import PretOut
from app.services import pret_service
from app.utils.security import get_current_user


router = APIRouter(tags=["prets"])


@router.get(
    "/membre/prets",
    response_model=List[PretOut],
    status_code=status.HTTP_200_OK,
)
def membre_list_prets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pret_service.list_prets_by_user(db, user_id=current_user.id)


class PretCreatePayload(BaseModel):
    livre_id: int = Field(..., alias="livreId")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


@router.post(
    "/membre/prets",
    response_model=PretOut,
    status_code=status.HTTP_201_CREATED,
)
def membre_create_pret(
    payload: PretCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pret_service.create_pret(db, user_id=current_user.id, book_id=payload.livre_id)
