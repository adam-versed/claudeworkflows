# analyze-performance v0.2

**Mindset**: "Where are the bottlenecks?" - Combine static analysis with live performance monitoring.

## Behavior

Comprehensive performance analysis combining automated script analysis with live testing capabilities for complete performance optimization.

### Automated Performance Analysis

Execute performance analysis scripts via Bash tool for measurable bottleneck detection:

**FIRST - Resolve SCRIPT_PATH:**

1. **Try project-level .claude folder**:

   ```bash
   Glob: ".claude/scripts/analyze/performance/*.py"
   ```

2. **Try user-level .claude folder**:

   ```bash
   Bash: ls "$HOME/.claude/scripts/analyze/performance/"
   ```

3. **Interactive fallback if not found**:
   - List searched locations: `.claude/scripts/analyze/performance/` and `$HOME/.claude/scripts/analyze/performance/`
   - Ask user: "Could not locate performance analysis scripts. Please provide full path to the scripts directory:"
   - Validate provided path contains expected scripts (check_bottlenecks.py, analyze_frontend.py, profile_database.py)
   - Set SCRIPT_PATH to user-provided location

**THEN - Execute with resolved SCRIPT_PATH:**

```bash
python [SCRIPT_PATH]/check_bottlenecks.py . --output-format json
python [SCRIPT_PATH]/analyze_frontend.py . --output-format json
python [SCRIPT_PATH]/profile_database.py . --output-format json
```

### Performance Assessment Areas

- **Database Optimization**: Query analysis, N+1 detection, index optimization, execution plans
- **Frontend Performance**: Bundle analysis, render optimization, memory leak detection
- **Algorithm Complexity**: CPU/memory profiling and optimization recommendations
- **Network Optimization**: Request optimization, caching strategy evaluation
- **Scalability Analysis**: Bottleneck identification for high-load scenarios

## Analysis Process

1. **Execute automated scripts** for measurable performance data
2. **Analyze performance metrics** in context of user experience
3. **Identify bottlenecks** through systematic profiling
4. **Prioritize optimizations** by impact and implementation effort
5. **Generate recommendations** with before/after validation

## Performance Areas

Database, Frontend, Algorithms, Memory, Network, Caching, Scalability

## Output Requirements

- Performance metrics report with script analysis results
- Bottleneck identification with impact assessment
- Optimization recommendations prioritized by ROI
- Implementation guidance with code examples

$ARGUMENTS
