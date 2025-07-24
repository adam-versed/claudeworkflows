# Hook-Based Command Template

## Purpose
Define the structure for command files that setup event hooks to enforce project-specific behaviors and standards through Claude's hook system.

## Core Approach
**Hook automation with clear configuration** - Setup event-driven hooks that automatically enforce rules, checks, or behaviors at specific tool execution points.

## Command Structure

### Mandatory Sections

#### 1. Command Header
```markdown
# [Command Name]

[One-line description of what the command sets up]

## Behavior

[Description of what the hooks will do when triggered, formatted as numbered list:]

1. **[Action 1]**: [What happens]
2. **[Action 2]**: [What happens]
3. **[Action 3]**: [What happens]
```

#### 2. Process Section
```markdown
## Process

1. **[Step 1]**: [Action description]
2. **[Step 2]**: [Action description]
3. **[Step 3]**: [Action description]
4. **[Step 4]**: [Action description with sub-items if needed]
   - [Sub-action 1]
   - [Sub-action 2]
5. **[Final Step]**: [Completion action]
```

#### 3. Hook Template Section
```markdown
## Hook Template

[Description of the hook pattern]

```toml
[[hooks]]
event = "[EventType]"

[hooks.matcher]
[matcher_field] = [value]
[additional_matchers]

command = "[command to execute]"
```

### Optional Sections

#### 1. Arguments Format
**Include when**: Command accepts user arguments
```markdown
## Arguments Format

Usage: `/[command-name] <arg1> <arg2>`

- **arg1**: [Description of first argument]
- **arg2**: [Description of second argument]
```

#### 2. Example Usage
**Include when**: Multiple use cases or complex arguments exist
```markdown
## Example Usage

```bash
# [Use case 1 description]
/[command] [example args 1]

# [Use case 2 description]
/[command] [example args 2]

# [Use case 3 description]
/[command] [example args 3]
```

#### 3. Implementation Steps
**Include when**: Detailed implementation guidance needed
```markdown
## Implementation Steps

1. **[Validation Step]**: [What to validate]
2. **[Setup Step]**: [What to create/configure]
3. **[Processing Step]**: [Main processing logic]
4. **[Configuration Step]**: [How to update configuration]
5. **[Confirmation Step]**: [Success reporting]
```

#### 4. Generated Configuration
**Include when**: Multiple configurations or complex outputs
```markdown
## Generated Configuration

[Description of what will be generated]

### For [Scenario 1]:
```toml
[configuration example]
```

### For [Scenario 2]:
```toml
[configuration example]
```

## Writing Standards for Hook Commands

### Hook Event Types
- **PreToolUse**: Before tool execution
- **PostToolUse**: After tool execution  
- **PreCommit**: Before git commit
- **PostCommit**: After git commit

### Matcher Fields
- **tool_name**: Target specific tools (Edit, MultiEdit, Write, etc.)
- **file_paths**: Glob patterns for file matching
- **command_pattern**: Match specific command patterns

### Command Patterns
- **Echo feedback**: `echo '[User message]' && [actual command]`
- **Conditional execution**: `[test condition] && [command] || [fallback]`
- **Multi-command**: `[command1] && [command2] && [command3]`

### Best Practices
1. **Preserve existing hooks**: Always read and append to existing settings
2. **Clear user feedback**: Echo messages before executing commands
3. **Idempotent setup**: Check if configuration already exists
4. **Validate inputs**: Ensure files/paths exist before setup
5. **Report success**: Confirm what was configured

## Template Usage

When creating a new hook-based command:

1. **Define the hook's purpose**: What behavior it enforces
2. **Identify trigger points**: Which events and tools to hook
3. **Design the command**: What executes when hook triggers
4. **Structure the setup**: How to install the hook configuration
5. **Document usage**: Clear examples and argument descriptions