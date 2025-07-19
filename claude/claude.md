## Build Approach Flags for claude enhanced workflows

- `--prototype` **When this flag is used**: Read and follow the guidance in `.claude/rules/prototype.md`  
  **Purpose**: Quick proof-of-concept development with minimal setup and rapid iteration

- `--tdd` **When this flag is used**: Read and follow the guidance in `.claude/rules/tdd.md`  
  **Purpose**: Systematic test-driven development with comprehensive test coverage and quality assurance

## Development Workflow Commands (Make-based)

**CRITICAL: Service Management Restrictions**
- **NEVER run `make dev` or `make stop`** - These commands start/stop development services
- **ALWAYS ask the user** to run these commands manually
- **Claude can use**: `make tail-log`, `make status`, `make lint`, `make test`, `make format`, `make clean`

### Available Commands

- `make dev` - **USER ONLY** - Start all development services (web, mobile, backend) with auto-reload
- `make tail-log` - **Claude can use** - Access unified development logs for debugging and context
- `make status` - **Claude can use** - Check if development services are running
- `make stop` - **USER ONLY** - Stop all development services
- `make lint` - **Claude can use** - Run code quality checks across monorepo
- `make test` - **Claude can use** - Execute test suites for all packages
- `make format` - **Claude can use** - Format code across all workspaces
- `make clean` - **Claude can use** - Clean build artifacts and logs
- `make help` - **Claude can use** - Show available commands

### Log Files and Debugging

- **Development logs**: Located at `./dev.log` in project root
- **Log format**: `[TIMESTAMP] [SERVICE] Message content`
- **Services**: `[WEB]` (Next.js), `[NATIVE]` (React Native/Expo), `[BACKEND]` (Convex)
- **Access logs**: Use `make tail-log` to read current development activity
- **Context gathering**: Logs provide complete context about frontend/backend requests and errors

### Workflow Integration

When debugging issues or understanding system state:
1. **Check service status**: `make status`
2. **Read development logs**: `make tail-log` (use Ctrl+C to exit)
3. **Run quality checks**: `make lint` and `make test`
4. **Ask user to restart services**: "Please run `make dev` to start/restart development services"

**Never attempt to start, stop, or restart development services automatically.**
