"""
Thin Gemini API wrapper — single point of contact for all LLM operations.
"""

import json
from typing import Type, TypeVar

import google.generativeai as genai
from pydantic import BaseModel

from core.config import settings
from utils.decorators import llm_retry, log_operation

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    """
    Central Gemini wrapper.

    All agents call this — never the SDK directly.
    Handles retries, JSON parsing, and Pydantic validation.
    """

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.MODEL_NAME)

    @llm_retry
    def generate(self, prompt: str) -> str:
        """Generate a raw text response from Gemini."""
        response = self.model.generate_content(prompt)
        return response.text

    @llm_retry
    def generate_json(self, prompt: str) -> dict:
        """Generate a response and parse it as JSON dict."""
        raw = self.generate(prompt)
        cleaned = self._clean_json(raw)
        return json.loads(cleaned)

    @llm_retry
    @log_operation("Structured LLM generation")
    def structured_generate(self, prompt: str, schema: Type[T]) -> T:
        """Generate structured output validated against a Pydantic model."""
        raw = self.generate(prompt)
        cleaned = self._clean_json(raw)
        parsed = json.loads(cleaned)
        return schema.model_validate(parsed)

    @staticmethod
    def _clean_json(text: str) -> str:
        """Strip markdown code fences from LLM JSON responses."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()


# Lazy singleton — initialized once, reused everywhere
_client: GeminiClient | None = None


def get_gemini_client() -> GeminiClient:
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client