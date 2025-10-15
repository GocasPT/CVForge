from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import Project
from backend.schemas import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_all(
        self,
        limit: int = 10,
        offset: int = 0,
        search: Optional[str] = None
    ) -> tuple[List[Project], int]:
        query = self.db.query(Project)
        
        if search:
            search_filter = (
                (Project.title.ilike(f"%{search}%")) |
                (Project.description.ilike(f"%{search}%"))
            )
            query = query.filter(search_filter)
        
        total = query.count()
        
        projects = query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()
        
        return projects, total
    
    def create(self, project_data: ProjectCreate) -> Project:
        project_dict = project_data.model_dump()
        
        new_project = Project(**project_dict)
        
        self.db.add(new_project)
        self.db.commit()
        self.db.refresh(new_project)
        
        return new_project
    
    def update(self, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
        project = self.get_by_id(project_id)
        
        if not project:
            return None
        
        update_data = project_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(project, field, value)
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def delete(self, project_id: int) -> bool:
        project = self.get_by_id(project_id)
        
        if not project:
            return False
        
        self.db.delete(project)
        self.db.commit()
        
        return True
    
    def exists(self, project_id: int) -> bool:
        return self.db.query(Project.id).filter(Project.id == project_id).first() is not None
    
    def get_by_technologies(self, technologies: List[str]) -> List[Project]:
        projects = []
        for tech in technologies:
            results = self.db.query(Project).filter(
                Project.technologies.contains(tech)
            ).all()
            projects.extend(results)
        
        seen = set()
        unique_projects = []
        for project in projects:
            if project.id not in seen:
                seen.add(project.id)
                unique_projects.append(project)
        
        return unique_projects