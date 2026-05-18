""""
Deterministic Core
        +
Embeddings Similarity
        +
1 Recruiter Critique Call
"""

from functools import lru_cache
from typing import List

import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.safe import safe_list, safe_str

from core.config import settings


class EmbeddingService:
    """
    Central embedding service for semantic similarity operations.

    Used by:
    - GitHub repo ranking (JD vs repo content)
    - ATS semantic scoring (JD vs resume)
    - Keyword matching (semantic, not just exact)
    """

    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.success("Embedding model loaded")

    # ─────────────────────────────────────────────
    # Embeddings
    # ─────────────────────────────────────────────

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        if not text.strip():
            raise ValueError("Input text is empty.")
        return self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Batch embeddings — faster than multiple single calls."""
        if not texts:
            raise ValueError("Text list is empty.")
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        )

    # ─────────────────────────────────────────────
    # Similarity
    # ─────────────────────────────────────────────

    def similarity_score(self, text_a: str | None, text_b: str | None) -> float:
        """Cosine similarity between two texts. Returns 0–100."""
        text_a = safe_str(text_a)
        text_b = safe_str(text_b)
        if not text_a or not text_b:
            return 0.0
        emb_a = self.embed_text(text_a)
        emb_b = self.embed_text(text_b)
        score = cosine_similarity([emb_a], [emb_b])[0][0]
        return round(float(score) * 100, 2)

    def batch_similarity(self, query: str | None, candidates: List[str]) -> List[float]:
        """Compare a query against multiple candidates. Returns list of 0–100 scores."""
        query = safe_str(query)
        candidates = safe_list(candidates)
        if not candidates:
            return []
        if not query:
            return [0.0 for _ in candidates]

        query_emb = self.embed_text(query)
        candidate_embs = self.embed_batch(candidates)
        scores = cosine_similarity([query_emb], candidate_embs)[0]
        return [round(float(s) * 100, 2) for s in scores]

    # ─────────────────────────────────────────────
    # Ranking
    # ─────────────────────────────────────────────

    def rank_by_similarity(
        self, query: str, candidates: List[str], top_k: int = 5
    ) -> List[dict]:
        """Rank texts by semantic similarity to query. Returns top-k {text, score} dicts."""
        scores = self.batch_similarity(query=query, candidates=candidates)

        ranked = sorted(
            [{"text": text, "score": score} for text, score in zip(candidates, scores)],
            key=lambda x: x["score"],
            reverse=True,
        )
        return ranked[:top_k]

    # ─────────────────────────────────────────────
    # Semantic Keyword Matching
    # ─────────────────────────────────────────────

    def semantic_keyword_match(
        self,
        jd_keywords: List[str],
        resume_content: List[str],
        threshold: float = 65,
    ) -> List[str]:
        """Find JD keywords that semantically match resume content (above threshold)."""
        return [
            keyword
            for keyword in jd_keywords
            if max(self.batch_similarity(keyword, resume_content)) >= threshold
        ]


# ─────────────────────────────────────────────
# Lazy Singleton
# ─────────────────────────────────────────────

_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Lazy singleton — prevents model reload on every import."""
    global _service
    if _service is None:
        _service = EmbeddingService()
    return _service