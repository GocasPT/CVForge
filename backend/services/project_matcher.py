import os
from typing import List

from config import SessionLocal
from models import Project
from services import EmbeddingService


class ProjectMatcherService(object):
    def __init__(self):
        self.embedding_service = EmbeddingService(os.environ.get("EMBEDDING_MODEL"))
        self.projects: List[Project] = []
        pass

    def _get_all_projects(self):
        session = SessionLocal()
        try:
            self.projects = session.query(Project).all()
            return [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "technologies": p.technologies
                } for p in self.projects
            ]

        finally:
            session.close()

    def match_projects(self, job_description: str, top_n: int = 5):
        self.projects = self._get_all_projects()
        if not self.projects:
            return []

        index = self.embedding_service.build_index(self.projects)
        results = self.embedding_service.search(index, job_description, top_n=top_n)
        return results
