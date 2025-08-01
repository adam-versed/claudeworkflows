# Create Claude Code Command

Create a new Claude Code slash command based on the task description provided in $ARGUMENTS.

## Behavior

Parse the arguments to extract:

1. **Scope**: "project" or "system" (default to project if not specified)
2. **Command name**: The name for the new command
3. **Task description**: What the command should do

Based on the scope:

- For "project" scope: Create the command file in `./claude_commands/[command-name].md`
- For "system" scope: Create the command file in `~/.claude/commands/[command-name].md`

## Command File Requirements

The generated command file should:

1. Have a clear title matching the command name
2. Include instructions that direct Claude to perform the specified task
3. Reference $ARGUMENTS where user input will be provided
4. Include an example usage showing how to invoke the command

## Process

1. **Parse Arguments**: Extract scope, command name, and task description from $ARGUMENTS
2. **Determine File Path**: Choose appropriate directory based on scope
3. **Create Directory**: Ensure the target directory exists (create ./claude_commands/ if needed for project scope)
4. **Generate Command File**: Create the command file with proper structure and content
5. **Confirm Creation**: Report the file location and provide usage instructions

## Template Structure

```markdown
# [Command Name Title]

[Task description and instructions for Claude]

## Behavior

[Detailed instructions on what Claude should do when this command is invoked]

## Process

[Step-by-step process if applicable]

$ARGUMENTS
```

## Example Usage

- `/create-command system lint-fix "Run linting tools and automatically fix issues in the codebase"`
- `/create-command project deploy-staging "Deploy the current branch to staging environment with pre-deployment checks"`

$ARGUMENTS
