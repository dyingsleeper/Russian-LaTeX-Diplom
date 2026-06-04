from __future__ import annotations

import re

_WHITESPACE = re.compile(r"\s+")
_URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_DATE = re.compile(r"\b\d{1,4}\.\d{1,2}\.\d{1,4}\b")
_TIME = re.compile(r"\b\d{1,2}:\d{2}\b")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def normalize_text(text: str) -> str:
    """Replace links, emails, dates, times, and numbers with placeholder
    tokens, then collapse whitespace. Original casing is preserved."""
    text = _URL.sub("LINK", text)
    text = _EMAIL.sub("EMAIL", text)
    text = _DATE.sub("DATE", text)
    text = _TIME.sub("TIME", text)
    text = _NUMBER.sub("NUM", text)
    return _WHITESPACE.sub(" ", text.strip())


def normalize_text_batch(texts: list[str]) -> list[str]:
    return [normalize_text(text) for text in texts]
