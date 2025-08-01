# This does trigger correctly - but finding pretool checks largely ineffective at the moment, will re-introduce later.

# Setup Coding Rules

This command adds PreToolUse event hooks that enforce coding style guidance from rules files. The LLM will be forced to read and apply the specified rules file before making any code edits.

## Behavior

Creates PreToolUse hooks for Edit, MultiEdit, and Write tools that:

1. **Detect Platform**: Identify operating system (Mac/Linux vs Windows) for shell command generation
2. **Copy Rules File**: Copies the specified rules file to `.claude/rules/` directory
3. **Create Hook Configuration**: Adds cross-platform PreToolUse hooks to `.claude/settings.local.json`
4. **Enforce Rules Reading**: Forces Claude to read the rules file before code modifications
5. **Target Specific Files**: Only applies rules to files matching the specified glob patterns

## Implementation Process

1. **Platform Detection**: Identify operating system for appropriate shell syntax
2. **Parse Arguments**: Extract rules file path and glob patterns from user input
3. **Create Rules Directory**: Ensure `.claude/rules/` directory exists
4. **Copy Rules File**: Copy the source rules file to the project's `.claude/rules/` folder
5. **Generate Hook Configuration**: Add platform-specific PreToolUse hooks to `.claude/settings.local.json` that:
   - Trigger on Edit, MultiEdit, and Write tools
   - Match the specified file glob patterns using cross-platform conditionals
   - Execute a command that reads the rules file and applies guidance
6. **Configure Rule Enforcement**: Set up hooks to read rules before any code modification

## Hook Templates

### Mac/Linux (using sh):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in [pattern]) echo \"✅ [HOOK TRIGGERED] Reading coding rules from .claude/rules/[rules-file]\" && cat .claude/rules/[rules-file] ;; esac'"
          }
        ]
      }
    ]
  }
}
```

### Windows (using PowerShell):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"if ($env:CLAUDE_TOOL_ARGS -match '[regex_pattern]') { Write-Host '✅ [HOOK TRIGGERED] Reading coding rules from .claude/rules/[rules-file]'; Get-Content .claude/rules/[rules-file] }\""
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
- **File Path Matching**: Uses shell conditionals (POSIX `case` for Mac/Linux, PowerShell regex for Windows) to check `$CLAUDE_TOOL_ARGS` for file patterns
- **Cross-Platform Support**: Automatically detects platform and generates appropriate shell commands

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

$ARGUMENTS
