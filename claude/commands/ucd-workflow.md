# UCD Workflow v1.0

## Usage

```bash
/ucd-workflow <FEATURE_DESCRIPTION> [--prototype] [--tdd] [--no-review] [--max-concurrent=N]
```

## Context

Feature to develop: $ARGUMENTS
Automated multi-agent workflow with quality gates
Sub-agents work in independent contexts with smart chaining

## Your Role

You are the **delivery-manager** coordinating CLaude Code Sub-Agents to execute complete User-Centered Design (UCD) workflow from initial concept to delivery through a quality-gated workflow that ensures min % code quality through intelligent looping.

**SINGLE STOP POINT**: Agent-driven process with ONE human interaction at Stage 5 (bypassed with `--no-review` flag)

**CRITICAL HALT**: Must halt for any plan deviations that reduce requirements - requires human approval

**RESUMPTION**: Check existing `docs/prd.md` and `docs/todos.md` to determine current stage and resume appropriately

**AGENT COORDINATION**: Use available sub-agents based on their expertise descriptions and task requirements

## UCD Workflow Stages

### Stage 1: Problem Definition & Planning

- Initialize `docs/` directory structure (check for existing `docs/prd.md` for resumption)
- Coordinate Claude Sub-Agents to define problem space, user personas, and technical foundation
- Establish platform choice, architecture approach, and technology stack
- Output: Initial PRD foundation with user and technical requirements

### Stage 2: Feature & UX Planning

- Create comprehensive MoSCoW feature breakdown
- Define user journeys, screen flows, and design system requirements
- Ensure WCAG 2.2 accessibility compliance planning
- Output: Complete `docs/prd.md` with features and UX specifications following `**/templates/prd.templates.md` spec

### Stage 3: Task Planning

- Focus ONLY on Must Have and Should Have features (exclude Could Have from initial planning)
- Create detailed task breakdown in `docs/todos.md` with dependencies following `**/templates/todos.templates.md` spec
- Validate task structure across all relevant agents
- Output: Comprehensive task plan with checkbox-based tracking

### Stage 4: Critical Review

- Security review for non-prototype builds (skip for prototype)
- Multi-agent critique of solution approach, prioritization, and risk assessment
- Incorporate feedback and adjust PRD/todos as needed
- Output: Refined plan with agent feedback integrated

### Stage 5: Human Review & Final Plan Approval

- **If `--no-review` flag**: Skip to Stage 6 automatically
- **If no flag**: Present complete plan for user review and feedback
- Incorporate user changes and re-run critique if significant modifications made
- **STOP**: "Plan review complete. Ready to proceed?" _(bypassed with `--no-review`)_

### Stage 6: Quality Setup & Project Initialization

- Set up project structure, git repository, and starter projects
- Favour use of established libraries and highly rated starter projects over bespoke setup to reduce effort
- Configure minimum quality gates: linting, build compilation, type checking, precommit hooks
- **If `--tdd` flag**: Set up unit test framework (Vitest) infrastructure only - no actual tests yet
- Set up Claude Hook Quality Gates with domain-specific rules and PreToolUse hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in *\"*.ts\"*) cat .claude/rules/typescript.rules.md ;; *\"*.tsx\"*) cat .claude/rules/react.rules.md ;; *\"/api/\"*) cat .claude/rules/api.rules.md ;; esac'"
          }
        ]
      }
    ]
  }
}
```

### Stage 7: Execution Loop with Quality Gates

- Execute each todo in `docs/todos.md` using todo-worktree workflow
- Coordinate appropriate agents to implement tasks with `analysis.md` and `task.md` in worktree root
- **TDD Process** (if `--tdd` flag):
  1. **qa-analyst**: Reviews task details and creates unit test coverage (all tests should initially fail)
  2. **Developer agent**: Implements code until all unit tests pass
- **Quality Threshold Scoring**: Multi-agent review with aggregate scores
  - **Prototype** (`--prototype`): 75% minimum score
  - **MVP/Production**: 95% minimum score
- **Quality Gate Logic**: Score ≥ threshold = merge approved, score < threshold = iteration required
- **Maximum 3 iterations per task** to prevent infinite loops
- Track progress in `docs/todos.md` only when quality threshold met

### Stage 8: Delivery Coordination

- Manage concurrent task execution with maximum concurrent tasks limited by `--max-concurrent=N` flag (default: 3)
- Coordinate cross-functional dependencies and agent workload distribution
- **CRITICAL**: HALT for any plan deviations that reduce requirements (requires human approval)
- Validate all Must Have features implemented against original PRD
- Confirm final quality gates pass for delivery

**CRITICAL HALT** → "Plan deviation detected that reduces requirements. Human approval required."

## Flags

- `--prototype`: Rapid iteration mode with 75% quality threshold
- `--tdd`: Test-driven development with comprehensive test coverage
- `--no-review`: Skip human review stage, proceed directly to execution
- `--max-concurrent=N`: Set maximum concurrent tasks for delivery manager (default: 3)
