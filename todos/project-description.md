# Project: Claude Code Workflows

Comprehensive hybrid AI-automation system that combines Claude Code's reasoning capabilities with measurable Python analysis scripts. Provides structured workflow commands for enhanced productivity with automated security, performance, architecture, and quality analysis.

## Purpose

Production-ready workflow automation platform that enhances Claude Code with measurable, automated analysis capabilities. Features 12 specialized commands, claude.md build switches, and 23 Python scripts providing comprehensive code analysis across security, performance, architecture, and quality dimensions.

## Features

- **12 Specialized Workflow Commands + claude.md Build Switches**: Organized across analyze, plan, and fix categories with global build switches
- **Automated OWASP Top 10 Security Coverage**: Vulnerability scanning, input validation, authentication checks
- **Performance Analysis**: Bottleneck detection, database profiling, frontend optimization
- **Architecture Assessment**: Coupling analysis, pattern evaluation, scalability checks
- **Code Quality Metrics**: Complexity analysis, dead code detection, style enforcement
- **Hybrid AI+Automation**: Combines Claude Code reasoning with measurable script outputs
- **MCP Tool Integration**: Context7 (--c7), Sequential thinking (--seq)
- **Cross-platform Compatibility**: Windows, macOS, Linux support with platform detection
- **Token-efficient Design**: Just-in-time loading pattern optimized for Claude Code

## Commands

### Analysis Commands (6)
- **analyze-security**: OWASP Top 10 security review with automated vulnerability scanning
- **analyze-architecture**: System design analysis with coupling and scalability checks  
- **analyze-performance**: Performance bottleneck identification and optimization recommendations
- **analyze-code-quality**: Code complexity and quality metrics analysis
- **analyze-root-cause**: Debug issue investigation with trace analysis and error patterns
- **analyze-ux**: User experience and accessibility evaluation

### Build Switches (claude.md)
- **--prototype**: Rapid prototyping and proof-of-concept development via global claude.md switches
- **--tdd**: Test-driven development workflow with comprehensive testing via global claude.md switches

### Plan Commands (3)
- **plan-solution**: Technical challenge solving with research-driven solution design
- **plan-ux-prd**: UX-focused product requirements documentation with interface specifications
- **plan-refactor**: Code refactoring strategy and implementation planning

### Fix Commands (3)
- **fix-bug**: Issue resolution with comprehensive root cause analysis
- **fix-performance**: Performance optimization and bottleneck resolution
- **fix-test**: Test failures and CI/CD issue resolution

## Structure

```
claude/
├── commands/           # 12 workflow command definitions
│   ├── analyze-*.md   # Analysis workflow commands (6)
│   ├── plan-*.md      # Planning workflow commands (3)
│   └── fix-*.md       # Fix workflow commands (3)
├── claude.md           # Global build switches (--prototype, --tdd)
└── scripts/           # Automated analysis scripts (23 total)
    ├── analyze/       # Analysis automation (16 scripts)
    │   ├── security/  # OWASP Top 10 security analysis (4)
    │   ├── performance/ # Performance profiling (3)
    │   ├── architecture/ # Architecture analysis (3)
    │   ├── code_quality/ # Quality metrics (2)
    │   └── root_cause/ # Debug analysis (4)
    ├── setup/         # Installation and dependencies (2 scripts + requirements.txt)
    └── utils/         # Cross-platform utilities (4)

docs/
├── project-description.md  # This file
├── todo.md                 # Task management
└── todos/                  # Workflow tracking

test_codebase/
└── app.py                  # Vulnerable test application

CLAUDE.md                   # Claude Code integration guide
```

## Technical Specifications

### Dependencies
Python 3.7+ required with comprehensive analysis dependencies:

**Security Analysis:**
- bandit (security linting)
- safety (vulnerability scanning) 
- semgrep (static analysis security scanner)

**Performance Analysis:**
- psutil (system and process utilities)
- memory-profiler (memory usage profiling)
- py-spy (Python profiler, Unix only)

**Code Quality Analysis:**
- flake8, pylint (code analysis and style)
- radon (complexity metrics)
- lizard (advanced complexity analysis)
- vulture (dead code detection)
- mccabe (complexity checking)

**Architecture Analysis:**
- pydeps (dependency analysis)
- networkx (graph analysis for dependencies)

### Setup Commands
```bash
# Install Python dependencies
cd claude/scripts/setup
pip install -r requirements.txt

# Test installation
python test_install.py

# Run comprehensive analysis
python ../run_all_analysis.py
```

### MCP Tool Integration
Commands support optional enhancement flags:
- `--c7`: Context7 for framework-specific documentation and best practices
- `--seq`: Sequential thinking for complex multi-step analysis breakdown

## Automated Analysis Capabilities

### Security Analysis (OWASP Top 10 Coverage)
- **scan_vulnerabilities.py**: Detects injection attacks (SQL, Command, LDAP, XPath) and XSS vulnerabilities
- **validate_inputs.py**: Comprehensive input validation and injection pattern detection
- **check_auth.py**: Authentication failure detection, session security, CSRF protection
- **detect_secrets.py**: Hardcoded credential and API key identification

### Performance Analysis
- **check_bottlenecks.py**: System performance bottleneck identification
- **profile_database.py**: Database query optimization and performance analysis
- **analyze_frontend.py**: Frontend performance optimization recommendations

### Architecture Analysis  
- **coupling_analysis.py**: Code coupling and dependency analysis
- **pattern_evaluation.py**: Architecture pattern assessment and recommendations
- **scalability_check.py**: System scalability and design evaluation

### Code Quality Analysis
- **complexity_metrics.py**: Comprehensive code complexity measurement
- **complexity_lizard.py**: Advanced complexity analysis with Lizard integration

## Test Environment

**test_codebase/app.py**: Intentionally vulnerable Python application for testing security analysis workflows:
- SQL injection vulnerabilities for testing scan_vulnerabilities.py
- Hardcoded credentials and API keys for testing detect_secrets.py  
- Input validation issues (eval() usage) for testing validate_inputs.py
- Authentication weaknesses for testing check_auth.py
- Unsafe SSL verification and other security anti-patterns

Use with security analysis commands to validate detection capabilities.

## Status

**Production Ready**: Fully implemented workflow system with comprehensive analysis capabilities, proven effectiveness across security, performance, architecture, and quality analysis domains. All 12 commands plus claude.md build switches operational with supporting automation scripts and cross-platform compatibility.