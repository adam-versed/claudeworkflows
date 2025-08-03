# Claude Code Workflows - Detailed Documentation

## Python Libraries and Dependencies

### Security Analysis

- `bandit` - Security linting and vulnerability detection
- `safety` - Known vulnerability scanning against CVE database
- `semgrep` - Static analysis security scanner

### Performance Analysis

- `psutil` - System and process monitoring utilities
- `memory-profiler` - Memory usage profiling and tracking
- `py-spy` - Python profiler for performance analysis (Unix only)

### Code Quality Analysis

- `flake8` - Python style guide enforcement (PEP 8)
- `pylint` - Comprehensive code analysis and linting
- `radon` - Code complexity metrics (cyclomatic, halstead)
- `lizard` - Advanced complexity analysis for multiple languages
- `vulture` - Dead code detection and cleanup
- `mccabe` - Complexity checker for functions

### Architecture Analysis

- `pydeps` - Dependency analysis and visualization
- `networkx` - Graph analysis for architectural patterns

### Multi-Language Testing Framework Detection

- `pytest` - Python testing framework and coverage analysis
- `pytest-cov` - Python test coverage measurement
- `jest` - JavaScript/TypeScript testing framework and coverage
- `nyc` - JavaScript/TypeScript code coverage tool
- `c8` - JavaScript/TypeScript native V8 coverage
- `jacoco` - Java code coverage library
- `cobertura` - Java/C# XML-based coverage reporting
- `go test` - Go built-in testing and coverage
- `tarpaulin` - Rust code coverage tool
- `grcov` - Rust coverage data collection
- `coverlet` - .NET Core coverage framework
- `dotcover` - JetBrains .NET coverage tool
- `simplecov` - Ruby code coverage analysis
- `phpunit` - PHP testing framework with coverage
- `xdebug` - PHP debugger and coverage tool
- `gcov` - GNU coverage testing tool (C/C++)
- `lcov` - Linux Test Project coverage visualization
- `llvm-cov` - LLVM coverage mapping tool
- `swift test` - Swift package manager testing
- `xccov` - Xcode command-line coverage tool
- `kover` - Kotlin code coverage engine

### Development Tools

- `black` - Opinionated code formatting
- `isort` - Import statement organization

### Core Dependencies

- `requests` - HTTP requests for external API integrations
- `python-dotenv` - Environment variable management

## MCP Tools Integration

### Available MCP Tools

- **`sequential-thinking`** - Multi-step reasoning and analysis breakdown (enables `--seq` flag)
- **`grep`** - Searches git repositories for matching code (enables `--gitgrep` flag)

## Installation Details

### Installation Options

```bash
# Current directory (uses ./.claude/)
./install.sh

# User global (uses ~/.claude/)
./install.sh ~

# Custom location
./install.sh /my/project/path

# Advanced options
./install.sh --dry-run       # Preview changes without making modifications
./install.sh --verbose      # Enable detailed debug output
./install.sh --skip-mcp     # Skip MCP tools installation (Python scripts only)
./install.sh --skip-python  # Skip Python dependencies installation
./install.sh --help         # Show detailed help and usage information
```

### Handling Existing .Claude Installations

**Automatic Backup:** All installation options automatically create a timestamped backup of your existing installation before making any changes.

The installer automatically detects existing `.claude` directories and the interactive terminal install will offer four options:

1. **Fresh Install:** install fresh (complete replacement)
2. **Merge:** Preserve user customizations while adding new features (no overwrites)
3. **Update Workflows Only:** Update built-in commands and scripts while preserving custom commands and all other files (recommended for updates)
4. **Cancel:** Exit without changes

## Uninstalling

To safely remove Claude Code Workflows components while preserving your .claude directory:

```bash
# Preview what would be removed (recommended first step)
./uninstall.sh --dry-run

# Uninstall from current directory
./uninstall.sh

# Uninstall from specific path
./uninstall.sh /path/to/installation

# Verbose output for detailed logging
./uninstall.sh --verbose
```

**Smart Uninstall Features:**

- **📦 Safe Removal**: Only removes workflow components, preserves .claude structure and user files
- **⚠️ Dependency Tracking**: Distinguishes pre-existing vs newly installed Python packages/MCP servers
- **💾 Automatic Backups**: Creates backups of MCP configuration and claude.md before changes
- **🧹 Thorough Cleanup**: Removes **pycache** folders and empty directories
- **📝 Installation Log**: Uses installation-log.txt to provide intelligent removal warnings

The uninstaller will interactively prompt for each Python package and MCP server removal, showing whether each item was:

- **🔧 Newly installed** by Claude Code Workflows (safer to remove)
- **⚠️ Pre-existing** before installation (likely used by other projects - caution advised)

## Security Analysis Details

### OWASP Top 10 Coverage

The security analysis provides comprehensive OWASP testing criteria coverage through automated vulnerability detection.

**Example with included test_codebase:**

```bash
/analyze-security
```

**Detected Issues:**

- **A01: Injection** → SQL injection in authentication
- **A02: Cryptographic Failures** → Hardcoded JWT secrets
- **A03: Injection** → Command injection via eval()
- **A07: Identity Failures** → Weak authentication patterns

## Analysis Scripts Architecture

**25 Analysis Scripts Organized by Category:**

```
claude/scripts/analyze/
├── security/        # OWASP Top 10 vulnerability detection
├── performance/     # Bottleneck detection, baseline establishment
├── architecture/    # Design analysis, coupling detection
├── code_quality/    # Complexity metrics, test coverage analysis
└── root_cause/      # Debugging and error pattern analysis
```

## Programming Language Support

### Universal Analysis (All Languages)

**Security:** Vulnerability scanning, secret detection, authentication analysis
**Architecture:** Dependency analysis, coupling detection, scalability assessment
**Code Quality:** Complexity metrics (via Lizard), dead code detection

### Language-Specific Analysis

**Supported Languages:** Python, JavaScript, TypeScript, Java, C#, Go, Rust, PHP, Ruby, C/C++, Swift, Kotlin

| Language                      | Test Coverage                | Performance Baseline          | Import Analysis         | Bottleneck Detection    |
| ----------------------------- | ---------------------------- | ----------------------------- | ----------------------- | ----------------------- |
| **Python**                    | ✅ pytest, coverage          | ✅ cProfile, memory-profiler  | ✅ import patterns      | ✅ AST analysis         |
| **JavaScript**                | ✅ jest, nyc, c8             | ✅ npm scripts, profiling     | ✅ import/require       | ✅ performance patterns |
| **TypeScript**                | ✅ jest, nyc, c8             | ✅ npm scripts, profiling     | ✅ import patterns      | ✅ performance patterns |
| **Java**                      | ✅ junit, jacoco             | ✅ maven/gradle, JFR          | ✅ import statements    | ✅ performance patterns |
| **Go**                        | ✅ go test, coverage         | ✅ go build, benchmarks       | ✅ import patterns      | ✅ performance patterns |
| **Rust**                      | ✅ cargo test, tarpaulin     | ✅ cargo bench, flamegraph    | ✅ use statements       | ✅ performance patterns |
| **C#**                        | ✅ dotnet test, coverlet     | ✅ dotnet build, profiling    | ✅ using statements     | ✅ performance patterns |
| **PHP/Ruby/C++/Swift/Kotlin** | ✅ Basic framework detection | ✅ Language-specific patterns | ✅ Full import analysis | ✅ performance patterns |

## Development Monitoring

### Overview

The `setup-dev-monitoring` command establishes comprehensive development monitoring infrastructure for any project structure through LLM-driven analysis and cross-platform automation. This workflow provides centralized logging, server start/stop control, and key event capture for LLM integration - inspired by @mitsuhiko's development workflow approach.

### Key Benefits

**Centralized Development Control:**

- **Unified logging** - All development services (frontend, backend, databases) log to a single aggregated file
- **Service orchestration** - Start/stop all development services with simple commands
- **Status monitoring** - Quick health checks across all project components
- **Event capture** - Key development events automatically formatted for LLM analysis

**LLM Integration Advantages:**

- **Context-rich debugging** - Claude can read unified logs to understand full system state
- **Intelligent troubleshooting** - Complete request/response flows captured for analysis
- **Automated issue detection** - Patterns across services identified through log analysis
- **Streamlined workflows** - No need to manually gather logs from multiple terminals

### Setup Process

The setup command uses intelligent project analysis to automatically:

1. **Discover project components** - Analyzes structure to identify all runnable services
2. **Install monitoring dependencies** - Cross-platform installation of required tools
3. **Generate orchestration files** - Creates Makefile and Procfile for service management
4. **Configure log aggregation** - Sets up unified logging with service-specific labels
5. **Validate setup** - Tests monitoring infrastructure before completion

### Generated Commands

After setup, your project gains these development commands:

```bash
# Start all development services with unified logging
make dev

# Access aggregated logs for debugging and LLM analysis
make tail-log

# Check service health and status
make status

# Stop all development services
make stop

# Code quality and testing
make lint
make test
make format
make clean
```

**Note:** Claude follows strict service management policies - it can read logs and check status, but users must manually run `make dev` and `make stop` commands for security.

## Special Notes

### Todo workflow

CC commands come from [badlogic](https://github.com/badlogic/claude-commands/blob/main/todo.md) - pairs well with the workflows, particularly /plan-\* as they produce todo.md lists. It's a more efficient version of CC plan mode/todos, but ive modified it to use Claude.md rather than a bespoke file for project description.

### Recommended Optionals

- **Context7 MCP** best practice documentation to support code generation
- **Sequential thinking MCP** use to breakdown complex tasks (can augment or cheaper alternative for non reasoning models)
