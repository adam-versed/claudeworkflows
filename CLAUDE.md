# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the Claude Code Workflows repository - a hybrid AI-automation system that provides specialized workflow commands, LLM actions, and Python analysis scripts for development automation. The system installs into `.claude/` directories and provides custom slash commands, agent orchestration, and quality gates.

## Common Development Tasks

### Installation and Setup

```bash
# Install to current directory (creates ./.claude/)
./claude-code/install.sh

# Install globally for user (creates ~/.claude/)
./claude-code/install.sh ~

# Install with optional monitoring setup
./claude-code/install.sh
/setup-dev-monitoring  # After installation
```

### Available Slash Commands

The system provides numerous slash commands organized by category:

- **Analysis**: `/analyze-security`, `/analyze-architecture`, `/analyze-performance`, `/analyze-code-quality`
- **Planning**: `/plan-solution`, `/plan-ux-prd`, `/plan-refactor`
- **Implementation**: `/todo-orchestrate`, `/todo-branch`, `/todo-worktree`
- **Fixes**: `/fix-bug`, `/fix-performance`
- **Quality**: `/add-code-precommit-checks`, `/add-code-posttooluse-quality-gates`

### Build Flags

Commands support various flags to modify behavior:

- `--prototype`: Rapid prototyping mode (relaxes quality gates)
- `--tdd`: Test-driven development mode
- `--seq`: Sequential thinking for complex breakdowns
- `--gitgrep`: Enhanced git repository search

## Architecture

### Directory Structure

```
claude-code/
├── agents/           # Agent definition files (*.md)
├── commands/         # Slash command implementations (*.md)
├── modes/           # Mode configuration files (*.modes.md)
├── rules/           # Framework-specific rules (*.rules.md)
├── scripts/         # Python analysis scripts
│   ├── analyze/     # Analysis tools by category
│   ├── plan/        # Planning utilities
│   └── setup/       # Setup and installation scripts
├── docs/            # Technical documentation
└── templates/       # Template files for generation

test_codebase/       # Example test projects
todos/               # Work-in-progress workflows
```

### Agent System

The repository implements an 8-agent orchestration system:

1. **build-orchestrator**: Central workflow coordinator
2. **plan-manager**: Task state and progress tracking
3. **fullstack-developer**: Cross-platform implementation
4. **solution-validator**: Pre-implementation validation
5. **quality-monitor**: Dynamic quality gate detection
6. **git-manager**: Version control operations
7. **documenter**: Documentation discovery
8. **log-monitor**: Runtime error detection
9. **cto**: Critical escalation handler (3 failures → CTO → 2 attempts → human)

### Python Scripts Architecture

The `scripts/` directory contains specialized Python analysis tools:

- **Security**: Uses bandit, safety, semgrep for vulnerability detection
- **Performance**: Uses psutil, memory-profiler, py-spy for profiling
- **Code Quality**: Uses flake8, pylint, radon, lizard for metrics
- **Architecture**: Uses pydeps, networkx for dependency analysis

### Command Implementation

Commands are Markdown files that can:

- Use `$ARGUMENTS` placeholder for dynamic values
- Be namespaced using subdirectories (e.g., `frontend:component`)
- Exist at project level (`.claude/commands/`) or user level (`~/.claude/commands/`)

### Mode System

Modes are activated by flags and modify Claude's behavior:

- Each mode has a corresponding `.modes.md` file
- Modes are resolved first from project `.claude/modes/`, then user `~/.claude/modes/`
- Modes contain specific instructions that override default behavior

## Quality Gates and Testing

The system implements dynamic quality gate detection that adapts to the project's technology stack. When working on changes:

1. Quality gates are automatically enforced unless `--prototype` flag is used
2. The quality-monitor agent detects available test/lint commands
3. Pre-commit checks can be added via `/add-code-precommit-checks`
4. Post-tool-use quality gates via `/add-code-posttooluse-quality-gates`

## Working with the Codebase

When making changes to this repository:

1. **Adding new commands**: Create `.md` files in `claude-code/commands/`
2. **Adding new agents**: Create `.md` files in `claude-code/agents/`
3. **Adding new modes**: Create `.modes.md` files in `claude-code/modes/`
4. **Adding analysis scripts**: Place Python scripts in appropriate `claude-code/scripts/analyze/` subdirectory

### Installation Script

The main installation script (`claude-code/install.sh`) handles:

- Creating `.claude/` directory structure
- Installing Python dependencies via pip
- Setting up MCP tools (optional)
- Creating backups of existing installations
- Cross-platform compatibility (macOS, Linux, Windows via WSL)

## Important Notes

1. This repository itself doesn't have traditional build/test commands - it's a collection of tools installed into other projects
2. The `test_codebase/` directory contains example projects for testing workflows
3. The `todos/wip-workflows/` directory contains experimental workflows under development
4. All agent communication flows through the build orchestrator except for specific exceptions documented in `workflow-config.md`
