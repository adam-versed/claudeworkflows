# Agent Creation Template

## Purpose

Define the universal approach for creating agent files that enable specialized AI subagents with focused expertise, clear invocation patterns, and effective task delegation.

## Core Approach

**Focused expertise, proactive delegation** - Create agents with single, clear responsibilities that Claude can automatically invoke based on task context and requirements.

## Agent Structure

### 1. YAML Frontmatter (Required)

```yaml
---
name: agent-name  # lowercase with hyphens
description: Use proactively for [primary purpose and invocation guidance]. MUST BE USED for [critical scenarios].\n\nExamples:\n- <example>\n  Context: Situation where this agent is needed.\n  user: "User request that triggers this agent"\n  assistant: "I'll use the agent-name agent to handle this specific task"\n  <commentary>\n  Explanation of why this agent is appropriate for this scenario.\n  </commentary>\n</example>\n- <example>\n  Context: Another common use case.\n  user: "Different request needing this expertise"\n  assistant: "Let me invoke the agent-name agent to address this requirement"\n  <commentary>\n  Clear reasoning for agent selection.\n  </commentary>\n</example>
model: opus  # opus (highly complex/organizational) > sonnet (complex execution) > haiku (simple/documentation)
color: blue  # visual identifier
tools: Read, Write, Edit, MultiEdit, Bash, Grep, Glob, LS, WebFetch, WebSearch, Task, TodoWrite, ExitPlanMode  # Optional - omit to inherit all tools. Select ONLY the minimum tools needed for the agent's specific tasks
---
```

### 2. Agent Prompt (Required)

#### Opening Statement

```markdown
You are a [role/expertise] specializing in [specific domain]. You [primary value proposition and key differentiator].
```

#### Core Sections Structure

**Choose the most appropriate structure based on agent type:**

##### Option A: Responsibility-Based Structure (Default)

```markdown
## Core Responsibilities

1. **Primary Responsibility**

   - Specific action or outcome
   - Key consideration or constraint
   - Quality expectation
   - Measurement criteria

2. **Secondary Responsibility**
   - Supporting actions
   - Integration points
   - Coordination needs
   - Success metrics

## Operational Approach

### [Key Workflow Name]

1. First concrete step
2. Analysis or assessment action
3. Implementation or execution
4. Validation or verification

### [Secondary Workflow]

1. Numbered steps for clarity
2. Each step actionable
3. Clear progression
4. Definite outcomes

## Output Format

Your [deliverables] should always include:

- **Component Name**: Description and purpose
- **Another Component**: What it contains
- **Final Component**: Expected format
```

##### Option B: Behavioral Structure (For Coordination Agents)

```markdown
## Key Behaviors

### When [Scenario/Trigger]

1. **Immediate Action**: What to do first
2. **Assessment**: What to evaluate
3. **Decision**: How to proceed
4. **Outcome**: What to deliver

### When [Different Scenario]

1. **Recognition**: How to identify
2. **Response**: Appropriate action
3. **Coordination**: Who to involve
4. **Resolution**: Success criteria

## Communication Patterns

**With [Stakeholder Type]:**

- Key information to provide
- Format for updates
- Frequency expectations
- Escalation triggers

## Critical Triggers

**IMMEDIATELY [action] when:**

- Specific condition detected
- Threshold exceeded
- Risk identified
- Approval needed
```

##### Option C: Process Structure (For Technical Agents)

```markdown
## Process Overview

When invoked:

1. Initial assessment step
2. Core analysis action
3. Implementation phase
4. Verification step
5. Delivery format

## Technical Approach

### [Technical Area]

- Specific methodology
- Tools and techniques
- Quality standards
- Output expectations

### Validation Criteria

- Success metrics
- Failure indicators
- Edge cases
- Recovery procedures

## Deliverables

For each [task type]:

- Required analysis
- Implementation details
- Testing approach
- Documentation needs
```

### 3. Closing Directive (Optional but Recommended)

```markdown
Remember: [Mission statement that reinforces the agent's core purpose and approach].
```

## Writing Standards

### Description Field Guidelines

1. **Opening phrase**: MUST start with "Use proactively for" to enable automatic delegation
2. **Critical triggers**: Include "MUST BE USED for" to specify mandatory invocation scenarios
3. **Examples**: 2-3 concrete scenarios with context, user input, and reasoning
4. **Format**: Single line with \n escapes, not multi-line YAML

### Prompt Guidelines

1. **Length**: 50-80 lines optimal (concise but complete)
2. **Voice**: Active and directive ("You ensure", "Monitor", "Coordinate")
3. **Specificity**: Concrete actions over abstract concepts
4. **Structure**: Numbered lists and clear hierarchies
5. **Emphasis**: Use **bold** for critical points sparingly
6. **Agent References**: When referring to other agents, always use the `@agent-[agentspecname]` format (e.g., `@agent-quality-monitor`, `@agent-fullstack-developer`)

### Tool Selection

1. **Minimal set**: Only tools necessary for the role
2. **Security**: Consider least privilege principle
3. **Efficiency**: Tools that support the primary workflow
4. **Omit if unsure**: Inherit all tools by leaving blank

## Agent Types and Patterns

### Execution Agents

- Focus on doing specific tasks
- Clear process steps
- Defined deliverables
- Success criteria

### Coordination Agents

- Focus on orchestration
- Communication patterns
- Dependency management
- Progress tracking

### Analysis Agents

- Focus on investigation
- Structured assessment
- Clear findings format
- Actionable recommendations

### Quality Agents

- Focus on standards
- Validation processes
- Issue identification
- Improvement suggestions

## Best Practices

1. **Single Responsibility**: One clear purpose per agent
2. **Proactive Language**: Enable automatic invocation
3. **Concrete Examples**: Real scenarios in description
4. **Action-Oriented**: Focus on what the agent does
5. **Clear Boundaries**: Define what's in and out of scope
6. **Output Formats**: Specify expected deliverables
7. **Escalation Paths**: When to involve humans

## Common Pitfalls to Avoid

1. **Over-broad scope**: Trying to do too much
2. **Vague triggers**: Unclear when to invoke
3. **Missing examples**: No concrete use cases
4. **Passive voice**: "Tasks should be" vs "Monitor tasks"
5. **No output format**: Unclear deliverables
6. **Tool overload**: Requesting unnecessary tools

## Validation Checklist

Before finalizing an agent:

- [ ] Name follows lowercase-hyphen convention
- [ ] Description includes 2-3 examples with \n formatting
- [ ] Opening statement clearly defines expertise
- [ ] Structure matches agent type (execution/coordination/analysis)
- [ ] All sections use active voice
- [ ] Output format is explicitly defined
- [ ] Agent references use @agent-[name] format consistently
- [ ] Tools are minimal and necessary
- [ ] Total length is 50-80 lines
- [ ] Includes memorable closing directive
