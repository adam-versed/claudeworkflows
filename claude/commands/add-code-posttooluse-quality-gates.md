# Add Quality Gates

Setup PostToolUse hooks that automatically run quality validation (lint, typecheck, build) after code modifications.

## Behavior

1. **Detect Project Type**: Identify package manager and project structure
2. **Analyze Scripts**: Examine existing quality gate scripts in project configuration
3. **Create Hook Configuration**: Generate PostToolUse hooks for automatic validation
4. **Target File Patterns**: Apply hooks to relevant source files based on project type

## Process

1. **Identify Project Environment**: Detect package manager and build tools
   - Node.js: package.json (npm, yarn, pnpm, bun)
   - Rust: Cargo.toml
   - Python: pyproject.toml, setup.py
   - Go: go.mod
2. **Analyze Quality Scripts**: Check for existing lint, typecheck, and build commands
3. **Setup Missing Scripts**: Add quality scripts if they don't exist
4. **Generate Hook Configuration**: Create `.claude/settings.local.json` with PostToolUse hooks
5. **Report Configuration**: Confirm successful setup with hook details and restart requirement

## Hook Template

PostToolUse hooks that trigger after Edit, MultiEdit, or Write operations on source files.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_ARGS\" =~ .*\\.(tsx?|jsx?) ]]; then echo '✅ [HOOK TRIGGERED] Running quality gates after file edit...' && npm run lint && npm run typecheck && npm run build; fi"
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
- **File Pattern Matching**: Uses bash conditionals to check `$CLAUDE_TOOL_ARGS` for file extensions

## Example Usage

```bash
# Setup quality gates for current project
/add-code-posttooluse-quality-gates

# The command will auto-detect project type and configure appropriate hooks
```

## Implementation Steps

1. **Validate Project**: Ensure project has recognizable structure
2. **Detect Build System**: Identify package manager and available commands
3. **Check Existing Scripts**: Read project configuration for quality commands
4. **Generate Commands**: Build appropriate command chain for detected tools
5. **Configure Hooks**: Create PostToolUse hooks with quality gate commands using JSON format
6. **Update Settings**: Write hooks to `.claude/settings.local.json`
7. **Confirm Setup**: Report configured quality gates, file patterns, and restart requirement

## Generated Configuration

Quality gate commands vary by project type and available tools.

### For TypeScript/JavaScript Projects:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_ARGS\" =~ .*\\.(tsx?|jsx?) ]]; then echo '✅ [HOOK TRIGGERED] Running quality gates after file edit...' && npm run lint && npm run typecheck && npm run build; fi"
          }
        ]
      }
    ]
  }
}
```

### For Python Projects:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_ARGS\" =~ \\.py$ ]]; then echo '✅ [HOOK TRIGGERED] Running quality gates after file edit...' && ruff check && mypy . && python -m build; fi"
          }
        ]
      }
    ]
  }
}
```

### For Rust Projects:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_ARGS\" =~ \\.rs$ ]]; then echo '✅ [HOOK TRIGGERED] Running quality gates after file edit...' && cargo clippy && cargo check && cargo build; fi"
          }
        ]
      }
    ]
  }
}
```

$ARGUMENTS
