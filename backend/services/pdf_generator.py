from pathlib import Path

from pdflatex import PDFLaTeX


class PDFGeneratorService(object):
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def generate(self, tex_path: Path) -> Path:
        return self._compile_pdf(tex_path)

    def _compile_pdf(self, tex_path: Path):
        pdf_latex = PDFLaTeX.from_texfile(tex_path)
        pdf_latex.set_output_directory(self.output_dir)
        pdf, log, completed_process = pdf_latex.create_pdf(keep_pdf_file=True)

        if completed_process.returncode != 0:
            raise RuntimeError("LaTeX compilation failed → check template\nError: " + completed_process.stderr)

        return Path(f"{self.output_dir}/{Path(tex_path).name.replace(".tex", ".pdf")}")

    def _clean_temp_files(self, tex_path: Path):
        for ext in [".aux", ".log"]:
            tmp_file = self.output_dir / f"{tex_path.stem}{ext}"
            if tmp_file.exists():
                tmp_file.unlink()
