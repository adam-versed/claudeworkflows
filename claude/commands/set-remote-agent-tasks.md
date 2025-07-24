# Set Remote Agent Tasks

Create feature branches with task specifications for the Claude Code GitHub agent to execute independently.

## Behavior

This command analyzes the provided task instructions and creates one or more feature branches, each with detailed task specifications that tag @claude-code-github-agent. Each branch will contain a markdown file with:
- Agent tagging for autonomous execution
- References to project documentation
- Specific scope and completion criteria
- Instructions to create PR when complete

## Process

1. **Parse Task Instructions**: Extract task requirements and determine optimal branch structure
2. **Analyze Current Context**: Consider current branch, project structure, and existing documentation
3. **Plan Branch Strategy**: Determine how to split tasks across feature branches for parallel execution
4. **Create Feature Branches**: Generate branches from current branch or main as appropriate
5. **Generate Task Specifications**: Create detailed markdown files in each branch with:
   - @claude-code-github-agent tag
   - References to docs/project_analysis.md and relevant documentation
   - Specific scope boundaries and success criteria
   - Completion instructions including PR creation
6. **Commit Specifications**: Commit task files with descriptive messages
7. **Report Summary**: List all created branches and their purposes

## Task Specification Template

Each generated task file should include:
- Agent tagging: `@claude-code-github-agent`
- Required reading section referencing project docs
- Clear scope boundaries (what to include/exclude)
- Specific issues/features to address with locations
- Completion criteria including PR creation
- Important notes about maintaining compatibility

## Example Usage

- `/set-remote-agent-tasks "Implement user authentication with OAuth providers Google and GitHub, including login/logout flows and profile management"`
- `/set-remote-agent-tasks "Refactor payment processing to support multiple providers (Stripe, PayPal) with unified interface and proper error handling"`
- `/set-remote-agent-tasks "Add comprehensive logging and monitoring with structured logs, metrics collection, and alerting for critical errors"`

$ARGUMENTS