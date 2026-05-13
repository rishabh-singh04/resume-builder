"""
Reusable decorators and context managers for the resume agent pipeline.
"""

import functools
import time
from contextlib import contextmanager
from typing import Callable

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


# ─────────────────────────────────────────────
# Retry Decorators
# ─────────────────────────────────────────────


def llm_retry(func: Callable) -> Callable:
    """Retry decorator for LLM API calls — 3 attempts, exponential backoff."""
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )(func)


def api_retry(func: Callable) -> Callable:
    """Retry decorator for external API calls (GitHub, Serper)."""
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )(func)


# ─────────────────────────────────────────────
# Logging Decorators
# ─────────────────────────────────────────────


def log_operation(operation: str):
    """Log start, completion time, and failure of an operation."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Starting: {operation}")
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.success(f"Completed: {operation} ({elapsed:.2f}s)")
                return result
            except Exception:
                elapsed = time.perf_counter() - start
                logger.exception(f"Failed: {operation} ({elapsed:.2f}s)")
                raise

        return wrapper

    return decorator


# ─────────────────────────────────────────────
# Context Managers
# ─────────────────────────────────────────────


@contextmanager
def timed_block(label: str):
    """Context manager that logs elapsed time for a block of code."""
    logger.info(f"Starting: {label}")
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"Finished: {label} ({elapsed:.2f}s)")


@contextmanager
def safe_operation(operation: str, default=None):
    """Context manager that catches exceptions and logs them, returning a default."""
    try:
        yield
    except Exception:
        logger.exception(f"Error in: {operation}")
        if default is not None:
            return default
        raise
