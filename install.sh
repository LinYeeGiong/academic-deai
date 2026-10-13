#!/usr/bin/env sh
# Install the academic-deai skill for any Agent Skills compatible agent.
#
#   sh install.sh              # auto-detect installed agents, install for each
#   sh install.sh --agents     # portable location only (~/.agents/skills)
#   sh install.sh --claude     # Claude Code only (~/.claude/skills)
#   sh install.sh --project    # this repo's .agents/skills (committed, team-wide)
#   sh install.sh --link       # symlink instead of copy (tracks git pull)
#   sh install.sh --list       # show what would be done, change nothing
#
# Works on Linux, macOS, and Windows (Git Bash / WSL / MSYS).

set -eu

SKILL=academic-deai
SRC=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/skills/$SKILL

MODE=copy
DRY=0
TARGETS=""
AUTO=1

for arg in "$@"; do
  case "$arg" in
    --link)    MODE=link ;;
    --list)    DRY=1 ;;
    --agents)  TARGETS="$TARGETS $HOME/.agents/skills";  AUTO=0 ;;
    --claude)  TARGETS="$TARGETS $HOME/.claude/skills";  AUTO=0 ;;
    --codex)   TARGETS="$TARGETS $HOME/.agents/skills";  AUTO=0 ;;
    --pi)      TARGETS="$TARGETS $HOME/.agents/skills";  AUTO=0 ;;
    --cursor)  TARGETS="$TARGETS $HOME/.cursor/skills";  AUTO=0 ;;
    --gemini)  TARGETS="$TARGETS $HOME/.gemini/skills";  AUTO=0 ;;
    --opencode) TARGETS="$TARGETS $HOME/.config/opencode/skills"; AUTO=0 ;;
    --goose)   TARGETS="$TARGETS $HOME/.config/goose/skills"; AUTO=0 ;;
    --project) TARGETS="$TARGETS $PWD/.agents/skills";    AUTO=0 ;;
    --all)     TARGETS="$TARGETS $HOME/.agents/skills $HOME/.claude/skills"; AUTO=0 ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) printf 'unknown option: %s (try --help)\n' "$arg" >&2; exit 2 ;;
  esac
done

[ -f "$SRC/SKILL.md" ] || { printf 'cannot find %s/SKILL.md\n' "$SRC" >&2; exit 1; }

# Auto-detect: always install to the portable location, plus any agent whose
# config directory already exists.
if [ "$AUTO" -eq 1 ]; then
  TARGETS="$HOME/.agents/skills"
  [ -d "$HOME/.claude" ]           && TARGETS="$TARGETS $HOME/.claude/skills"
  [ -d "$HOME/.cursor" ]           && TARGETS="$TARGETS $HOME/.cursor/skills"
  [ -d "$HOME/.gemini" ]           && TARGETS="$TARGETS $HOME/.gemini/skills"
  [ -d "$HOME/.config/opencode" ]  && TARGETS="$TARGETS $HOME/.config/opencode/skills"
  [ -d "$HOME/.config/goose" ]     && TARGETS="$TARGETS $HOME/.config/goose/skills"
fi

printf 'source: %s\n' "$SRC"
printf 'mode:   %s\n\n' "$MODE"

for base in $TARGETS; do
  dest=$base/$SKILL
  if [ "$DRY" -eq 1 ]; then
    printf '  would install -> %s\n' "$dest"
    continue
  fi

  mkdir -p "$base"
  # Replace any previous install. Remove a symlink itself, never its target.
  if [ -L "$dest" ]; then
    rm -f "$dest"
  elif [ -e "$dest" ]; then
    rm -rf "$dest"
  fi

  if [ "$MODE" = link ]; then
    # Git Bash/MSYS may silently copy on `ln -s`; check what we actually got.
    if ln -s "$SRC" "$dest" 2>/dev/null && [ -L "$dest" ]; then
      printf '  linked  -> %s\n' "$dest"
    else
      rm -rf "$dest"
      cp -R "$SRC" "$dest"
      printf '  copied  -> %s  (symlink unavailable; on Windows use install.ps1 -Link)\n' "$dest"
    fi
  else
    cp -R "$SRC" "$dest"
    printf '  copied  -> %s\n' "$dest"
  fi
done

[ "$DRY" -eq 1 ] && exit 0

cat <<'EOF'

Done. Restart your agent (or run /reload) and invoke the skill:

  Claude Code   /academic-deai
  Codex         $academic-deai
  pi            /skill:academic-deai
  others        ask in plain words, e.g. "帮我把这段去AI化"

Scanner (optional, needs Python 3.9+):
  python <skill dir>/scripts/scan.py <file> --format md
EOF
