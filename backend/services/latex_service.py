from __future__ import annotations
import datetime
import logging
from pathlib import Path
from string import Template
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class TemplateNotFoundError(FileNotFoundError):
    pass


def escape_latex(text: str) -> str:
    """
    Basic LaTeX escape for common special characters.
    This is intentionally conservative; for more advanced use consider a templating
    engine that supports safe blocks or use a whitelist approach.
    """
    if text is None:
        return ""
    
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\^{}",
    }

    s = str(text)
    for k, v in replacements.items():
        s = s.replace(k, v)
        
    return s


class LaTeXService:
    def __init__(self, template_dir: Path, output_dir: Path | None = None):
        self.template_dir = Path(template_dir)
        if output_dir is None:
            output_dir = Path.cwd() / "backend" / "data" / "generated"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_available_templates(self) -> List[str]:
        return [p.stem for p in self.template_dir.glob("*.tex")]

    def load_template(self, template_name: str) -> str:
        template_path = self.template_dir / f"{template_name}.tex"
        if not template_path.exists():
            raise TemplateNotFoundError(f"Template '{template_name}' not found at {template_path}")
        return template_path.read_text(encoding="utf-8")

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render template using string.Template with very basic escaping.
        For lists (e.g. projects) caller should pre-render to a single string,
        or extend this function to accept richer structures.
        """
        template_str = self.load_template(template_name)
        # # escape values conservatively
        # escaped_context = {
        #     k: (v if isinstance(v, str) and v.startswith(r"\latexraw:") else escape_latex(v))
        #     for k, v in context.items()
        # }
        # # allow raw LaTeX by prefixing a string with '\latexraw:' (explicit opt-in)
        # safe_context = {
        #     k: (v[len(r"\latexraw:"):] if isinstance(v, str) and v.startswith(r"\latexraw:") else str(v))
        #     for k, v in escaped_context.items()
        # }

        safe_context = {
            'full_name': context.get('full_name'),
            'email': context.get('email'),
            # 'projects': ''.join(
            #     f"\\textbf{{{p['title']}}} \\\\ {p['description']} \\\\[1em]\n" for p in context.get('projects')
            # )
            'projects': context.get('projects')
        }

        template = Template(template_str)
        return template.safe_substitute(context)

    def save_rendered(self, template_name: str, context: Dict[str, Any]) -> Path:
        rendered_tex = self.render(template_name, context)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"cv_{timestamp}.tex"
        output_path.write_text(rendered_tex, encoding="utf-8")
        logger.info("Rendered LaTeX saved to %s", output_path)
        return output_path
