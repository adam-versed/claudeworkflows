# convert build commands to switches

**Status:** In Progress
**Created:** 2025-07-12T17:50:07
**Started:** 2025-07-12T17:50:07
**Agent PID:** 738

## Description
Convert build-prototype.md and build-tdd.md from standalone commands to switch commands available in a global claude.md file. Create the claude.md in the root /claude folder and update install scripts to handle merging with existing claude.md files.

## Implementation Plan
- [x] Read current build-prototype.md and build-tdd.md content
- [x] Create claude.md in /claude folder with switch command definitions
- [x] Convert build commands to switch format for global availability
- [x] Update install.sh to handle claude.md merging logic
- [x] Remove standalone build-prototype.md and build-tdd.md files (already done)
- [x] Update documentation to reflect command count changes (14→12)
- [x] Test install script claude.md handling
- [x] Refactor claude.md to be a navigation hub pointing to rules/
- [x] Create claude/rules/ directory with prototype.md and tdd.md
- [x] Update install script to verify rules directory
- [ ] User test: Validate switch commands work and install script handles merging

## Original Todo
lets change the build-prototype.md and build-tdd.md to be switch commands that are available in the global claude.md - this should be in the root of our /claude folder and our install scripts should include a new section that looks for the presence of a claude.md, if its found the contents of ours is appended to the existing one as a new rules section, if it doesnt we just copy in our file.