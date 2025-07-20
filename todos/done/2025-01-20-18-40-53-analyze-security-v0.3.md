# Analyze Security v0.3
**Status:** Done
**Agent PID:** 48438

## Original Todo
review analyze-security.md with the programmatic-prompt-commandfile.md approach and create a new version iterated to v0.3

## Description
Transform analyze-security.md from v0.2 to v0.3 by adopting the programmatic-prompt-commandfile.md approach to greatly reduce token usage without sacrificing accuracy and task understanding. This involves restructuring the verbose 208-line workflow into a concise 4-phase process with numbered steps, removing bloat (symbols legend, verbose autonomous search patterns), adding strategic STOP interactions, implementing quality gates validation, and streamlining task transfer to todos.md. The update maintains comprehensive OWASP Top 10 coverage and hybrid automated/contextual analysis while significantly improving usability and reducing complexity.

## Implementation Plan
- [x] Read current analyze-security.md v0.2 (claude/commands/analyze-security.md)
- [x] Create new v0.3 structure with token efficiency focus
- [x] Enhance script integration with .claude directory notes
- [x] Add todos.md integration workflow
- [x] Automated test: Verify new structure follows programmatic standards and reduces token usage by ~50%
- [x] Fix install.sh update mode: Prevent deletion of existing user command files when updating
- [x] User test: Confirm v0.3 maintains OWASP Top 10 coverage and analysis accuracy while improving usability

## Notes
[Implementation notes]