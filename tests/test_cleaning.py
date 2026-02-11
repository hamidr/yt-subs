import re

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from yt_subs.cleaning import clean_subtitle
from yt_subs.types import CleanedTranscript, SubtitleContent, SubtitleLanguage

scenarios("features/subtitle_cleaning.feature")


@given("a VTT subtitle file", target_fixture="subtitle_content")
def vtt_content(sample_vtt_text, english_manual_language):
    return SubtitleContent(language=english_manual_language, raw_text=sample_vtt_text)


@given("an SRT subtitle file", target_fixture="subtitle_content")
def srt_content(sample_srt_text, english_manual_language):
    return SubtitleContent(language=english_manual_language, raw_text=sample_srt_text)


@when("I clean the subtitle content", target_fixture="cleaned")
def clean_content(subtitle_content):
    return clean_subtitle(subtitle_content)


@then(parsers.parse('the result should not contain "{text}"'))
def result_should_not_contain(cleaned, text):
    assert text not in cleaned.text


@then(parsers.parse('the result should contain "{text}"'))
def result_should_contain(cleaned, text):
    assert text in cleaned.text


@then(parsers.parse('"{text}" should appear exactly {count:d} time'))
def text_appears_n_times(cleaned, text, count):
    actual = cleaned.text.splitlines().count(text)
    assert actual == count, f"Expected '{text}' {count} time(s), found {actual}"


@then("the result should not contain a line that is just a number")
def no_bare_number_lines(cleaned):
    for line in cleaned.text.splitlines():
        assert not re.match(r"^\d+$", line.strip()), f"Found bare number line: {line!r}"
