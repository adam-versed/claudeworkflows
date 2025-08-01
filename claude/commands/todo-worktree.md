# Todo Implementation Program

# imported from https://github.com/badlogic/claude-commands

# modified to use Claude.md rather than bespoke project desc

Structured workflow to transform vague todos into implemented features using git worktrees and subagent assignment. Supports task isolation, resumption, and clean commit history.

## Workflow

**CRITICAL**

- You MUST follow workflow phases in order: INIT → SELECT → REFINE → IMPLEMENT → COMMIT
- You MUST get user confirmation or input at each STOP
- You MUST iterate on refinement STOPs until user confirms
- You MUST NOT mention yourself in commit messages or add yourself as a commiter
- You MUST consult with the user in case of unexpected errors
- You MUST not forget to commits files you added/deleted/modified in the IMPLEMENT phase

### INIT

1. Check for task resume: If `task.md` exists in current directory:
   - Read `task.md` and `Claude.md` in full in parallel
   - Update `**Agent PID:** [Bash(echo $PPID)]` in task.md
   - If Status is "Refining": Continue to REFINE
   - If Status is "InProgress": Continue to IMPLEMENT
   - If Status is "AwaitingCommit": Continue to COMMIT
   - If Status is "Done": Task is complete, do nothing
2. Add `/todos/worktrees/` to .gitignore: `rg -q "/todos/worktrees/" .gitignore || echo -e "\n/todos/worktrees/" >> .gitignore`
3. Read `Claude.md` in full

   - If missing:
     - Use parallel Task agents to analyze codebase:
       - Identify purpose, features
       - Identify languages, frameworks, tools (build, dependency management, test, etc.)
       - Identify components and architecture
       - Extract commands from build scripts (package.json, CMakeLists.txt, etc.)
       - Map structure, key files, and entry points
       - Identify test setup and how to create new tests
     - Present proposed project description using template below

       ```markdown
       # Project: [Name]

       [Concise description]

       ## Features

       [List of key features and purpose]

       ## Tech Stack

       [Languages, frameworks, build tools, etc.]

       ## Structure

       [Key directories, entry points, important files]

       ## Architecture

       [How components interact, main modules]

       ## Commands

       - Build: [command]
       - Test: [command]
       - Lint: [command]
       - Dev/Run: [command if applicable]

       ## Testing

       [How to create and run tests]

       ```

     - STOP → Any corrections needed? (y/n)"
     - Write confirmed content to `Claude.md`

4. Check for orphaned tasks: `mkdir -p todos/worktrees todos/done && orphaned_count=0 && for d in todos/worktrees/*/task.md; do [ -f "$d" ] || continue; pid=$(grep "^**Agent PID:" "$d" | cut -d' ' -f3); [ -n "$pid" ] && ps -p "$pid" >/dev/null 2>&1 && continue; orphaned_count=$((orphaned_count + 1)); task_name=$(basename $(dirname "$d")); task_title=$(head -1 "$d" | sed 's/^# //'); echo "$orphaned_count. $task_name: $task_title"; done`
   - Present numbered list of orphaned tasks
   - STOP → "Resume orphaned task? (number or title/ignore)"
     - If resume
       - Assign subagent to worktree directory with /todo-worktree as first action
       - STOP → "Subagent assigned to worktree. The subagent will resume work automatically."
     - else go to SELECT

### SELECT

1. Read `todos/todos.md` in full
2. Present numbered list of todos with one line summaries
3. STOP → "Which todo would you like to work on? (enter number)"
4. Remove selected todo from `todos/todos.md` and commit: `git commit -am "Remove todo: [task-title]"`
5. Create git worktree with branch: `git worktree add -b [task-title-slug] todos/worktrees/$(date +%Y-%m-%d-%H-%M-%S)-[task-title-slug]/ HEAD`
6. Change CWD to worktree: `cd todos/worktrees/[timestamp]-[task-title-slug]/`
7. Initialize `task.md` from template in worktree root:

   ```markdown
   # [Task Title]

   **Status:** Refining
   **Agent PID:** [Bash(echo $PPID)]

   ## Original Todo

   [raw todo text from todos/todos.md]

   ## Description

   [what we're building]

   ## Implementation Plan

   [how we are building it]

   - [ ] Code change with location(s) if applicable (src/file.ts:45-93)
   - [ ] Automated test: ...
   - [ ] User test: ...

   ## Notes

   [Implementation notes]
   ```

8. Commit and push initial task setup: `git add . && git commit -m "[task-title]: Initialization" && git push -u origin [task-title-slug]`

### REFINE

1. Research codebase with parallel Task agents:
   - Where in codebase changes are needed for this todo
   - What existing patterns/structures to follow
   - Which files need modification
   - What related features/code already exist
2. Append analysis by agents verbatim to `analysis.md`
3. Draft description → STOP → "Use this description? (y/n)"
4. Draft implementation plan → STOP → "Use this implementation plan? (y/n)"
5. Update `task.md` with fully refined content and set `**Status**: InProgress`
6. Commit refined plan: `git add -A && git commit -m "[task-title]: Refined plan"`
7. Assign subagent to worktree directory with /todo-worktree as first action to start implementation
8. STOP → "Subagent assigned to worktree. The subagent will begin implementation automatically."

### IMPLEMENT

1. Execute the implementation plan checkbox by checkbox:
   - **During this process, if you discover unforeseen work is needed, you MUST:**
     - Pause and propose a new checkbox for the plan
     - STOP → "Add this new checkbox to the plan? (y/n)"
     - Add new checkbox to `task.md` before proceeding
   - For the current checkbox:
     - Make code changes
     - Summarize changes
     - STOP → "Approve these changes? (y/n)"
     - Mark checkbox complete in `task.md`
     - Commit progress, including added/modified/deleted files: `git add -A && git commit -m "[text of checkbox]"`
2. After all checkboxes are complete, run project validation (lint/test/build).
   - If validation fails:
     - Report full error(s)
     - Propose one or more new checkboxes to fix the issue
     - STOP → "Add these checkboxes to the plan? (y/n)"
     - Add new checkbox(es) to implementation plan in `task.md`
     - Go to step 1 of `IMPLEMENT`.
3. Present user test steps → STOP → "Do all user tests pass? (y/n)"
4. Check if project description needs updating:
   - If implementation changed structure, features, or commands:
     - Present proposed updates to `Claude.md`
     - STOP → "Update project description as shown? (y/n)"
     - If yes, update `Claude.md`
5. Set `**Status**: AwaitingCommit` in `task.md`
6. Commit: `git add -A && git commit -m "Complete implementation"`

### COMMIT

1. Present summary of what was done
2. STOP → "Ready to create PR? (y/n)"
3. Set `**Status**: Done` in `task.md`
4. Move task and analysis to done with git tracking:
   - `git mv task.md todos/done/[timestamp]-[task-title-slug].md`
   - `git mv analysis.md todos/done/[timestamp]-[task-title-slug]-analysis.md`
5. Commit all changes: `git add -A && git commit -m "Complete"`
6. Push branch to remote and create pull request using GitHub CLI
7. STOP → "PR created. Delete the worktree? (y/n)"
   - If yes: `git -C "$(git rev-parse --show-toplevel)" worktree remove todos/worktrees/[timestamp]-[task-title-slug]`
   - Note: If Claude was spawned in the worktree, the working directory will become invalid after removal
