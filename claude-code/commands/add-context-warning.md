# Add Context Warning

Adds a Stop event hook to Claude Code settings that monitors context usage and plays a terminal bell when context usage exceeds 80%.

## Behavior

This command will:

1. Read the current user settings from `~/.claude/settings.json`
2. Add or update a Stop event hook that checks context usage percentage
3. The hook will play the terminal bell (ASCII character 7) if context usage is above 80%
4. Save the updated settings

## Process

1. **Check existing settings**: Read current user settings.json file
2. **Parse hook input**: The Stop hook receives session information including the transcript path
3. **Create hook script**: Generate a Python script that:
   - Reads the transcript to determine context usage
   - Checks if usage is above 80%
   - Plays terminal bell if threshold exceeded
4. **Update settings**: Add the hook configuration to the Stop event
5. **Save settings**: Write the updated configuration back to settings.json

## Implementation Details

The hook will:

- Execute when Claude finishes responding (Stop event)
- Parse the transcript to extract context usage information
- Use `printf '\a'` or `echo -e '\a'` to play the terminal bell
- Only alert once per Stop event to avoid repeated bells

$ARGUMENTS
