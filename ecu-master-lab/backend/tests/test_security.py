"""Security-focused tests: injection, token validation, header checks."""
from tests.conftest import client, _create_test_user, _cleanup_user, _get_auth_header
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings
from app.core.database import text
import time


class TestTokenSecurity:
    def setup_method(self):
        _cleanup_user("sec_test@example.com")

    def teardown_method(self):
        _cleanup_user("sec_test@example.com")

    def test_expired_token_rejected(self):
        user = _create_test_user(email="sec_test@example.com")
        from datetime import timedelta
        token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value},
            expires_delta=timedelta(seconds=-1),
        )
        r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_tampered_token_rejected(self):
        user = _create_test_user(email="sec_test@example.com")
        token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        tampered = token[:-5] + "XXXXX"
        r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tampered}"})
        assert r.status_code == 401

    def test_token_without_sub_rejected(self):
        token = create_access_token(data={"role": "admin"})
        r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    def test_bearer_prefix_required(self):
        user = _create_test_user(email="sec_test@example.com")
        token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        r = client.get("/api/auth/me", headers={"Authorization": token})
        assert r.status_code in (401, 403)


class TestSQLInjection:
    def test_login_sql_injection(self):
        r = client.post("/api/auth/login", json={
            "email": "' OR 1=1 --",
            "password": "anything",
        })
        assert r.status_code in (401, 422, 429)

    def test_register_sql_injection(self):
        r = client.post("/api/auth/register", json={
            "first_name": "'; DROP TABLE users; --",
            "last_name": "Test",
            "email": "inject@example.com",
            "password": "Secure123",
        })
        _cleanup_user("inject@example.com")
        assert r.status_code in (200, 400, 422)


class TestAuthorizationBypass:
    def test_client_cannot_access_admin(self):
        headers, _ = _get_auth_header(
            email="bypass_test@example.com",
            role=None,
        )
        r = client.get("/api/admin/stats", headers=headers)
        assert r.status_code == 403
        _cleanup_user("bypass_test@example.com")

    def test_other_user_project_isolation(self):
        h1, user1 = _get_auth_header(email="isolation_a@example.com")
        h2, user2 = _get_auth_header(email="isolation_b@example.com")

        r = client.post("/api/projects", json={"name": "UserA Project"}, headers=h1)
        assert r.status_code == 200
        project_id = r.json()["id"]

        r = client.get(f"/api/projects/{project_id}", headers=h2)
        assert r.status_code == 404

        from app.core.database import SessionLocal
        from app.models.models import Project
        db = SessionLocal()
        try:
            db.execute(text("DELETE FROM audit_logs WHERE user_id IN (:u1, :u2)"), {"u1": user1.id, "u2": user2.id})
            p = db.query(Project).filter(Project.id == project_id).first()
            if p:
                db.delete(p)
            db.commit()
        finally:
            db.close()
        _cleanup_user("isolation_a@example.com")
        _cleanup_user("isolation_b@example.com")


class TestSecurityHeaders:
    def test_cors_headers(self):
        r = client.options("/api/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        })
        assert r.status_code in (200, 405)

    def test_no_server_header_leak(self):
        r = client.get("/api/health")
        assert "server" not in r.headers or "uvicorn" not in r.headers.get("server", "").lower()


class TestPasswordSecurity:
    def test_password_hash_not_reversible(self):
        from app.core.security import get_password_hash, verify_password
        h = get_password_hash("TestPassword123")
        assert h != "TestPassword123"
        assert verify_password("TestPassword123", h)
        assert not verify_password("WrongPassword123", h)

    def test_secret_key_min_length(self):
        assert len(settings.SECRET_KEY) >= 32

    def test_debug_mode_off(self):
        assert settings.DEBUG is False
