#!/bin/sh
# Convenience launcher. Verify the downloaded installer before running it.
# This cannot verify the launcher itself when it is fetched and piped to sh.
set -eu

entry_revision=06139455da07e336d6969b66f90194afeb9302b8
entry_sha256=c8d4a9cc367fc40b754374c2fa7e774bd288db1a3806d645835eb65922d195f7

resolve_main() (
    ref=refs/heads/main
    result=$(git ls-remote --exit-code https://github.com/rocker-code/my-ai-skills.git "$ref")
    set -- $result
    if [ "$#" -ne 2 ] || [ "$2" != "$ref" ]; then
        echo 'Could not resolve the current main revision.' >&2
        exit 1
    fi
    printf '%s\n' "$1"
)

revision=
have_revision=false
option=
for argument do
    case "$option" in
        --revision)
            [ "$have_revision" = false ] || { echo 'Duplicate --revision.' >&2; exit 2; }
            revision=$argument; have_revision=true; option=
            ;;
        --agent)
            case "$argument" in opencode|codex) : ;; *) echo 'Supported agents: opencode, codex.' >&2; exit 2 ;; esac
            option=
            ;;
        '')
            case "$argument" in
                --revision|--agent) option=$argument ;;
                *) echo 'Usage: sh install.sh [--revision FULL_GIT_SHA] [--agent opencode|codex ...]' >&2; exit 2 ;;
            esac
            ;;
    esac
done
if [ -n "$option" ]; then
    echo "Missing value for $option." >&2
    exit 2
fi
if [ "$have_revision" = false ]; then
    revision=$(resolve_main)
    set -- "$@" --revision "$revision"
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
python3 "$tmp" "$@"

data=${XDG_DATA_HOME:-$HOME/.local/share}/my-ai-skills/active
if ! test -f "$data/manifest.json" || ! test -x "$data/scripts/worktree-reservation" ||
   ! python3 -c '
import json,pathlib,sys
active=pathlib.Path(sys.argv[1])
record=json.loads((active.parent/"guidance.json").read_text())
assert record["schema"] == 2 and record["agents"]
for agent,entry in record["agents"].items():
    assert agent in ("opencode","codex")
    skill=pathlib.Path(entry["skills"])/"apply-issue"
    assert skill.is_symlink() and skill.resolve() == (active/"skills/apply-issue").resolve()
    assert (skill/"SKILL.md").is_file() and pathlib.Path(entry["instructions"]).is_file()
' "$data" || ! openspec --version ||
   ! test -x "$HOME/.local/bin/worktree-reservation" ||
   [ "$(command -v worktree-reservation || :)" != "$HOME/.local/bin/worktree-reservation" ] ||
   ! worktree-reservation --help >/dev/null; then
    echo 'Post-install verification failed; inspect the installer output and active installation.' >&2
    exit 1
fi
echo 'Post-install verification passed (package, skill, OpenSpec and global command).'
