"""Database / ORM integrity tests."""
from sqlalchemy import text
from app.core.database import engine, list_tables
from app.models.models import Base as V1Base
from app.models.new.ecu_models import Base as V2Base


EXPECTED_V1_TABLES = {
    "users", "projects", "vehicles", "ecus", "jobs",
    "file_versions", "audit_logs",
}


class TestDatabaseConnection:
    def test_engine_connects(self):
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_list_tables(self):
        tables = list_tables()
        assert len(tables) >= 50
        assert "users" in tables
        assert "projects" in tables


class TestORMModels:
    def test_v1_tables_registered(self):
        v1_tables = set()
        for mapper in V1Base.registry.mappers:
            v1_tables.add(mapper.local_table.name)
        assert EXPECTED_V1_TABLES.issubset(v1_tables)

    def test_v2_tables_registered(self):
        v2_tables = set()
        for mapper in V2Base.registry.mappers:
            v2_tables.add(mapper.local_table.name)
        assert len(v2_tables) >= 35
        assert "analyses" in v2_tables
        assert "ecu_files" in v2_tables
        assert "manufacturers" in v2_tables

    def test_all_orm_tables_exist_in_db(self):
        db_tables = set(list_tables())
        v1_tables = set()
        for mapper in V1Base.registry.mappers:
            v1_tables.add(mapper.local_table.name)
        v2_tables = set()
        for mapper in V2Base.registry.mappers:
            v2_tables.add(mapper.local_table.name)
        all_orm = v1_tables | v2_tables
        missing = all_orm - db_tables
        assert not missing, f"ORM tables missing from DB: {missing}"
