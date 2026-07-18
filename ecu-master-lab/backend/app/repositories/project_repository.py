"""
Repository Project — accès aux données projets ECU.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.models import Project, ProjectStatus


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_by_user(self, user_id: int) -> List[Project]:
        return (
            self.db.query(Project)
            .filter(Project.user_id == user_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    def create(self, **kwargs) -> Project:
        project = Project(**kwargs)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project: Project, **kwargs) -> Project:
        for key, value in kwargs.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def count(self) -> int:
        return self.db.query(Project).count()

    def count_by_status(self, status: ProjectStatus) -> int:
        return self.db.query(Project).filter(Project.status == status).count()

    def list_all(self) -> List[Project]:
        return self.db.query(Project).order_by(Project.created_at.desc()).all()
