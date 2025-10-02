from config import SessionLocal
from models import Project
from services import EmbeddingService

class ProjectMatcher(object):
    def __init__(self):
        self.embedding_service = EmbeddingService('paraphrase-multilingual-MiniLM-L12-v2')
        pass

    def _get_all_projects(self):
        session = SessionLocal()
        try:
            projects = session.query(Project).all()
            return [{"id": p.id, "title": p.title, "description": p.description, "technologies": p.technologies} for p in projects]

        finally:
            session.close()

    def match_projects(self, job_description: str, top_n: int = 5):
        projects = self._get_all_projects()
        if not projects:
            return []

        index = self.embedding_service.build_index(projects)
        results = self.embedding_service.search(index, job_description, top_n=top_n)
        return results