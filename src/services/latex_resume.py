"""LaTeX resume generator — renders TailoredResume into .tex files using Jinja2."""

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from loguru import logger

from models.tailored_resume import TailoredResume
from utils.decorators import log_operation


class LatexGeneratorService:
    """Generates .tex files from TailoredResume using Jinja2 templates."""

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            template_dir = str(Path(__file__).parent / "templates")

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=False,
        )
        self.env.filters["latex_escape"] = self._latex_escape

    @log_operation("LaTeX generation")
    def generate_tex(
        self,
        tailored_resume: TailoredResume,
        output_path: str = "output/resume.tex",
    ) -> str:
        """Render a TailoredResume into a .tex file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        template = self.env.get_template("resume.tex.j2")
        rendered = template.render(resume=tailored_resume)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)

        logger.success(f"TEX generated: {output_path}")
        return output_path

    @staticmethod
    def _latex_escape(text: str) -> str:
        """Escape special LaTeX characters to prevent compilation errors."""
        if not text:
            return ""
        special_chars = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        for char, escaped in special_chars.items():
            text = text.replace(char, escaped)
        return text