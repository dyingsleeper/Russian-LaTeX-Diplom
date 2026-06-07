from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from diplom_ai.data.preprocessing import normalize_text
from diplom_ai.email.contracts import NormalizedEmailDraft, RawEmailRecord, TextQuality
from diplom_ai.email.parsing import extract_best_text, parse_email_bytes
from diplom_ai.storage.repositories import EmailRepository


@dataclass(frozen=True)
class NormalizeEmailsResult:
    completed: int
    failed: int


_QUOTED_PRINTABLE_SOFT_BREAK = re.compile(r"=\r?\n")
_HTML_ENTITY = re.compile(r"&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);")
_REPEATED_SYMBOL = re.compile(r"([^\w\s])\1{2,}")
_CSS_DECLARATION = re.compile(
    r"(?i)\b(?:font-size|line-height|margin|padding|color|background|display|width|height)"
    r"\s*:\s*[^;{}]+;?"
)
_CSS_BLOCK = re.compile(r"(?is)(?:@media\b[^{]*\{.*?\}|[.#]?[a-z0-9_-]+\s*\{[^{}]*\})")
_FOOTER_PATTERNS = (
    re.compile(r"(?i)\bunsubscribe\b"),
    re.compile(r"(?i)\bmanage preferences\b"),
    re.compile(r"(?i)\bprivacy policy\b"),
    re.compile(r"(?i)\bview (?:this email )?in (?:your )?browser\b"),
    re.compile(r"(?i)\byou (?:are receiving|received) (?:this email|this message)\b"),
    re.compile(r"(?i)\bthis email was sent\b"),
    re.compile(r"(?i)\bотписаться\b"),
    re.compile(r"(?i)\bуправлени[ея] подписк"),
    re.compile(r"(?i)\bполитик[аи] конфиденциальности\b"),
    re.compile(r"(?i)\bписьмо отправлено\b"),
)


def normalize_raw_email(raw_email: RawEmailRecord) -> NormalizedEmailDraft:
    raw_bytes = raw_email.raw_mime_path.read_bytes()
    parsed = parse_email_bytes(raw_bytes)
    subject = normalize_text(parsed.subject or raw_email.subject_raw)
    body_text = _clean_email_body(_strip_reply_and_signature(extract_best_text(parsed.message)))
    normalized_text = normalize_text(f"{subject} {body_text}".strip())
    return NormalizedEmailDraft(
        raw_email_id=raw_email.id,
        mailbox_id=raw_email.mailbox_id,
        subject=subject,
        body_text=body_text,
        normalized_text=normalized_text,
        language=_detect_language(normalized_text),
        text_quality=_text_quality(normalized_text),
    )


def normalize_pending_emails(
    *,
    repository: EmailRepository,
    mailbox_id: str,
    limit: int | None = None,
) -> NormalizeEmailsResult:
    completed = 0
    failed = 0
    for raw_email in repository.list_raw_emails(
        mailbox_id=mailbox_id,
        status="pending",
        limit=limit,
    ):
        try:
            normalized = normalize_raw_email(raw_email)
            repository.save_normalized_email(normalized)
            repository.mark_raw_email_status(raw_email.id, "completed")
            completed += 1
        except Exception:
            repository.mark_raw_email_status(
                raw_email.id,
                "failed",
                error_code="normalize_error",
                error_message="Unable to normalize raw email",
            )
            failed += 1
    return NormalizeEmailsResult(completed=completed, failed=failed)


def _strip_reply_and_signature(text: str) -> str:
    kept_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(">"):
            continue
        lowered = stripped.lower()
        if _is_reply_boundary(lowered) or _is_signature_boundary(lowered):
            break
        kept_lines.append(stripped)
    return "\n".join(kept_lines)


def _clean_email_body(text: str) -> str:
    text = _QUOTED_PRINTABLE_SOFT_BREAK.sub("", text)
    text = _strip_invisible_unicode(text)
    text = _HTML_ENTITY.sub(" ", text)
    text = _REPEATED_SYMBOL.sub("", text)
    text = _CSS_BLOCK.sub(" ", text)
    cleaned_lines: list[str] = []
    for raw_line in text.splitlines():
        line = _CSS_DECLARATION.sub(" ", raw_line)
        line = _strip_emoji(line)
        line = normalize_text(line).strip(" \t-–—:|")
        if not line:
            continue
        if _is_footer_line(line) or _is_css_noise_line(line):
            continue
        cleaned_lines.append(line)
    return normalize_text(" ".join(cleaned_lines))


def _strip_invisible_unicode(text: str) -> str:
    return "".join(char for char in text if unicodedata.category(char) != "Cf")


def _strip_emoji(text: str) -> str:
    return "".join(char for char in text if not _is_emoji_or_decorative(char))


def _is_emoji_or_decorative(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x1F000 <= codepoint <= 0x1FAFF
        or 0x2600 <= codepoint <= 0x27BF
        or 0x2300 <= codepoint <= 0x23FF
        or 0x2B00 <= codepoint <= 0x2BFF
        or 0x2190 <= codepoint <= 0x21FF
        or codepoint
        in {
            0xFE0E,
            0xFE0F,
            0x20E3,
            0x203C,
            0x2049,
            0x2122,
            0x2139,
            0x24C2,
            0x3030,
            0x303D,
            0x3297,
            0x3299,
        }
    )


def _is_reply_boundary(lowered_line: str) -> bool:
    return (
        lowered_line.startswith("on ")
        and lowered_line.endswith(" wrote:")
        or lowered_line.endswith(" писал(а):")
        or lowered_line.endswith(" написал(а):")
        or lowered_line.endswith(" пишет:")
        or lowered_line.startswith("-----original message-----")
        or lowered_line.startswith("----- forwarded message -----")
        or lowered_line.startswith("пересылаемое сообщение")
    )


def _is_signature_boundary(lowered_line: str) -> bool:
    return lowered_line in {"--", "regards", "best regards", "kind regards", "с уважением"} or (
        lowered_line.startswith("best regards,")
        or lowered_line.startswith("regards,")
        or lowered_line.startswith("kind regards,")
        or lowered_line.startswith("с уважением,")
    )


def _is_footer_line(line: str) -> bool:
    return any(pattern.search(line) for pattern in _FOOTER_PATTERNS)


def _is_css_noise_line(line: str) -> bool:
    lowered = line.lower()
    if "@media" in lowered or "!important" in lowered:
        return True
    css_markers = sum(
        marker in lowered
        for marker in ("font-size", "line-height", "padding", "margin", "{", "}")
    )
    return css_markers >= 2


def _detect_language(text: str) -> str:
    cyrillic = sum(1 for char in text if "а" <= char.lower() <= "я" or char.lower() == "ё")
    latin = sum(1 for char in text if "a" <= char.lower() <= "z")
    if cyrillic == 0 and latin == 0:
        return "unknown"
    if cyrillic >= latin:
        return "ru"
    return "en"


def _text_quality(text: str) -> TextQuality:
    if not text:
        return "empty"
    if len(text.split()) < 2:
        return "too_short"
    return "ok"
