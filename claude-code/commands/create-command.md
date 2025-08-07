# Create Claude Code Command

Create a new Claude Code slash command based on the task description provided in $ARGUMENTS.

## Behavior

**IMPORTANT**: Focus on clarity and specific requirements rather than vague quality descriptors. Avoid prompting for "production-ready" code - this often leads to over-engineering.

Parse the arguments to extract:

1. **Scope**: "project" or "user" (default to project if not specified)
2. **Command name**: The name for the new command
3. **Task description**: What the command should do

**Proactively**: Suggest improvements and take initiative in command design when beneficial.

Based on the scope:

- For "project" scope: Create the command file in `./commands/[command-name].md`
- For "user" scope: Create the command file in `$HOME/.claude/commands/[command-name].md`

## Command File Requirements

The generated command file should:

1. Have a clear title matching the command name
2. Include specific, actionable instructions that direct Claude to perform the task
3. Reference $ARGUMENTS where user input will be provided
4. Use "think" for complex analysis needs (avoid over-analysis)
5. **IMPORTANT**: Avoid backward compatibility unless specifically needed - Claude tends to preserve old code unnecessarily

## Process

1. **Parse Arguments**: Extract scope, command name, and task description from $ARGUMENTS
2. **Determine File Path**: Choose appropriate directory based on scope
3. **Create Directory**: Ensure the target directory exists (create ./claude_commands/ if needed for project scope)
4. **Generate Command File**: think harder and create the command file with proper structure and content
5. **Confirm Creation**: Report the file location and provide usage instructions

## Template Structure

```markdown
# [Command Name Title]

[Clear, specific task description and instructions for Claude]

## Behavior

**IMPORTANT**: [Single critical instruction using IMPORTANT keyword instead of repetition]

[Specific instructions on what Claude should do when this command is invoked]

## Process

[Step-by-step process if applicable]

If complex analysis is needed, use "think" to trigger more thorough analysis (use sparingly).

$ARGUMENTS
```

## Example Usage

- `/create-command user lint-fix "Run linting tools and automatically fix issues in the codebase"`
- `/create-command project deploy-staging "Deploy the current branch to staging environment with pre-deployment checks"`

$ARGUMENTS
