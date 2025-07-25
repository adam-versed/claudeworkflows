# plan-refactor v0.3

**Mindset**: "Improve without breaking" - Strategic technical debt reduction and modernization planning through automated analysis, proven patterns, and comprehensive testing frameworks.

## Workflow Process

### Phase 1: Technical Debt Assessment

1. **Execute automated analysis** - Run comprehensive technical debt assessment

   ```bash
   # Note: LLM must locate script installation directory dynamically using Glob tool
   # Scripts may be in project-level .claude/ or user-level ~/.claude/ directories
   python [SCRIPT_PATH]/run_all_analysis.py . --output-format json
   python [SCRIPT_PATH]/complexity_metrics.py . --output-format json
   python [SCRIPT_PATH]/coupling_analysis.py . --output-format json
   python [SCRIPT_PATH]/check_bottlenecks.py . --output-format json
   ```

2. **Identify refactoring priorities** - Analyze complexity hotspots and architectural debt

   - Cross-reference security vulnerabilities with refactoring scope

3. **Generate technical debt report** - Compile results into executive summary
   - Define migration scope with clear boundaries and dependencies

**STOP** → "Technical debt analysis complete. Proceed with strategy development? (y/n)"

### Phase 2: Migration Strategy Development

1. **Research proven refactoring patterns** - Use Context7 for industry-proven strategies

   - Identify patterns: Strangler Fig, Module Federation, Blue-Green deployment

2. **Create phased migration plan** - Design incremental strategy with minimal risk

   - Define feature flag integration for safe deployment

3. **Define rollback procedures** - Establish automated rollback mechanisms
   - Create safety nets and monitoring for each migration phase

**STOP** → "Migration strategy defined. Ready to create implementation plan? (y/n)"

### Phase 3: Implementation Planning

1. **Generate detailed task breakdown** - Create implementation timeline with checkpoints

   - Plan integration testing at each migration phase

2. **Create testing strategy** - Establish baselines and regression coverage

   ```bash
   # Note: LLM must locate script installation directory dynamically using Glob tool
   # Scripts may be in project-level .claude/ or user-level ~/.claude/ directories
   python [SCRIPT_PATH]/test_coverage_analysis.py . --output-format json
   ```

3. **Define success metrics** - Set measurable complexity and performance targets
   - Create development velocity impact assessment framework

### Phase 4: Quality Validation and Task Transfer

1. **Validate plan completeness** - Verify approaches and rollback procedures

   - Ensure success metrics are measurable and achievable

2. **Quality Gates Validation**

   - [ ] Technical debt hotspots identified and prioritized
   - [ ] Migration strategy validated against proven patterns
   - [ ] Implementation phases include comprehensive rollback procedures
   - [ ] Testing strategy covers regression prevention and performance validation
   - [ ] All refactoring targets have defined success metrics

3. **Transfer tasks to todos.md** - Generate actionable implementation tasks
   - Append formatted tasks with clear phases to todos.md

**STOP** → "Implementation plan complete and validated. Transfer to todos.md? (y/n)"

## Enhanced Optional Flags

**--c7**: Research proven refactoring patterns and migration strategies:

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

## Task Format for todos.md Transfer

```markdown
## [System/Component] Refactoring Implementation

### Phase [PHASE-NUMBER]: [PHASE-TITLE]

- [ ] [PHASE-TASK]
- [ ] [PHASE-TASK]
- [ ] [PHASE-TASK]
```

$ARGUMENTS
