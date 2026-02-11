import json
import urllib.request
from typing import Protocol

from .types import DEFAULT_MODEL, SummarizationError


class Summarizer(Protocol):
    def summarize(self, transcript: str, prompt: str) -> str: ...


class OllamaSummarizer:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = "http://localhost:11434",
    ):
        self._model = model
        self._base_url = base_url

    @property
    def model(self) -> str:
        return self._model

    def summarize(self, transcript: str, prompt: str) -> str:
        full_prompt = f"{prompt}\n\n{transcript}"
        payload = json.dumps({
            "model": self._model,
            "prompt": full_prompt,
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self._base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body["response"]
        except Exception as exc:
            raise SummarizationError(
                f"Ollama summarization failed: {exc}"
            ) from exc
