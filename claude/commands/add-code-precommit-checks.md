# Pre-Commit Rules

Setup PreToolUse hooks that enforce quality standards by preventing commits containing code violations.

## Behavior

1. **Intercept Commits**: Catch git commit operations before execution
2. **Scan Staged Files**: Check all staged files for quality violations
3. **Block Violations**: Prevent commits containing rule violations with detailed error messages
4. **Enforce Standards**: Maintain code quality by preventing workarounds and disabled checks

## Process

1. **Detect Python**: Find available Python command (python3, python, or py)
2. **Setup Directory Structure**: Create `.claude/scripts/` if it doesn't exist
3. **Copy Validation Script**: Install pre-commit-rules.py to project's scripts directory
4. **Configure Permissions**: Make validation script executable
5. **Generate Hook**: Add PreToolUse hook to `.claude/settings.local.json`
6. **Confirm Setup**: Report successful configuration with Python command used and restart requirement

## Hook Template

PreToolUse hook that triggers before git commit operations to validate staged files.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_ARGS\" =~ git.*commit ]]; then echo '✅ [HOOK TRIGGERED] Running pre-commit checks' && [PYTHON_COMMAND] .claude/scripts/pre-commit-rules.py; fi"
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
- **Git Command Matching**: Hook uses bash conditionals to detect git commit commands in `$CLAUDE_TOOL_ARGS`

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

## Implementation Steps

1. **Validate Python**: Check for Python 3 availability in order: python3, python, py
2. **Create Script Directory**: Ensure `.claude/scripts/` exists
3. **Copy Validation Script**: Install pre-commit-rules.py with violation detection logic
4. **Set Executable**: Apply appropriate permissions to script
5. **Read Existing Config**: Preserve any existing hooks in settings.local.json
6. **Add PreCommit Hook**: Configure hook with detected Python command using JSON format
7. **Report Success**: Confirm hook installation, Python command used, and restart requirement

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
