# Create Session Notes

Capture a comprehensive summary of the current chat session including all discussions, actions taken, and outstanding tasks in an append only log.

## Behavior

When this command is invoked, Claude should:

1. **Analyze the current session** to identify all significant discussions and actions
2. **Append to session-notes.md** (create if it doesn't exist) with timestamp header

## Output Format

```markdown
## Session Summary - [TIMESTAMP]

### Discussion Overview

[Brief summary of main topics and goals]

### Actions Taken

- [List of completed tasks and changes made]

### Files Referenced/Modified

- `/path/to/file1.ext` - [Description of what was done]
- `/path/to/file2.ext` - [Description of what was done]

### Outstanding Tasks

- [List of incomplete or pending tasks]

### Key Decisions/Discoveries

- [Important findings or choices made]

### Next Steps

- [Recommended actions for continuing the work]

### Context for Continuation

[Any additional context needed to pick up where this session left off]

---
```

$ARGUMENTS
