Feature: Subtitle cleaning
  As a user viewing a transcript
  I want VTT/SRT formatting stripped and duplicates removed
  So that I get clean, readable text

  Scenario: Strip VTT metadata headers
    Given a VTT subtitle file
    When I clean the subtitle content
    Then the result should not contain "WEBVTT"
    And the result should not contain "Kind:"
    And the result should not contain "Language:"

  Scenario: Strip timestamp lines
    Given a VTT subtitle file
    When I clean the subtitle content
    Then the result should not contain "-->"

  Scenario: Strip HTML tags
    Given a VTT subtitle file
    When I clean the subtitle content
    Then the result should not contain "<c>"
    And the result should contain "Hello and welcome to this video"

  Scenario: Strip VTT positioning metadata
    Given a VTT subtitle file
    When I clean the subtitle content
    Then the result should not contain "align:start"
    And the result should not contain "position:"

  Scenario: Deduplicate repeated lines
    Given a VTT subtitle file
    When I clean the subtitle content
    Then "Today we will talk about Nix" should appear exactly 1 time

  Scenario: Strip SRT sequence numbers
    Given an SRT subtitle file
    When I clean the subtitle content
    Then the result should not contain a line that is just a number
    And the result should contain "Hello and welcome to this video"

  Scenario: Produce clean transcript from VTT
    Given a VTT subtitle file
    When I clean the subtitle content
    Then the result should contain "Hello and welcome to this video"
    And the result should contain "Today we will talk about Nix"
    And the result should contain "Nix is a powerful package manager"
    And the result should contain "It provides reproducible builds"
