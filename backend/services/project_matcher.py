import logging
from typing import List
from sqlalchemy import select
from config import settings, get_db
from models import Project
from services import EmbeddingService

logger = logging.getLogger(__name__)

class ProjectMatcherService(object):
    def __init__(self):
        self.db = get_db()
        self.embedding_service = EmbeddingService(settings.embedding_model)
        pass

    def _get_all_projects(self):
        with self.db.begin() as session:
            stmt = select(Project)
            projects = session.scalars(stmt).all()
            
        return projects

    def match_projects(self, job_description: str, top_n: int = 5):
        projects = self._get_all_projects()
        if not projects:
            return []

        projects_dict = [p.as_dict() for p in projects]

        index = self.embedding_service.build_index(projects_dict)
        results = self.embedding_service.search(index, job_description, top_n=top_n)
        return results
