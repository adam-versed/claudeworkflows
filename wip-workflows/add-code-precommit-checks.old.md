# Pre-Commit Rules

This command adds a pre-commit hook to a project's `.claude/settings.toml` that enforces specific coding rules by preventing commits that contain rule violations.

## Behavior

Creates a PreToolUse hook that intercepts git commit operations and scans staged files for rule violations. If any violations are found, the commit is blocked with detailed error messages.

## Quality Gate Rules Enforced

### Linting Rules

- Prevents adding `// eslint-disable` or similar disable comments
- Blocks modifications to lint configuration files that bypass errors

### Build Failures

- Prevents ignoring build failures
- Blocks modifications to build configuration that skip failing code

### TypeScript Rules

- Prevents adding `// @ts-ignore` comments
- Blocks using `as any` to bypass type errors
- Prevents modifying tsconfig.json to reduce strictness

### Unit Tests

- Prevents adding `.skip()` or `.todo()` to failing tests
- Blocks modifying test configuration to exclude failing tests
- Prevents using `--passWithNoTests` to bypass test requirements

### Integration Tests

- Prevents skipping or disabling failing integration tests
- Blocks modifying test configuration to exclude failing scenarios

## Process

1. **Check Python availability**: Detect the correct Python command (python3, python, or py)
2. **Check for existing .claude directory**: Create if it doesn't exist
3. **Read existing settings.toml**: Preserve any existing configuration
4. **Copy validation script**: Copy pre-commit-rules.py to project's .claude/scripts/ directory
5. **Make script executable**: Set appropriate permissions
6. **Add pre-commit hook**: Insert the quality gate enforcement hook with detected Python command
7. **Configure hook**: Set up the PreToolUse event matcher for git commits

## Hook Configuration

The generated hook will:

- Trigger on `PreToolUse` event
- Match `tool_name = "git_commit"`
- Run a Python validation script that:
  - Gets list of staged files from `git diff --cached --name-only`
  - Scans each file for quality gate violations
  - Reports specific violations with line numbers
  - Exits with failure code if any violations exist

## Implementation

The command will:

1. **Detect Python command**: Check for `python3`, `python`, or `py` and verify Python 3 availability
2. **Copy the script**: Copy `pre-commit-rules.py` to the project's `.claude/scripts/` directory
3. **Set permissions**: Make the script executable
4. **Generate hook**: Add a hook to `.claude/settings.toml` using the detected Python command

## Python Command Detection

The script checks for Python availability in this order:

1. `python3` (preferred on Unix/Linux/macOS)
2. `python` (common alias, verified to be Python 3)
3. `py` (Windows Python Launcher)

Each command is verified to actually run Python 3.x before being selected.

## Example Generated Hook

```toml
[[hooks]]
event = "PreToolUse"

[hooks.matcher]
tool_name = "git_commit"

command = "[PYTHON_COMMAND] .claude/scripts/pre-commit-rules.py"
```

Where `[PYTHON_COMMAND]` is automatically detected (e.g., `python3`, `python`, or `py`).

The Python script (`pre-commit-rules.py`) provides:

- Detailed line-by-line checking of staged files
- Support for multiple programming languages (JS/TS, Python, etc.)
- Clear violation reporting with file paths and line numbers
- Warning messages for configuration file changes
- Extensible architecture for adding new rules

## Example Usage

```
/add-code-precommit-checks
```

This will add the pre-commit quality gate enforcement hook to the current project's `.claude/settings.toml`.

$ARGUMENTS
