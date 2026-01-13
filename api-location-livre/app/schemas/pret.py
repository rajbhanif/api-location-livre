from datetime import date
from pydantic import BaseModel, ConfigDict


class PretOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    date_pret: date
    date_retour: date
    renouvellements: int
    model_config = ConfigDict(from_attributes=True)
