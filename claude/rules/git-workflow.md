# Git Workflow

## Worktree Commands
```bash
# Create worktree
worktree() { git worktree add -b "$1" "todos/worktrees/$(date +%Y-%m-%d-%H-%M-%S)-$1/"; }

# Commit and push
commit() { git add -A && git commit -m "$1"; }
push() { git push -u origin "$1"; }

# Archive task
archive() { git mv task.md "todos/done/$(date +%Y-%m-%d-%H-%M-%S)-$1.md"; }

# Cleanup
cleanup() { git worktree remove "todos/worktrees/$1"; }
```

## Branch Naming
- format: `YYYY-MM-DD-HH-MM-SS-task-slug`
- slug: lowercase, hyphens, no spaces

## Commit Messages
- `[task-title]: [action]`
- Examples: `auth-fix: init`, `auth-fix: refined`, `auth-fix: complete`