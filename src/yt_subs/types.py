from dataclasses import dataclass
from enum import Enum


class SubtitleSource(Enum):
    MANUAL = "manual"
    AUTO = "auto"


@dataclass(frozen=True)
class SubtitleFormat:
    ext: str
    url: str


@dataclass(frozen=True)
class SubtitleLanguage:
    code: str
    name: str
    source: SubtitleSource
    formats: tuple[SubtitleFormat, ...]


@dataclass(frozen=True)
class SubtitleContent:
    language: SubtitleLanguage
    raw_text: str


@dataclass(frozen=True)
class CleanedTranscript:
    language_code: str
    text: str


class YtSubsError(Exception):
    pass


class NoSubtitlesAvailableError(YtSubsError):
    pass


class SubtitleDownloadError(YtSubsError):
    pass


class SummarizationError(YtSubsError):
    pass


DEFAULT_MODEL = "llama3"

DEFAULT_PREFERRED_LANGS = ("en", "fa", "fr", "nl", "es")

DEFAULT_SUMMARIZATION_PROMPT = (
    "Summarize the following video transcript concisely. "
    "Include the key points and main takeaways:"
)
