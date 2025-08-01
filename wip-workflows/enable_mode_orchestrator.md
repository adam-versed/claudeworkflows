# Night Mode Orchestrator (`/enable_mode_orchestrator`)

**Purpose**: Autonomous orchestration of multiple subagents for parallel todo task implementation with quality oversight, designed to survive context compaction and maintain state across sessions.

**Usage**: `claude /enable_mode_orchestrator [max-agents]`

## INIT: CLAUDE.md Setup and Validation

**Check for existing configuration**: Read project CLAUDE.md to verify night mode setup
**Skip if present**: If ORCHESTRATOR_MODE variable and orchestrator instructions exist, and ORCHESTRATOR is set to true, proceed to Phase 1

**If configuration missing or NIGHT_MODE = false, update CLAUDE.md to**:

```markdown
# Global variables

ORCHESTRATOR = true

<ORCHESTRATOR if = true else skip>
When in ORCHESTRATOR there is no human oversight, work is actioned up to PR but worktrees are not deleted and left for review the following day.

Read and follow the instructions in '/Users/adamjackson/.claude/commands/enable_mode_orchestrator.md' for autonomous todo orchestration.

Use subagents to work your way through the @todos/todos.md using the night mode orchestrator workflow.
</ORCHESTRATOR>
```

**Validation**:

- Verify NIGHT_MODE = true is set
- Confirm orchestrator reference is in place
- Validate project has todos/todos.md file
- Check that current working directory is project root

## Phase 1: Task Discovery and Project Root Validation

**CRITICAL**: Ensure orchestrator always operates from project root to prevent nested worktrees

1. **Validate working directory**: Confirm current directory is project root

   - Use `git rev-parse --show-toplevel` to get actual repository root
   - Compare with current working directory (`pwd`)
   - Check that current directory equals git repository root
   - Confirm we're NOT in a worktree by checking `git worktree list` output
   - If not in project root, navigate to `$(git rev-parse --show-toplevel)` before proceeding

2. **Execute todo-worktree INIT phase**: Run `/todo-worktree` workflow ignoring STOP commands
3. **Read todos list**: Parse `todos/todos.md` for available uncompleted tasks
4. **Calculate agent count**: Use $ARGUMENTS or default to available task count (max 3)
5. **Create worktrees from project root**: Execute SELECT phase for each task without user interaction

**Commands from project root**:

```bash
# Verify we're in the actual project root (not a worktree)
PROJECT_ROOT=$(git rev-parse --show-toplevel)
CURRENT_DIR=$(pwd)
if [ "$CURRENT_DIR" != "$PROJECT_ROOT" ]; then
  cd "$PROJECT_ROOT"
fi

# Confirm we're not in a worktree by checking the main entry in worktree list
git worktree list | head -1 | grep -q "$(pwd)"

# Create worktrees from verified project root
git worktree add -b [task-slug] todos/worktrees/$(date +%Y-%m-%d-%H-%M-%S)-[task-slug]/ HEAD
```

**Tool**: Task - Launch subagent with worktree path
**Usage**: Pass worktree absolute path and instruction to run `/todo-worktree` from that location

## Phase 2: Subagent Coordination

1. **Launch up to 3 subagents**: Create one Task agent per worktree (maximum 3 concurrent)
2. **Pass worktree paths**: Provide absolute path to each subagent
3. **Initialize subagents**: Each runs `/todo-worktree` from their worktree directory
4. **Monitor initialization**: Track subagent startup and task pickup
5. **Manage concurrency**: Start new subagents as others complete (maintain up to 3 active)

**Subagent Instructions**:

- Change to provided worktree directory
- Execute `/todo-worktree` to continue from current task state
- Report back to orchestrator at each STOP interaction
- Wait for orchestrator approval before proceeding
- Run quality gates before considering task complete

## Phase 3: Implementation Oversight

1. **Validation requests**: When subagent reaches REFINE phase STOP points

   - Review task description and implementation plan
   - Research best practices using WebSearch
   - Enhance plan with industry standards
   - Approve or request modifications

2. **Implementation checkpoints**: When subagent completes IMPLEMENT steps
   - Review code changes and approach
   - Validate against project patterns
   - Check security and performance implications
   - Approve continuation or request changes

**Tool**: WebSearch - Research best practices for task type
**Usage**: Search "[task-type] best practices [framework]" for enhancement guidance

**Quality Gate**: Code Review
**Pass Criteria**: Follows project patterns, secure, performant
**Failure Action**: Request specific improvements before proceeding

## Phase 4: Quality Assurance

1. **Pre-commit validation**: Before subagent reaches COMMIT phase

   - Verify all quality gates pass
   - Confirm test coverage adequate
   - Check documentation updates
   - Validate integration requirements

2. **Final approval**: Before PR creation
   - Comprehensive review of all changes
   - Confirm lint/test/build success
   - Approve PR submission

**Quality Gate**: Build Validation
**Command**: Project-specific build/test commands
**Pass Criteria**: Zero errors, all tests pass
**Failure Action**: Block PR until resolved

## Phase 5: Completion Tracking and Branch Preservation

1. **Monitor progress**: Track each subagent through completion
2. **Handle conflicts**: Resolve merge conflicts or overlapping changes
3. **Coordinate PRs**: Manage PR submission order if dependencies exist
4. **Preserve branches**: **NEVER delete worktree branches** - leave for human review
5. **Continue orchestration**: Pick next tasks from todos.md and launch new subagents

**Git**: Track completed tasks but preserve branches
**Command**: Mark task complete in todos.md but retain worktree
**Expected**: Completed task marked, worktree branch preserved for review

## Phase 6: Auto-Stop Condition

**Stop orchestration when**: Reaching Phase 6 of todos/todos.md
**Action**: Set NIGHT_MODE = false in CLAUDE.md
**Result**: Orchestrator deactivates, preserves all work for human review

## Context Compaction Resilience

**State Recovery**: If context is compacted during orchestration:

1. CLAUDE.md contains NIGHT_MODE = true and orchestrator reference
2. Claude will automatically read this file and resume orchestration
3. Check current working directory and return to project root if needed
4. Resume from current state in todos/todos.md
5. Continue with up to 3 concurrent subagents

## Research Enhancement Patterns

**Framework-Specific**: Search "[framework] [feature-type] implementation patterns"
**Security**: Search "[feature-type] security best practices"
**Testing**: Search "[framework] testing strategies [feature-type]"
**Performance**: Search "[feature-type] optimization techniques"

## Coordination Rules

- **Project root operation**: Always ensure orchestrator operates from project root
- **Sequential STOP handling**: Process one subagent validation request at a time
- **Quality first**: Never approve substandard work for speed
- **Clear feedback**: Provide specific, actionable improvement requests
- **Progress visibility**: Report overall progress across all active tasks
- **Concurrent limit**: Maximum 3 active subagents at any time
- **Branch preservation**: Never delete worktree branches - preserve for human review
- **Context resilience**: Designed to survive and resume after context compaction

$ARGUMENTS
