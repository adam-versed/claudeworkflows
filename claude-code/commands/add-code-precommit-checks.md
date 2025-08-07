# Pre-Commit Checks

Setup pre-commit framework to enforce quality standards by preventing commits containing code violations.

## Required Workflow

**YOU MUST follow these steps in order:**

1. **Check git repository**: Verify this is a git repository (required for git hooks)

2. **Check existing setup**:

   - Look for `.pre-commit-config.yaml` in project root
   - Check if pre-commit is already installed in the git repo
   - If already configured, report and exit

3. **Install pre-commit**:

   - Check if pre-commit is available globally
   - If not, install it using pip/pipx/brew based on what's available
   - Report installation method used

4. **Analyze project and generate config**:

   - Detect project languages and frameworks
   - Select appropriate pre-commit hooks based on project type
   - Create `.pre-commit-config.yaml` with relevant hooks

5. **Install git hooks**:

   - Run `pre-commit install` to set up git hooks
   - This makes pre-commit run automatically on `git commit`

6. **Report completion**:
   - List what hooks were configured
   - Confirm pre-commit is active

## Critical Rules

- **NEVER assume specific tools**: Detect what's actually used in the project
- **NEVER overwrite existing config**: If `.pre-commit-config.yaml` exists, report and exit
- **ALWAYS verify git repository**: Pre-commit requires a git repo to function
- **ALWAYS use appropriate hooks**: Match hooks to detected languages/tools

## TypeScript/JavaScript Config Template

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-json
      - id: check-yaml
      - id: check-merge-conflict

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [javascript, typescript, jsx, tsx, json, css]

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.(js|jsx|ts|tsx)$
        types: [file]
        additional_dependencies:
          - eslint@8.56.0
          - typescript
```

## Python Config Template

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-ast
      - id: check-docstring-first
      - id: check-yaml

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

$ARGUMENTS
