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

- If user request contains flag `--prototype` → Resolve and read `rapid-prototype.modes.md`
- If user request contains flag `--tdd` → Resolve and read `tdd.modes.md`
- If user request contains flag `--seq` → Resolve and read `sequential-thinking.modes.md`
- If user request contains flag `--gitgrep` → Resolve and read `grep-search.modes.md`
- If user request contains flag `--serena` → Resolve and read `serena.modes.md`

### Enforcement Rules:

1. **Check flags first**: Before using any specialized tools or workflows, verify the corresponding flag is present
2. **No flag, no mode**: If a flag is not present, DO NOT use that mode's tools or workflows
3. **Read mode files only when needed**: Only read the mode file when its flag is detected
4. **Follow mode instructions exactly**: Once a mode file is read, follow its instructions precisely
