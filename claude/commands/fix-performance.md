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

## Optional Flags
--c7: Use to discover proven optimization strategies for your specific bottleneck type and technology stack (e.g., React.memo patterns, database query optimization, caching strategies)
--seq: Use for complex performance fixes - creates structured approach: 'measure baseline performance', 'profile application', 'identify specific bottleneck', 'implement targeted optimization', 'validate improvement and monitor'

## Performance Areas
Database, Frontend, Algorithms, Memory, Network, Caching

## Output Requirements
- Performance issue analysis with specific bottleneck identification
- Optimization implementation with measurable improvement targets
- Before/after performance comparison with validation results
- Ongoing monitoring strategy for performance regression prevention

$ARGUMENTS