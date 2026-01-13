from typing import List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.reservation import ReservationOut
from app.services import reservation_service
from app.utils.security import require_role, get_current_user

router = APIRouter(tags=["reservations"])

class ReservationCreate(BaseModel):
    livre_id: int = Field(..., alias="livreId")

@router.post("/reservations", dependencies=[Depends(require_role("membre","bibliothecaire","admin"))], response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return reservation_service.create_reservation(db, user_id=user.id, book_id=payload.livre_id)

@router.get("/bibliothecaire/reservations/file-attente/{livre_id}", dependencies=[Depends(require_role("bibliothecaire","admin"))], response_model=List[ReservationOut], status_code=status.HTTP_200_OK)
def biblio_file_attente(livre_id: int, db: Session = Depends(get_db)):
    return reservation_service.list_queue(db, livre_id)

@router.post("/bibliothecaire/reservations/next/{livre_id}", dependencies=[Depends(require_role("bibliothecaire","admin"))], response_model=ReservationOut | None, status_code=status.HTTP_200_OK)
def biblio_reservation_disponible(livre_id: int, db: Session = Depends(get_db)):
    return reservation_service.next_in_queue(db, livre_id)
