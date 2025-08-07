## Monitor User Request For Flags Enabled Modes

**When a `--[FLAG]` flag is present in the user request, resolve and read the corresponding mode file**:

### Flag Conditions and Path Resolution:

**ONLY when a flag is detected, resolve the mode file path:**

1. **First try project-level .claude folder**:

   - Check if `.claude/modes/*.modes.md` exists using Glob tool

2. **Then try user-level .claude folder**:

   - Check if `$HOME/.claude/modes/*.modes.md` exists using Bash tool

3. **Use the first path that exists**

### Flag to Mode Mapping:

- If user request contains flag `--prototype` → Resolve, read and enforce `rapid-prototype.modes.md`
- If user request contains flag `--tdd` → Resolve, read and enforce `tdd.modes.md`
- If user request contains flag `--seq` → Resolve, read and enforce `sequential-thinking.modes.md`
- If user request contains flag `--gitgrep` → Resolve, read and enforce `grep-search.modes.md`
- If user request contains flag `--serena` → Resolve, read and enforce `serena.modes.md`

## Behaviour Rules

1. Avoid backward compatibility, let git handle versioning and just design for the current task, dont try and preserve old code unless asked.
2. KISS - keep it simple, stupid is your mantra - we should always favour established libraries over bespoke code and we should always take the least intrusive and least effor approach to complete a task, without sacrifcing accuracy or the user objective.
3. Always look to use `mcp__serena` tool for codebase search activities - its more efficient than grep or glob.
