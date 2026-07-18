"""
Repository FileVersion — accès aux versions de fichiers.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.models import FileVersion


class FileVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, version_id: int) -> Optional[FileVersion]:
        return self.db.query(FileVersion).filter(FileVersion.id == version_id).first()

    def get_by_project(self, project_id: int) -> List[FileVersion]:
        return (
            self.db.query(FileVersion)
            .filter(FileVersion.project_id == project_id)
            .order_by(FileVersion.version_number)
            .all()
        )

    def create(self, **kwargs) -> FileVersion:
        fv = FileVersion(**kwargs)
        self.db.add(fv)
        self.db.commit()
        self.db.refresh(fv)
        return fv

    def count(self) -> int:
        return self.db.query(FileVersion).count()
