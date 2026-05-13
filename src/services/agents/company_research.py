"""Company Research agent — uses Serper API to research company for resume tailoring."""

from typing import Optional

import requests
from loguru import logger

from core.config import settings
from core.gemini_client import get_gemini_client
from services.prompts.company_research import COMPANY_RESEARCH_PROMPT
from utils.decorators import api_retry, log_operation


class CompanyInsight:
    """Structured company research results."""

    def __init__(self, data: dict):
        self.company_name: str = data.get("company_name", "")
        self.confirmed_tech_stack: list = data.get("confirmed_tech_stack", [])
        self.engineering_culture: list = data.get("engineering_culture", [])
        self.recent_initiatives: list = data.get("recent_initiatives", [])
        self.hiring_signals: list = data.get("hiring_signals", [])
        self.role_specific_keywords: list = data.get("role_specific_keywords", [])
        self.summary: str = data.get("summary", "")


class CompanyResearchService:
    """Researches company tech stack, culture, and hiring signals using Serper + Gemini."""

    SEARCH_QUERIES = [
        '"{company}" engineering blog technology stack',
        '"{company}" tech stack {year}',
        '"{company}" engineering culture values hiring',
    ]

    def __init__(self):
        self.client = get_gemini_client()

    @log_operation("Company research")
    def research(
        self,
        company_name: str,
        role_title: str,
    ) -> Optional[CompanyInsight]:
        """Research a company and return structured insights."""
        if not company_name:
            logger.warning("No company name provided — skipping research")
            return None

        if not settings.SERPER_API_KEY:
            logger.warning("No SERPER_API_KEY configured — skipping company research")
            return None

        search_results = self._search_company(company_name)
        if not search_results:
            return None

        return self._analyze_results(
            company_name=company_name,
            role_title=role_title,
            search_results=search_results,
        )

    # ─────────────────────────────────────────────
    # Serper Search
    # ─────────────────────────────────────────────

    @api_retry
    def _search_company(self, company_name: str) -> str:
        """Search for company information using Serper API."""
        from datetime import datetime

        all_results = []
        year = datetime.now().year

        for query_template in self.SEARCH_QUERIES:
            query = query_template.format(company=company_name, year=year)

            try:
                response = requests.post(
                    "https://google.serper.dev/search",
                    headers={"X-API-KEY": settings.SERPER_API_KEY},
                    json={"q": query, "num": 5},
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                for result in data.get("organic", []):
                    all_results.append(
                        f"Title: {result.get('title', '')}\n"
                        f"Snippet: {result.get('snippet', '')}\n"
                    )
            except Exception:
                logger.warning(f"Serper search failed for query: {query}")
                continue

        return "\n---\n".join(all_results) if all_results else ""

    # ─────────────────────────────────────────────
    # LLM Analysis
    # ─────────────────────────────────────────────

    def _analyze_results(
        self,
        company_name: str,
        role_title: str,
        search_results: str,
    ) -> CompanyInsight:
        """Use Gemini to synthesize search results into structured insights."""
        prompt = COMPANY_RESEARCH_PROMPT.format(
            company_name=company_name,
            role_title=role_title,
            search_results=search_results,
        )

        data = self.client.generate_json(prompt)
        return CompanyInsight(data)
