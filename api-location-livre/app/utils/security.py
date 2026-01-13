from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.db.deps import get_db
from app.models.user import User
from app.repositories import user_repo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/connexion")


# ========= PASSWORDS =========


def hash_password(password: str) -> str:
    """
    Hash le mot de passe en utilisant bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond au hash stocké.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ========= JWT HELPERS =========


def _create_token(data: Dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
    """
    Crée un JWT (access ou refresh) avec une date d'expiration.
    Ajoute aussi le champ "type" dans le payload pour distinguer les deux.
    """
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Crée un access token (durée en minutes, paramètre JWT_EXPIRES_MIN).
    """
    settings = get_settings()
    expires = timedelta(minutes=settings.JWT_EXPIRES_MIN)
    return _create_token(data, expires, token_type="access")


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Crée un refresh token (durée en jours, paramètre JWT_REFRESH_EXPIRES_DAYS).
    """
    settings = get_settings()
    expires = timedelta(days=settings.JWT_REFRESH_EXPIRES_DAYS)
    return _create_token(data, expires, token_type="refresh")


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Décode un access token. Retourne le payload ou None si invalide / mauvais type.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Décode un refresh token. Retourne le payload ou None si invalide / mauvais type.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


# ========= CURRENT USER & ROLES =========


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Récupère l'utilisateur courant à partir de l'access token Bearer.
    Lève 401 si token invalide / expiré / type incorrect.
    """
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise credentials_exception
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_repo.get_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user


def require_role(*roles: str):
    """
    Dépendance FastAPI pour exiger un ou plusieurs rôles.

    Usage :
        @router.get("/admin/truc", dependencies=[Depends(require_role("admin"))])
    """

    def dep(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return user

    return dep
