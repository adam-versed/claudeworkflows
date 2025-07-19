# Create an install.sh that copies the claude folder subdirectories to a choice of project folder or user folder specified as an argument, it should lead to adding them within a .claude directory, which the script may need to create or if present copy items to. Additionally we need to run the install scripts in scripts/setup for the analysis scripts and we need to add something to handle installing mcp tools context7 and sequential thinking.

**Status:** Done
**Started:** 2025-07-12T15:58:45
**Created:** 2025-07-12T15:54:31
**Agent PID:** 738

## Description
Create a comprehensive installation script (install.sh) that deploys the Claude Code Workflows system to user-specified locations. The script handles directory setup, copies all 18 workflow commands and 23 Python analysis scripts, installs Python dependencies via the existing setup infrastructure, and provides guidance for MCP tools installation (context7, sequential thinking, magic UI).

Key Requirements: Support custom installation paths with examples for project-local (./project/.claude) and user-global (~/.claude) locations, handle existing .claude directories gracefully, execute Python dependency installation using existing scripts/setup infrastructure, validate installations across platforms, and provide clear user guidance for MCP tools setup since these are Claude Code extensions rather than traditional packages.

## Implementation Plan
- [x] **Create install.sh script** (install.sh:1-394) - Main installation script with argument parsing and environment detection
- [x] **Add environment validation functions** (install.sh:113-181) - Check Python 3.7+, Node.js, Claude CLI, and platform compatibility
- [x] **Implement directory setup logic with custom paths** (install.sh:183-239) - Handle user-specified installation paths with examples (./project/.claude, ~/.claude), validate paths, and handle existing .claude directories with conflict resolution
- [x] **Add file copy operations** (install.sh:241-281) - Copy claude/ directory structure with proper permissions and filtering
- [x] **Integrate Python dependency installation** (install.sh:283-308) - Leverage existing claude/scripts/setup/install_dependencies.py infrastructure
- [x] **Add MCP tools installation guidance** (install.sh:310-352) - Install sequential-thinking and context7 MCP tools via Claude CLI
- [x] **Create CLI integration** - Not needed: workflow uses direct Claude Code commands via CLAUDE.md
- [x] **Add verification and testing** (install.sh:354-384) - Execute test_install.py and validate MCP tools installation
- [x] **Implement error handling and logging** (install.sh:78-111, 386-394) - Comprehensive error handling with rollback capability and detailed logging
- [x] **Add usage documentation** (install.sh:10-76) - Usage examples, help text, installation modes, and custom path examples
- [x] **Automated test**: Run install.sh in dry-run mode to verify script logic
- [x] **User test**: Test installation script on target system with both custom paths and default modes

## Notes
- Created comprehensive 550+ line install.sh script with full functionality
- Supports custom installation paths with examples for project-local and user-global
- Includes backup/merge options for existing installations
- Implements robust error handling with detailed logging
- Provides dry-run mode for testing before actual installation
- Integrates with existing Python setup infrastructure
- Handles MCP tools installation via Claude CLI commands
- Fixed argument parsing to properly handle flags vs target paths
- Added dry-run compatible logic to avoid file system checks during testing
- Automated test passed: dry-run mode works correctly without making changes
- Fixed compatibility issues: removed timeout command and handled interactive Python script
- User test passed: successful installation to /tmp/test-claude with Python dependencies

## Original Todo
Create an install.sh that copies the claude folder subdirectories to a choice of project folder or user folder specified as an argument, it should lead to adding them within a .claude directory, which the script may need to create or if present copy items to. Additionally we need to run the install scripts in scripts/setup for the analysis scripts and we need to add something to handle installing mcp tools context7 and sequential thinking.