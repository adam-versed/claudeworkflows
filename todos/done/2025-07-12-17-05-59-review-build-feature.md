# review build-feature.md with user

**Status:** In Progress
**Created:** 2025-07-12T17:05:59
**Started:** 2025-07-12T17:06:45
**Agent PID:** 738

## Description
Review and discuss the build-feature.md command to determine its fitness for purpose and whether it should be improved, refactored, merged with other commands, or dropped entirely.

## Implementation Plan
- [x] Read and analyze build-feature.md structure and content
- [x] Compare with related commands (plan-feature.md, build-plan.md) to identify overlap
- [x] Identify key issues: time allocation, scope boundaries, command overlap
- [x] Discuss with user the command's purpose and relationship to other commands
- [x] Evaluate whether build-feature should be standalone, merged, or dropped
- [x] User decision: Delete build-feature.md and build-plan.md (redundant with plan-feature + build-tdd)
- [x] Delete claude/commands/build-feature.md
- [x] Delete claude/commands/build-plan.md
- [x] Update README.md to remove references to deleted commands
- [x] Update docs/project-description.md to reflect reduced command count
- [x] User test: Verify deletion and documentation updates are complete

## Original Todo
review build-feature.md with user

## Notes
- Found 65% of build-feature is planning (Discovery 25% + Planning 40%) which overlaps heavily with plan-feature.md
- Time allocation seems backwards for a "build" command (40% planning vs 20% implementation)
- Unclear when to use build-feature vs plan-feature vs build-plan
- Quality gates mix specific and vague metrics
- DECISION: Deleted both build-feature.md and build-plan.md as their core value (ensuring existing functionality works) is better handled by plan-feature.md + build-tdd.md
- Updated command count from 18 to 16 across README.md and project-description.md
- Removed all references to deleted commands from documentation