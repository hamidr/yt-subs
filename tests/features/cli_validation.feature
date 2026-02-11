Feature: CLI argument validation
  As a user
  I want clear error messages for invalid CLI usage
  So that I know how to use the tool correctly

  Scenario: No arguments prints usage and exits with error
    When I run the CLI with no arguments
    Then the exit code should be non-zero
    And the output should contain "usage"

  Scenario: Direct language download with -l flag
    Given a video with available subtitles
    When I run the CLI with "-l en" and a URL
    Then the exit code should be 0
    And the summarizer should use model "llama3"

  Scenario: Custom model via environment variable
    Given a video with available subtitles
    When I run the CLI with "-l en", a URL, and YT_SUBS_MODEL="mistral"
    Then the summarizer should use model "mistral"

  Scenario: No subtitles found for specified language
    Given a video with available subtitles
    When I run the CLI with "-l xx" and a URL
    Then the exit code should be 1
    And the error output should contain "no subtitles found for language"

  Scenario: No subtitles available at all
    Given a video with no subtitles available
    When I run the CLI with no -l flag and a URL
    Then the exit code should be 1
    And the error output should contain "no subtitles available"
