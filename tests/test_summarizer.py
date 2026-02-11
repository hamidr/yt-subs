import json
from unittest.mock import MagicMock, patch

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from yt_subs.summarizer import OllamaSummarizer
from yt_subs.types import DEFAULT_SUMMARIZATION_PROMPT, SummarizationError

scenarios("features/summarization.feature")

SAMPLE_TRANSCRIPT = "Nix is a powerful package manager.\nIt provides reproducible builds."
SAMPLE_SUMMARY = "This video discusses Nix, a powerful package manager for reproducible builds."


@given("a transcript and the default model", target_fixture="summarizer_setup")
def default_model_setup():
    return OllamaSummarizer(), SAMPLE_TRANSCRIPT


@given(
    parsers.parse('a transcript and model "{model}"'),
    target_fixture="summarizer_setup",
)
def custom_model_setup(model):
    return OllamaSummarizer(model=model), SAMPLE_TRANSCRIPT


@given("a transcript and a failing Ollama server", target_fixture="summarizer_setup")
def failing_server_setup():
    return OllamaSummarizer(base_url="http://localhost:99999"), SAMPLE_TRANSCRIPT


@when("I summarize the transcript", target_fixture="summarize_result")
def do_summarize(summarizer_setup):
    summarizer, transcript = summarizer_setup
    captured = {}

    def mock_urlopen(req):
        body = json.loads(req.data.decode("utf-8"))
        captured["model"] = body["model"]
        captured["prompt"] = body["prompt"]

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            {"response": SAMPLE_SUMMARY}
        ).encode("utf-8")
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    with patch("yt_subs.summarizer.urllib.request.urlopen", side_effect=mock_urlopen):
        result = summarizer.summarize(transcript, DEFAULT_SUMMARIZATION_PROMPT)

    return {"result": result, **captured}


@when("I attempt to summarize the transcript", target_fixture="summarize_error")
def do_summarize_failing(summarizer_setup):
    summarizer, transcript = summarizer_setup

    with patch(
        "yt_subs.summarizer.urllib.request.urlopen",
        side_effect=ConnectionError("Connection refused"),
    ):
        with pytest.raises(SummarizationError) as exc_info:
            summarizer.summarize(transcript, DEFAULT_SUMMARIZATION_PROMPT)
    return exc_info


@then(parsers.parse('the summarization request should use model "{model}"'))
def check_model(summarize_result, model):
    assert summarize_result["model"] == model


@then("the response should contain the summary text")
def check_summary_text(summarize_result):
    assert summarize_result["result"] == SAMPLE_SUMMARY


@then("a SummarizationError should be raised")
def check_error_raised(summarize_error):
    assert summarize_error.type is SummarizationError
