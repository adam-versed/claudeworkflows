# Todo Orchestrator (`/orchestrate-todos`)

**Purpose**: Orchestrate multiple subagents for parallel todo task implementation with quality oversight
**Usage**: `claude /orchestrate-todos [max-agents]`

## Phase 1: Task Discovery and Assignment

1. **Execute todo-worktree INIT phase**: Run `/todo-worktree` workflow ignoring STOP commands
2. **Read todos list**: Parse `todos/todos.md` for available tasks
3. **Calculate agent count**: Use $ARGUMENTS or default to available task count (max 3)
4. **Create worktrees**: Execute SELECT phase for each task without user interaction

**Commands**:
```bash
git worktree add -b [task-slug] todos/worktrees/$(date +%Y-%m-%d-%H-%M-%S)-[task-slug]/ HEAD
```

**Tool**: Task - Launch subagent with worktree path
**Usage**: Pass worktree absolute path and instruction to run `/todo-worktree` from that location

## Phase 2: Subagent Coordination

1. **Launch subagents**: Create one Task agent per worktree
2. **Pass worktree paths**: Provide absolute path to each subagent
3. **Initialize subagents**: Each runs `/todo-worktree` from their worktree directory
4. **Monitor initialization**: Track subagent startup and task pickup

**Subagent Instructions**:
- Change to provided worktree directory
- Execute `/todo-worktree` to continue from current task state
- Report back to orchestrator at each STOP interaction
- Wait for orchestrator approval before proceeding

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

## Phase 5: Completion Tracking

1. **Monitor progress**: Track each subagent through completion
2. **Handle conflicts**: Resolve merge conflicts or overlapping changes
3. **Coordinate PRs**: Manage PR submission order if dependencies exist
4. **Cleanup**: Remove completed worktrees after successful PR merge

**Git**: Track completed tasks
**Command**: `git worktree remove [worktree-path]`
**Expected**: Clean workspace, completed task in done folder

## Research Enhancement Patterns

**Framework-Specific**: Search "[framework] [feature-type] implementation patterns"
**Security**: Search "[feature-type] security best practices"
**Testing**: Search "[framework] testing strategies [feature-type]"
**Performance**: Search "[feature-type] optimization techniques"

## Coordination Rules

- **Sequential STOP handling**: Process one subagent validation request at a time
- **Quality first**: Never approve substandard work for speed
- **Clear feedback**: Provide specific, actionable improvement requests
- **Progress visibility**: Report overall progress across all active tasks

$ARGUMENTS