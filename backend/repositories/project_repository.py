from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from config import get_db
from models import Project


class ProjectRepo:
    def __init__(self):
        self.session: Session = get_db()

    def create(self, project: Project) -> Project:
        with self.session.begin() as session:
            session.add(project)

        return project

    def list(self, limit: int = 50, offset: int = 0, search: str | None = None) -> tuple[Sequence[Project], int]:
        stmt = select(Project)

        if search:
            stmt = stmt.filter(
                (Project.title.ilike(f"%{search}%")) |
                (Project.description.ilike(f"%{search}%"))
            )

        total_stmt = select(func.count(Project.id))
        if search:
            total_stmt = total_stmt.filter(
                (Project.title.ilike(f"%{search}%")) |
                (Project.description.ilike(f"%{search}%"))
            )

        stmt = stmt.offset(offset).limit(limit).order_by(Project.created_at.desc())

        with self.session.begin() as session:
            total = session.scalar(total_stmt)
            projects = session.scalars(stmt).all()

        return projects, total

    def list_all(self):
        stmt = select(Project)

        with self.session.begin() as session:
            list = session.scalars(stmt).all()

        return list

    def get_by_id(self, id: int) -> Optional[Project]:
        stmt = select(Project).where(Project.id == id)

        with self.session.begin() as session:
            result = session.scalar(stmt)

        return result

    def update(self, id: int, project: Project) -> Project:
        #TODO: find project → update project → return updated project
        return project

    def delete(self, id: int) -> bool:
        stmt = select(Project).where(Project.id == id)

        with self.session.begin() as session:
            result = session.scalar(stmt)
            session.delete(result)

        return True
