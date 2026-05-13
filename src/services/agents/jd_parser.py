"""JD Parser agent — converts raw job description text into structured JobDescription."""

import json

from loguru import logger

from core.gemini_client import get_gemini_client
from models.jd import JobDescription
from services.prompts.jd_parser import JD_PARSER_PROMPT
from utils.decorators import llm_retry, log_operation


class JDParserService:
    """Parses raw JD text into a structured JobDescription model."""

    def __init__(self):
        self.client = get_gemini_client()

    @llm_retry
    @log_operation("JD parsing")
    def parse(self, jd_text: str) -> JobDescription:
        """
        Parse raw JD text.

        Args:
            jd_text: Raw job description text.

        Returns:
            Validated JobDescription model.
        """
        prompt = JD_PARSER_PROMPT.format(jd_text=jd_text)

        try:
            return self.client.structured_generate(
                prompt=prompt,
                schema=JobDescription,
            )
        except json.JSONDecodeError as e:
            raise ValueError("Gemini returned invalid JSON for JD parsing.") from e