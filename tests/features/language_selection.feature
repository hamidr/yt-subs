Feature: Language selection
  As a user
  I want to filter subtitles to my preferred languages
  So that I only see relevant options

  Scenario: Filter to preferred languages
    Given a list of subtitle languages including preferred and non-preferred
    When I filter to preferred languages "en", "fa", "fr", "nl", "es"
    Then I should only get languages with codes "en", "fa", "fr", "nl", "es"
    And "de" should not be in the results
    And "ja" should not be in the results
