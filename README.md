# CVForge

AI-powered CV generator that automatically matches your projects to job descriptions.

## Setup

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. Copy `.env.example` → `.env` and configure paths
4. Copy `config/profile.json.example` → `config/profile.json`
5. `python main.py` (starts API on http://localhost:8000)

### Frontend
1. `cd frontend`
2. `pnpm install`
3. `pnpm run dev` (starts UI on http://localhost:8080)

## Usage
1. Add your profile information in the Profile section
2. Add projects and experiences in their respective sections
3. Go to Generate, paste a job description
4. Review matched projects and generate PDF CV

## API Endpoints
- `GET/POST /api/profile` - Manage profile data
- `GET/POST /api/projects` - CRUD projects
- `GET/POST /api/experiences` - CRUD work experiences
- `POST /api/generate` - Generate CV from job description
