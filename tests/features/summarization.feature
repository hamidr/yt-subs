Feature: Summarization
  As a user
  I want to summarize a transcript using Ollama
  So that I get a concise overview of the video content

  Scenario: Summarize with default model
    Given a transcript and the default model
    When I summarize the transcript
    Then the summarization request should use model "llama3"
    And the response should contain the summary text

  Scenario: Summarize with custom model
    Given a transcript and model "mistral"
    When I summarize the transcript
    Then the summarization request should use model "mistral"

  Scenario: Handle Ollama connection failure
    Given a transcript and a failing Ollama server
    When I attempt to summarize the transcript
    Then a SummarizationError should be raised
