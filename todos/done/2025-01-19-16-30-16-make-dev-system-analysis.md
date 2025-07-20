# Analysis: Make-Based Development System

## System Overview

The make-based development system is designed to provide a **standardized, agentic-friendly development environment** that works consistently across different programming languages and project types. It serves as a universal interface between Claude Code and development workflows.

## Core Components & Functionality

### 1. **Standardized Makefile Interface**
- **`make dev`**: Starts all project services (frontend, backend, databases) - **Claude should NEVER run this automatically**
- **`make tail-log`**: Provides Claude access to unified development logs for context understanding
- **`make lint`**: Code quality checks
- **`make format`**: Code formatting
- **`make test`**: Run test suites
- **`make clean`**: Cleanup tasks

### 2. **Process Management via Shoreman**
- Uses **shoreman** (shell-based foreman implementation) to manage multiple concurrent processes
- Reads **Procfile** to define services (e.g., `frontend: cd web && npm run dev`, `backend: watchexec -r -e go,sql -- go run cmd/main.go`)
- **Custom error messages** designed to be descriptive for Claude (e.g., "Service already running, auto-reload enabled, no action needed")
- Writes process state to **shoreman.pid** for process tracking
- Handles graceful startup/shutdown of multiple services

### 3. **File Watching with Watchexec**
- **watchexec** monitors file changes and triggers auto-recompilation
- Language-specific file patterns (`.go`, `.sql`, `.js`, `.ts`, `.py`, etc.)
- Recursive directory watching
- Integrates with build tools for each project type

### 4. **Unified Logging System**
- **Central dev.log file** captures output from all services with timestamps
- Fresh log on each restart (prevents infinite growth)
- Provides Claude with complete context about frontend and backend activity
- Enables Claude to understand request flows, errors, and system state

## Multi-Language & Cross-Platform Support

### **Project Type Detection & Setup**:
- **Node.js**: package.json detection, npm/yarn scripts, Vite/webpack dev servers
- **Go**: go.mod detection, watchexec with .go/.sql files, `go run` commands  
- **Python**: requirements.txt/pyproject.toml detection, uvicorn/flask dev servers
- **Generic**: Flexible Procfile configuration for any language

### **Cross-Platform Considerations**:
- **Unix/macOS**: Full shoreman + watchexec support
- **Windows**: May require alternative process management (foreman or custom scripts)
- **Docker**: Can be containerized for consistent environments

## Integration with Claude Code Workflows

### **Claude Behavior Patterns**:
1. **Never Start Services**: Claude should ask users to run `make dev` instead of running it automatically
2. **Context Gathering**: Use `make tail-log` to understand current system state when debugging
3. **Error Understanding**: Modified shoreman provides Claude-friendly error messages
4. **Workflow Integration**: Integrates with existing analyze/fix/plan commands

### **CLAUDE.md Documentation**:
```markdown
## Development Commands

- `make dev` - **YOU SHOULD NEVER RUN THIS** - Ask user to run this to start all development services. This command starts both frontend and backend servers with auto-reload and auto-compile. Never stop the server.
- `make tail-log` - Read unified development logs to understand current system state and debug issues
- `make lint` - Run code quality checks
- `make test` - Run test suites
- `make format` - Format code

## Log Files
- Development logs are in ./dev.log - use `make tail-log` to read them
- This provides context about frontend/backend requests, errors, and system state
```

## Command File Location & Structure

This should be implemented as **`claude/commands/setup-make-dev.md`** following the established command file patterns with:

- **Header comment** with label and version (per todos.md requirements)
- **Behavior section** describing the agentic approach
- **Context gathering** phase to understand project type and requirements
- **Investigation process** using existing architecture analysis
- **Implementation phases** for Makefile, Procfile, and tooling setup
- **Validation steps** to ensure the system works correctly
- **Integration** with todos.md for task tracking

## Concrete Implementation Details

### Make System Integration Points

**Key Make Targets:**
- `make dev` - Start development services (NEVER stop, auto-reload, auto-compile)
- `make tail-log` - Read unified log file for debugging
- `make lint` - Run linting
- `make format` - Code formatting 
- `make clean` - Clean build artifacts
- `make test` - Run tests

**Procfile Structure:**
```
frontend: cd web && npm run dev
backend: watchexec -r -e go,sql -- go run cmd/minbb/main.go
```

**Watchexec Integration:**
- Watches `.go` and `.sql` files recursively
- Auto-restarts backend on file changes
- Unified logging to `dev.log` file

### Current Command Structure

**Existing commands in `/claude/commands/`:**
- analyze-* (architecture, code-quality, performance, root-cause, security, ux)
- fix-* (bug, performance, test)
- plan-* (refactor, solution, ux-prd)

**Command format follows pattern:**
- Header with purpose and version (e.g., `# plan-solution v0.7`)
- Structured workflow with phases
- Stop points for user input
- Template sections

### Integration Requirements

**File Locations:**
- Command files: `/claude/commands/`
- Rules: `/claude/rules/`
- Templates: `/claude/templates/`
- Todo management: `/todos/todos.md`

**Error Message Customization:**
- Modified shoreman.sh to provide agentic-friendly error messages
- "Service already running. Auto reload, no need to do anything" when trying to restart
- Better context for debugging through unified logs

## Key Benefits

1. **Consistency**: Same interface across all project types
2. **Agentic-Friendly**: Predictable commands and error messages for Claude
3. **Developer Experience**: Unified logging and auto-recompilation
4. **Flexibility**: Works with any language that can be defined in a Procfile
5. **Context Awareness**: Claude can understand full system state through logs
6. **Process Safety**: Prevents Claude from accidentally disrupting running services

This system essentially creates a **development environment abstraction layer** that provides Claude Code with reliable, consistent interfaces for interacting with projects regardless of their underlying technology stack, while maintaining the flexibility to work with diverse programming languages and frameworks.