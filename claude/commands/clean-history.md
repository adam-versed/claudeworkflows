# Clean History (`clean-history`)

**Purpose**: Clean Claude's configuration file to reduce size and remove large content
**Usage**: `claude /clean-history [--clear-all-history]`

## Workflow Process

### Phase 1: Script Resolution and Validation

1. **Resolve script path** - Locate clean_claude_config.py script

   **FIRST - Resolve SCRIPT_PATH:**

   1. **Try project-level .claude folder**:

      ```bash
      Glob: ".claude/scripts/utils/clean_claude_config.py"
      ```

   2. **Try user-level .claude folder**:

      ```bash
      Bash: ls "$HOME/.claude/scripts/utils/"
      ```

   3. **Interactive fallback if not found**:
      - List searched locations: `.claude/scripts/utils/` and `$HOME/.claude/scripts/utils/`
      - Ask user: "Could not locate clean_claude_config.py script. Please provide full path to the script:"
      - Validate provided path exists and is executable
      - Set SCRIPT_PATH to user-provided location

2. **Validate Claude config file** - Check config file accessibility

   ```bash
   Bash: ls -la "$HOME/.claude.json"
   ```

3. **Create backup** - Ensure config backup exists before cleaning

   ```bash
   Bash: cp "$HOME/.claude.json" "$HOME/.claude.json.backup.$(date +%Y%m%d-%H%M%S)"
   ```

**STOP** → "Config validated and backed up. Proceed with cleaning? (y/n)"

### Phase 2: Configuration Cleaning

1. **Execute cleaning script** - Run script with appropriate mode

   **Default mode (preserve history structure, remove large content):**

   ```bash
   python3 [SCRIPT_PATH]/clean_claude_config.py
   ```

   **Clear all history mode (maximum size reduction):**

   ```bash
   python3 [SCRIPT_PATH]/clean_claude_config.py --clear-all-history
   ```

2. **Verify cleaning results** - Check file size reduction and script output

   ```bash
   Bash: ls -lh "$HOME/.claude.json" "$HOME/.claude.json.backup"*
   ```

3. **Display cleaning summary** - Show before/after file sizes and operations performed

**STOP** → "Cleaning complete. Review results and test Claude functionality? (y/n)"

### Phase 3: Validation and Testing

1. **Test configuration validity** - Verify Claude can read cleaned config

   ```bash
   Bash: claude --version
   ```

2. **Check MCP server removal** - Confirm context7 MCP server was removed

   ```bash
   Bash: claude mcp list
   ```

3. **Validate file integrity** - Ensure JSON structure is valid

   ```bash
   python3 -c "import json; json.load(open('$HOME/.claude.json'))"
   ```

**STOP** → "Validation complete. Archive old backups? (y/n)"

### Phase 4: Cleanup and Documentation

1. **Archive old backups** - Manage backup files (optional)

   - List existing backup files
   - Offer to remove backups older than 7 days
   - Keep most recent 3 backups

2. **Document cleaning operation** - Record cleaning statistics

   - File size before/after
   - Cleaning mode used
   - Items removed/cleaned

## Enhanced Optional Flags

**--clear-all-history**: Complete history deletion for maximum file size reduction
**--preserve-structure**: Default mode - clean large content but preserve chat history structure
**--verbose**: Show detailed file sizes, cleaning operations, and validation steps

## Quality Gates

**Configuration integrity**:

- **Command**: `python3 -c "import json; json.load(open('$HOME/.claude.json'))"`
- **Pass criteria**: JSON parses without errors
- **Failure action**: Restore from backup and retry

**Claude functionality**:

- **Command**: `claude --version`
- **Pass criteria**: Command executes successfully
- **Failure action**: Restore from backup and investigate

**MCP server cleanup**:

- **Command**: `claude mcp list`
- **Pass criteria**: context7 not listed in active servers
- **Failure action**: Manual verification of mcpServers section

$ARGUMENTS
