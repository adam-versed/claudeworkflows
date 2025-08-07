# fix-performance v0.2

**Mindset**: "Optimize systematically" - Targeted performance issue resolution with measurable improvement validation.

## Behavior

Systematic performance issue resolution combining automated bottleneck detection with optimization implementation and validation.

### Performance Optimization Strategy

- **Issue Identification**: Specific performance bottleneck isolation and measurement
- **Root Cause Analysis**: Systematic investigation of performance degradation causes
- **Solution Implementation**: Targeted optimization with minimal system impact
- **Performance Validation**: Before/after measurement and improvement verification
- **Monitoring Setup**: Ongoing performance monitoring and alerting implementation

## Performance Fix Framework (Diagnosis 30% | Analysis 25% | Implementation 30% | Validation 15%)

### Performance Diagnosis

- **Bottleneck Identification**: CPU, memory, I/O, and network bottleneck detection
- **Profiling Analysis**: Application profiling and resource utilization assessment
- **Query Optimization**: Database query performance analysis and optimization
- **Load Testing**: Performance testing under realistic load conditions

### Root Cause Analysis

- **Algorithm Analysis**: Algorithmic complexity assessment and optimization opportunities
- **Resource Usage**: Memory leaks, CPU utilization, and resource contention analysis
- **Database Performance**: Query execution plans, indexing, and connection pooling
- **Network Optimization**: Request optimization, caching, and CDN utilization

### Implementation Strategy

- **Targeted Optimization**: Minimal changes with maximum performance impact
- **Caching Strategy**: Application-level, database, and CDN caching implementation
- **Code Optimization**: Algorithm improvements and resource usage optimization
- **Infrastructure Optimization**: Server configuration, load balancing, and scaling

### Performance Validation

- **Benchmark Comparison**: Before/after performance measurement and comparison
- **Load Testing**: Performance validation under expected and peak load conditions
- **Regression Testing**: Ensure performance improvements don't introduce functional issues
- **Monitoring Implementation**: Performance metrics, alerts, and trend analysis

## Script Integration

Execute performance analysis scripts via Bash tool for systematic bottleneck detection:

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

## Performance Areas

Database, Frontend, Algorithms, Memory, Network, Caching

## Output Requirements

- Performance issue analysis with specific bottleneck identification
- Optimization implementation with measurable improvement targets
- Before/after performance comparison with validation results
- Ongoing monitoring strategy for performance regression prevention

$ARGUMENTS
