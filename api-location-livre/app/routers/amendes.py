from datetime import date
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from app.config.settings import get_settings
from app.db.deps import get_db
from app.services import pret_service
from app.utils.security import require_role, get_current_user

router = APIRouter(tags=["amendes"])

@router.get("/membre/amendes", dependencies=[Depends(require_role("membre","bibliothecaire","admin"))])
def get_membre_amendes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    settings = get_settings()
    today = date.today()
    amendes = []
    total = 0.0
    for p in pret_service.list_prets_by_user(db, user_id=user.id):
        due = p.date_retour  # champ utilisé comme 'date retour prévue'
        if due and today > due:
            days_late = (today - due).days
            amount = round(days_late * settings.FINE_PER_DAY, 2)
            amendes.append({"pretId": p.id, "joursRetard": days_late, "montant": amount, "statut": "due"})
            total += amount
    return {"total": round(total,2), "details": amendes}

@router.post("/membre/amendes/payer", dependencies=[Depends(require_role("membre","bibliothecaire","admin"))], status_code=status.HTTP_200_OK)
def payer_amende():
    # Démo : on considérerait le paiement comme externe; rien à persister ici
    return {"message": "Amende payée"}
