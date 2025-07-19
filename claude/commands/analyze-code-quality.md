# analyze-code-quality v0.2

**Mindset**: "Quality first" - Systematic code quality assessment with measurable metrics and improvement recommendations.

## Behavior

Comprehensive code quality analysis combining automated metrics with architectural assessment for maintainable, readable code.

### Code Quality Assessment Areas

- **Complexity Metrics**: Cyclomatic complexity, function length, parameter count analysis
- **Code Patterns**: Design pattern compliance and anti-pattern identification
- **Maintainability**: Code readability, documentation quality, and structure assessment
- **Technical Debt**: Code smells, duplication, and refactoring opportunities
- **SOLID Principles**: Single responsibility, open-closed, Liskov substitution compliance
- **Testing Quality**: Test coverage, test quality, and testability assessment

## Script Integration

Execute code quality analysis scripts via Bash tool for measurable quality metrics:

**Note**: LLM must locate the script installation directory dynamically using Glob tool to find script paths, then execute with correct absolute paths.

```bash
# Example execution format (LLM will determine actual paths):
python [SCRIPT_PATH]/complexity_lizard.py . --output-format json
python [SCRIPT_PATH]/complexity_metrics.py . --output-format json
```

**Script Location Process:**
1. Use Glob tool to find script paths: `**/scripts/analyze/code_quality/*.py`
2. Verify script availability and determine correct absolute paths
3. Execute scripts with resolved paths

## Optional Flags

--c7: Use when evaluating if specific code implementations follow current best practices for your framework/language (e.g., React hooks patterns, Python PEP standards, Go idiomatic code)
--seq: Use when code quality issues are complex or interconnected - breaks analysis into actionable steps like 'assess complexity metrics', 'check SOLID compliance', 'evaluate test coverage', 'identify refactoring opportunities'

## Output Requirements

- Code quality metrics report with complexity analysis
- Technical debt assessment with prioritized improvement opportunities
- Best practices compliance evaluation with specific recommendations
- Quality improvement roadmap with implementation guidance

$ARGUMENTS
