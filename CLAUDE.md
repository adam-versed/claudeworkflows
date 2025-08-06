# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the Claude Code Workflows repository - a hybrid AI-automation system that provides specialized workflow commands, LLM actions, and Python analysis scripts for multi-function, just-in-time development automation.

## Commands for Development

### Running Quality Checks

Based on project type detected:

**Node.js/TypeScript projects:**

- Lint: `npm run lint` or `npm run check` (if biome is used)
- Type check: `npm run type-check` or `npm run typecheck`
- Build: `npm run build`
- Test: `npm run test`
- Format: `npm run format` or `npm run format:check`

**Python projects:**

- Lint: `flake8 .` or `pylint .` or `ruff check`
- Test: `pytest`
- Format: `black .` or `ruff format`

**Rust projects:**

- Lint: `cargo clippy`
- Build: `cargo build`
- Test: `cargo test`

### Workflow Commands

The repository provides specialized commands under `/claude/commands/`:

- `/analyze-security` - Comprehensive security analysis following OWASP Top 10
- `/analyze-architecture` - Architecture pattern detection and evaluation
- `/analyze-performance` - Frontend and backend performance analysis
- `/plan-solution` - Research and plan implementation approaches
- `/todo-orchestrate` - Execute implementation plans with multi-agent coordination
- `/create-project` - Initialize new projects using better-t-stack CLI
- `/setup-dev-monitoring` - Setup unified development monitoring dashboard

### Build Flags

Special modes can be activated with flags:

- `--prototype` - Rapid prototyping mode (relaxed testing requirements)
- `--tdd` - Test-driven development mode
- `--seq` - Sequential thinking mode for complex problem breakdown
- `--gitgrep` - Enhanced grep search mode

## High-Level Architecture

### Agent System

The repository implements a 9-agent orchestration system under `/claude/agents/`:

1. **build orchestrator** (conceptual) - Coordinates tasks across agents via `/todo-orchestrate` command
2. **@agent-fullstack-developer** - Implements features across web and mobile platforms
3. **@agent-quality-monitor** - Dynamically detects tech stack and enforces quality gates
4. **@agent-solution-validator** - Validates technical approaches before implementation
5. **@agent-plan-manager** - Tracks task state and progress
6. **@agent-log-monitor** - Monitors runtime errors in development logs
7. **@agent-documenter** - Manages documentation discovery and prevents duplication
8. **@agent-git-manager** - Handles version control operations and commits
9. **@agent-cto** - Critical escalation for failed tasks (3 failures trigger escalation)

### OpenCode Integration

The agents have been ported to OpenCode format under `/opencode/agents/` with:

- OpenCode YAML frontmatter configuration
- Orchestration handled by `/orchestrate` mode instead of a specific agent
- All inter-agent references updated to use "orchestrator mode" terminology

### Directory Structure

- `/claude/` - Core workflow system

  - `/agents/` - Agent definitions and state machines
  - `/commands/` - Workflow command implementations
  - `/modes/` - Special operational modes
  - `/rules/` - Technology-specific rules and patterns
  - `/scripts/` - Python analysis and automation scripts
  - `/templates/` - Templates for various outputs

- `/opencode/` - OpenCode integration

  - `/agents/` - OpenCode-compatible agent definitions
  - `/modes/` - OpenCode workflow modes (orchestrate)

- `/test_codebase/` - Example monorepo for testing workflows
- `/wip-workflows/` - Experimental workflow agents
- `/docs/` - Extended documentation

### Quality Gate System

The quality monitor agent dynamically detects project technology and runs appropriate checks:

1. **Tech Stack Detection** - Identifies Node.js, Python, Rust, Go projects
2. **Command Discovery** - Finds available lint, typecheck, build, test commands
3. **Mode-Aware Execution** - Respects `--prototype` flag to skip tests
4. **Failure Escalation** - 3 failures → CTO agent → 2 attempts → human

### Development Monitoring

When `/setup-dev-monitoring` is run:

- Creates unified `/dev.log` for all services
- Provides real-time service status dashboard
- Auto-detects tech stack for optimal monitoring
- Enables commands: `make dev`, `make status`, `make logs`

## Important Patterns

1. **Always run quality gates after implementation** - Use discovered commands, not hardcoded assumptions
2. **Check for existing implementations** - Search before creating new utilities or components
3. **Follow project conventions** - Maintain consistency with existing patterns
4. **Use specialized agents proactively** - Let agents handle their domain expertise
5. **Track tasks with TodoWrite** - Essential for complex multi-step implementations
6. **Escalate after 3 failures** - CTO agent provides expert guidance

## Notes for Working in This Repository

- This is a tool repository, not a typical application codebase
- Commands are markdown files that define workflows, not executable scripts
- Python scripts under `/scripts/` provide programmatic analysis
- The `/test_codebase/` is for testing workflows, not the main project
- Agent coordination happens through the build orchestrator (conceptual role), not direct communication
- Some configuration files (`message-formats.md`, `state-machine.md`, `workflow-config.md`) are documentation-only and not actively used by the agent system
