# Build Workflow Configuration

## Overview

This document defines the interaction rules, communication flows, and operational procedures for the build workflow agent system.

## Agent Roster

1. **build orchestrator** - Central workflow coordinator
2. **@agent-plan-manager** - Task state and progress tracking
3. **@agent-fullstack-developer** - Implementation across web/mobile
4. **@agent-solution-validator** - Pre-implementation validation
5. **@agent-quality-monitor** - Independent quality verification
6. **@agent-git-manager** - Version control operations
7. **@agent-documenter** - Documentation discovery and deduplication
8. **@agent-log-monitor** - Runtime error detection
9. **@agent-cto** - Escalation handler (3 failures → CTO → 2 attempts → human)

## Workflow Phases

### Phase 0: Discovery & Codebase Review (When starting from implementation plan)

- @agent-documenter checks existing resources
- @agent-cto performs comprehensive codebase and documentation review
- @agent-solution-validator researches approaches
- Output: Context for implementation, updated documentation

### Phase 1: Planning & Validation

- build orchestrator assigns to @agent-solution-validator
- @agent-solution-validator reviews approach
- @agent-documenter provides existing docs
- Output: Approved technical approach

### Phase 2: Implementation

- @agent-fullstack-developer receives approved design
- @agent-log-monitor watches for runtime errors
- Output: Implemented feature (no self-validation required)

### Phase 3: Quality Verification

- @agent-quality-monitor dynamically detects tech stack and available quality commands
- @agent-quality-monitor executes appropriate gates (skips tests in --prototype mode)
- @agent-log-monitor confirms no runtime errors
- Output: Quality approval or rejection

### Phase 4: Commit

- @agent-git-manager commits approved changes
- Handles pre-commit hooks
- Updates @agent-plan-manager on completion
- Output: Committed code

## Communication Rules

### 1. Central Coordination

- All agent communication flows through build orchestrator
- No direct agent-to-agent communication except:
  - @agent-log-monitor → @agent-quality-monitor (error reports)
  - All agents → @agent-plan-manager (state updates)

### 2. Task Assignment Flow

```
User → build orchestrator → @agent-plan-manager (create task)
                         ↓
            [If planFile] @agent-cto (codebase review)
                         ↓
                    @agent-documenter (check existing)
                         ↓
                 @agent-solution-validator (approve approach)
                         ↓
                @agent-fullstack-developer (implement)
                         ↓
                 @agent-quality-monitor (verify)
                         ↓
                   @agent-git-manager (commit)
```

### 3. Failure Handling

```
Agent fails task (attempt 1)
      ↓
Agent fails task (attempt 2)
      ↓
Agent fails task (attempt 3)
      ↓
build orchestrator → @agent-cto (escalation)
                      ↓
               @agent-cto guides agent (attempt 1)
                      ↓
               @agent-cto guides agent (attempt 2)
                      ↓
                Human escalation
```

## Quality Gate Enforcement

### Required Gates (Always)

1. Linting passes (`npm run lint`)
2. Type checking passes (`npm run typecheck`)
3. Build succeeds (`npm run build`)
4. No errors in dev.log
5. @agent-quality-monitor approval

### Optional Gates (Project-Specific)

1. Test execution (MVP projects, skipped in --prototype mode)
2. Coverage thresholds
3. Performance benchmarks
4. Security scanning

### Prototype Mode (--prototype flag)

- Skips unit, integration, and e2e test execution
- Maintains lint, typecheck, build, and dev.log verification
- All agents receive prototype context for appropriate behavior
- Quality monitor automatically adjusts gate execution

### Gate Verification Flow

1. @agent-quality-monitor dynamically detects and executes all quality gates
2. @agent-git-manager enforces quality approval before commit
3. Pre-commit hooks final check

## State Management

### Task States

- `pending` - Created, not assigned
- `assigned` - Assigned to orchestrator
- `planning` - In validation phase
- `validated` - Approach approved
- `in_progress` - Implementation active
- `testing` - Running quality checks
- `quality_review` - Under quality monitor review
- `approved` - Quality gates passed
- `committing` - Git operations in progress
- `completed` - Successfully committed
- `cto_intervention` - Under CTO review
- `human_escalation` - Requires human input

### State Transition Rules

- Only @agent-plan-manager can update states
- States must follow defined transitions
- Failure can revert to previous state
- CTO intervention is special state

## Escalation Procedures

### Triggers for Escalation

1. 3 failures on same task by same agent
2. Conflicting requirements between agents
3. Security vulnerabilities detected
4. External dependencies blocking progress

### CTO Intervention Process

1. build orchestrator provides context
2. CTO analyzes with "think harder"
3. CTO guides failing agent
4. Maximum 2 CTO attempts
5. Human escalation if still failing

### Human Escalation Format

```
HUMAN ESCALATION REQUIRED

Task: [Task ID and description]
Agent: [Failing agent]
Failures: [Total attempts including CTO]
Issue: [Root cause analysis]
Attempted Solutions: [What was tried]
Recommendation: [Suggested human action]
```

## Inter-Agent Dependencies

### build orchestrator depends on:

- @agent-plan-manager (task states)
- All agents (task execution)

### @agent-fullstack-developer depends on:

- @agent-solution-validator (approved designs)
- @agent-documenter (existing resources)

### @agent-quality-monitor depends on:

- @agent-log-monitor (error reports)
- @agent-fullstack-developer (completed work)

### @agent-git-manager depends on:

- @agent-quality-monitor (approval)
- build orchestrator (clearance)
- Reports pre-commit failures back to build orchestrator (not fixes them)

## Operational Guidelines

### 1. Task Initialization

- Start with @agent-cto codebase review if implementing from planFile
- Always start with @agent-documenter check
- Require solution validation for non-trivial tasks
- Update @agent-plan-manager immediately

### 2. Quality Standards

- No bypassing quality gates
- Independent verification required
- Runtime errors block progress

### 3. Documentation

- Check before creating
- Single source of truth
- Update registry on changes

### 4. Communication

- Clear, structured messages
- Include correlation IDs
- Report state changes immediately

### 5. Failure Recovery

- Preserve failure context
- Increment counters accurately
- Escalate at thresholds

## Performance Metrics

### Success Indicators

- First-attempt success rate >70%
- CTO escalations <10%
- Human escalations <2%
- Quality gate pass rate >80%

### Warning Signs

- Repeated failures same issue
- Increasing CTO interventions
- Quality gates frequently failing
- Long task durations

## Configuration Updates

This configuration should be updated when:

- New agents added to workflow
- State machine changes
- Quality gates modified
- Escalation thresholds adjusted

Last Updated: [Current Date]
Version: 1.0
