# Add Quality Gates

Setup PostToolUse hooks that automatically run quality validation (lint, typecheck, build) after code modifications.

## Behavior

1. **Detect Platform**: Identify operating system (Mac/Linux vs Windows) for shell command generation
2. **Detect Project Type**: Identify package manager and project structure
3. **Analyze Scripts**: Examine existing quality gate scripts in project configuration
4. **Create Hook Configuration**: Generate cross-platform PostToolUse hooks for automatic validation
5. **Target File Patterns**: Apply hooks to relevant source files based on project type

## Implementation Process

1. **Platform Detection**: Identify operating system for appropriate shell syntax
2. **Project Environment Detection**: Identify package manager and build tools
   - Node.js: package.json (npm, yarn, pnpm, bun)
   - Rust: Cargo.toml
   - Python: pyproject.toml, setup.py
   - Go: go.mod
3. **Quality Script Analysis**: Check for existing lint, typecheck, and build commands
4. **Missing Script Setup**: Add quality scripts if they don't exist
5. **Hook Generation**: Create `.claude/settings.local.json` with platform-specific PostToolUse hooks
6. **Configuration Report**: Confirm successful setup with hook details and restart requirement


## Important Notes

- **Hook Visibility**: Echo messages are only visible when using Ctrl+R verbose mode
- **Activation**: After adding hooks, you must exit and restart Claude Code for the new hooks to become active
- **File Pattern Matching**: Uses shell conditionals (POSIX `case` for Mac/Linux, PowerShell regex for Windows) to check `$CLAUDE_TOOL_ARGS` for file extensions
- **Cross-Platform Support**: Automatically detects platform and generates appropriate shell commands

## Example Usage

```bash
# Setup quality gates for current project
/add-code-posttooluse-quality-gates

# The command will auto-detect project type and configure appropriate hooks
```


## Generated Configuration

Quality gate commands vary by project type and available tools.

### For TypeScript/JavaScript Projects:

**Mac/Linux:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in *.ts|*.tsx|*.js|*.jsx) echo \"✅ [HOOK TRIGGERED] Running quality gates after file edit...\" && npm run lint && npm run typecheck && npm run build ;; esac'"
          }
        ]
      }
    ]
  }
}
```

**Windows:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"if ($env:CLAUDE_TOOL_ARGS -match '\\.(ts|tsx|js|jsx)$') { Write-Host '✅ [HOOK TRIGGERED] Running quality gates after file edit...'; npm run lint; npm run typecheck; npm run build }\""
          }
        ]
      }
    ]
  }
}
```

### For Python Projects:

**Mac/Linux:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in *.py) echo \"✅ [HOOK TRIGGERED] Running quality gates after file edit...\" && ruff check && mypy . && python -m build ;; esac'"
          }
        ]
      }
    ]
  }
}
```

**Windows:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"if ($env:CLAUDE_TOOL_ARGS -match '\\.py$') { Write-Host '✅ [HOOK TRIGGERED] Running quality gates after file edit...'; ruff check; mypy .; python -m build }\""
          }
        ]
      }
    ]
  }
}
```

### For Rust Projects:

**Mac/Linux:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in *.rs) echo \"✅ [HOOK TRIGGERED] Running quality gates after file edit...\" && cargo clippy && cargo check && cargo build ;; esac'"
          }
        ]
      }
    ]
  }
}
```

**Windows:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"if ($env:CLAUDE_TOOL_ARGS -match '\\.rs$') { Write-Host '✅ [HOOK TRIGGERED] Running quality gates after file edit...'; cargo clippy; cargo check; cargo build }\""
          }
        ]
      }
    ]
  }
}
```

$ARGUMENTS
