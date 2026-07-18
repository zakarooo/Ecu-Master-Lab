import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.models import User
from app.core.security import get_password_hash, create_access_token

client = TestClient(app)


def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db


def _cleanup_user(email: str):
    db = SessionLocal()
    try:
        from sqlalchemy import text
        u = db.query(User).filter(User.email == email).first()
        if u:
            db.execute(text("DELETE FROM audit_logs WHERE user_id = :uid"), {"uid": u.id})
            db.execute(text("DELETE FROM file_versions WHERE project_id IN (SELECT id FROM projects WHERE user_id = :uid)"), {"uid": u.id})
            db.execute(text("DELETE FROM jobs WHERE project_id IN (SELECT id FROM projects WHERE user_id = :uid)"), {"uid": u.id})
            db.execute(text("DELETE FROM ecus WHERE project_id IN (SELECT id FROM projects WHERE user_id = :uid)"), {"uid": u.id})
            db.execute(text("DELETE FROM vehicles WHERE project_id IN (SELECT id FROM projects WHERE user_id = :uid)"), {"uid": u.id})
            db.execute(text("DELETE FROM projects WHERE user_id = :uid"), {"uid": u.id})
            db.delete(u)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def _create_test_user(email="testuser@example.com", password="Test1234", role=None):
    _cleanup_user(email)
    db = SessionLocal()
    try:
        from app.models.models import UserRole
        user = User(
            first_name="Test",
            last_name="User",
            email=email,
            phone="+33612345678",
            hashed_password=get_password_hash(password),
            role=role or UserRole.CLIENT,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def _get_auth_header(email="testuser@example.com", password="Test1234", role=None):
    user = _create_test_user(email=email, password=password, role=role)
    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}, user
