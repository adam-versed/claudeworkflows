# analyze-performance v0.2

**Mindset**: "Where are the bottlenecks?" - Combine static analysis with live performance monitoring.

## Behavior
Comprehensive performance analysis combining automated script analysis with live testing capabilities for complete performance optimization.

### Automated Performance Analysis
Execute performance analysis scripts via Bash tool for measurable bottleneck detection:

**Note**: LLM must locate the script installation directory dynamically using Glob tool to find script paths, then execute with correct absolute paths.

```bash
# Example execution format (LLM will determine actual paths):
python [SCRIPT_PATH]/check_bottlenecks.py . --output-format json
python [SCRIPT_PATH]/analyze_frontend.py . --output-format json
python [SCRIPT_PATH]/profile_database.py . --output-format json
```

**Script Location Process:**
1. Use Glob tool to find script paths: `**/scripts/analyze/performance/*.py`
2. Verify script availability and determine correct absolute paths
3. Execute scripts with resolved paths

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

## Optional Flags
--c7: Use when you need proven optimization techniques for your specific stack (e.g., React rendering optimizations, Django ORM query patterns, database indexing strategies)
--seq: Use for complex performance issues requiring step-by-step investigation - breaks down into 'profile application', 'identify bottlenecks', 'analyze database queries', 'evaluate caching strategies', 'measure improvements'

## Performance Areas
Database, Frontend, Algorithms, Memory, Network, Caching, Scalability

## Output Requirements
- Performance metrics report with script analysis results
- Bottleneck identification with impact assessment
- Optimization recommendations prioritized by ROI
- Implementation guidance with code examples

$ARGUMENTS