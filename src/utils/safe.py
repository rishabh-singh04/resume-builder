from typing import Iterable, List, Optional


def safe_str(value: Optional[str]) -> str:
    """Normalize a nullable string to a trimmed safe string."""
    return "" if value is None else str(value).strip()


def safe_list(values: Optional[Iterable[Optional[str]]]) -> List[str]:
    """Normalize a nullable iterable of strings into a list of trimmed non-empty strings."""
    if values is None:
        return []
    return [str(v).strip() for v in values if v is not None and str(v).strip()]
