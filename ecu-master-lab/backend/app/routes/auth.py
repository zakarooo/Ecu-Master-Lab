from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, validate_password_strength
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.models import User, UserRole, AuditLog
from app.models.schemas import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

from datetime import datetime, timedelta
from sqlalchemy import func
import secrets

_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 300


def _check_rate_limit(ip: str, db: Session) -> None:
    cutoff = datetime.utcnow() - timedelta(seconds=_LOCKOUT_SECONDS)
    recent = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "LOGIN_FAILED",
        AuditLog.resource_type == ip,
        AuditLog.created_at >= cutoff,
    ).scalar() or 0
    if recent >= _MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Trop de tentatives. Réessayez dans {} minutes.".format(_LOCKOUT_SECONDS // 60),
        )


def _record_attempt(ip: str, db: Session) -> None:
    log = AuditLog(
        user_id=None,
        action="LOGIN_FAILED",
        resource_type=ip,
        resource_id=0,
    )
    db.add(log)
    db.commit()


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    from app.core.security import validate_password_strength
    try:
        validate_password_strength(user_data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Un compte avec cet email existe déjà")

    verification_token = secrets.token_urlsafe(32)

    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.CLIENT,
        is_email_verified=False,
        email_verification_token=verification_token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log = AuditLog(user_id=user.id, action="REGISTER", resource_type="user", resource_id=user.id)
    db.add(log)
    db.commit()

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip, db)

    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        _record_attempt(client_ip, db)
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    log = AuditLog(user_id=user.id, action="LOGIN", resource_type="user", resource_id=user.id)
    db.add(log)
    db.commit()

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


class VerifyEmailRequest(BaseModel):
    token: str


@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email_verification_token == data.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token de vérification invalide")
    user.is_email_verified = True
    user.email_verification_token = None
    db.commit()
    return {"message": "Email vérifié avec succès"}


class ForgotPasswordRequest(BaseModel):
    email: str


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}
    reset_token = secrets.token_urlsafe(32)
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé", "token": reset_token}


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == data.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token invalide")
    if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expiré")
    try:
        validate_password_strength(data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user.hashed_password = get_password_hash(data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()
    return {"message": "Mot de passe réinitialisé avec succès"}


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


@router.put("/profile", response_model=UserResponse)
def update_profile(data: UpdateProfileRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.email and data.email != current_user.email:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        current_user.email = data.email
        current_user.is_email_verified = False
        current_user.email_verification_token = secrets.token_urlsafe(32)
    if data.first_name is not None:
        current_user.first_name = data.first_name
    if data.last_name is not None:
        current_user.last_name = data.last_name
    if data.phone is not None:
        current_user.phone = data.phone

    log = AuditLog(user_id=current_user.id, action="UPDATE_PROFILE", resource_type="user", resource_id=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.put("/password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    try:
        validate_password_strength(data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    current_user.hashed_password = get_password_hash(data.new_password)

    log = AuditLog(user_id=current_user.id, action="CHANGE_PASSWORD", resource_type="user", resource_id=current_user.id)
    db.add(log)
    db.commit()
    return {"message": "Mot de passe modifié avec succès"}
