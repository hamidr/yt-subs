import urllib.request

import yt_dlp

from .types import (
    NoSubtitlesAvailableError,
    SubtitleContent,
    SubtitleDownloadError,
    SubtitleFormat,
    SubtitleLanguage,
    SubtitleSource,
)


def _parse_formats(raw_formats: list[dict]) -> tuple[SubtitleFormat, ...]:
    return tuple(
        SubtitleFormat(ext=f["ext"], url=f["url"])
        for f in raw_formats
        if "ext" in f and "url" in f
    )


def _parse_subtitle_entries(
    entries: dict, source: SubtitleSource
) -> list[SubtitleLanguage]:
    languages = []
    for code, raw_formats in entries.items():
        formats = _parse_formats(raw_formats)
        if formats:
            languages.append(
                SubtitleLanguage(
                    code=code,
                    name=code,
                    source=source,
                    formats=formats,
                )
            )
    return languages


def list_languages(url: str) -> list[SubtitleLanguage]:
    """List all available subtitle languages for a YouTube video.

    Uses yt-dlp to extract subtitle metadata without downloading.
    Returns both manual and auto-generated subtitle languages.
    """
    ydl_opts = {"skip_download": True, "quiet": True, "no_warnings": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    languages = []
    languages.extend(
        _parse_subtitle_entries(info.get("subtitles", {}), SubtitleSource.MANUAL)
    )
    languages.extend(
        _parse_subtitle_entries(
            info.get("automatic_captions", {}), SubtitleSource.AUTO
        )
    )
    return languages


def filter_preferred(
    languages: list[SubtitleLanguage],
    preferred: tuple[str, ...],
) -> list[SubtitleLanguage]:
    """Filter languages to only those in the preferred list."""
    preferred_set = set(preferred)
    return [lang for lang in languages if lang.code in preferred_set]


def fetch_subtitle_content(
    language: SubtitleLanguage, preferred_ext: str = "vtt"
) -> SubtitleContent:
    """Fetch the raw subtitle text for a given language.

    Prefers the format matching preferred_ext, falls back to the first available.
    """
    fmt = next(
        (f for f in language.formats if f.ext == preferred_ext),
        language.formats[0] if language.formats else None,
    )
    if fmt is None:
        raise SubtitleDownloadError(
            f"No formats available for language '{language.code}'"
        )

    try:
        with urllib.request.urlopen(fmt.url) as resp:
            raw_text = resp.read().decode("utf-8")
    except Exception as exc:
        raise SubtitleDownloadError(
            f"Failed to download subtitles for '{language.code}': {exc}"
        ) from exc

    return SubtitleContent(language=language, raw_text=raw_text)
