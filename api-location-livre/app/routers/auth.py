from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
)
from app.repositories import user_repo
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


# ===================== SCHEMAS =====================


class InscriptionRequest(BaseModel):
    nom: str = Field(..., min_length=1)
    email: EmailStr
    motDePasse: str = Field(..., min_length=6)


class UserOut(BaseModel):
    id: int
    nom: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ===================== ENDPOINTS =====================


@router.post(
    "/inscription",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def inscription(
    data: InscriptionRequest,
    db: Session = Depends(get_db),
):
    """
    Inscription d'un nouvel utilisateur "membre".
    """
    existing = user_repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur existe déjà avec cet email",
        )

    user = user_repo.create(
        db,
        nom=data.nom,
        email=data.email,
        password_hash=hash_password(data.motDePasse),
        role="membre",
    )

    return user


@router.post(
    "/connexion",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Connexion avec email + mot de passe.
    Retourne un access_token + refresh_token.
    """
    user = user_repo.get_by_email(db, form.username)
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifiants invalides",
        )

    payload = {"sub": user.email, "role": user.role}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    data: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Rafraîchit le token d'accès à partir d'un refresh token valide.
    """
    decoded = decode_refresh_token(data.refresh_token)
    if decoded is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré",
        )

    email = decoded.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide",
        )

    user = user_repo.get_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur inconnu",
        )

    payload = {"sub": user.email, "role": user.role}
    new_access = create_access_token(payload)
    new_refresh = create_refresh_token(payload)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
    )


@router.get("/whoami", status_code=status.HTTP_200_OK)
def whoami(user: Any = Depends(get_current_user)):
    """
    Retourne les infos du user courant (basé sur l'access token).

    - Sans token / token invalide -> get_current_user lève 401
    - Avec token valide -> 200 + infos de base
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non authentifié",
        )

    return {
        "id": getattr(user, "id", None),
        "nom": getattr(user, "nom", None),
        "email": getattr(user, "email", None),
        "role": getattr(user, "role", None),
    }
