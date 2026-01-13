from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.book import BookOut
from app.services import book_service

router = APIRouter(tags=["catalogue"])

@router.get("/catalogue", response_model=List[BookOut])
def catalogue_simple(db: Session = Depends(get_db)):
    return book_service.list_all(db)

@router.get("/membre/catalogue", response_model=List[BookOut])
def catalogue_membre(db: Session = Depends(get_db)):
    return book_service.list_all(db)

@router.get("/catalogue/recherche", response_model=List[BookOut])
def recherche_catalogue(q: Optional[str] = Query(None, min_length=1), db: Session = Depends(get_db)):
    return book_service.search(db, q) if q else book_service.list_all(db)
