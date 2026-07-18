"""
Repository AuditLog — accès aux logs d'audit.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.models import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> AuditLog:
        log = AuditLog(**kwargs)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_user(self, user_id: int) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def get_by_resource(self, resource_type: str, resource_id: int) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.resource_type == resource_type, AuditLog.resource_id == resource_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def list_recent(self, limit: int = 50) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def count(self) -> int:
        return self.db.query(AuditLog).count()
