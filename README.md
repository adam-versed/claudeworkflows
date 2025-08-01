# Claude Code Workflows

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **Hybrid AI-Automation System for Claude Code**
> Specialized workflow commands + LLM actions + Python analysis scripts = multi-function, just-in-time development automation

## 📋 TL;DR

**Installation:**

```bash
./install.sh              # Install to current directory
./install.sh ~            # Install globally
./setup-dev-monitoring    # Optional: Setup unified dev logging for easier debugging
```

**Workflow Strengths:**

- **Contextual awareness** - Understands your project technologies, frameworks, and patterns
- **Hybrid approach** - Combines LLM intelligence with programmatic scripts for accuracy
- **Just-in-time** - Reduces token usage by only analyzing what's needed when needed
- **Debuging-Efficiencies** - Uses make to setup server monitoring and commands LLM can use to retrieve failures, saving on copy and pasting all the time

## 🚀 Examples

### Example 1: Research and Implement a Solution

```bash
# Research and plan approaches for implementing real-time updates
/plan-solution --tdd "Add real-time updates using WebSockets"

# After choosing an approach, implement with isolated work branches
/todo-worktree
```

### Example 2: Security Analysis

```bash
# Get comprehensive security report following OWASP Top 10
/analyze-security

# Returns vulnerability scan, secret detection, and auth analysis
```

## 🛠️ Commands

See [detailed documentation](docs/detailed-documentation.md) for complete command reference.

**Analysis:** `/analyze-security`, `/analyze-architecture`, `/analyze-performance`, `/analyze-code-quality`
**Planning:** `/plan-solution`, `/plan-ux-prd`, `/plan-refactor`
**Implementation:** `/todo-branch`, `/todo-worktree`
**Fixes:** `/fix-bug`, `/fix-performance`, `/fix-test`
**Hooks:** `/add-code-pretooluse-rules`, `/add-code-posttooluse-quality-gates`

**Build Flags:** `--prototype` (rapid POC), `--tdd` (test-driven), `--c7` (framework best practices), `--seq` (complex breakdown)

## 📁 WIP Workflows

The `wip-workflows/` directory contains experimental workflow agents I'm testing. These aren't production-ready but shared for experimentation:

- `delivery-manager.md` - Project coordination and tracking
- `solution-architect.md` - Architecture design and tech stack selection
- `product-manager.md` - User-centered design and requirements
- `ux-designer.md` - UI/UX design and accessibility
- `mobile-developer.md` - Cross-platform mobile development
- `web-developer.md` - Web feature implementation
- `qa-analyst.md` - Comprehensive testing specialist
- `security-architect.md` - Security best practices and reviews
- `user-researcher.md` - Persona development and behavioral analysis

Feel free to explore and adapt these for your own experimentation.

## 📄 License

MIT License - See LICENSE file for details.
