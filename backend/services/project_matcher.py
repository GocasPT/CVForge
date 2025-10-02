from typing import Optional

from services import EmbeddingService

class ProjectMatcher(object):
    def __init__(self, model_name: Optional[str]):
        self.embedding_service = EmbeddingService(model_name)
        pass

    def match_projects(self, job_description: str, projects: list[dict], top_n: int = 5):
        index = self.embedding_service.build_index(projects)
        results = self.embedding_service.search(index, job_description, top_n=top_n)
        return results