#!/bin/sh
# Explicitly update to the current main revision. This trusts the latest
# repository content, unlike the pinned entrypoint in install.sh.
set -eu

origin=https://github.com/rocker-code/my-ai-skills.git
ref=refs/heads/main
result=$(git ls-remote --exit-code "$origin" "$ref")
set -- $result
if [ "$#" -ne 2 ] || [ "$2" != "$ref" ]; then
    echo 'Could not resolve the current main revision.' >&2
    exit 1
fi
revision=$1
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
sh "$tmp" --revision "$revision"
