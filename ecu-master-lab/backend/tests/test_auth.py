import pytest
from tests.conftest import client, _cleanup_user, _create_test_user, _get_auth_header


REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
ME_URL = "/api/auth/me"


class TestRegister:
    def setup_method(self):
        _cleanup_user("reg_new@example.com")
        _cleanup_user("reg_existing@example.com")

    def teardown_method(self):
        _cleanup_user("reg_new@example.com")
        _cleanup_user("reg_existing@example.com")

    def test_register_success(self):
        r = client.post(REGISTER_URL, json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "reg_new@example.com",
            "password": "Secure123",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "reg_new@example.com"

    def test_register_duplicate_email(self):
        _create_test_user(email="reg_existing@example.com")
        r = client.post(REGISTER_URL, json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "reg_existing@example.com",
            "password": "Secure123",
        })
        assert r.status_code == 400

    def test_register_weak_password_no_uppercase(self):
        r = client.post(REGISTER_URL, json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "reg_new@example.com",
            "password": "weak1234",
        })
        assert r.status_code in (400, 422)

    def test_register_weak_password_no_number(self):
        r = client.post(REGISTER_URL, json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "reg_new@example.com",
            "password": "WeakPassNoNum",
        })
        assert r.status_code in (400, 422)

    def test_register_short_password(self):
        r = client.post(REGISTER_URL, json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "reg_new@example.com",
            "password": "Ab1",
        })
        assert r.status_code in (400, 422)

    def test_register_invalid_email(self):
        r = client.post(REGISTER_URL, json={
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "not-an-email",
            "password": "Secure123",
        })
        assert r.status_code in (400, 422)

    def test_register_short_name(self):
        r = client.post(REGISTER_URL, json={
            "first_name": "J",
            "last_name": "Dupont",
            "email": "reg_new@example.com",
            "password": "Secure123",
        })
        assert r.status_code in (400, 422)


class TestLogin:
    def setup_method(self):
        _create_test_user(email="login_test@example.com", password="Login123")

    def teardown_method(self):
        _cleanup_user("login_test@example.com")

    def test_login_success(self):
        r = client.post(LOGIN_URL, json={
            "email": "login_test@example.com",
            "password": "Login123",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data

    def test_login_wrong_password(self):
        r = client.post(LOGIN_URL, json={
            "email": "login_test@example.com",
            "password": "WrongPass123",
        })
        assert r.status_code == 401

    def test_login_nonexistent_user(self):
        r = client.post(LOGIN_URL, json={
            "email": "nobody@example.com",
            "password": "Test1234",
        })
        assert r.status_code == 401

    def test_login_rate_limiting(self):
        for _ in range(6):
            client.post(LOGIN_URL, json={
                "email": "login_test@example.com",
                "password": "WrongPass123",
            })
        r = client.post(LOGIN_URL, json={
            "email": "login_test@example.com",
            "password": "WrongPass123",
        })
        assert r.status_code == 429


class TestMe:
    def setup_method(self):
        _cleanup_user("me_test@example.com")

    def teardown_method(self):
        _cleanup_user("me_test@example.com")

    def test_me_authenticated(self):
        headers, _ = _get_auth_header(email="me_test@example.com")
        r = client.get(ME_URL, headers=headers)
        assert r.status_code == 200
        assert r.json()["email"] == "me_test@example.com"

    def test_me_no_token(self):
        r = client.get(ME_URL)
        assert r.status_code == 403

    def test_me_invalid_token(self):
        r = client.get(ME_URL, headers={"Authorization": "Bearer invalidtoken123"})
        assert r.status_code == 401
