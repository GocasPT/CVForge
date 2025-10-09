from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import (
    profile,
    projects,
    experiences,
    templates,
    generate,
)

app = FastAPI(title="CVForge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints principais
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(experiences.router, prefix="/api/experiences", tags=["Experiences"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])

@app.get("/")
def root():
    return {"message": "CVForge API is running!"}
