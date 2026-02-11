import argparse
import os
import sys

from .cleaning import clean_subtitle
from .subtitles import (
    fetch_subtitle_content,
    filter_preferred,
    list_languages,
)
from .summarizer import OllamaSummarizer, Summarizer
from .types import (
    DEFAULT_MODEL,
    DEFAULT_PREFERRED_LANGS,
    DEFAULT_SUMMARIZATION_PROMPT,
    NoSubtitlesAvailableError,
    SubtitleLanguage,
    SubtitleSource,
    YtSubsError,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yt-subs",
        description="Download YouTube subtitles and summarize with Ollama",
    )
    parser.add_argument(
        "-l",
        metavar="LANG",
        dest="lang",
        help="Subtitle language code (e.g. en, es, fr). "
        "If omitted, shows interactive language picker.",
    )
    parser.add_argument("url", help="YouTube video URL")
    return parser


def _format_language_entry(lang: SubtitleLanguage) -> str:
    source_tag = "[manual]" if lang.source == SubtitleSource.MANUAL else "[auto]  "
    return f"{source_tag} {lang.code}  {lang.name}"


def interactive_select(languages: list[SubtitleLanguage]) -> SubtitleLanguage | None:
    """Present a numbered menu on stderr and return the selected language."""
    print("Select subtitle language:", file=sys.stderr)
    for i, lang in enumerate(languages, 1):
        print(f"  {i}) {_format_language_entry(lang)}", file=sys.stderr)

    print(file=sys.stderr)
    try:
        choice = input("Enter number: ")
    except (EOFError, KeyboardInterrupt):
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(languages):
            return languages[idx]
    except ValueError:
        pass

    return None


def _find_language_by_code(
    languages: list[SubtitleLanguage], code: str
) -> SubtitleLanguage | None:
    """Find first matching language by code, preferring manual over auto."""
    manual = [l for l in languages if l.code == code and l.source == SubtitleSource.MANUAL]
    if manual:
        return manual[0]
    auto = [l for l in languages if l.code == code and l.source == SubtitleSource.AUTO]
    if auto:
        return auto[0]
    return None


def main(argv: list[str] | None = None, summarizer: Summarizer | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    model = os.environ.get("YT_SUBS_MODEL", DEFAULT_MODEL)

    try:
        languages = list_languages(args.url)
    except Exception as exc:
        print(f"error: failed to fetch video info: {exc}", file=sys.stderr)
        return 1

    if args.lang:
        selected = _find_language_by_code(languages, args.lang)
        if selected is None:
            print(
                f"error: no subtitles found for language '{args.lang}'.",
                file=sys.stderr,
            )
            return 1
    else:
        preferred = filter_preferred(languages, DEFAULT_PREFERRED_LANGS)
        if not preferred:
            print("error: no subtitles available for this video.", file=sys.stderr)
            return 1

        selected = interactive_select(preferred)
        if selected is None:
            print("error: no language selected.", file=sys.stderr)
            return 1

    source_tag = "[manual]" if selected.source == SubtitleSource.MANUAL else "[auto]"
    print(f"Downloading {selected.code} subtitles ({source_tag})...", file=sys.stderr)

    try:
        content = fetch_subtitle_content(selected)
    except YtSubsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    transcript = clean_subtitle(content)

    if summarizer is None:
        summarizer = OllamaSummarizer(model=model)

    try:
        summary = summarizer.summarize(transcript.text, DEFAULT_SUMMARIZATION_PROMPT)
    except YtSubsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(summary)
    return 0


def entrypoint() -> None:
    sys.exit(main())
