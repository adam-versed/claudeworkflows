# Pre-Commit Rules

Setup PreToolUse hooks that enforce quality standards by preventing commits containing code violations.

## Behavior

1. **Detect Platform**: Identify operating system (Mac/Linux vs Windows) for shell command generation
2. **Intercept Commits**: Catch git commit operations before execution
3. **Scan Staged Files**: Check all staged files for quality violations
4. **Block Violations**: Prevent commits containing rule violations with detailed error messages
5. **Enforce Standards**: Maintain code quality by preventing workarounds and disabled checks

## Implementation Process

1. **Platform Detection**: Identify operating system for appropriate shell syntax
2. **Detect Python**: Find available Python command (python3, python, or py) with platform-specific detection
3. **Setup Directory Structure**: Create `.claude/scripts/` if it doesn't exist
4. **Copy Validation Script**: Install pre-commit-rules.py to project's scripts directory
5. **Configure Permissions**: Make validation script executable (Unix-like systems)
6. **Generate Hook**: Add cross-platform PreToolUse hook to `.claude/settings.local.json`
7. **Confirm Setup**: Report successful configuration with Python command used and restart requirement

## Hook Templates

PreToolUse hooks that trigger before git commit operations to validate staged files.

### Mac/Linux (using sh):
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in *git*commit*) echo \"✅ [HOOK TRIGGERED] Running pre-commit checks\" && [PYTHON_COMMAND] .claude/scripts/pre-commit-rules.py ;; esac'"
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
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"if ($env:CLAUDE_TOOL_ARGS -match 'git.*commit') { Write-Host '✅ [HOOK TRIGGERED] Running pre-commit checks'; [PYTHON_COMMAND] .claude/scripts/pre-commit-rules.py }\""
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
- **Git Command Matching**: Uses shell conditionals (POSIX `case` for Mac/Linux, PowerShell regex for Windows) to detect git commit commands in `$CLAUDE_TOOL_ARGS`
- **Cross-Platform Support**: Automatically detects platform and generates appropriate shell commands
- **Python Detection**: Identifies correct Python executable for each platform (python3/python on Unix, py on Windows)

## Quality Rules Enforced

### Linting Violations

- **Disabled Linting**: Prevents `// eslint-disable` or similar comments
- **Config Bypasses**: Blocks modifications to lint configs that ignore errors

### Type Safety Violations

- **Type Ignores**: Prevents `// @ts-ignore` comments
- **Any Types**: Blocks `as any` type assertions
- **Config Weakening**: Prevents reducing tsconfig.json strictness

### Test Violations

- **Skipped Tests**: Prevents `.skip()` or `.todo()` on failing tests
- **Test Exclusions**: Blocks config changes that exclude failing tests
- **No-Test Flags**: Prevents `--passWithNoTests` usage

### Build Violations

- **Build Failures**: Prevents ignoring build errors
- **Config Bypasses**: Blocks build config changes that skip failures

## Example Usage

```bash
# Add pre-commit quality checks to current project
/add-code-precommit-checks

# The hook will automatically detect Python and configure validation
```


## Generated Configuration

The validation script provides comprehensive checking across multiple languages.

### Script Features:

- Line-by-line analysis of staged files
- Multi-language support (JavaScript, TypeScript, Python, etc.)
- Clear violation reporting with file:line references
- Configuration change warnings
- Extensible rule architecture

### Example Output:

```
Quality Gate Violations Found:

src/app.ts:45 - Found '// @ts-ignore' comment
src/utils.js:23 - Found 'eslint-disable' directive
tests/api.test.ts:89 - Found '.skip()' on test

Commit blocked. Fix violations before committing.
```

$ARGUMENTS
