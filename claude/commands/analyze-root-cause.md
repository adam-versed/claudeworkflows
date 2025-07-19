# analyze-root-cause v0.2

**Mindset**: "Find the real problem" - Systematic root cause analysis using evidence-based investigation methodology.

## Behavior
Comprehensive root cause analysis combining automated investigation tools with systematic reasoning for accurate problem identification.

### Root Cause Investigation Areas
- **Change Correlation**: Recent code changes and their impact analysis
- **Error Pattern Analysis**: Error log analysis and pattern identification
- **Execution Tracing**: Code execution flow and failure point identification
- **Five Whys Analysis**: Iterative questioning to reach fundamental causes
- **Timeline Analysis**: Sequence of events leading to the issue
- **Environmental Factors**: System configuration and dependency analysis

### Enhanced Debugging (--verbose flag)
- **Comprehensive Logging**: Structured logging with contextual information and trace correlation
- **Distributed Tracing**: Cross-service request tracing and performance analysis
- **Diagnostic Instrumentation**: Metrics collection, profiling, and observability enhancement
- **Error Context**: Detailed error information with stack traces and state capture
- **Performance Monitoring**: Resource usage tracking and bottleneck identification
- **Event Correlation**: Event timeline and causal relationship analysis

## Script Integration
Execute root cause analysis scripts via Bash tool for systematic investigation:

**Note**: LLM must locate the script installation directory dynamically using Glob tool to find script paths, then execute with correct absolute paths.

```bash
# Example execution format (LLM will determine actual paths):
python [SCRIPT_PATH]/trace_execution.py . --output-format json
python [SCRIPT_PATH]/recent_changes.py . --output-format json
python [SCRIPT_PATH]/error_patterns.py . --output-format json
python [SCRIPT_PATH]/simple_trace.py . --output-format json
```

**Script Location Process:**
1. Use Glob tool to find script paths: `**/scripts/analyze/root_cause/*.py`
2. Verify script availability and determine correct absolute paths
3. Execute scripts with resolved paths

## Optional Flags
--c7: Use when investigating framework-specific issues to understand common failure patterns and debugging approaches for your technology stack (e.g., React debugging tools, Python traceback analysis, Node.js memory leak detection)
--seq: Use for complex bugs where the cause isn't obvious - systematically breaks down investigation into 'reproduce issue', 'analyze error patterns', 'check recent changes', 'trace execution flow', 'identify root cause'
--verbose: Use when you need detailed diagnostic output including comprehensive logging setup, distributed tracing configuration, and detailed error context capture for complex debugging scenarios

## Output Requirements
- Root cause analysis report with evidence-based findings
- Change correlation analysis with impact assessment
- Error pattern identification with frequency analysis
- Investigation timeline with causal relationships

$ARGUMENTS