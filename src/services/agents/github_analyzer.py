"""GitHub Analyzer agent — fetches repos, ranks by relevance, enriches with LLM."""

from typing import List

from github import Github
from loguru import logger

from core.config import settings
from core.gemini_client import get_gemini_client
from models.github import GitHubMetrics, GitHubProject
from services.prompts.github_analyzer import GITHUB_ANALYZER_PROMPT
from services.embeddings import get_embedding_service
from utils.decorators import llm_retry, log_operation
from utils.safe import safe_list, safe_str


class GitHubAnalyzerService:
    """Analyzes GitHub profile repositories against a target job description."""

    MAX_REPOS = 15
    TOP_K = 5

    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN) if settings.GITHUB_TOKEN else None
        self.client = get_gemini_client()
        self.embeddings = get_embedding_service()

    @log_operation("GitHub profile analysis")
    def analyze_user(self, username: str, jd_text: str) -> List[GitHubProject]:
        """Analyze a GitHub user's repos for a specific JD."""
        if not self.github:
            logger.warning("No GITHUB_TOKEN configured — skipping GitHub analysis")
            return []

        repos = self._fetch_repositories(username)
        if not repos:
            return []

        ranked_repos = self._rank_repositories(repos=repos, jd_text=jd_text)
        enriched = []

        for repo_data in ranked_repos:
            try:
                project = self._enrich_repo(repo_data, jd_text)
                enriched.append(project)
            except Exception:
                logger.exception(f"Failed to analyze repo: {repo_data['repo'].name}")

        logger.success(f"Analyzed {len(enriched)} repositories")
        return enriched

    # ─────────────────────────────────────────────
    # Repo Fetching
    # ─────────────────────────────────────────────

    def _fetch_repositories(self, username: str):
        """Fetch non-fork, non-archived, non-trivial public repos sorted by activity."""
        user = self.github.get_user(username)

        repos = [
            repo
            for repo in user.get_repos()
            if not repo.fork and not repo.private and not repo.archived and repo.size >= 50
        ]

        repos.sort(key=lambda r: (r.stargazers_count, r.updated_at), reverse=True)
        return repos[: self.MAX_REPOS]

    # ─────────────────────────────────────────────
    # Embedding-Based Ranking
    # ─────────────────────────────────────────────

    def _rank_repositories(self, repos, jd_text: str):
        """Rank repos by semantic similarity to JD using embeddings."""
        repo_texts = []
        readmes = {}

        for repo in repos:
            readme = self._get_readme(repo)
            readmes[repo.name] = readme
            text_blob = f"{safe_str(repo.name)} {safe_str(repo.description)} {' '.join(safe_list(repo.get_topics()))} {safe_str(readme)[:3000]}"
            repo_texts.append(text_blob)

        ranked = self.embeddings.rank_by_similarity(
            query=jd_text,
            candidates=repo_texts,
            top_k=self.TOP_K,
        )

        ranked_repos = []
        for rank in ranked:
            index = repo_texts.index(rank["text"])
            ranked_repos.append({
                "repo": repos[index],
                "score": rank["score"],
                "readme": readmes[repos[index].name],
            })

        return ranked_repos

    # ─────────────────────────────────────────────
    # README Extraction
    # ─────────────────────────────────────────────

    @staticmethod
    def _get_readme(repo) -> str:
        """Extract README text, truncated to 8000 chars."""
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode("utf-8", errors="ignore")[:8000]
        except Exception:
            return ""

    # ─────────────────────────────────────────────
    # LLM Enrichment (only for top-ranked repos)
    # ─────────────────────────────────────────────

    @llm_retry
    def _enrich_repo(self, repo_data: dict, jd_text: str) -> GitHubProject:
        """Use Gemini to enrich a top-ranked repo with resume-relevant analysis."""
        repo = repo_data["repo"]

        prompt = GITHUB_ANALYZER_PROMPT.format(
            jd=jd_text,
            repo_name=safe_str(repo.name),
            description=safe_str(repo.description),
            languages=safe_str(repo.language),
            topics=", ".join(safe_list(repo.get_topics())),
            readme=safe_str(repo_data["readme"]),
            embedding_score=repo_data["score"],
        )

        parsed = self.client.structured_generate(prompt=prompt, schema=GitHubProject)

        # Override with real metadata (LLM may hallucinate these)
        parsed.repo_name = repo.name
        parsed.repo_url = repo.html_url
        parsed.description = repo.description
        parsed.primary_language = repo.language
        parsed.metrics = GitHubMetrics(
            stars=repo.stargazers_count,
            forks=repo.forks_count,
            watchers=repo.subscribers_count,
            open_issues=repo.open_issues_count,
        )
        parsed.last_commit_date = repo.updated_at

        return parsed