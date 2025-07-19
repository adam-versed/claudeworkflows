# Programmatic Prompt Workflow Rules

## Purpose
Define the universal approach for creating command files that balance conciseness with clarity, maintaining complete phase workflows with numbered steps, code snippets, and user interactions.

## Core Approach
**Concise precision, complete structure** - Use minimal words to express complete phase workflows with numbered steps, code snippets, and user interactions.

## Command Structure

### Mandatory Sections
**Required for all command files:**

#### 1. Command Header
**Purpose**: Provide immediate context and usage instructions
```markdown
# [Command Name] (`[command]`)

**Purpose**: [One-line description]
**Usage**: `claude /[command] [flags]`

#### 2. Phase Structure
**Purpose**: Create clear workflow progression that guides LLM through logical steps while maintaining user visibility and control
```markdown
### Phase [N]: [Name]
1. **Action**: [step description]
2. **Next action**: [step description]
```

### Optional Sections
**Include only when needed:**

#### 1. STOP Interactions
**Include when**: User input is required for context, decisions, or approvals
**Purpose**: Get user input at critical decision points to ensure alignment and maintain collaborative workflow
```markdown
**STOP** → [specific question]
```

#### 2. Bash Commands
**Include when**: System operations or automation is required
**Purpose**: Provide executable commands for system operations and automation, ensuring commands are immediately actionable without interpretation
```markdown
**Command**: `specific command`
**Output**: [expected result format]
```

#### 3. Tool Usage Definition
**Include when**: External tools are needed for analysis or operations
**Purpose**: Standardize tool invocation patterns for consistency and eliminate ambiguity in tool selection and usage
```markdown
**Tool**: [tool name] - [specific purpose]
**Usage**: [tool invocation pattern]
```

#### 4. Structured Outputs
**Include when**: Analysis results or deliverables need consistent formatting
**Purpose**: Provide consistent formats for analysis results and deliverables that enable clear communication and easy consumption
```markdown
**Format**: [table/list/template structure]
**Example**: [sample output]
```

#### 5. Git Usage
**Include when**: Repository operations or version control workflows are involved
**Purpose**: Standardize git operations with consistent patterns for commits, branches, and workflows to ensure proper version control practices
```markdown
**Git**: [operation purpose]
**Command**: `git [command]`
**Expected**: [result format]
```

#### 6. Quality Gates
**Include when**: Code quality, testing, or validation requirements exist
**Purpose**: Define universal quality standards that apply regardless of technology stack, ensuring consistent quality enforcement
```markdown
**Quality gate**: [gate name]
**Command**: [validation command]
**Pass criteria**: [success condition]
**Failure action**: [remediation steps]
```

## Writing Standards

- **Use**: Active voice - "Run command" - ensures immediate understanding
- **Use**: Specific verbs - "Execute", "Create", "Validate" - provides clear direction
- **Use**: Direct instructions - "Check file" - eliminates ambiguity
- **Use**: Bullet points over paragraphs - maintains scannability
- **Use**: Tables for comparisons - enables quick understanding of options
- **Use**: Headings for structure - provides clear navigation
- **Use**: Code blocks for commands - provides copy-paste ready formats