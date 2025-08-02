# plan-solution v0.2

**Purpose**: Research-driven technical challenge solving with systematic analysis and implementation planning.

## Workflow

### Phase 1: Context Gathering

**STOP** → "To ensure my analysis addresses your specific situation, please provide:

**1. Technical Challenge:**

- Describe the specific problem, feature, or system requirement you need to address
- Include any current pain points or limitations you're experiencing
- Specify if this involves analyzing/improving a current codebase or general planning

**2. Technical Environment Constraints:**

- Existing technology stack, platforms, or infrastructure requirements
- Legacy system integration requirements
- Compliance, security, or regulatory constraints
- Team skill sets and technology preferences

**3. Development Approach Preferences:**

- Do you prefer leveraging established libraries/frameworks vs custom development?
- Priority: speed to market, cost optimization, technical control, or long-term maintainability?
- Available development resources and timeline constraints

Please provide your technical challenge and any relevant constraints, or confirm if you'd like me to proceed with general assumptions."

### Phase 2: System Analysis (Conditional)

**Only execute if analyzing a current codebase** (skip for general planning questions):

1. **Run architecture analysis**:

   **FIRST - Resolve SCRIPT_PATH:**

   1. **Try project-level .claude folder**:

      ```bash
      Glob: ".claude/scripts/analyze/architecture/*.py"
      ```

   2. **Try user-level .claude folder**:

      ```bash
      Bash: ls "$HOME/.claude/scripts/analyze/architecture/"
      ```

   3. **Interactive fallback if not found**:
      - List searched locations: `.claude/scripts/analyze/architecture/` and `$HOME/.claude/scripts/analyze/architecture/`
      - Ask user: "Could not locate architecture analysis scripts. Please provide full path to the scripts directory:"
      - Validate provided path contains expected scripts (pattern_evaluation.py, scalability_check.py, coupling_analysis.py)
      - Set SCRIPT_PATH to user-provided location

   **THEN - Execute with resolved SCRIPT_PATH:**

   ```bash
   python [SCRIPT_PATH]/pattern_evaluation.py .
   python [SCRIPT_PATH]/scalability_check.py .
   python [SCRIPT_PATH]/coupling_analysis.py .
   ```

2. **Document findings**:
   - Current patterns identified
   - Scalability constraints
   - Integration points
   - Technical debt considerations

**If general planning** (no current codebase): Proceed directly to Phase 3.

### Phase 3: Research & Solutions

1. **Research best practices** (web search)
2. **Develop 3 solution approaches**:
   - **Solution 1**: Conservative/established approach
   - **Solution 2**: Balanced approach
   - **Solution 3**: Innovative/modern approach

### Phase 4: Comparative Analysis

| Aspect                     | Solution 1     | Solution 2     | Solution 3     |
| -------------------------- | -------------- | -------------- | -------------- |
| **Development Complexity** | [Rating/Notes] | [Rating/Notes] | [Rating/Notes] |
| **Integration Effort**     | [Rating/Notes] | [Rating/Notes] | [Rating/Notes] |
| **Technology Risk**        | [Rating/Notes] | [Rating/Notes] | [Rating/Notes] |
| **Team Readiness**         | [Rating/Notes] | [Rating/Notes] | [Rating/Notes] |

### Phase 5: Recommendation & Roadmap

**Recommended Solution**: [Choose one]

**Justification**:

- Technical alignment with current system
- Balance of risk vs benefit
- Resource/timeline fit

**Implementation Roadmap**:

- **Phase 1**: Foundation setup ([timeline])
- **Phase 2**: Core implementation ([timeline])
- **Phase 3**: Optimization & testing ([timeline])

**Success Criteria**:

- Performance benchmarks: [metrics]
- Integration success: [validation approach]
- Monitoring setup: [observability plan]

### Phase 6: Task Transfer

**STOP** → "Ready to transfer implementation roadmap to todos.md?"

**If confirmed**:

1. Check `./todos/todos.md` exists
2. Append implementation tasks
3. Format as actionable checkboxes
4. Confirm transfer complete

## Flags

- `--critique`: Critique your reasoning around the user request, the solution options you select and the final recommendation

## Templates

**Solution format**:

```
## [Solution Name]
**Approach**: [Technical strategy]
**Stack**: [Technologies]
**Complexity**: [Effort/Resources]
**Risk**: [Assessment]
```
