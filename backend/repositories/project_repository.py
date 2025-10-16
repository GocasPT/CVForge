from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Project


class ProjectRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, project: Project) -> Project:
        self.session.add(project)
        return project

    def list(self, limit: int = 50, offset: int = 0, search: str | None = None) -> tuple[Sequence[Project], int]:
        stmt = select(Project)

        if search:
            stmt = stmt.filter(
                (Project.title.ilike(f"%{search}%")) |
                (Project.description.ilike(f"%{search}%"))
            )

        stmt = stmt.offset(offset).limit(limit).order_by(Project.created_at.desc())

        total = 0
        projects = self.session.scalars(stmt).all()

        return projects, total

    def list_all(self):
        stmt = select(Project)
        return self.session.scalars(stmt).all()

    def get_by_id(self, id: int) -> Optional[Project]:
        stmt = select(Project).where(Project.id == id)
        return self.session.scalar(stmt)

    def update(self, id: int, project: Project) -> Project:
        #TODO: find project → update project → return updated project
        return project

    def delete(self, id: int) -> None:
        stmt = select(Project).where(Project.id == id)
        self.session.delete(stmt)
