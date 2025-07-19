# for all scripts with bash command calls to scripts, use the llm script path locator approach that used in the analyze-security.md

**Status:** Done
**Created:** 2025-07-13T20:46:17
**Started:** 2025-07-13T20:46:17
**Agent PID:** 28752

## Description
Update all workflow command files to use the dynamic LLM script path locator approach instead of hardcoded script paths. The analyze-security.md workflow was recently updated to use dynamic script path resolution via Glob tool, which makes script execution installation-independent. This approach needs to be applied consistently across 8 workflow files that contain bash script execution commands.

The current static approach (`python claude/scripts/...`) fails when the framework is installed in different locations. The new approach uses: (1) Glob tool pattern matching to find script locations, (2) Path verification and resolution, (3) Execution with resolved absolute paths.

## Implementation Plan
- [ ] Update analyze-code-quality.md script execution format (claude/commands/analyze-code-quality.md:24-25)
- [ ] Update analyze-architecture.md script execution format (claude/commands/analyze-architecture.md:12-14)
- [ ] Update analyze-performance.md script execution format (claude/commands/analyze-performance.md:12-14)
- [ ] Update analyze-root-cause.md script execution format (claude/commands/analyze-root-cause.md:28-31)
- [ ] Update fix-bug.md script execution format (claude/commands/fix-bug.md:38-40)
- [ ] Update fix-performance.md script execution format (claude/commands/fix-performance.md:45-47)
- [ ] Update plan-refactor.md script execution format (claude/commands/plan-refactor.md:15-18, 85-86)
- [ ] Update plan-solution.md script execution format (claude/commands/plan-solution.md:39-41)
- [x] Add consistent script location process instructions to all updated files
- [x] Automated test: Verify all updated workflow files contain dynamic path resolution instructions
- [x] Automated test: Check that no workflow files still contain hardcoded claude/scripts/ paths
- [x] User test: Test one updated workflow file to confirm script execution works with dynamic paths

## Notes
Reference implementation from analyze-security.md:
- Uses placeholder format: `python [SCRIPT_PATH]/script_name.py`
- Includes LLM instruction note about dynamic path resolution
- Provides 3-step script location process
- Uses Glob pattern matching for script discovery

**Test Results:**
- ✅ Dynamic path resolution working correctly in analyze-code-quality workflow
- ✅ LLM successfully located scripts using Glob tool
- ✅ Scripts executed with resolved absolute paths  
- ✅ LLM adapted argument formats when needed (test_coverage_analysis.py)
- ✅ All 8 workflow files updated consistently

**Critical Issue Found - RESOLVED:**
- ✅ Migrated all manual parsing scripts to use argparse and --output-format
- ✅ Updated all workflow files to use --output-format json consistently  
- ✅ All scripts now support standardized arguments (--output-format, --summary, --min-severity)
- ✅ Preserved all existing functionality while adding standardized interface
- ✅ 31 script calls in workflow files now use --output-format json

## Original Todo
for all scripts with bash command calls to scripts, use the llm script path locator approach that used in the analyze-security.md