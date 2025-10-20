from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from config import get_db
from models import Experience


class ExperienceRepo:
    def __init__(self):
        self.session: Session = get_db()

    def create(self, experience: Experience) -> Experience:
        with self.session.begin() as session:
            session.add(experience)

        return experience

    def list(self, limit: int = 50, offset: int = 0, search: str | None = None) -> tuple[Sequence[Experience], int]:
        stmt = select(Experience)

        if search:
            stmt = stmt.filter(
                (Experience.position.ilike(f"%{search}%")) |
                (Experience.company.ilike(f"%{search}%")) |
                (Experience.description.ilike(f"%{search}%"))
            )
        total_stmt = select(func.count(Experience.id))

        if search:
            total_stmt = total_stmt.filter(
                (Experience.position.ilike(f"%{search}%")) |
                (Experience.company.ilike(f"%{search}%")) |
                (Experience.description.ilike(f"%{search}%"))
            )

        stmt = stmt.offset(offset).limit(limit).order_by(Experience.created_at.desc())

        with self.session.begin() as session:
            total = session.scalar(total_stmt)
            experiences = session.scalars(stmt).all()

        return experiences, total

    def get_by_id(self, id: int) -> Optional[Experience]:
        stmt = select(Experience).where(Experience.id == id)

        with self.session.begin() as session:
            result = session.scalar(stmt)

        return result

    def update(self, id: int, experience: Experience) -> Experience:
        existing_experience = self.get_by_id(id)
        if existing_experience:
            for key, value in experience.__dict__.items():
                if key != '_sa_instance_state':
                    setattr(existing_experience, key, value)
            self.session.commit()
            self.session.refresh(existing_experience)
            return existing_experience
        return None

    def delete(self, id: int) -> bool:
        stmt = select(Experience).where(Experience.id == id)

        with self.session.begin() as session:
            result = session.scalar(stmt)
            session.delete(result)

        return True