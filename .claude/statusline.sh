#!/bin/bash
input=$(cat)

# Extract all fields in one jq call
eval "$(echo "$input" | jq -r '
  @sh "MODEL=\(.model.display_name)",
  @sh "SESSION_NAME=\(.session_name // "")",
  @sh "DIR=\(.workspace.current_dir)",
  @sh "PCT=\(.context_window.used_percentage // 0 | floor)",
  @sh "VIM_MODE=\(.vim.mode // "")",
  @sh "WORKTREE=\(.worktree.name // "")",
  @sh "DURATION_MS=\(.cost.total_duration_ms // 0 | floor)",
  @sh "COST=\(.cost.total_cost_usd // 0)"
')"

# Build context bar
FILLED=$((PCT * 10 / 100))
EMPTY=$((10 - FILLED))
BAR=""
[ "$FILLED" -gt 0 ] && BAR=$(printf "%${FILLED}s" | tr ' ' '▓')
[ "$EMPTY" -gt 0 ] && BAR="${BAR}$(printf "%${EMPTY}s" | tr ' ' '░')"

# Git status with per-directory caching
CACHE_FILE="/tmp/statusline-git-cache-$(echo "$DIR" | md5 -q 2>/dev/null || echo "$DIR" | md5sum | cut -d' ' -f1)"
CACHE_MAX_AGE=5

cache_is_stale() {
    [ ! -f "$CACHE_FILE" ] || \
    [ $(($(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0))) -gt $CACHE_MAX_AGE ]
}

if cache_is_stale; then
    if git -C "$DIR" rev-parse --git-dir > /dev/null 2>&1; then
        BRANCH=$(git -C "$DIR" branch --show-current 2>/dev/null)
        # Fallback for detached HEAD
        [ -z "$BRANCH" ] && BRANCH=$(git -C "$DIR" rev-parse --short HEAD 2>/dev/null)
        STAGED=$(git -C "$DIR" diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
        MODIFIED=$(git -C "$DIR" diff --numstat 2>/dev/null | wc -l | tr -d ' ')
        UNTRACKED=$(git -C "$DIR" ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
        REMOTE=$(git -C "$DIR" remote get-url origin 2>/dev/null | sed 's/git@github.com:/https:\/\/github.com\//' | sed 's/\.git$//')
        echo "$BRANCH|$STAGED|$MODIFIED|$UNTRACKED|$REMOTE" > "$CACHE_FILE"
    else
        echo "||||" > "$CACHE_FILE"
    fi
fi

IFS='|' read -r BRANCH STAGED MODIFIED UNTRACKED REMOTE < "$CACHE_FILE"

# Build status line
LINE="[$MODEL] ${BAR} ${PCT}%"

[ -n "$SESSION_NAME" ] && LINE="$LINE | 󰋱 $SESSION_NAME"
[ -n "$WORKTREE" ] && LINE="$LINE |  $WORKTREE"

# Directory / Git repo
DIR_NAME="${DIR##*/}"
if [ -n "$BRANCH" ]; then
    if [ -n "$REMOTE" ]; then
        LINE="$LINE | 󰊢 \e]8;;${REMOTE}\a${DIR_NAME}\e]8;;\a  $BRANCH"
    else
        LINE="$LINE | 󰊢 ${DIR_NAME}  $BRANCH"
    fi
    [ "$STAGED" -gt 0 ] 2>/dev/null && LINE="$LINE +$STAGED"
    [ "$MODIFIED" -gt 0 ] 2>/dev/null && LINE="$LINE ~$MODIFIED"
    [ "$UNTRACKED" -gt 0 ] 2>/dev/null && LINE="$LINE ?$UNTRACKED"
else
    LINE="$LINE | 󰉋 ${DIR_NAME}"
fi

[ -n "$VIM_MODE" ] && LINE="$LINE |  $VIM_MODE"

# Duration & Cost
MINS=$((DURATION_MS / 60000)); SECS=$(((DURATION_MS % 60000) / 1000))
LINE="$LINE | 󱎫 ${MINS}m${SECS}s | 󰄘 \$$(printf '%.2f' "$COST")"

printf '%b\n' "$LINE"
