# setup-dev-monitoring v0.2

**Purpose**: Establish comprehensive development monitoring infrastructure for any project structure through LLM-driven analysis and cross-platform automation.

## Phase 1: Project Component Discovery

1. Use LS and Glob tools to explore project structure without assumptions
2. Analyze project to identify runnable/compilable components and determine appropriate log labels:
   - **Frontend examples**: Next.js web → FRONTEND, React app → WEB, Vue.js → UI
   - **Backend examples**: Express API → API, Convex database → BACKEND, FastAPI → SERVER
   - **Services examples**: Redis → CACHE, PostgreSQL → DB, Worker processes → WORKER
   - **Build tools**: Webpack → BUILD, Vite → DEV, TypeScript → COMPILE
3. Identify each component's:
   - Entry point and start command
   - Port/endpoint if applicable
   - Technology stack and framework
   - Development vs production behavior
4. Document component structure with proposed log labels

## Phase 2: Watch Pattern Analysis

1. Determine file watching requirements based on discovered technologies:
   - **Native hot-reload**: Next.js, Vite, Create React App (no additional watching needed)
   - **Requires watching**: Static sites, custom builds, non-framework projects
   - **Watch patterns**: `src/**/*.{ts,tsx,js,jsx}`, `**/*.py`, `**/*.go`, etc.
2. Identify technologies that handle their own file watching vs. those needing external tools
3. **STOP** → "Component analysis complete. Proceed with setup? (y/n)"

## Phase 3: System Dependencies Check and Install

1. Use Glob tool to locate dependency script: `**/scripts/utils/check_system_dependencies.py`
2. Execute dependency check:

```bash
python [resolved_path]/check_system_dependencies.py --monitoring --install-commands
```

3. If missing dependencies found, use Glob tool to locate installation script: `**/scripts/utils/install_monitoring_tools.py`
4. Execute dry-run to preview installation plan:

```bash
python [resolved_path]/install_monitoring_tools.py --project-type [component_types] --dry-run
```

5. Present dry-run results showing what would be installed
6. **STOP** → "Proceed with dependency installation? (y/n)"
7. If approved, run installation without --dry-run flag

## Phase 4: Makefile Generation

1. Use Glob tool to locate Makefile generation script: `**/scripts/utils/generate_makefile.py`
2. Execute Makefile generation with component analysis:

```bash
python [resolved_path]/generate_makefile.py \
  --components '[component_json]' \
  --watch-patterns '[watch_patterns_json]' \
  --output-dir [current_directory]
```

3. Review generated Makefile targets and safety warnings

## Phase 5: Procfile Generation

1. Use Glob tool to locate Procfile generation script: `**/scripts/utils/generate_procfile.py`
2. Execute Procfile generation with component details:

```bash
python [resolved_path]/generate_procfile.py \
  --components '[component_json]' \
  --log-format unified \
  --output-dir [current_directory]
```

3. Review generated service definitions and log formatting

## Phase 6: Project CLAUDE.md Integration

1. Use Glob tool to locate CLAUDE.md update script: `**/scripts/setup/dev-monitoring/update_claude_md.py`
2. Execute CLAUDE.md update to add development workflow commands:

```bash
python [resolved_path]/update_claude_md.py \
  --project-dir [current_directory] \
  --components '[component_json]'
```

3. Script will:
   - Create CLAUDE.md if it doesn't exist
   - Add "Development Workflow Commands (Make-based)" section
   - Include service management restrictions and available commands
   - Document log files and debugging workflow

## Phase 6: Validation and Testing

1. Validate generated files:
   - Makefile syntax check
   - Procfile service definitions
   - Log aggregation setup
   - Health check endpoints
   - CLAUDE.md exists and contains make commands
2. Test monitoring infrastructure:
   - Execute `make status` to verify commands work
   - Check log file creation capability
   - Validate component health checks
3. **STOP** → "Monitoring setup complete. Test successful? (y/n)"

## Optional Flags

- `--c7`: Research technology-specific monitoring and watch capabilities
- `--seq`: Detailed step-by-step analysis breakdown
