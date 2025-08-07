## Monitor User Request For Flags Enabled Modes

**When a `--[FLAG]` flag is present in the user request, resolve and read the corresponding mode file**:

### Flag Conditions and Path Resolution:

**ONLY when a flag is detected, resolve the mode file path:**

1. **First try project-level .claude folder**:

   - Check if `~/.config/opencode/instructions/*.instructions.md` exists using Glob tool

2. **Then try user-level .claude folder**:

   - Check if `$HOME/.config/opencode/instructions/*.instructions.md` exists using Bash tool

3. **Use the first path that exists**

### Flag to Mode Mapping:

- If user request contains flag `--prototype` → Resolve, read and enforce `rapid-prototype.instructions.md`
- If user request contains flag `--tdd` → Resolve, read and enforce `tdd.instructions.md`
- If user request contains flag `--seq` → Resolve, read and enforce `sequential-thinking.instructions.md`
- If user request contains flag `--gitgrep` → Resolve, read and enforce `grep-search.instructions.md`

## Behaviour Rules

1. Avoid backward compatibility, let git handle versioning and just design for the current task, dont try and preserve old code unless asked.
2. KISS - keep it simple, stupid is your mantra - we should always favour established libraries over bespoke code and we should always take the least intrusive and least effor approach to complete a task, without sacrifcing accuracy or the user objective.
