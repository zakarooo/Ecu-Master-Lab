import pytest
from tests.conftest import client, _get_auth_header, _cleanup_user, _create_test_user
from app.models.models import UserRole


class TestAdminStats:
    def setup_method(self):
        self.headers, _ = _get_auth_header(
            email="admin_test@example.com",
            role=UserRole.ADMIN,
        )

    def teardown_method(self):
        _cleanup_user("admin_test@example.com")

    def test_stats_admin(self):
        r = client.get("/api/admin/stats", headers=self.headers)
        assert r.status_code == 200
        data = r.json()
        assert "total_users" in data
        assert "total_projects" in data
        assert isinstance(data["total_users"], int)

    def test_stats_non_admin_forbidden(self):
        headers, _ = _get_auth_header(
            email="client_test@example.com",
            role=UserRole.CLIENT,
        )
        r = client.get("/api/admin/stats", headers=headers)
        assert r.status_code == 403
        _cleanup_user("client_test@example.com")

    def test_stats_no_auth(self):
        r = client.get("/api/admin/stats")
        assert r.status_code == 403


class TestAdminUsers:
    def setup_method(self):
        self.headers, _ = _get_auth_header(
            email="admin_users@example.com",
            role=UserRole.ADMIN,
        )

    def teardown_method(self):
        _cleanup_user("admin_users@example.com")
        _cleanup_user("target_user@example.com")

    def test_list_users(self):
        r = client.get("/api/admin/users", headers=self.headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_update_user_role(self):
        user = _create_test_user(email="target_user@example.com")
        r = client.put(
            f"/api/admin/users/{user.id}",
            json={"role": "expert"},
            headers=self.headers,
        )
        assert r.status_code == 200

    def test_update_nonexistent_user(self):
        r = client.put(
            "/api/admin/users/999999",
            json={"role": "admin"},
            headers=self.headers,
        )
        assert r.status_code == 404


class TestAdminAuditLogs:
    def setup_method(self):
        self.headers, _ = _get_auth_header(
            email="admin_audit@example.com",
            role=UserRole.ADMIN,
        )

    def teardown_method(self):
        _cleanup_user("admin_audit@example.com")

    def test_list_audit_logs(self):
        r = client.get("/api/admin/audit-logs", headers=self.headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
