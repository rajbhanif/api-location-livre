from fastapi import APIRouter, Depends
from app.utils.security import require_role
router = APIRouter(tags=["audit"])

@router.get("/admin/audit", dependencies=[Depends(require_role("admin"))])
def consulter_audit():
    return [{"id": 1, "action": "CONNEXION"}]
