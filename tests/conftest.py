from pathlib import Path

import pytest

from yt_subs.types import SubtitleFormat, SubtitleLanguage, SubtitleSource

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_vtt_text() -> str:
    return (FIXTURES_DIR / "sample.vtt").read_text()


@pytest.fixture
def sample_srt_text() -> str:
    return (FIXTURES_DIR / "sample.srt").read_text()


@pytest.fixture
def english_manual_language() -> SubtitleLanguage:
    return SubtitleLanguage(
        code="en",
        name="English",
        source=SubtitleSource.MANUAL,
        formats=(
            SubtitleFormat(ext="vtt", url="https://example.com/subs/en.vtt"),
        ),
    )


@pytest.fixture
def english_auto_language() -> SubtitleLanguage:
    return SubtitleLanguage(
        code="en",
        name="English",
        source=SubtitleSource.AUTO,
        formats=(
            SubtitleFormat(ext="vtt", url="https://example.com/auto/en.vtt"),
        ),
    )
