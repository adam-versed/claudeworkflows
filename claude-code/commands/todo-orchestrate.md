---
description: "Todo orchestration with automated multi-agent coordination from implementation plan to delivery"
allowed-tools:
  ["Task", "Read", "Write", "Edit", "TodoWrite", "Bash", "Grep", "Glob", "LS"]
---

# Todo Orchestrate - Implementation Plan Execution

Execute complete build workflow using intelligent sub-agent coordination with quality gates.

## Usage

```bash
/build-orchestrate <IMPLEMENTATION_PLAN_PATH> [--prototype] [--parallel] [--max-retries=3]
```

## Arguments

- `IMPLEMENTATION_PLAN_PATH`: Path to implementation plan file

## Flags

- `--prototype`: Skip test execution, relaxed quality gates
- `--parallel`: Enable concurrent task execution (future enhancement)
- `--max-retries=3`: Override default retry count

## Context

- Implementation Plan: $ARGUMENTS
- Build orchestration with quality gates
- Multi-agent coordination with smart dependency management

## Your Role

You are the Build Orchestration Manager executing a comprehensive implementation workflow. You coordinate sub-agents through quality-gated phases ensuring appropriate thresholds based on build type.

## Workflow Orchestration Logic

### Phase 0: Initial Setup

**Parse and Initialize:**

```
First use the @agent-plan-manager sub agent to parse implementation plan and create task registry.
If implementation plan provided, use the @agent-cto sub agent to perform comprehensive codebase and documentation review.
Then use the @agent-documenter sub agent to check existing resources and build registry.
Set prototype mode flag if --prototype argument present.
```

### Main Orchestration Loop

**Execute continuous task processing through all phases until all tasks completed:**

```
while (phases remain with incomplete tasks):

  # Process all tasks in current phase
  while (tasks remain in current phase in non-completed states):

    ## 1. Task Selection
    Use the @agent-plan-manager sub agent to get next highest priority pending task in current phase.
    Update task state to "assigned".

    ## 2. Phase 1 - Validation
    Use the @agent-documenter sub agent to check existing documentation.
    Use the @agent-solution-validator sub agent to validate technical approach.
    Pass --prototype flag if set so validator knows quality expectations.
    If rejected: retry up to 3 times, then escalate to @agent-cto sub agent.
    Update task state to "validated" on approval.

    ## 3. Phase 2 - Implementation
    Use the @agent-fullstack-developer sub agent with validated approach.
    Developer implements feature and checks dev.log for runtime errors before completion.
    Update task state: in_progress → testing.
    If implementation fails: retry up to 3 times, escalate to @agent-cto sub agent.

    ## 4. Phase 3 - Quality Verification
    Use the @agent-quality-monitor sub agent for verification.
    Quality monitor dynamically detects tech stack and available commands.
    Quality monitor executes appropriate gates and verifies clean dev.log.
    If --prototype mode: quality monitor automatically skips test execution.
    If production mode: quality monitor includes all available tests.

    On PASS: Update task state to "approved".
    On FAIL: Update task state back to "in_progress".
            Use the @agent-fullstack-developer sub agent to fix specific quality failures.
    If fails 3 times: escalate to @agent-cto sub agent with --prototype context.

    ## 5. Phase 4 - Commit
    Use the @agent-git-manager sub agent to attempt commit.

    On SUCCESS: Update task state to "completed".
    On PRE-COMMIT FAILURE:
      Update task state back to "in_progress".
      Use the @agent-fullstack-developer sub agent to fix pre-commit issues.
    If 3 pre-commit failures: escalate to @agent-cto sub agent.

    ## 6. Failure Escalation
    On 3rd failure at any phase:
      Use the @agent-cto sub agent with full context including --prototype flag.
      @agent-cto gets 2 attempts to resolve via guided agent interactions.
      @agent-cto is aware of --prototype quality expectations.
    After 2 @agent-cto failures: halt with human escalation message.

  end while (task loop)

  # Phase completed - generate user testing plan
  Use the @agent-documenter sub agent to:
    - Create phase[id]-user-testing-plan.md
    - Document all features implemented in this phase
    - Provide step-by-step validation instructions
    - Include expected outcomes and success criteria
    - Store in centralized documentation area

  Log: "Phase completed. User testing plan created. Moving to next phase with incomplete tasks."

end while (phase loop)
```

### Completion Report

**Generate final status using @agent-plan-manager:**

- Report all completed tasks and any remaining issues
- Provide commit references and next steps
- Generate comprehensive workflow completion summary
- List all phase user testing plans created by @agent-documenter

## Key Features

- **Continuous Orchestration**: Single command runs entire workflow to completion
- **Dynamic Quality Gates**: @agent-quality-monitor adapts to project tech stack
- **Prototype Mode Support**: Automatic test skipping with --prototype flag
- **Intelligent Failure Handling**: 3 failures → CTO → 2 attempts → human escalation
- **State Persistence**: Progress tracked throughout execution via @agent-plan-manager
- **Phase Testing Plans**: Automatic generation of user testing plans after each phase

## Expected Iterations

- **New Projects**: Initial setup and tool configuration
- **Existing Projects**: Immediate quality gate execution
- **Prototype Mode**: Faster iteration with relaxed testing requirements
- **Production Mode**: Full quality verification including comprehensive testing

## Output Format

1. **Phase 0 Initialization** - Setup and preparation status
2. **Orchestration Loop Progress** - Real-time task execution updates
3. **Quality Gate Results** - Pass/fail status with specific details
4. **Completion Summary** - Final deliverables and workflow metrics

---

## Execute Workflow

**Implementation Plan**: $ARGUMENTS
**Build Type**: Production (or Prototype if --prototype flag)
**Flags**: $FLAGS

Starting build orchestration with quality gates...

### 🚀 Phase 0: Initial Setup

Use the **@agent-plan-manager** sub agent to:

- Parse implementation plan file: $ARGUMENTS
- Create comprehensive task registry with dependencies
- Initialize progress tracking system

Use the **@agent-cto** sub agent to:

- Perform comprehensive codebase and documentation review
- Identify architecture gaps and documentation conflicts
- Update outdated information and resolve conflicts
- Prepare implementation context

Use the **@agent-documenter** sub agent to:

- Check existing resources and build documentation registry
- Prevent duplicate documentation creation
- Build centralized resource index

### 🔄 Main Orchestration Loop

**Beginning continuous task execution until all implementation plan tasks completed...**

For each pending task, execute the complete workflow:

1. **Task Assignment** → @agent-plan-manager
2. **Documentation Check** → @agent-documenter
3. **Approach Validation** → @agent-solution-validator
4. **Feature Implementation** → @agent-fullstack-developer
5. **Quality Verification** → @agent-quality-monitor
6. **Code Commit** → @agent-git-manager

**Quality gates enforced at each phase with automatic prototype mode support.**

### ✅ Completion Report

Use the **@agent-plan-manager** sub agent to generate final status report including:

- Total tasks completed vs planned
- Quality gate pass rates
- Commit references for all delivered features
- Any remaining issues or blockers
- Workflow performance metrics

**Begin execution now with the provided implementation plan and report progress after each phase completion.**
