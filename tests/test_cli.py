import json
import os
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from yt_subs.cli import main
from yt_subs.types import (
    SubtitleFormat,
    SubtitleLanguage,
    SubtitleSource,
)

from .fixtures.yt_dlp_info import INFO_NO_SUBS, INFO_WITH_SUBS

scenarios("features/cli_validation.feature")

SAMPLE_VTT = """\
WEBVTT
Kind: captions
Language: en

00:00:00.000 --> 00:00:03.000
Hello and welcome

00:00:03.000 --> 00:00:06.000
This is a test
"""

SAMPLE_SUMMARY = "A brief welcome and test video."


def _mock_yt_dlp(info_dict):
    """Create a mock for yt_dlp.YoutubeDL that returns the given info dict."""
    mock_ydl = MagicMock()
    mock_ydl.extract_info.return_value = info_dict
    mock_cls = MagicMock()
    mock_cls.return_value.__enter__ = MagicMock(return_value=mock_ydl)
    mock_cls.return_value.__exit__ = MagicMock(return_value=False)
    return mock_cls


def _mock_urlopen_vtt(req_or_url):
    """Mock urlopen to return sample VTT content."""
    mock_resp = MagicMock()
    if hasattr(req_or_url, "data"):
        # Ollama API call
        mock_resp.read.return_value = json.dumps(
            {"response": SAMPLE_SUMMARY}
        ).encode("utf-8")
    else:
        # Subtitle fetch
        mock_resp.read.return_value = SAMPLE_VTT.encode("utf-8")
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ── Steps ─────────────────────────────────────────────────────────────


@when("I run the CLI with no arguments", target_fixture="cli_result")
def run_no_args(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([])
    captured = capsys.readouterr()
    return {"exit_code": exc_info.value.code, "stderr": captured.err, "stdout": captured.out}


@given("a video with available subtitles", target_fixture="video_info")
def video_with_subs():
    return INFO_WITH_SUBS


@given("a video with no subtitles available", target_fixture="video_info")
def video_no_subs():
    return INFO_NO_SUBS


@when(
    parsers.parse('I run the CLI with "-l en" and a URL'),
    target_fixture="cli_result",
)
def run_with_lang(video_info, capsys):
    captured_model = {}

    def mock_urlopen(req_or_url):
        resp = _mock_urlopen_vtt(req_or_url)
        if hasattr(req_or_url, "data"):
            body = json.loads(req_or_url.data.decode("utf-8"))
            captured_model["model"] = body["model"]
        return resp

    env = os.environ.copy()
    env.pop("YT_SUBS_MODEL", None)

    with (
        patch("yt_subs.subtitles.yt_dlp.YoutubeDL", _mock_yt_dlp(video_info)),
        patch("yt_subs.subtitles.urllib.request.urlopen", side_effect=mock_urlopen),
        patch("yt_subs.summarizer.urllib.request.urlopen", side_effect=mock_urlopen),
        patch.dict(os.environ, env, clear=True),
    ):
        exit_code = main(["-l", "en", "https://youtube.com/watch?v=test"])

    captured = capsys.readouterr()
    return {
        "exit_code": exit_code,
        "stdout": captured.out,
        "stderr": captured.err,
        "model": captured_model.get("model"),
    }


@when(
    parsers.parse('I run the CLI with "-l en", a URL, and YT_SUBS_MODEL="{model}"'),
    target_fixture="cli_result",
)
def run_with_custom_model(video_info, model, capsys):
    captured_model = {}

    def mock_urlopen(req_or_url):
        resp = _mock_urlopen_vtt(req_or_url)
        if hasattr(req_or_url, "data"):
            body = json.loads(req_or_url.data.decode("utf-8"))
            captured_model["model"] = body["model"]
        return resp

    with (
        patch("yt_subs.subtitles.yt_dlp.YoutubeDL", _mock_yt_dlp(video_info)),
        patch("yt_subs.subtitles.urllib.request.urlopen", side_effect=mock_urlopen),
        patch("yt_subs.summarizer.urllib.request.urlopen", side_effect=mock_urlopen),
        patch.dict(os.environ, {"YT_SUBS_MODEL": model}),
    ):
        exit_code = main(["-l", "en", "https://youtube.com/watch?v=test"])

    captured = capsys.readouterr()
    return {
        "exit_code": exit_code,
        "stdout": captured.out,
        "stderr": captured.err,
        "model": captured_model.get("model"),
    }


@when(
    parsers.parse('I run the CLI with "-l xx" and a URL'),
    target_fixture="cli_result",
)
def run_with_bad_lang(video_info, capsys):
    with patch("yt_subs.subtitles.yt_dlp.YoutubeDL", _mock_yt_dlp(video_info)):
        exit_code = main(["-l", "xx", "https://youtube.com/watch?v=test"])

    captured = capsys.readouterr()
    return {
        "exit_code": exit_code,
        "stdout": captured.out,
        "stderr": captured.err,
    }


@when(
    "I run the CLI with no -l flag and a URL",
    target_fixture="cli_result",
)
def run_no_lang_no_subs(video_info, capsys):
    with patch("yt_subs.subtitles.yt_dlp.YoutubeDL", _mock_yt_dlp(video_info)):
        exit_code = main(["https://youtube.com/watch?v=test"])

    captured = capsys.readouterr()
    return {
        "exit_code": exit_code,
        "stdout": captured.out,
        "stderr": captured.err,
    }


@then("the exit code should be non-zero")
def check_nonzero_exit(cli_result):
    assert cli_result["exit_code"] != 0


@then(parsers.parse("the exit code should be {code:d}"))
def check_exit_code(cli_result, code):
    assert cli_result["exit_code"] == code


@then(parsers.parse('the output should contain "{text}"'))
def check_output_contains(cli_result, text):
    combined = cli_result.get("stdout", "") + cli_result.get("stderr", "")
    assert text.lower() in combined.lower(), f"Expected '{text}' in output, got: {combined!r}"


@then(parsers.parse('the error output should contain "{text}"'))
def check_error_contains(cli_result, text):
    assert text in cli_result["stderr"], (
        f"Expected '{text}' in stderr, got: {cli_result['stderr']!r}"
    )


@then(parsers.parse('the summarizer should use model "{model}"'))
def check_model_used(cli_result, model):
    assert cli_result.get("model") == model
