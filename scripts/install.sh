#!/bin/sh
# Convenience launcher. Verify the downloaded installer before running it.
# This cannot verify the launcher itself when it is fetched and piped to sh.
set -eu

entry_revision=c48ac58beadc0a9712f59f60458a5c3df3ed5bfb
entry_sha256=0e6103f3be6f1797978dba6bf09fd9485acf75346b4e9803ec271cd167cd75ed

if [ "$#" -eq 0 ]; then
    ref=refs/heads/main
    result=$(git ls-remote --exit-code https://github.com/rocker-code/my-ai-skills.git "$ref")
    set -- $result
    if [ "$#" -ne 2 ] || [ "$2" != "$ref" ]; then
        echo 'Could not resolve the current main revision.' >&2
        exit 1
    fi
    revision=$1
else
    if [ "$#" -ne 2 ] || [ "$1" != --revision ]; then
        echo 'Usage: sh install.sh [--revision FULL_GIT_SHA]' >&2
        exit 2
    fi
    revision=$2
fi
case "$revision" in
    *[!0-9a-f]*) echo 'Revision must be a full lowercase Git SHA.' >&2; exit 2 ;;
esac
if [ "${#revision}" -ne 40 ]; then
    echo 'Revision must be a full 40-character Git SHA.' >&2
    exit 2
fi

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT HUP INT TERM
curl -fsSL "https://raw.githubusercontent.com/rocker-code/my-ai-skills/$entry_revision/scripts/install-global" -o "$tmp"
python3 -c 'import hashlib,sys;sys.exit(0 if hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()==sys.argv[2] else 1)' "$tmp" "$entry_sha256" || {
    echo 'Installer SHA-256 mismatch; refusing to execute.' >&2
    exit 1
}
python3 "$tmp" --revision "$revision" --agent opencode

data=${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active
skills=${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills
if ! test -f "$data/manifest.json" || ! test -x "$data/scripts/worktree-reservation" ||
   ! test -f "$skills/apply-issue/SKILL.md" || ! openspec --version; then
    echo 'Post-install verification failed; inspect the installer output and active installation.' >&2
    exit 1
fi
echo 'Post-install verification passed (package, skill and OpenSpec).'
