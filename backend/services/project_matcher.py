from backend.config import SessionLocal
from backend.models import Project
from backend.services import EmbeddingService

class ProjectMatcher(object):
    def __init__(self):
        self.embedding_service = EmbeddingService()
        pass

    def _get_all_projects(self):
        session = SessionLocal()
        try:
            projects = session.query(Project).all()
            return [{"id": p.id, "title": p.title, "description": p.description} for p in projects]

        finally:
            session.close()

    def match_projects(self, job_description: str, projects: list[dict], top_n: int = 5):
        projects = self._get_all_projects()
        if not projects:
            return []

        index = self.embedding_service.build_index(projects)
        results = self.embedding_service.search(index, job_description, top_n=top_n)
        return results