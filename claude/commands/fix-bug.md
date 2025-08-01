# fix-bug v0.2

**Mindset**: "Fix it right, keep it working" - Preserve existing functionality while eliminating defects.

## Behavior

Systematic bug diagnosis and resolution using structured debugging methodology with comprehensive validation.

## Systematic Bug Resolution Framework

### Comprehensive Diagnosis (35%)

- **Bug Reproduction**: Controlled environment with minimal reproduction case
- **Error Investigation**: Stack trace analysis, log analysis, state inspection
- **Root Cause Analysis**: Five Whys technique, timeline analysis, change correlation
- **Impact Assessment**: Severity classification and business impact evaluation

### Planning Phase (25%)

- **Fix Strategy Selection**: Minimal fix vs systematic fix approach
- **Risk Assessment**: Regression risk, performance risk, security implications
- **Testing Strategy**: Reproduction test, regression suite, edge case coverage
- **Rollback Planning**: Rollback triggers, procedures, monitoring strategy

### Implementation Phase (30%)

- **Test-Driven Fixing**: Write failing test, implement fix, expand test coverage
- **Root Cause Focus**: Address fundamental cause, not just symptoms
- **Defensive Programming**: Add validation, error handling, logging
- **Code Quality**: Maintain readability and maintainability

### Validation Phase (10%)

- **Before/After Comparison**: Document exact behavior change
- **Regression Testing**: Run full test suite to ensure no side effects
- **Integration Verification**: Cross-component interactions work correctly
- **Manual Testing**: Human verification of fix in realistic scenarios

## Script Integration

Execute debugging analysis scripts via Bash tool for systematic issue analysis:

**FIRST - Resolve SCRIPT_PATH:**

1. **Try project-level .claude folder**:

   ```bash
   Glob: ".claude/scripts/analyze/root_cause/*.py"
   ```

2. **Try user-level .claude folder**:

   ```bash
   Bash: ls "$HOME/.claude/scripts/analyze/root_cause/"
   ```

3. **Interactive fallback if not found**:
   - List searched locations: `.claude/scripts/analyze/root_cause/` and `$HOME/.claude/scripts/analyze/root_cause/`
   - Ask user: "Could not locate root cause analysis scripts. Please provide full path to the scripts directory:"
   - Validate provided path contains expected scripts (trace_execution.py, recent_changes.py, error_patterns.py)
   - Set SCRIPT_PATH to user-provided location

**THEN - Execute with resolved SCRIPT_PATH:**

```bash
python [SCRIPT_PATH]/trace_execution.py . --output-format json
python [SCRIPT_PATH]/recent_changes.py . --output-format json
python [SCRIPT_PATH]/error_patterns.py . --output-format json
```

## Optional Flags

--seq: Use for difficult bugs requiring systematic investigation - creates a structured approach: 'reproduce bug consistently', 'isolate variables', 'analyze root cause', 'implement targeted fix', 'verify solution and prevent regression'
--c7: Use to find debugging techniques and tools specific to your technology (e.g., Chrome DevTools for React, pdb strategies for Python, gdb for C/C++, Node.js inspector)

## Quality Gates

- **Diagnosis Gate**: Reproducible bug with identified root cause
- **Planning Gate**: Comprehensive fix strategy with risk mitigation
- **Implementation Gate**: Working fix with comprehensive test coverage
- **Validation Gate**: No regressions with enhanced monitoring

## Output Requirements

- Detailed bug reproduction steps and root cause analysis
- Minimal, targeted fix addressing fundamental cause
- Comprehensive test suite including reproduction test
- Bug analysis documentation with lessons learned

## Symbol Legend

- 🐛 Bug identification & analysis
- 🔍 Root cause investigation needed
- 🧪 Testing strategy required
- ⚠ Regression risk assessment
- 🎯 Fix validation criteria
- 🚨 Critical bug requiring immediate attention
- ✅ Bug fix validation passed

$ARGUMENTS
