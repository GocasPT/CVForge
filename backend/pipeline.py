from pathlib import Path
from services import ProfileService, ProjectMatcher, LaTeXService, PDFGenerator

def generate_cv(job_description: str, template: str = "basic") -> Path:
    print("=========== A iniciar pipeline ===========")

    profile = ProfileService(Path("backend/config/profile.json")).load_profile()
    matcher = ProjectMatcher()
    latex = LaTeXService(Path("backend/templates"), Path("backend/data/generated"))
    pdf = PDFGenerator(Path("backend/data/generated"))

    print(f"Profile: \n\tname: {profile.personal.get('full_name')}\n\temail: {profile.personal.get('email')}\n\t{profile.personal.get('summary')}")

    projects = matcher.match_projects(job_description)
    print("\nMatching Results:")
    for r in projects:
        print(f"\tRank {r['rank']} | Score {r['score']:.3f} | Projeto: {r['project']['title']}")

    projects = [p['project'] for p in projects]
    formatted = ""
    for p in projects:
        formatted += f"\\textbf{{{p['title']}}} \\\\ {p['description']} \\\\[1em]\n"
    context = {
        "full_name": profile.personal.get('full_name'),
        "email": profile.personal.get('email'),
        "projects": formatted
    }

    print("\nA gerar LaTeX...")
    tex_path = latex.save_rendered(template, context)
    print("✅ LaTeX gerado com sucesso!")
    print("A compilar PDF...")
    pdf_path = pdf.generate(tex_path)
    print("✅ PDF gerado com sucesso!")

    print("=========== A finalizar pipeline ===========")

    return pdf_path
