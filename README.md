# Claude Code Workflows

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **Hybrid AI-Automation System for Claude Code**  
> 12 specialized workflow commands + 25 Python analysis scripts + claude.md build switches = Production-ready development automation

## 📋 TL;DR Executive Summary

**What it is:** Claude Code workflows for a lightweight but comprehensive development toolkit including:

- combines the best of LLM and programmitc scripts to reduce context errors, hallucinations and token usage
- task planning modes ('/plan-solution --tdd'), different modes to create a todos.md (good partnership with @badlogics /todo framework)
- code analysis modes ('/analyze-security'), programmatic + llm analysis of different codebase factors
- easy access dev monitoring ('/setup-dev-monitoring'), programmatic setup of time saving dev logging system that enables quick capture of events between your LLM chat(s) and terminal sesion(s)

**Quick Start:** Run `./install.sh` → Use commands like `/analyze-security`, `/plan-solution --tdd`, `/setup-dev-monitoring` → Get insights instantly.

**Key Features:** [🔍 6 Analysis Commands](#-analysis-commands-6) • [📐 3 Planning Commands](#-plan-commands-3) • [🔧 3 Fix Commands](#-fix-commands-3) • [🔒 OWASP Security Testing](#-security-analysis) • [⚡ 25 Analysis Scripts](#-analysis-scripts-architecture) • [🌐 Multi-Language Support](#-programming-language-support) • [🔧 Development Monitoring](#-development-monitoring)

**Installation:** [Quick Install](#-installation) • [MCP Tools](#mcp-tools-optional-enhancement) • [Dependencies](#python-libraries-installed) • [Uninstall](#uninstalling)

---

Transform your Claude Code experience with measurable, automated analysis across **security**, **performance**, **architecture**, and **code quality**. Get professional-grade insights in seconds, not hours.

## 🛠️ Installation

### Prerequisites

- **Python 3.7+** (automation scripts)
- **Claude Code CLI** (claude code base + mcp tools)
- **Node.js** (any version, for MCP tools, optional)

### Recommended Optionals

- **Context7 MCP** best practice documentation to support code generation
- **Sequential thinking MCP** use to breakdown complext tasks (can augment or cheaper alternative for non reasoning models)

- **Todo workflow** CC command from [badlogic](https://github.com/badlogic/claude-commands/blob/main/todo.md) - pairs well with the workflows, particularly /plan-\* as they produce todo.md lists. It's a more efficient version of CC plan mode/todos

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

### Python Libraries Installed

**Security Analysis:**

- `bandit` - Security linting and vulnerability detection
- `safety` - Known vulnerability scanning against CVE database
- `semgrep` - Static analysis security scanner

**Performance Analysis:**

- `psutil` - System and process monitoring utilities
- `memory-profiler` - Memory usage profiling and tracking
- `py-spy` - Python profiler for performance analysis (Unix only)

**Code Quality Analysis:**

- `flake8` - Python style guide enforcement (PEP 8)
- `pylint` - Comprehensive code analysis and linting
- `radon` - Code complexity metrics (cyclomatic, halstead)
- `lizard` - Advanced complexity analysis for multiple languages
- `vulture` - Dead code detection and cleanup
- `mccabe` - Complexity checker for functions

**Architecture Analysis:**

- `pydeps` - Dependency analysis and visualization
- `networkx` - Graph analysis for architectural patterns

**Multi-Language Testing Framework Detection:**

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

**Development Tools:**

- `black` - Opinionated code formatting
- `isort` - Import statement organization

**Core Dependencies:**

- `requests` - HTTP requests for external API integrations
- `python-dotenv` - Environment variable management

### MCP Tools (Optional Enhancement)

When Claude CLI is available, these MCP tools are automatically installed to enhance workflow capabilities:

**Available MCP Tools:**

- **`sequential-thinking`** - Multi-step reasoning and analysis breakdown (enables `--seq` flag)
- **`context7`** - Framework documentation and best practices (enables `--c7` flag)

**MCP Tool Benefits:**

- **Context7** - Framework-specific best practices and contextually accurate language detection (React, Vue, Django, Spring, etc.) via `--c7` flag
- **Sequential Thinking** - Complex problem breakdown via `--seq` flag

**Context7 ensures our analysis scripts provide contextually correct results** by understanding:

- Framework conventions (React hooks, Django models, Spring annotations)
- Language-specific patterns (Go interfaces, Rust ownership, TypeScript generics)
- Build tool configurations (Maven, Gradle, npm, Cargo)

```bash
# Install with MCP tools (requires Claude CLI + Node.js)
./install.sh

# Install without MCP tools (Python scripts only)
./install.sh --skip-mcp
```

### Uninstalling

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

## 🎯 Commands Reference

### 🔍 Analysis Commands (6)

| Command                     | Purpose                      | Key Features                                                  |
| --------------------------- | ---------------------------- | ------------------------------------------------------------- |
| **`/analyze-security`**     | OWASP Top 10 security review | Vulnerability scanning, secret detection, auth analysis       |
| **`/analyze-architecture`** | System design analysis       | Coupling analysis, scalability assessment, pattern evaluation |
| **`/analyze-performance`**  | Performance optimization     | Bottleneck detection, database profiling, resource analysis   |
| **`/analyze-code-quality`** | Code metrics & quality       | Complexity analysis, dead code detection, style enforcement   |
| **`/analyze-root-cause`**   | Debug investigation          | Error patterns, execution tracing, change analysis            |
| **`/analyze-ux`**           | User experience review       | Accessibility evaluation, usability assessment                |

### 📐 Plan Commands (3)

| Command              | Purpose                         | Key Features                                                   |
| -------------------- | ------------------------------- | -------------------------------------------------------------- |
| **`/plan-solution`** | Technical challenge solving     | Research-driven solution design with 3 options                 |
| **`/plan-ux-prd`**   | UX-focused product requirements | User experience design, interface specifications               |
| **`/plan-refactor`** | Refactoring strategy            | Code improvement planning, automated analysis, risk assessment |

### 🔧 Fix Commands (3)

| Command                | Purpose                  | Key Features                                 |
| ---------------------- | ------------------------ | -------------------------------------------- |
| **`/fix-bug`**         | Issue resolution         | Root cause analysis, comprehensive debugging |
| **`/fix-performance`** | Performance optimization | Bottleneck resolution, scaling improvements  |
| **`/fix-test`**        | Test failure resolution  | CI/CD debugging, test suite optimization     |

### 🎛️ Universal Build Flags

Enhance any command with these flags (defined in claude.md):

| Flag              | Purpose                    | When to Use                                                  |
| ----------------- | -------------------------- | ------------------------------------------------------------ |
| **`--prototype`** | Rapid prototyping approach | Quick proof-of-concept development with minimal setup        |
| **`--tdd`**       | Test-driven development    | Systematic test-first development with quality gates         |
| **`--c7`**        | Context7 integration       | Framework-specific best practices (React, Vue, Django, etc.) |
| **`--seq`**       | Sequential thinking        | Complex multi-step analysis breakdown                        |

**Example Usage:**

```bash
# Security analysis with framework best practices
/analyze-security --c7

# Feature planning with test-driven development and sequential analysis
/plan-solution --tdd --seq

# Rapid prototype development
/plan-solution --prototype
```

## 🔒 Security Analysis

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

## ⚡ Analysis Scripts Architecture

**25 Analysis Scripts Organized by Category:**

```
claude/scripts/analyze/
├── security/        # OWASP Top 10 vulnerability detection
├── performance/     # Bottleneck detection, baseline establishment
├── architecture/    # Design analysis, coupling detection
├── code_quality/    # Complexity metrics, test coverage analysis
└── root_cause/      # Debugging and error pattern analysis
```

**Dependencies:** 20+ production-ready packages including bandit, safety, psutil, flake8, pylint, radon, lizard, vulture, pydeps, and networkx.

## 🌐 Programming Language Support

### Universal Analysis (All Languages)

**Security:** Vulnerability scanning, secret detection, authentication analysis  
**Architecture:** Dependency analysis, coupling detection, scalability assessment  
**Code Quality:** Complexity metrics (via Lizard), dead code detection

### Language-Specific Analysis

**Supported Languages:** Python, JavaScript, TypeScript, Java, C#, Go, Rust, PHP, Ruby, C/C++, Swift, Kotlin

| Language       | Test Coverage            | Performance Baseline         | Import Analysis      | Bottleneck Detection     |
| -------------- | ------------------------ | ---------------------------- | -------------------- | ------------------------ |
| **Python**     | ✅ pytest, coverage      | ✅ cProfile, memory-profiler | ✅ import patterns   | ✅ AST analysis          |
| **JavaScript** | ✅ jest, nyc, c8         | ✅ npm scripts, profiling    | ✅ import/require    | ✅ performance patterns  |
| **TypeScript** | ✅ jest, nyc, c8         | ✅ npm scripts, profiling    | ✅ import patterns   | ✅ performance patterns  |
| **Java**       | ✅ junit, jacoco         | ✅ maven/gradle, JFR         | ✅ import statements | ✅ performance patterns  |
| **Go**         | ✅ go test, coverage     | ✅ go build, benchmarks      | ⚠️ Basic             | ✅ performance patterns  |
| **Rust**       | ✅ cargo test, tarpaulin | ✅ cargo bench, flamegraph   | ⚠️ Basic             | ✅ performance patterns  |
| **C#**         | ✅ dotnet test, coverlet | ✅ dotnet build, profiling   | ✅ using statements  | ✅ performance patterns  |
| **Others**     | ⚠️ Basic detection       | ⚠️ Basic detection           | ❌                   | ✅ file pattern analysis |

**Context7 Integration:** Use `--c7` flag with any analysis command for framework-specific best practices and contextually accurate language detection.

## 🔧 Development Monitoring

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

### Usage

```bash
# Setup monitoring for current project
/setup-dev-monitoring
```

### Generated Commands added to project Claude.md

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

## 🤝 Contributing

This project enhances Claude Code with production-ready automation. Contributions welcome for:

- Additional analysis scripts
- New workflow commands
- Platform-specific optimizations
- MCP tool integrations

## 📄 License

MIT License - See LICENSE file for details.

---
