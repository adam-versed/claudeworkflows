# setup-dev-monitoring v0.91

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

1. Review discovered components for overlaps:
   - **Single-focus**: Commands that start one service (e.g., `npm run dev` in specific directory)
   - **Multi-focus**: Orchestrators that start multiple services (e.g., `turbo run dev`, `docker-compose up`)
   - **Duplicates**: Same service started via different commands
2. **Exclusion principle**: When orchestrator commands overlap with individual component commands, exclude the orchestrator for better log attribution
3. Identify port conflicts between components
4. 🛑 **STOP - USER CONFIRMATION REQUIRED** → "Exclude overlapping components: [list components to exclude from monitoring]? (y/n)"
5. Do not proceed until user confirmation received

## Phase 3: Watch Pattern Analysis

1. Determine file watching requirements based on discovered technologies:
   - **Native hot-reload**: Next.js, Vite, Create React App (no additional watching needed)
   - **Requires watching**: Static sites, custom builds, non-framework projects
   - **EXCLUDE from watching**: Documentation files (_.md), log files (_.log), config files
   - **Watch patterns**: Only source code - `src/**/*.{ts,tsx,js,jsx}`, `**/*.py`, `**/*.go`, etc.
2. **Default approach**: Allow projects with NO custom watch requirements - framework hot-reload is sufficient
3. Identify technologies that handle their own file watching vs. those needing external tools
4. 🛑 **STOP - USER CONFIRMATION REQUIRED** → "Component analysis complete. Proceed with setup? (y/n)"
5. Do not proceed until user confirmation received

## Phase 4: System Dependencies Check and Install

1. **Try project level first**: Use Glob tool to locate installer script: `**/scripts/setup/dev-monitoring/install_monitoring_dependencies.py`
2. **If not found, try user level**: Use Bash tool to get home directory and construct path: `$HOME/.claude/scripts/setup/dev-monitoring/install_monitoring_dependencies.py`
3. Execute dependency check and installation (script includes integrated prerequisite checking):

```bash
python [resolved_path]/install_monitoring_dependencies.py --dry-run
```

4. Parse dry-run output to identify:
   - Prerequisites status (Python 3.x)
   - Core tools status (make, watchexec, foreman)
   - Only missing dependencies that need installation
5. ONLY if missing dependencies found: 🛑 STOP - USER CONFIRMATION REQUIRED → “Install missing core tools: [list only missing tools]? (y/n)”
   - Only proceed with installation if user approves:

```bash
python [resolved_path]/install_monitoring_dependencies.py
```

## Phase 5: Existing File Handling

1. Check for existing Procfile and Makefile in current directory:
   ```bash
   if [ -f "Procfile" ] || [ -f "Makefile" ]; then
       echo "Existing files found:"
       [ -f "Procfile" ] && echo "  - Procfile"
       [ -f "Makefile" ] && echo "  - Makefile"
   fi
   ```
2. If existing files found:
   - 🛑 **STOP - USER CONFIRMATION REQUIRED** → "Existing Procfile/Makefile found. Choose action: (b)ackup existing files, (o)verwrite, or (c)ancel?"
   - Do not proceed until user confirmation received
   - Respect user choice: backup, overwrite, or cancel workflow
   - If backup chosen: Create timestamped backups before proceeding
     ```bash
     TIMESTAMP=$(date +%Y%m%d_%H%M%S)
     [ -f "Procfile" ] && cp Procfile "Procfile.backup.$TIMESTAMP"
     [ -f "Makefile" ] && cp Makefile "Makefile.backup.$TIMESTAMP"
     ```
   - If overwrite chosen: Continue to next phase
   - If cancel chosen: 🛑 **STOP Exit workflow**
3. If no existing files: Continue to next phase

## Phase 6: Makefile Generation

1. Use Glob tool to locate Makefile generation script: `**/scripts/utils/generate_makefile.py`
2. **If not found, try user level**: Use Bash tool to get home directory and construct path: `$HOME/.claude/scripts/utils/generate_makefile.py`
3. Execute Makefile generation using component analysis from Phases 1-3:

```bash
python [resolved_path]/generate_makefile.py \
  --components '[
    {
      "name": "frontend",
      "label": "FRONTEND",
      "cwd": "apps/web",
      "start_command": "npm run dev",
      "port": 3000
    },
    {
      "name": "backend",
      "label": "BACKEND",
      "cwd": "packages/backend",
      "start_command": "npm run dev",
      "port": null
    }
  ]' \
  --watch-patterns '[
    "src/**/*.{ts,tsx,js,jsx}",
    "packages/**/*.py"
  ]' \
  --output-dir [current_directory]
```

4. Review generated Makefile targets and safety warnings

## Phase 7: Procfile Generation

1. Use Glob tool to locate Procfile generation script: `**/scripts/utils/generate_procfile.py`
2. **If not found, try user level**: Use Bash tool to get home directory and construct path: `$HOME/.claude/scripts/utils/generate_procfile.py`
3. Execute Procfile generation using same component analysis from Phases 1-3:

```bash
python [resolved_path]/generate_procfile.py \
  --components '[
    {
      "name": "frontend",
      "label": "FRONTEND",
      "cwd": "apps/web",
      "start_command": "npm run dev",
      "port": 3000
    },
    {
      "name": "backend",
      "label": "BACKEND",
      "cwd": "packages/backend",
      "start_command": "npm run dev",
      "port": null
    }
  ]' \
  --log-format unified \
  --output-dir [current_directory]
```

4. **CRITICAL**: Ensure ALL frontend and backend components include logging pipeline:
   - Every service MUST pipe output to `./dev.log` with timestamps
   - Format: `2>&1 | while IFS= read -r line; do echo "[$(date '+%H:%M:%S')] [SERVICE] $line"; done | tee -a ./dev.log`
   - **Port handling**: Next.js services should use both `PORT=X` and `-- --port X` for reliability
   - **No separate logs service**: Individual services handle their own logging via `tee`
5. Review generated service definitions and log formatting

## Phase 8: Project CLAUDE.md Integration

1. Use Glob tool to locate CLAUDE.md update script: `~/.claude/scripts/setup/dev-monitoring/update_claude_md.py`
2. **If not found, try user level**: Use Bash tool to get home directory and construct path: `$HOME/.claude/scripts/setup/dev-monitoring/update_claude_md.py`
3. Execute CLAUDE.md update to add development workflow commands:

```bash
python [resolved_path]/update_claude_md.py \
  --project-dir [current_directory] \
  --components '[
    {
      "name": "frontend",
      "label": "FRONTEND",
      "cwd": "apps/web",
      "start_command": "npm run dev",
      "port": 3000
    },
    {
      "name": "backend",
      "label": "BACKEND",
      "cwd": "packages/backend",
      "start_command": "npm run dev",
      "port": null
    }
  ]'
```

## Phase 9: Validation and Testing

1. **CRITICAL VALIDATION** - Check generated files contain real commands:
   - **Makefile**: NO `echo "No start command defined"` placeholders allowed - must use actual start commands from component analysis
   - **Procfile**: All services must have actual runnable commands (npm run dev, npx convex dev, etc.)
   - **Log paths**: Must use `./dev.log` NOT `/dev.log` (read-only filesystem) in both Makefile and Procfile
   - All services must include proper logging pipeline with timestamps
2. Validate other files:
   - Makefile syntax check
   - Log aggregation setup works
   - CLAUDE.md exists and contains make commands
3. "Monitoring setup complete and validated. please test the commands with make dev / status / logs"
