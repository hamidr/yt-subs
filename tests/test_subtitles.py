from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from yt_subs.subtitles import fetch_subtitle_content, filter_preferred, list_languages
from yt_subs.types import (
    SubtitleFormat,
    SubtitleLanguage,
    SubtitleSource,
)

from .fixtures.yt_dlp_info import INFO_NO_SUBS, INFO_WITH_SUBS

scenarios("features/subtitle_download.feature")
scenarios("features/language_selection.feature")


# ── Subtitle download feature ────────────────────────────────────────


@given("a video with manual and auto subtitles", target_fixture="mock_info")
def video_with_subs():
    return INFO_WITH_SUBS


@given("a video with no subtitles", target_fixture="mock_info")
def video_with_no_subs():
    return INFO_NO_SUBS


@when("I list available languages", target_fixture="languages")
def do_list_languages(mock_info):
    with patch("yt_subs.subtitles.yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_cls.return_value.__exit__ = MagicMock(return_value=False)
        return list_languages("https://youtube.com/watch?v=test")


@then('I should get manual subtitles for "en" and "fr"')
def check_manual_subs(languages):
    manual = [l for l in languages if l.source == SubtitleSource.MANUAL]
    codes = {l.code for l in manual}
    assert codes == {"en", "fr"}


@then('I should get auto subtitles for "en", "es", "nl", "fa", "de", and "ja"')
def check_auto_subs(languages):
    auto = [l for l in languages if l.source == SubtitleSource.AUTO]
    codes = {l.code for l in auto}
    assert codes == {"en", "es", "nl", "fa", "de", "ja"}


@then("I should get an empty list")
def check_empty_list(languages):
    assert languages == []


@given("a language with a VTT format URL", target_fixture="fetch_language")
def language_with_vtt_url():
    return SubtitleLanguage(
        code="en",
        name="English",
        source=SubtitleSource.MANUAL,
        formats=(
            SubtitleFormat(ext="vtt", url="https://example.com/subs/en.vtt"),
        ),
    )


@when("I fetch the subtitle content", target_fixture="fetched_content")
def do_fetch_content(fetch_language, sample_vtt_text):
    with patch("yt_subs.subtitles.urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = sample_vtt_text.encode("utf-8")
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        return fetch_subtitle_content(fetch_language)


@then("I should get the raw VTT text")
def check_raw_vtt(fetched_content, sample_vtt_text):
    assert fetched_content.raw_text == sample_vtt_text
    assert fetched_content.language.code == "en"


# ── Language selection feature ────────────────────────────────────────


@given(
    "a list of subtitle languages including preferred and non-preferred",
    target_fixture="all_languages",
)
def all_languages_fixture():
    with patch("yt_subs.subtitles.yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = INFO_WITH_SUBS
        mock_ydl_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_cls.return_value.__exit__ = MagicMock(return_value=False)
        return list_languages("https://youtube.com/watch?v=test")


@when(
    parsers.parse('I filter to preferred languages "{langs}"'),
    target_fixture="filtered",
)
def do_filter(all_languages, langs):
    preferred = tuple(l.strip() for l in langs.split(","))
    return filter_preferred(all_languages, preferred)


@then(parsers.parse('I should only get languages with codes "{codes}"'))
def check_filtered_codes(filtered, codes):
    expected = {c.strip() for c in codes.split(",")}
    actual = {l.code for l in filtered}
    assert actual <= expected, f"Got unexpected codes: {actual - expected}"


@then(parsers.parse('"{code}" should not be in the results'))
def code_not_in_results(filtered, code):
    codes = {l.code for l in filtered}
    assert code not in codes
