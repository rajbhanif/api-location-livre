from pydantic import Field
from app.schemas.base import APIModel

class ReservationOut(APIModel):
    id: int
    user_id: int = Field(..., alias="utilisateurId")
    book_id: int = Field(..., alias="livreId")
