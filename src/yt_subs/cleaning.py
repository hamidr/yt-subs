import re

from .types import CleanedTranscript, SubtitleContent

_METADATA_RE = re.compile(r"^(WEBVTT|Kind:|Language:|NOTE)")
_TIMESTAMP_RE = re.compile(r".*-->.*")
_SEQ_NUMBER_RE = re.compile(r"^\d+$")
_HTML_TAG_RE = re.compile(r"<[^>]*>")
_POSITIONING_RE = re.compile(r"align:start position:\d+%?")
_INLINE_TIMESTAMP_RE = re.compile(r"\b\d{2}:\d{2}:\d{2}\.\d+\b")


def _is_metadata(line: str) -> bool:
    return bool(_METADATA_RE.match(line))


def _is_timestamp(line: str) -> bool:
    return bool(_TIMESTAMP_RE.match(line))


def _is_seq_number(line: str) -> bool:
    return bool(_SEQ_NUMBER_RE.match(line))


def _strip_tags(line: str) -> str:
    return _HTML_TAG_RE.sub("", line)


def _strip_positioning(line: str) -> str:
    return _POSITIONING_RE.sub("", line)


def _strip_inline_timestamps(line: str) -> str:
    return _INLINE_TIMESTAMP_RE.sub("", line)


def clean_subtitle(content: SubtitleContent) -> CleanedTranscript:
    """Clean VTT/SRT subtitle text into a plain transcript.

    Strips metadata, timestamps, HTML tags, positioning info,
    and deduplicates lines (preserving order).
    """
    seen: set[str] = set()
    lines: list[str] = []

    for raw_line in content.raw_text.splitlines():
        if _is_metadata(raw_line):
            continue
        if _is_timestamp(raw_line):
            continue
        if _is_seq_number(raw_line.strip()):
            continue

        line = _strip_tags(raw_line)
        line = _strip_positioning(line)
        line = _strip_inline_timestamps(line)
        line = line.strip()

        if not line:
            continue
        if line in seen:
            continue

        seen.add(line)
        lines.append(line)

    return CleanedTranscript(
        language_code=content.language.code,
        text="\n".join(lines),
    )
