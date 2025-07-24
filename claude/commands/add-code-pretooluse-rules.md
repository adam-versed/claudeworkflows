# Setup Coding Rules

This command adds PreToolUse event hooks that enforce coding style guidance from rules files. The LLM will be forced to read and apply the specified rules file before making any code edits.

## Behavior

Creates PreToolUse hooks for Edit, MultiEdit, and Write tools that:

1. **Copy Rules File**: Copies the specified rules file to `.claude/rules/` directory
2. **Create Hook Configuration**: Adds PreToolUse hooks to `.claude/settings.local.json`
3. **Enforce Rules Reading**: Forces Claude to read the rules file before code modifications
4. **Target Specific Files**: Only applies rules to files matching the specified glob patterns

## Process

1. **Parse Arguments**: Extract rules file path and glob patterns from user input
2. **Create Rules Directory**: Ensure `.claude/rules/` directory exists
3. **Copy Rules File**: Copy the source rules file to the project's `.claude/rules/` folder
4. **Generate Hook Configuration**: Add PreToolUse hooks to `.claude/settings.local.json` that:
   - Trigger on Edit, MultiEdit, and Write tools
   - Match the specified file glob patterns using bash conditionals
   - Execute a command that reads the rules file and applies guidance
5. **Configure Rule Enforcement**: Set up hooks to read rules before any code modification

## Hook Template

The generated hooks will follow this pattern in JSON format:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_ARGS\" =~ [glob_pattern] ]]; then echo '✅ [HOOK TRIGGERED] Reading coding rules from .claude/rules/[rules-file]' && cat .claude/rules/[rules-file]; fi"
          }
        ]
      }
    ]
  }
}
```

## Important Notes

- **Hook Visibility**: Echo messages are only visible when using Ctrl+R verbose mode
- **Activation**: After adding hooks, you must exit and restart Claude Code for the new hooks to become active
- **File Path Matching**: Since direct file path matching isn't supported, hooks use bash conditionals to check `$CLAUDE_TOOL_ARGS`

## Arguments Format

Usage: `/setup-coding-rules <rules-file-path> <glob-patterns>`

- **rules-file-path**: Path to the source rules file to copy (e.g., `~/coding-standards.md`)
- **glob-patterns**: Space-separated file patterns to target (e.g., `"*.ts" "*.tsx" "*.js"`)

## Example Usage

```bash
# Setup TypeScript coding rules for all TS/TSX files
/setup-coding-rules ~/my-coding-standards.md "*.ts" "*.tsx"

# Setup Python coding rules for Python files
/setup-coding-rules ./python-style-guide.md "*.py"

# Setup general coding rules for multiple file types
/setup-coding-rules ./team-coding-standards.md "*.ts" "*.tsx" "*.js" "*.jsx" "*.py"
```

## Implementation Steps

1. **Validate Input**: Ensure rules file exists and glob patterns are provided
2. **Setup Directory Structure**: Create `.claude/rules/` if it doesn't exist
3. **Copy Rules File**: Copy source file to `.claude/rules/` with same filename
4. **Read Existing Settings**: Read current `.claude/settings.local.json` to preserve existing hooks
5. **Generate New Hooks**: Create PreToolUse hooks with the specified configuration using JSON format
6. **Update Settings**: Merge new hooks into `.claude/settings.local.json`
7. **Confirm Setup**: Report successful configuration with hook details and restart requirement

$ARGUMENTS
