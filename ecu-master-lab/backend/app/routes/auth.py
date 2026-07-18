from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.models import User, UserRole, AuditLog
from app.models.schemas import UserCreate, UserLogin, UserResponse, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

from datetime import datetime, timedelta
from sqlalchemy import func

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

    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.CLIENT,
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
