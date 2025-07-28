# analyze-architecture v0.2

**Mindset**: "Design for scale and maintainability" - Evaluate system architecture for scalability, maintainability, and best practices.

## Behavior

Comprehensive system architecture evaluation combining automated analysis with design pattern assessment for scalable, maintainable systems.

### Automated Architecture Analysis

Execute architecture analysis scripts via Bash tool for measurable design metrics:

**Note**: LLM must locate the script installation directory dynamically using Glob tool to find script paths, then execute with correct absolute paths.

```bash
# Example execution format (LLM will determine actual paths):
# LLM must locate script installation directory dynamically using Glob tool
# Scripts may be in project-level .claude/ or user-level ~/.claude/ directories
python [SCRIPT_PATH]/pattern_evaluation.py . --output-format json
python [SCRIPT_PATH]/scalability_check.py . --output-format json
python [SCRIPT_PATH]/coupling_analysis.py . --output-format json
```

**Script Location Process:**

1. Use Glob tool to find script paths: `**/scripts/analyze/architecture/*.py`
2. Verify script availability and determine correct absolute paths
3. Execute scripts with resolved paths

### Architecture Assessment Areas

- **Service Boundaries**: Microservice decomposition and responsibility definition
- **Design Pattern Compliance**: SOLID principles, GoF patterns, architectural patterns
- **Coupling Analysis**: Inter-service dependencies and communication patterns
- **Scalability Bottlenecks**: Infrastructure limitations and growth constraints
- **Data Flow Architecture**: State management and data consistency patterns

## Analysis Process

1. **Execute automated scripts** for quantitative architecture metrics
2. **Evaluate design patterns** against established best practices
3. **Assess scalability** through bottleneck identification
4. **Analyze coupling** between components and services
5. **Generate recommendations** for architectural improvements

## Optional Flags

--c7: Use when you need to validate your architecture decisions against current industry standards for your specific tech stack (e.g., microservices patterns for Node.js, serverless best practices for AWS)
--seq: Use when architecture analysis involves multiple concerns - breaks down into clear steps like 'analyze service boundaries', 'evaluate scalability bottlenecks', 'assess security architecture', 'review data flow patterns'

## Assessment Areas

Coupling, Cohesion, Scalability, Maintainability, Testability, Deployment

## Output Requirements

- Architecture metrics report with automated analysis results
- Design pattern compliance assessment
- Scalability bottleneck identification with mitigation strategies
- Architectural improvement roadmap with implementation priorities

$ARGUMENTS
