from typing import List
from fastapi import APIRouter, status, Depends
from pydantic import BaseModel, Field, ConfigDict

from app.utils.security import require_role


router = APIRouter(tags=["notifications"])

NOTIFS: List[dict] = []


class RappelRetour(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    pret_id: int = Field(..., alias="pretId")


class Retard(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    pret_id: int = Field(..., alias="pretId")
    jours_retard: int = Field(..., alias="joursRetard")


class ConfirmationEmprunt(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    pret_id: int = Field(..., alias="pretId")



@router.get(
    "/admin/notifications",
    dependencies=[Depends(require_role("admin"))],
    status_code=status.HTTP_200_OK,
)
def admin_list_notifications():
    """Voir toutes les notifications générées."""
    return NOTIFS


@router.post(
    "/admin/notifications/rappel-retour",
    dependencies=[Depends(require_role("admin"))],
    status_code=status.HTTP_201_CREATED,
)
def admin_create_rappel_retour(payload: RappelRetour):
    nid = len(NOTIFS) + 1
    notif = {
        "id": nid,
        "type": "rappel_retour",
        "pretId": payload.pret_id,
        "message": f"Rappel : retour du prêt {payload.pret_id}",
        "lu": False,
    }
    NOTIFS.append(notif)
    return notif


@router.post(
    "/admin/notifications/retard",
    dependencies=[Depends(require_role("admin"))],
    status_code=status.HTTP_201_CREATED,
)
def admin_create_notification_retard(payload: Retard):
    nid = len(NOTIFS) + 1
    notif = {
        "id": nid,
        "type": "retard",
        "pretId": payload.pret_id,
        "message": f"Retard : prêt {payload.pret_id} ({payload.jours_retard} jours)",
        "lu": False,
    }
    NOTIFS.append(notif)
    return notif


@router.post(
    "/admin/notifications/confirmation-emprunt",
    dependencies=[Depends(require_role("admin"))],
    status_code=status.HTTP_201_CREATED,
)
def admin_confirm_emprunt(payload: ConfirmationEmprunt):
    nid = len(NOTIFS) + 1
    notif = {
        "id": nid,
        "type": "confirmation_emprunt",
        "pretId": payload.pret_id,
        "message": f"Confirmation : prêt {payload.pret_id} enregistré",
        "lu": False,
    }
    NOTIFS.append(notif)
    return notif
