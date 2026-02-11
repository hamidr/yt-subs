Feature: Subtitle download
  As a user
  I want to list and fetch subtitles from YouTube videos
  So that I can get transcripts for summarization

  Scenario: List languages from a video with subtitles
    Given a video with manual and auto subtitles
    When I list available languages
    Then I should get manual subtitles for "en" and "fr"
    And I should get auto subtitles for "en", "es", "nl", "fa", "de", and "ja"

  Scenario: List languages from a video with no subtitles
    Given a video with no subtitles
    When I list available languages
    Then I should get an empty list

  Scenario: Fetch subtitle content
    Given a language with a VTT format URL
    When I fetch the subtitle content
    Then I should get the raw VTT text
