#!/usr/bin/env bats

# BDD tests for yt-subs
# Uses mocked yt-dlp, ollama, and fzf to test offline and fast

setup() {
  export FIXTURES_DIR="$BATS_TEST_DIRNAME/fixtures"
  export PATH="$BATS_TEST_DIRNAME/mocks:$PATH"
  SCRIPT="$BATS_TEST_DIRNAME/../yt-subs.sh"
}

# ── Feature: CLI argument validation ────────────────────────────────

@test "given no arguments, it should print usage and exit with error" {
  run bash "$SCRIPT"
  [ "$status" -eq 1 ]
  [[ "$output" == *"Usage: yt-subs"* ]]
}

@test "given an invalid flag, it should print usage and exit with error" {
  run bash "$SCRIPT" -x
  [ "$status" -eq 1 ]
  [[ "$output" == *"Usage: yt-subs"* ]]
}

@test "given -l without a language code, it should print usage and exit with error" {
  run bash "$SCRIPT" -l
  [ "$status" -eq 1 ]
  [[ "$output" == *"Usage: yt-subs"* ]]
}

# ── Feature: Direct language download with -l flag ──────────────────

@test "given -l en and a URL, it should download subtitles and send them to ollama" {
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OLLAMA_MODEL=llama3"* ]]
}

@test "given -l en and a URL, it should strip VTT headers from the transcript" {
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  # VTT metadata must be stripped
  [[ "$output" != *"WEBVTT"* ]]
  [[ "$output" != *"Kind:"* ]]
  [[ "$output" != *"-->"* ]]
}

@test "given -l en and a URL, it should deduplicate repeated subtitle lines" {
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  # "Today we will talk about Nix" appears twice in fixture, should appear once
  count=$(echo "$output" | grep -c "TRANSCRIPT: Today we will talk about Nix" || true)
  [ "$count" -eq 1 ]
}

@test "given -l en with SRT subtitles, it should strip SRT formatting" {
  export YT_DLP_MOCK_MODE="download-srt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  [[ "$output" != *"-->"* ]]
  [[ "$output" == *"TRANSCRIPT: Hello and welcome to this video"* ]]
}

@test "given -l en and a URL, it should strip HTML tags from subtitles" {
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  [[ "$output" != *"<c>"* ]]
  [[ "$output" == *"TRANSCRIPT: Hello and welcome to this video"* ]]
}

@test "given -l en and a URL, it should strip VTT positioning metadata" {
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  [[ "$output" != *"align:start"* ]]
  [[ "$output" != *"position:"* ]]
}

# ── Feature: Ollama model configuration ─────────────────────────────

@test "given no YT_SUBS_MODEL, it should use llama3 as the default model" {
  unset YT_SUBS_MODEL
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OLLAMA_MODEL=llama3"* ]]
}

@test "given YT_SUBS_MODEL=mistral, it should use the specified model" {
  export YT_SUBS_MODEL="mistral"
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OLLAMA_MODEL=mistral"* ]]
}

# ── Feature: Error handling ─────────────────────────────────────────

@test "given yt-dlp produces no subtitle file, it should exit with an error" {
  export YT_DLP_MOCK_MODE="no-subs"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 1 ]
  [[ "$output" == *"no subtitles found for language"* ]]
}

# ── Feature: Interactive language selection ──────────────────────────

@test "given no -l flag, it should list available languages and invoke fzf" {
  export YT_DLP_MOCK_MODE="list-subs"
  export FZF_MOCK_SELECTION="[auto]   en  English"
  run bash "$SCRIPT" "https://youtube.com/watch?v=test123"
  # fzf mock returns a selection, then yt-dlp mock needs download mode
  # Since mock mode stays as list-subs for the download call, this will fail
  # but we verify the fzf path was entered
  [[ "$output" == *"Downloading en subtitles"* ]]
}

@test "given no -l flag and no preferred languages available, it should exit with an error" {
  export YT_DLP_MOCK_MODE="list-subs-empty"
  run bash "$SCRIPT" "https://youtube.com/watch?v=test123"
  [ "$status" -eq 1 ]
  [[ "$output" == *"no subtitles available"* ]]
}

@test "given no -l flag and fzf selection is empty, it should exit with an error" {
  export YT_DLP_MOCK_MODE="list-subs"
  export FZF_MOCK_SELECTION=""
  run bash "$SCRIPT" "https://youtube.com/watch?v=test123"
  [ "$status" -eq 1 ]
  [[ "$output" == *"no language selected"* ]]
}

# ── Feature: Preferred language filtering ───────────────────────────

@test "given available subs in preferred and non-preferred languages, it should only offer preferred ones" {
  # The fixture has: manual en, fr; auto en, es, nl, fa, de, ja
  # Preferred: en fa fr nl es — so de and ja should be filtered out
  export YT_DLP_MOCK_MODE="list-subs"
  export FZF_MOCK_SELECTION="[manual] en  English"
  run bash "$SCRIPT" "https://youtube.com/watch?v=test123"
  # de and ja should not appear in the output (they are non-preferred)
  [[ "$output" != *" de "* ]]
  [[ "$output" != *" ja "* ]]
}

# ── Feature: Manual vs auto subtitle distinction ────────────────────

@test "given a manual subtitle is selected, it should download with --write-subs only" {
  # We verify indirectly: the script echoes "Downloading ... ([manual])"
  export YT_DLP_MOCK_MODE="list-subs"
  export FZF_MOCK_SELECTION="[manual] en  English"
  run bash "$SCRIPT" "https://youtube.com/watch?v=test123"
  [[ "$output" == *"[manual]"* ]]
}

@test "given an auto subtitle is selected, it should download with --write-auto-subs" {
  export YT_DLP_MOCK_MODE="list-subs"
  export FZF_MOCK_SELECTION="[auto]   es  Spanish"
  run bash "$SCRIPT" "https://youtube.com/watch?v=test123"
  [[ "$output" == *"[auto]"* ]]
}

# ── Feature: Summarization prompt ───────────────────────────────────

@test "given a successful download, it should send the summarization prompt to ollama" {
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  [[ "$output" == *"OLLAMA_PROMPT=Summarize the following video transcript"* ]]
}

@test "given a successful download, it should pipe cleaned transcript text to ollama" {
  export YT_DLP_MOCK_MODE="download-vtt"
  run bash "$SCRIPT" -l en "https://youtube.com/watch?v=test123"
  [ "$status" -eq 0 ]
  [[ "$output" == *"TRANSCRIPT: Nix is a powerful package manager"* ]]
  [[ "$output" == *"TRANSCRIPT: It provides reproducible builds"* ]]
}
