# plan-refactor v0.2

**Mindset**: "Improve without breaking" - Strategic technical debt reduction and modernization planning with extensive code analysis and automated safety nets.

## Behavior

Comprehensive refactoring strategy combining automated code analysis, proven migration patterns, and detailed testing plans to ensure safe technical debt reduction and modernization without functionality loss.

### Automated Analysis Integration

Execute comprehensive code analysis using existing automation scripts for token-efficient technical debt identification:

**Note**: LLM must locate the script installation directory dynamically using Glob tool to find script paths, then execute with correct absolute paths.

```bash
# Example execution format (LLM will determine actual paths):
python [SCRIPT_PATH]/run_all_analysis.py . --output-format json
python [SCRIPT_PATH]/complexity_metrics.py . --output-format json
python [SCRIPT_PATH]/coupling_analysis.py . --output-format json
python [SCRIPT_PATH]/check_bottlenecks.py . --output-format json
```

**Script Location Process:**
1. Use Glob tool to find script paths: `**/scripts/*.py` and `**/scripts/analyze/*/*.py`
2. Verify script availability and determine correct absolute paths
3. Execute scripts with resolved paths

**Analysis Integration:**
- Execute pre-analysis to identify technical debt hotspots and refactoring candidates
- Generate automated reports with complexity metrics and architectural debt assessment
- Identify performance bottlenecks and optimization opportunities through script automation
- Use existing security analysis for vulnerability remediation planning
- Token-efficient analysis execution with summary modes and focused reporting

## Refactoring Framework (Analysis 35% | Strategy 25% | Implementation 25% | Validation 15%)

### Phase 1: Extensive Code Analysis

**Automated Technical Debt Assessment:**
- **Complexity Hotspots**: Execute complexity_metrics.py to identify high-complexity modules requiring refactoring
- **Architectural Debt**: Run coupling_analysis.py to find tight coupling and structural improvement opportunities
- **Performance Debt**: Use check_bottlenecks.py and profile_database.py to identify optimization targets
- **Security Debt**: Execute security analysis scripts for vulnerability remediation prioritization
- **Code Quality Issues**: Automated detection of code smells, dead code, and maintainability problems

**Migration Area Identification:**
- Automated analysis of user-requested migration areas (legacy frameworks, outdated patterns, performance issues)
- Cross-reference user requirements with automated analysis findings
- Prioritize refactoring candidates based on impact, effort, and risk assessment
- Generate migration scope definition with clear boundaries and dependencies

### Phase 2: Context7-Enhanced Migration Strategy

**Proven Pattern Integration:**
Use Context7 to research and implement industry-proven refactoring patterns:

```
--c7 queries for migration patterns:
- Strangler Fig Pattern for legacy system migration
- Module Federation for monolith decomposition
- Database migration strategies (blue-green, shadow mode)
- Framework migration patterns (React class→hooks, Angular upgrade paths)
- Microservices extraction patterns
- API versioning and backward compatibility strategies
```

**Technology-Specific Best Practices:**
- Research current best practices for target technology stack
- Validate migration approach against industry standards and case studies
- Incorporate lessons learned from similar refactoring projects
- Identify potential pitfalls and proven mitigation strategies

### Phase 3: Implementation Strategy

**Phased Migration Planning:**
- **Phase Breakdown**: Incremental refactoring strategy with minimal risk phases
- **Dependency Management**: Automated dependency analysis and migration sequencing
- **Feature Flag Integration**: Safe deployment strategy with rollback capabilities
- **Parallel Development**: Strategy for maintaining development velocity during refactoring

**Change Management Strategy:**
- Version control strategy for large refactoring efforts
- Code review checkpoints and quality gates
- Integration testing at each migration phase
- Documentation updates and knowledge transfer planning

### Phase 4: Comprehensive Testing Strategy

**Automated Testing Plan:**
```bash
# Example execution format (LLM will determine actual paths):
python [SCRIPT_PATH]/test_coverage_analysis.py . --output-format json
python [SCRIPT_PATH]/performance_baseline.py . --output-format json
```

**Testing Framework:**
- **Baseline Establishment**: Automated performance and functionality baselines before refactoring
- **Regression Test Planning**: Identify critical features and functions requiring regression test coverage
- **Integration Testing**: API contract validation and system integration verification
- **Performance Testing**: Before/after performance comparison with automated benchmarking
- **Rollback Testing**: Automated rollback procedure validation and safety net verification

**Quality Assurance Strategy:**
- Automated code quality validation at each migration phase
- Performance regression detection and alerting
- Functional parity verification through automated testing
- User acceptance testing strategy for critical business functions
- **Regression Test Coverage Planning**: Identify and document critical features requiring regression test coverage based on refactoring scope

## Enhanced Optional Flags

**--c7**: Research proven refactoring patterns and migration strategies for your specific technical debt:
- Legacy system modernization (strangler fig, anti-corruption layer)
- Framework migrations (React, Angular, Vue upgrade paths)
- Database refactoring (schema evolution, data migration)
- Microservices extraction (domain boundaries, service splitting)
- Performance optimization (caching strategies, query optimization)

**--seq**: Structure complex refactoring into manageable phases:
- Phase 1: 'Execute automated analysis and identify technical debt hotspots'
- Phase 2: 'Research migration patterns and create strategy with Context7'
- Phase 3: 'Plan implementation phases with safety nets and rollback procedures'
- Phase 4: 'Generate comprehensive testing strategy and validation framework'
- Phase 5: 'Create monitoring and success metrics for refactoring impact'

## Automation Integration

**Existing Script Leverage:**
- Use run_all_analysis.py for comprehensive pre-refactoring assessment
- Integrate complexity_metrics.py findings into refactoring prioritization
- Leverage security analysis for vulnerability remediation planning
- Use performance analysis scripts for optimization target identification

**Token Cost Reduction:**
- Pre-computed analysis summaries instead of manual code review
- Automated report generation with executive summaries
- Script-based technical debt quantification and prioritization
- Automated dependency and impact analysis

## Task List Transfer

**Final Step:** After completing the refactoring strategy, present the comprehensive plan to the user:

"**Refactoring Plan Summary:**
- **Technical Debt Identified**: [Automated analysis summary]
- **Migration Strategy**: [Context7-informed approach]
- **Implementation Phases**: [Detailed timeline with milestones]
- **Testing Strategy**: [Comprehensive validation plan]
- **Regression Test Requirements**: [Critical features needing regression test coverage]
- **Risk Mitigation**: [Safety nets and rollback procedures]

Are you satisfied with this refactoring plan and ready to proceed? If yes, I'll transfer the implementation tasks to your project's todo.md file for tracking."

**If user confirms:**
1. Check if `./todos/todos.md` exists
2. If it exists, append the refactoring tasks from the plan
3. If it doesn't exist, create it with the refactoring tasks
4. Format tasks as actionable items with clear phases and milestones
5. Confirm to user that tasks have been added to todo.md

**Task Format Example:**
```markdown
## [System/Component] Refactoring Tasks

### Phase 1: Pre-refactoring Preparation
- [ ] Create comprehensive test baseline for affected areas
- [ ] Document current system behavior and dependencies
- [ ] Set up feature flags for gradual rollout
- [ ] Establish performance benchmarks

### Phase 2: Core Refactoring
- [ ] Refactor [high-priority component] using [pattern]
- [ ] Migrate [legacy system] to [modern approach]
- [ ] Update [database/API] following migration strategy
- [ ] Implement rollback procedures

### Phase 3: Validation & Optimization
- [ ] Run full regression test suite
- [ ] Validate performance improvements
- [ ] Complete security vulnerability remediation
- [ ] Update documentation and knowledge base
```

## Output Requirements

- **Automated Technical Debt Assessment**: Script-generated analysis with complexity metrics and architectural debt
- **Context7-Enhanced Migration Strategy**: Research-backed refactoring approach with proven patterns
- **Comprehensive Testing Plan**: Automated test generation with regression prevention and performance validation
- **Implementation Roadmap**: Phased approach with safety nets, rollback procedures, and success metrics
- **Todo.md Integration**: Approved plans automatically transferred to actionable task tracking

## Validation Framework

**Success Metrics:**
- Code complexity reduction (measurable through automated metrics)
- Performance improvement validation (before/after benchmarking)
- Security vulnerability remediation (automated security scan comparison)
- Test coverage maintenance or improvement
- Development velocity impact assessment

**Safety Measures:**
- Automated rollback procedures for each migration phase
- Feature flag integration for gradual rollout
- Performance monitoring and alerting
- Functionality parity verification through comprehensive testing

$ARGUMENTS