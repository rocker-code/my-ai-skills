#!/bin/sh
# Convenience launcher. Verify the downloaded installer before running it.
# This cannot verify the launcher itself when it is fetched and piped to sh.
set -eu

entry_revision=57733e891659174b79c772fb4f16d8b47fe6c93c
entry_sha256=07caf29cb6a331fbb00310a3e3df836834b8f55aa89059f28032f6f8a8215fa1
revision=$entry_revision

if [ "$#" -ne 0 ]; then
    if [ "$#" -ne 2 ] || [ "$1" != --revision ]; then
        echo 'Usage: sh install.sh [--revision FULL_GIT_SHA]' >&2
        exit 2
    fi
    revision=$2
    case "$revision" in
        *[!0-9a-f]*) echo 'Revision must be a full lowercase Git SHA.' >&2; exit 2 ;;
    esac
    if [ "${#revision}" -ne 40 ]; then
        echo 'Revision must be a full 40-character Git SHA.' >&2
        exit 2
    fi
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
