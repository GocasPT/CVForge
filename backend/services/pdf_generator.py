from pathlib import Path
import logging
from pdflatex import PDFLaTeX

logger = logging.getLogger(__name__)


class PDFGeneratorService:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir).absolute()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, tex_path: Path) -> Path:
        """Compile tex_path into a PDF and return the PDF path."""
        tex_path = Path(tex_path).absolute()
        if not tex_path.exists():
            raise FileNotFoundError(f"TeX file not found: {tex_path}")

        try:
            pdf_path = self._compile_pdf(tex_path)
            self._clean_temp_files(tex_path)
            return pdf_path
        except Exception as exc:
            logger.exception("PDF generation failed for %s", tex_path)
            raise

    def _compile_pdf(self, tex_path: Path) -> Path:
        pdf_latex = PDFLaTeX.from_texfile(str(tex_path))
        pdf_latex.set_output_directory(str(self.output_dir))
        pdf, log, completed_process = pdf_latex.create_pdf(keep_pdf_file=True)

        if hasattr(completed_process, "returncode") and completed_process.returncode != 0:
            stderr = getattr(completed_process, "stderr", "<no stderr>")
            raise RuntimeError(f"LaTeX compilation failed (returncode={completed_process.returncode}). Stderr: {stderr!s}")

        pdf_filename = tex_path.with_suffix(".pdf").name
        return self.output_dir / pdf_filename

    def _clean_temp_files(self, tex_path: Path) -> None:
        for ext in [".aux", ".log", ".out", ".toc"]:
            tmp_file = self.output_dir / f"{tex_path.stem}{ext}"
            try:
                if tmp_file.exists():
                    tmp_file.unlink()
            except Exception:
                logger.warning("Could not remove temp file %s", tmp_file)
