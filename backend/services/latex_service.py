import datetime
import os
from pathlib import Path
from string import Template


class LaTeXService(object):
    def __init__(self, template_dir: Path, output_dir: Path):
        self.template_dir = template_dir
        self.output_dir = output_dir

    def get_available_templates(self) -> list:
        return [f for f in os.listdir(self.template_dir) if f.endswith(".tex")]

    def load_template(self, template_name: str) -> str:
        template_path = Path(self.template_dir) / f"{template_name}.tex"
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    def render(self, template_name: str, context: dict) -> str:
        template_str = self.load_template(template_name)
        template = Template(template_str)
        return template.safe_substitute(context)

    def save_rendered(self, template_name: str, context: dict) -> Path:
        rendered_tex = self.render(template_name, context)

        output_dir = Path("backend/data/generated")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"cv_{timestamp}.tex"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_tex)

        return output_path
