from pydantic import field_validator
from app.schemas.base import APIModel
from datetime import datetime

class BookBase(APIModel):
    title: str
    author: str
    year: int
    total_copies: int
    available_copies: int

    @field_validator('year')
    @classmethod
    def check_year(cls, v):
        if v < 1400 or v > datetime.utcnow().year:
            raise ValueError("year doit être plausible (1400..année courante)")
        return v

    @field_validator('available_copies')
    @classmethod
    def copies_non_negative(cls, v):
        if v < 0:
            raise ValueError("available_copies ne peut pas être négatif")
        return v

class BookOut(BookBase):
    id: int
    class Config:
        from_attributes = True
