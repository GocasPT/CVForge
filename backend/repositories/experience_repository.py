from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Experience


class ExperienceRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, experience: Experience) -> Experience:
        self.session.add(experience)
        return experience

    def list(self, limit: int = 50, offset: int = 0, search: str | None = None) -> tuple[Sequence[Experience], int]:
        stmt = select(Experience)

        if search:
            stmt = stmt.filter(
                (Experience.position.ilike(f"%{search}%")) |
                (Experience.company.ilike(f"%{search}%")) |
                (Experience.description.ilike(f"%{search}%"))
            )

        stmt = stmt.offset(offset).limit(limit).order_by(Experience.created_at.desc())

        total = 0
        experiences = self.session.scalars(stmt).all()

        return experiences, total

    def get_by_id(self, id: int) -> Optional[Experience]:
        stmt = select(Experience).where(Experience.id == id)
        return self.session.scalar(stmt)

    def update(self, id: int, experience: Experience) -> Experience:
        #TODO: find experience → update experience → return updated experience
        return experience

    def delete(self, id: int) -> None:
        stmt = select(Experience).where(Experience.id == id)
        self.session.delete(stmt)