# Add Quality Gates

This command automatically sets up quality gate hooks in the current project by creating a `.claude/settings.toml` file with post-tool-use hooks that run linting, type checking, and build validation after file edits.

## Behavior

1. **Detect Package Manager**: Identify which package manager is being used (npm, yarn, pnpm, bun, etc.)
2. **Check Existing Scripts**: Examine package.json or equivalent to find existing quality gate scripts
3. **Create Missing Scripts**: If quality gate scripts don't exist, add them to the package configuration
4. **Generate Hook Configuration**: Create `.claude/settings.toml` with appropriate hooks based on the project type

## Process

1. **Identify Project Type and Package Manager**:

   - Check for package.json (Node.js projects)
   - Check for Cargo.toml (Rust projects)
   - Check for pyproject.toml or setup.py (Python projects)
   - Check for go.mod (Go projects)

2. **Analyze Existing Scripts**:

   - Look for existing lint, typecheck, and build scripts
   - Identify the specific tools being used (ESLint, Biome, TSC, etc.)

3. **Setup Missing Quality Gates**:

   - If no lint script exists, add one based on available tools
   - If no build script exists, add one based on project type
   - If no typecheck script exists (for TypeScript projects), add one

4. **Create Hook Configuration**:
   - Generate `.claude/settings.toml` with PostToolUse hooks
   - Configure hooks to run on appropriate file patterns
   - Include all relevant quality gate commands

## Hook Template

The generated hooks should follow this pattern:

```toml
[[hooks]]
event = "PostToolUse"

[hooks.matcher]
tool_name = "Edit"
file_paths = ["*.ts", "*.tsx", "*.js", "*.jsx"]  # Adjust based on project

command = "echo 'Running quality gates...' && [LINT_COMMAND] && [TYPECHECK_COMMAND] && [BUILD_COMMAND]"
```

## Supported Quality Gates

### Lint Commands

- `npm run lint`, `yarn lint`, `pnpm lint`, `bun lint`
- `eslint`, `biome check`, `ruff check`
- `uv run lint`, `poetry run lint`

### Build Commands

- `npm run build`, `yarn build`, `pnpm build`, `bun build`
- `cargo build`, `go build`, `dotnet build`
- `tsc`, `webpack`, `vite build`, `next build`
- `uv run build`, `poetry run build`

### Type Check Commands

- `tsc --noEmit`
- `npm run typecheck`, `yarn typecheck`, `pnpm typecheck`, `bun typecheck`
- `uv run typecheck`

## Example Usage

```
/add-code-posttooluse-quality-gates.md
```

This will analyze the current project and set up appropriate quality gate hooks.

$ARGUMENTS
