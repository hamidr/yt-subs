# yt-subs

Download YouTube subtitles and summarize them with Ollama.

## Features

- Download manual or auto-generated subtitles from any YouTube video
- Interactive language picker with fzf (filtered to preferred languages)
- Strips VTT/SRT formatting, HTML tags, timestamps, and duplicate lines
- Sends cleaned transcript to a local Ollama model for summarization
- Configurable model via `YT_SUBS_MODEL` environment variable

## Installation

### Nix (standalone)

```bash
# Run directly
nix run github:hamid/yt-subs

# Install to profile
nix profile install github:hamid/yt-subs
```

### As a flake input

```nix
{
  inputs.yt-subs.url = "github:hamid/yt-subs";

  # Use the package
  # inputs.yt-subs.packages.${system}.default

  # Or use the overlay
  # overlays = [ inputs.yt-subs.overlays.default ];
  # then: pkgs.yt-subs
}
```

## Usage

```bash
# Specify a language directly
yt-subs -l en https://youtube.com/watch?v=VIDEO_ID

# Interactive language picker (requires fzf)
yt-subs https://youtube.com/watch?v=VIDEO_ID

# Use a different Ollama model
YT_SUBS_MODEL=mistral yt-subs -l en https://youtube.com/watch?v=VIDEO_ID
```

### Options

| Flag | Description |
|------|-------------|
| `-l <lang>` | Subtitle language code (e.g. `en`, `es`, `fr`). If omitted, opens an interactive picker. |

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `YT_SUBS_MODEL` | `llama3` | Ollama model to use for summarization |

### Preferred languages

When using the interactive picker, only these languages are shown: `en`, `fa`, `fr`, `nl`, `es`.

## Development

```bash
# Enter dev shell (provides yt-dlp, ollama, fzf, shellcheck, bats)
nix develop

# Run tests
bats test/yt-subs.bats

# Lint
shellcheck yt-subs.sh
```

## License

[GPLv3](LICENSE)
