"""Resume Parser agent — extracts structured data from resume PDF or text."""

import json

import pdfplumber
from loguru import logger

from core.gemini_client import get_gemini_client
from models.resume import ParsedResume
from services.prompts.resume_parser import RESUME_PARSER_PROMPT
from utils.decorators import llm_retry, log_operation


class ResumeParserService:
    """Parses resume PDF or raw text into a structured ParsedResume model."""

    def __init__(self):
        self.client = get_gemini_client()

    @log_operation("Resume PDF parsing")
    def parse_pdf(self, pdf_path: str) -> ParsedResume:
        """Parse a resume from PDF file."""
        extracted_text = self._extract_pdf_text(pdf_path)
        return self.parse_text(extracted_text)

    @llm_retry
    @log_operation("Resume text parsing")
    def parse_text(self, resume_text: str) -> ParsedResume:
        """Parse raw resume text into structured model."""
        prompt = RESUME_PARSER_PROMPT.format(resume_text=resume_text)

        try:
            return self.client.structured_generate(
                prompt=prompt,
                schema=ParsedResume,
            )
        except json.JSONDecodeError as e:
            raise ValueError("Gemini returned invalid JSON for resume parsing.") from e

    @staticmethod
    def _extract_pdf_text(pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber (handles layout-heavy resumes well)."""
        logger.info(f"Extracting PDF text: {pdf_path}")
        text_chunks = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_chunks.append(text)

        full_text = "\n".join(text_chunks)
        if not full_text.strip():
            raise ValueError("No text extracted from PDF.")

        return full_text