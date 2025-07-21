# setup-dev-monitoring v0.3

**Purpose**: Establish comprehensive development monitoring infrastructure for any project structure through LLM-driven analysis and cross-platform automation.

## Phase 1: Project Component Discovery

1. Use LS and Glob tools to explore project structure without assumptions
2. Analyze project to identify runnable/compilable components and determine appropriate log labels:
   - **Frontend examples**: Next.js web → FRONTEND, React app → WEB, Vue.js → UI
   - **Backend examples**: Express API → API, Convex database → BACKEND, FastAPI → SERVER
   - **Services examples**: Redis → CACHE, PostgreSQL → DB, Worker processes → WORKER
   - **Build tools**: Webpack → BUILD, Vite → DEV, TypeScript → COMPILE
3. Identify each component's ACTUAL start commands by examining:
   - **package.json scripts**: `"dev"`, `"start"`, `"serve"` commands
   - **Directory structure**: Look for `cd apps/web && npm run dev` patterns
   - **Framework detection**: Next.js (`next dev`), Convex (`npx convex dev`), etc.
   - **Port configuration**: Extract PORT settings from package.json or framework defaults
4. **CRITICAL**: Never use placeholder commands like `echo "No start command defined"` - always find actual runnable commands
5. **MANDATORY VALIDATION**: Before proceeding to file generation, ensure ALL components have valid start_command values:
   - Each component MUST have real commands like `npm run dev`, `npx convex dev`, `python manage.py runserver`
   - NO placeholder text, empty strings, or default values allowed
   - Makefile generation will FAIL if any component lacks a proper start command
6. Document component structure with proposed log labels AND verified start commands

## Phase 2: Component Overlap Analysis

1. Analyze the components discovered in Phase 1 to identify overlaps where:
   - **Single-focus components**: Target a specific service (e.g., `npm run dev` in `apps/frontend`)
   - **Multi-focus components**: Orchestrate multiple services (e.g., `turbo run dev`, `lerna run dev`, `docker-compose up`)
   - **Same service via different paths**: Both direct and orchestrated commands starting the same service

2. **Overlap detection principles**:
   - If a global orchestrator command (multi-focus) starts the same services as individual commands (single-focus), DROP the orchestrator
   - If multiple commands start the same service on the same port, KEEP only the most specific one
   - Prefer individual component commands over orchestrators for better log attribution
   - Example: If you have `frontend`, `backend`, AND `turbo run dev` that starts both, DROP `turbo`

3. **Port conflict analysis**:
   - Check if multiple components specify the same port
   - If conflicts exist, note which components conflict and recommend resolution

4. **Create refined component list**:
   - Remove multi-focus orchestrators that duplicate single-focus components
   - Keep standalone services that aren't covered by orchestrators
   - Ensure each service is started exactly once

5. **STOP** → "Component overlap analysis complete. Remove [list components to drop]? (y/n)"
   - Show original component count vs refined count
   - List specific components being dropped and why
   - If no overlaps detected, proceed without changes

## Phase 3: Watch Pattern Analysis

1. Determine file watching requirements based on discovered technologies:
   - **Native hot-reload**: Next.js, Vite, Create React App (no additional watching needed)
   - **Requires watching**: Static sites, custom builds, non-framework projects
   - **EXCLUDE from watching**: Documentation files (_.md), log files (_.log), config files
   - **Watch patterns**: Only source code - `src/**/*.{ts,tsx,js,jsx}`, `**/*.py`, `**/*.go`, etc.
2. **Default approach**: Allow projects with NO custom watch requirements - framework hot-reload is sufficient
3. Identify technologies that handle their own file watching vs. those needing external tools
4. **STOP** → "Component analysis complete. Proceed with setup? (y/n)"

## Phase 7: System Dependencies Check and Install

1. Use Glob tool to locate installer script: `~/.claude/**/scripts/setup/dev-monitoring/install_monitoring_tools.py` OR `**/scripts/setup/dev-monitoring/install_monitoring_tools.py`
2. Execute dependency check and installation (script includes integrated prerequisite checking):

```bash
python [resolved_path]/install_monitoring_tools.py --dry-run --project-type [detected_types]
```

3. **Parse dry-run output** to identify:
   - Prerequisites status (Python, Git, Node.js)
   - Tools already installed (skip these)
   - Only missing dependencies that need installation
4. **ONLY if missing dependencies found**, run actual installation:

```bash
python [resolved_path]/install_monitoring_tools.py --project-type [detected_types]
```

5. **STOP** → "Install missing dependencies: [list only missing tools]? (y/n)"
6. If approved, execute only the installation commands for missing tools

## Phase 3.5: Existing File Handling

1. Check for existing Procfile and Makefile in current directory:
   ```bash
   if [ -f "Procfile" ] || [ -f "Makefile" ]; then
       echo "Existing files found:"
       [ -f "Procfile" ] && echo "  - Procfile"
       [ -f "Makefile" ] && echo "  - Makefile"
   fi
   ```
2. If existing files found:
   - **STOP** → "Existing Procfile/Makefile found. Choose action: (b)ackup existing files, (o)verwrite, or (c)ancel?"
   - If backup chosen: Create timestamped backups before proceeding
     ```bash
     TIMESTAMP=$(date +%Y%m%d_%H%M%S)
     [ -f "Procfile" ] && cp Procfile "Procfile.backup.$TIMESTAMP"
     [ -f "Makefile" ] && cp Makefile "Makefile.backup.$TIMESTAMP"
     ```
   - If overwrite chosen: Continue to next phase
   - If cancel chosen: Exit workflow
3. If no existing files: Continue to next phase

## Phase 7: Makefile Generation

1. Use Glob tool to locate Makefile generation script: `~/.claude/**/scripts/utils/generate_makefile.py` OR `**/scripts/utils/generate_makefile.py`
2. Execute Makefile generation with component analysis:

```bash
python [resolved_path]/generate_makefile.py \
  --components '[component_json]' \
  --watch-patterns '[watch_patterns_json]' \
  --output-dir [current_directory]
```

3. Review generated Makefile targets and safety warnings

## Phase 7: Procfile Generation

1. Use Glob tool to locate Procfile generation script: `~/.claude/**/scripts/utils/generate_procfile.py` OR `**/scripts/utils/generate_procfile.py`
2. Execute Procfile generation with component details:

```bash
python [resolved_path]/generate_procfile.py \
  --components '[component_json]' \
  --log-format unified \
  --output-dir [current_directory] \
  --force-logging
```

3. **CRITICAL**: Ensure ALL frontend and backend components include logging pipeline:
   - Every service MUST pipe output to `./dev.log` with timestamps
   - Format: `2>&1 | while IFS= read -r line; do echo "[$(date '+%H:%M:%S')] [SERVICE] $line"; done | tee -a ./dev.log`
   - Even services without custom watches must log their output
   - No service should run without contributing to unified logging
4. Review generated service definitions and log formatting

## Phase 7: Project CLAUDE.md Integration

1. Use Glob tool to locate CLAUDE.md update script: `~/.claude/**/scripts/setup/dev-monitoring/update_claude_md.py` OR `**/scripts/setup/dev-monitoring/update_claude_md.py`
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

## Phase 7: Validation and Testing

1. **CRITICAL VALIDATION** - Check generated files contain real commands:
   - **Makefile**: NO `echo "No start command defined"` placeholders allowed - must use actual start commands from component analysis
   - **Procfile**: All services must have actual runnable commands (npm run dev, npx convex dev, etc.)
   - **Log paths**: Must use `./dev.log` NOT `/dev.log` (read-only filesystem) in both Makefile and Procfile
   - All services must include proper logging pipeline with timestamps
2. Validate other files:
   - Makefile syntax check
   - Log aggregation setup works
   - CLAUDE.md exists and contains make commands
3. Test monitoring infrastructure:
   - Execute `make status` to verify commands work
   - Verify log file creation uses writable path
   - Test that frontend/backend components can start and log output
4. **STOP** → "Monitoring setup complete and validated. All services have real start commands? (y/n)"

## Optional Flags

- `--c7`: Research technology-specific monitoring and watch capabilities
- `--seq`: Detailed step-by-step analysis breakdown
