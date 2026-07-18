from tests.conftest import client, _get_auth_header, _cleanup_user
from app.core.database import SessionLocal
from app.models.models import Project


class TestProjects:
    def setup_method(self):
        self.headers, self.user = _get_auth_header(email="proj_test@example.com")
        self.project_ids = []

    def teardown_method(self):
        db = SessionLocal()
        try:
            for pid in self.project_ids:
                p = db.query(Project).filter(Project.id == pid).first()
                if p:
                    db.delete(p)
            db.commit()
        finally:
            db.close()
        _cleanup_user("proj_test@example.com")

    def test_create_project(self):
        r = client.post("/api/projects", json={
            "name": "Test ECU Project",
            "vehicle_make": "BMW",
            "vehicle_model": "E46",
            "vehicle_year": 2003,
            "vehicle_engine": "330i",
        }, headers=self.headers)
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Test ECU Project"
        assert data["status"] == "pending"
        self.project_ids.append(data["id"])

    def test_list_projects(self):
        r = client.get("/api/projects", headers=self.headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_get_project(self):
        r = client.post("/api/projects", json={
            "name": "Get Test",
        }, headers=self.headers)
        pid = r.json()["id"]
        self.project_ids.append(pid)

        r = client.get(f"/api/projects/{pid}", headers=self.headers)
        assert r.status_code == 200
        assert r.json()["id"] == pid

    def test_get_project_not_found(self):
        r = client.get("/api/projects/999999", headers=self.headers)
        assert r.status_code == 404

    def test_project_requires_auth(self):
        r = client.get("/api/projects")
        assert r.status_code == 403
