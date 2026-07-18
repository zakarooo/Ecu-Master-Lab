from tests.conftest import client


class TestHealth:
    def test_health_endpoint(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "app" in data
        assert "version" in data

    def test_docs_disabled_in_production(self):
        r = client.get("/docs")
        assert r.status_code == 404

    def test_openapi_disabled_in_production(self):
        r = client.get("/openapi.json")
        assert r.status_code == 404
