# Add Quality Gates

Setup PostToolUse hooks that automatically run quality validation (lint, typecheck, build) after code modifications.

## Required Workflow

**YOU MUST follow these steps in order:**

1. **Check for existing settings**: Read `.claude/settings.local.json` if it exists. If PostToolUse hooks already reference quality commands or scripts, report this and exit without making changes.

2. **Detect the platform**: Use system information to determine Mac/Linux vs Windows for correct shell syntax.

3. **Identify project type and discover actual commands**:

   - For Node.js projects (has package.json): Parse the scripts section and extract actual script names (NOT hardcoded assumptions)
   - For Rust projects (has Cargo.toml): Check for workspace commands
   - For Python projects (has pyproject.toml/setup.py): Check for defined scripts or Makefile targets
   - For Go projects (has go.mod): Check for Makefile or standard commands

4. **Check for quality gate scripts**: Look for `.claude/scripts/run-quality-gates.sh` or similar. If found, prefer using this over individual commands.

5. **Analyze discovered commands for redundancy**:

   - If a quality script exists that already runs multiple checks, use only that
   - If commands overlap (e.g., both `check` and `lint` where `check` includes linting), use only the comprehensive one
   - NEVER generate hooks for commands that don't exist in the project

6. **Generate hooks using discovered commands**:

   - Use the actual command names found in step 3
   - If no quality commands exist, report this and suggest what could be added
   - Merge with existing PostToolUse entries if they exist (don't create duplicate blocks)

7. **Report what was done**: List discovered commands, what hooks were created, and what was skipped due to existing configuration.

## Critical Rules

- **NEVER assume command names**: Do not assume `npm run lint`, `ruff check`, etc. exist. Always discover actual commands.
- **NEVER create duplicate hooks**: If PostToolUse already has quality checks, exit with a report.
- **NEVER add commands that don't exist**: Only create hooks for commands found in project configuration.
- **ALWAYS prefer consolidated scripts**: If `.claude/scripts/run-quality-gates.sh` exists, use it instead of individual commands.
- **ALWAYS check for command overlap**: Don't run both `npm run check` and `npm run lint` if `check` already includes linting.

## Example Usage

```bash
# Setup quality gates for current project
/add-code-posttooluse-quality-gates

# The command will:
# 1. Analyze your project to find actual quality commands
# 2. Check for existing hooks to avoid duplication
# 3. Generate hooks only for commands that exist
```

## Example Behaviors

### Scenario 1: Fresh project with package.json

**Discovery phase output:**

```
Analyzing project configuration...
✓ Found package.json
✓ Discovered scripts:
  - check: "biome check ."
  - typecheck: "tsc --noEmit"
✓ No existing quality gate hooks found
✓ No .claude/scripts/run-quality-gates.sh found

Creating PostToolUse hook with discovered commands...
```

**Generated hook uses discovered commands:**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in *.ts|*.tsx|*.js|*.jsx) echo \"✅ [HOOK TRIGGERED] Running discovered quality gates: check, typecheck\" && npm run check && npm run typecheck ;; esac'"
          }
        ]
      }
    ]
  }
}
```

### Scenario 2: Dynamic command generation

**How echo messages should reflect discovered commands:**

If discovered: `validate: "eslint . && tsc"` and `test: "jest"`

Generated hook would be:

```json
{
  "type": "command",
  "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in *.ts|*.tsx|*.js|*.jsx) echo \"✅ [HOOK TRIGGERED] Running discovered quality gates: validate, test\" && npm run validate && npm run test ;; esac'"
}
```

If using quality script:

```json
{
  "type": "command",
  "command": "sh -c 'case \"$CLAUDE_TOOL_ARGS\" in *.ts|*.tsx|*.js|*.jsx) echo \"✅ [HOOK TRIGGERED] Running quality gate script\" && bash .claude/scripts/run-quality-gates.sh ;; esac'"
}
```

**Key point**: The echo message MUST indicate what was actually discovered and will be run, not hardcoded command names.

$ARGUMENTS
