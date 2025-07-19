# check for use of magic mcp in framework, remove --magic references if not used

**Status:** In Progress
**Started:** 2025-07-13T16:48:10
**Agent PID:** 36629

## Description
Remove all references to Magic MCP from the Claude Code Workflows framework. The codebase currently contains multiple references to Magic MCP and `--magic` flags in documentation, help text, and project descriptions, but there is no actual Magic MCP installation or implementation. The goal is to clean up these orphaned references to accurately reflect that only sequential-thinking and context7 MCP tools are actually supported.

## Implementation Plan
- [x] Remove Magic UI description from README.md MCP Tool Benefits (README.md:133)
- [x] Remove --magic flag from feature flags table in README.md (README.md:218)
- [x] Update example command comment to reflect remaining flags (README.md:227)
- [x] Remove --magic flag from example command in README.md (README.md:230)
- [x] Remove --magic help text from install.sh (install.sh:785)
- [x] Remove Magic UI from MCP Tool Integration list (project-description.md:17)
- [x] Remove --magic flag explanation from project-description.md (project-description.md:118)
- [x] Remove Magic→UI from MCP abbreviations in RULES.md (RULES.md:88)
- [x] Automated test: Verify no magic/--magic references remain in codebase
- [x] Automated test: Verify README table structure remains valid after row removal
- [x] Automated test: Verify all documentation formatting is maintained
- [x] User test: Review README.md and confirm Magic MCP references are removed
- [x] User test: Run install.sh --help and confirm no --magic flag mentioned
- [x] User test: Verify project-description.md accurately reflects available MCP tools

## Original Todo
- check for use of magic mcp in framework, dont believe it is so the references to --magic should be removed from install, uninstall and readme.