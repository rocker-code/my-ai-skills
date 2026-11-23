#!/bin/sh
# Explicitly update to the current main revision via the same verified
# installer entrypoint used by install.sh.
set -eu

resolve_main() (
    origin=https://github.com/rocker-code/my-ai-skills.git
    ref=refs/heads/main
    result=$(git ls-remote --exit-code "$origin" "$ref")
    set -- $result
    if [ "$#" -ne 2 ] || [ "$2" != "$ref" ]; then
        echo 'Could not resolve the current main revision.' >&2
        exit 1
    fi
    printf '%s\n' "$1"
)
option=
for argument do
    if [ "$option" = --agent ]; then
        case "$argument" in opencode|codex) : ;; *) echo 'Supported agents: opencode, codex.' >&2; exit 2 ;; esac
        option=
    elif [ "$argument" = --agent ]; then
        option=--agent
    else
        echo 'Usage: sh update.sh [--agent opencode|codex ...]' >&2
        exit 2
    fi
done
[ -z "$option" ] || { echo 'Missing --agent value.' >&2; exit 2; }
revision=$(resolve_main)
case "$revision" in
    *[!0-9a-f]*) echo 'Invalid main revision.' >&2; exit 1 ;;
esac
if [ "${#revision}" -ne 40 ]; then
    echo 'Invalid main revision.' >&2
    exit 1
fi

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT HUP INT TERM
curl -fsSL "https://raw.githubusercontent.com/rocker-code/my-ai-skills/$revision/scripts/install.sh" -o "$tmp"
sh "$tmp" --revision "$revision" "$@"
