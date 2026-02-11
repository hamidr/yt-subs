"""Mock yt-dlp extract_info return values for testing."""


def make_info_dict(
    *,
    subtitles: dict | None = None,
    automatic_captions: dict | None = None,
) -> dict:
    """Build a minimal yt-dlp info_dict with subtitle entries.

    Each subtitle entry maps a language code to a list of format dicts
    like: [{"ext": "vtt", "url": "https://..."}, ...]
    """
    return {
        "id": "dQw4w9WgXcQ",
        "title": "Test Video",
        "subtitles": subtitles or {},
        "automatic_captions": automatic_captions or {},
    }


INFO_WITH_SUBS = make_info_dict(
    subtitles={
        "en": [
            {"ext": "vtt", "url": "https://example.com/subs/en.vtt"},
            {"ext": "ttml", "url": "https://example.com/subs/en.ttml"},
        ],
        "fr": [
            {"ext": "vtt", "url": "https://example.com/subs/fr.vtt"},
        ],
    },
    automatic_captions={
        "en": [
            {"ext": "vtt", "url": "https://example.com/auto/en.vtt"},
        ],
        "es": [
            {"ext": "vtt", "url": "https://example.com/auto/es.vtt"},
        ],
        "nl": [
            {"ext": "vtt", "url": "https://example.com/auto/nl.vtt"},
        ],
        "fa": [
            {"ext": "vtt", "url": "https://example.com/auto/fa.vtt"},
        ],
        "de": [
            {"ext": "vtt", "url": "https://example.com/auto/de.vtt"},
        ],
        "ja": [
            {"ext": "vtt", "url": "https://example.com/auto/ja.vtt"},
        ],
    },
)

INFO_NO_SUBS = make_info_dict()
