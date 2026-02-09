#!/usr/bin/env bash

set -eo pipefail

MODEL="${YT_SUBS_MODEL:-llama3}"
LANG_FLAG=""
sub_type=""
PREFERRED_LANGS="en fa fr nl es"

usage() {
	echo "Usage: yt-subs [-l <lang>] <youtube-url>" >&2
	echo "  -l <lang>  Subtitle language code (e.g. en, es, fr)" >&2
	echo "             If omitted, shows interactive language picker (requires fzf)" >&2
	echo "Set YT_SUBS_MODEL to override the ollama model (default: llama3)" >&2
	exit 1
}

while getopts ":l:" opt; do
	case $opt in
	l) LANG_FLAG="$OPTARG" ;;
	*) usage ;;
	esac
done
shift $((OPTIND - 1))

if [ -z "${1:-}" ]; then
	usage
fi

URL="$1"
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

if [ -z "$LANG_FLAG" ]; then
	# Fetch available subtitles and let user pick
	sub_list=$(yt-dlp --list-subs --skip-download "$URL" 2>&1)

	# Parse manual and auto-generated subtitle languages
	langs=""
	section=""
	while IFS= read -r line; do
		case "$line" in
		*"Available subtitles"*) section="manual" ;;
		*"Available automatic captions"*) section="auto" ;;
		*)
			if [ -n "$section" ]; then
				code=$(echo "$line" | awk '{print $1}')
				name=$(echo "$line" | awk '{$1=""; $NF=""; sub(/^ +/, ""); sub(/ +$/, ""); print}')
				# skip header lines and empty codes
				case "$code" in
				Language | "" | --*) continue ;;
				esac
				if [ "$section" = "manual" ]; then
					langs+="[manual] $code  $name"$'\n'
				else
					langs+="[auto]   $code  $name"$'\n'
				fi
			fi
			;;
		esac
	done <<<"$sub_list"

	# Filter to preferred languages only
	filtered=""
	while IFS= read -r entry; do
		code=$(echo "$entry" | awk '{print $2}')
		for pl in $PREFERRED_LANGS; do
			if [ "$code" = "$pl" ]; then
				filtered+="$entry"$'\n'
				break
			fi
		done
	done <<<"$langs"
	langs="$filtered"

	if [ -z "$langs" ]; then
		echo "error: no subtitles available for this video." >&2
		exit 1
	fi

	if ! command -v fzf &>/dev/null; then
		echo "error: fzf is required for interactive language selection." >&2
		echo "Install fzf or use -l <lang> to specify a language." >&2
		exit 1
	fi

	selection=$(echo -n "$langs" | fzf --prompt="Select subtitle language: " --height=~40%)
	if [ -z "$selection" ]; then
		echo "error: no language selected." >&2
		exit 1
	fi

	sub_type=$(echo "$selection" | awk '{print $1}')
	LANG_FLAG=$(echo "$selection" | awk '{print $2}')

	echo "Downloading $LANG_FLAG subtitles ($sub_type)..."
fi

if [ "$sub_type" = "[manual]" ]; then
	yt-dlp --skip-download --write-subs --sub-lang "$LANG_FLAG" \
		--no-warnings -q -o "$tmpdir/%(title)s.%(ext)s" "$URL"
else
	yt-dlp --skip-download --write-auto-subs --write-subs --sub-lang "$LANG_FLAG" \
		--no-warnings -q -o "$tmpdir/%(title)s.%(ext)s" "$URL"
fi

sub_file=$(find "$tmpdir" -type f | head -1)

if [ -z "$sub_file" ]; then
	echo "error: no subtitles found for language '$LANG_FLAG'." >&2
	exit 1
fi

# Strip VTT/SRT formatting to plain text
clean_text=$(sed -e '/^WEBVTT/d' \
	-e '/^Kind:/d' \
	-e '/^Language:/d' \
	-e '/^NOTE/d' \
	-e '/^[0-9][0-9]*$/d' \
	-e '/-->/d' \
	-e 's/<[^>]*>//g' \
	-e 's/align:start position:[0-9%]*//g' \
	-e 's/\b[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9]*\b//g' \
	-e '/^[[:space:]]*$/d' \
	"$sub_file" | awk '{
	# trim leading/trailing whitespace
	gsub(/^[[:space:]]+|[[:space:]]+$/, "")
	if ($0 == "") next
	if (!seen[$0]++) print
}')

echo "$clean_text" | ollama run "$MODEL" \
	"Summarize the following video transcript concisely. Include the key points and main takeaways:"
