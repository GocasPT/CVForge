from typing import List
from backend.config import settings, get_db
from backend.models import Project
from backend.services import EmbeddingService

class ProjectMatcherService(object):
    def __init__(self):
        self.embedding_service = EmbeddingService(settings.embedding_model)
        self.projects: List[Project] = []
        pass

    def _get_all_projects(self):
        db = get_db()
        self.projects = db.query(Project).all()
        return [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "technologies": p.technologies
            } for p in self.projects
        ]

    def match_projects(self, job_description: str, top_n: int = 5):
        self.projects = self._get_all_projects()
        if not self.projects:
            return []

        index = self.embedding_service.build_index(self.projects)
        results = self.embedding_service.search(index, job_description, top_n=top_n)
        return results
