---
description: "User-Centered Design workflow with automated multi-agent orchestration from concept to delivery"
allowed-tools:
  [
    "Task",
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "Grep",
    "Glob",
    "TodoWrite",
    "Bash",
  ]
---

# UCD Workflow - User-Centered Design Pipeline

Execute complete UCD development workflow using intelligent sub-agent coordination with quality gates.

## Usage

```bash
/ucd-workflow <FEATURE_DESCRIPTION> [--prototype] [--tdd] [--no-review] [--max-concurrent=N]
```

## Flags

- `--prototype`: Rapid iteration mode with 75% quality threshold
- `--tdd`: Test-driven development with comprehensive test coverage
- `--no-review`: Skip human review stage, proceed directly to execution
- `--max-concurrent=N`: Set maximum concurrent tasks for delivery manager (default: 3)

## Context

- Feature to develop: $ARGUMENTS
- Automated UCD workflow with quality gates
- Multi-agent coordination with smart dependency management

## Your Role

You are the UCD Delivery Manager orchestrating a comprehensive user-centered design workflow. You coordinate sub-agents through quality-gated stages ensuring appropriate thresholds based on build type.

## Sub-Agent Chain Process

Execute the following chain using Claude Code's sub-agent orchestration:

```
First use the user-researcher sub agent to analyze user needs and create personas for [$ARGUMENTS].
then use the product-manager sub agent to define the problem, articulate the product vision, and prioritize features using MoSCoW.
then use the ux-designer sub agent to design user flows, screens, information architecture, and establish the visual design system.
then use the solution-architect sub agent to design the technical architecture, select the tech stack, and plan implementation.
then use the product-manager sub agent to review and critique the plan, providing a quality score (≥75% for prototype or ≥95% for production).
If the quality gate is passed, the delivery-manager sub agent creates `prd.md` and `todos.md`, initializes the project, and coordinates implementation. If the quality gate is not met, loop back to each sub agent responsible with feedback for refinement, repeating up to 3 iterations.
```

## Workflow Logic

### Quality Gate Mechanism

- **Prototype Mode (--prototype)**: ≥75% quality threshold
- **Production/MVP Mode**: ≥95% quality threshold
- **Human Review**: Required at Stage 5 unless --no-review flag
- **Maximum 3 iterations**: Prevent infinite loops

### Chain Execution Stages

spec-analyst sub agent: Generate requirements.md, user-stories.md, acceptance-criteria.md
spec-architect sub agent: Create architecture.md, api-spec.md, tech-stack.md
spec-developer sub agent: Implement code based on specifications
spec-validator sub agent: Multi-dimensional quality scoring (0-100%)
Quality Gate Decision:
If ≥95%: Continue to spec-tester sub agent
If <95%: Return to spec-analyst sub agent with specific feedback
spec-tester sub agent: Generate comprehensive test suite (final step)

## Expected Iterations

- **Round 1**: Initial UCD plan (typically 70-85% quality)
- **Round 2**: Refined plan addressing feedback (typically 85-95%)
- **Round 3**: Final optimization if needed (meets threshold)

## Output Format

1. **Workflow Initiation** - Start sub-agent chain with feature description
2. **Progress Tracking** - Monitor each sub-agent completion
3. **Quality Gate Decisions** - Report review scores and next actions
4. **Completion Summary** - Final deliverables and implementation status

## Key Benefits

- **Optional Human Checkpoint**: One off checkpoint before plan implementation with bypass option
- **User-Centered Approach**: Start with user research and personas
- **Quality-Adjusted Thresholds**: Different standards for prototype vs production
- **Intelligent Feedback Loops**: Review feedback guides improvements
- **Single Command Execution**: One command triggers entire workflow

---

## Execute Workflow

**Feature Description**: $ARGUMENTS
**Build Type**: $BUILD_TYPE
**Flags**: $FLAGS

Starting UCD workflow with quality gates...

Phase 1 specification

Phase 2 architecture design

Phase 3 Implementation

Phase 4 Quality validation

Phase 5: Test Generation (Final)

### 🔍 Phase 1: User Research

First use the **user-researcher** sub agent to:

- Analyze target user demographics and behaviors
- Create detailed user personas with goals and pain points
- Document user needs and expectations

### 🔍 Phase 2: Problem Definition & Product Vision

Then use the **product-manager** sub agent to:

- Define problem space and opportunity areas
- MoSCow prioritised featuers
- Success measurements and KPIs

### 🎨 Phase 3: UX & Ui Design

Then use the **ux-designer** sub agents to:

- Design user flows
- Define information architecture
- Establish design system requirements
- Ensure WCAG 2.2 accessibility compliance

### 🏗️ Phase 4: Technical Architecture

Then use the **solution-architect** sub agent to:

- Select optimal platform and tech stack
- Design system architecture and components
- Plan security and performance strategies
- Create deployment and scaling approach

### ✅ Phase 5: Quality Review & Critique

Then use the **product-manager** sub agent to evaluate:

- User experience completeness and coherence
- Technical feasibility and risk assessment
- Feature prioritization alignment
- Security and compliance requirements
- **Provide quality score (0-100%)**

### 🔄 Quality Gate Decision

**If --prototype flag**: Score ≥75% to proceed
**If production/MVP**: Score ≥95% to proceed
**If below threshold**: Loop back to each sub agent responsible with feedback

### Phase 6: Create PRD & todos

Then use the **delivery-manager** sub agent to:

- create the `docs/prd.md` and `docs/todos.md`
- based on the output from sub agents in the prior phases
- uses the `.claude/templates/prd.templates.md` and `.claude/templates/todos.templates.md`

### 🚦 Phase 7: Human Review Checkpoint

**If --no-review flag**: Skip to Phase 6
**Otherwise**: Present complete plan for human approval

- Provide user with link to `docs/prd.md` and `docs/todos.md`
- Await user confirmation to proceed
- Incorporate feedback if provided

### 🚀 Phase 8: Project Initialization & Delivery

Use the **solution-architect** sub agent to:

- setup the project structure
- setup the .claude/rules for coding standards
- reference the `.claude/rules/*.rules.md` with relevant globs as hooks in the `.claude/settings.local.json`

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

Use the **qa-analyst** sub agent to:

- setup the automated quality gates (lint + autoformat, build compilation, language specific type checks)
- **If --tdd flag** setup project testing frameworks i.e. vitest

Finally use the **delivery-manager** sub agent to:

- Review `docs/todos.md` and select task(s) up to --max-concurrent
- Create task worktrees for parallel execution using:

```bash
git worktree add -b [task-title-slug] todos/worktrees/$(date +%Y-%m-%d-%H-%M-%S)-[task-title-slug]/ HEAD
```

- Coordinate implementation with quality loops
- Track progress against original requirements

## Expected Output Structure

```
project/
├── docs/
│   ├── prd.md              # Product Requirements Document
│   ├── todos.md            # Task breakdown with tracking
│   ├── personas/           # User persona documents
│   ├── journeys/           # User journey maps
│   └── architecture/       # Technical design docs
├── .claude/
│   ├── hooks.json          # Quality gate configurations
│   └── rules/              # Domain-specific rules
├── src/                    # Implementation code
├── tests/                  # Test suites (if --tdd)
├── worktrees/              # Git worktree feature branches
└── [project structure based on tech choice]
```

## Critical Halt Conditions

- **Requirement Reduction**: Any deviation that reduces original requirements
- **Scope Creep**: Significant expansion beyond original scope

**Begin execution now with the provided feature description and report progress after each sub-agent completion.**
