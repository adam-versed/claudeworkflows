# Add Serena MCP

Configures and adds the Serena MCP server to Claude Code for the current project directory, enabling advanced IDE-like code analysis and editing capabilities.

## Behavior

This command sets up Serena MCP (Model Context Protocol) server for the current project with the IDE assistant context, providing powerful semantic code tools for efficient codebase navigation and editing.

When invoked, Claude will:

1. Detect the current project directory
2. Remove any existing Serena MCP configuration
3. Add Serena MCP server with the correct configuration
4. Verify the connection is established

## Process

1. **Check Prerequisites**: Verify that `uvx` is installed (part of the `uv` Python package manager)
2. **Get Project Path**: Determine the absolute path of the current working directory
3. **Remove Existing Config**: Clean up any previous Serena configuration with `claude mcp remove serena` (ignore if it doesn't exist)
4. **Add Serena MCP**: Execute the command:
   ```bash
   claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)
   ```
5. **Verify Connection**: Run `claude mcp list` to confirm Serena appears as connected
6. **Report Status**: Inform the user whether setup was successful

## Notes

- Uses the `ide-assistant` context which excludes certain tools handled by Claude Code itself
- The `--` separator is critical for passing complex arguments to the MCP server
- Serena provides 20+ semantic tools for code analysis without reading entire files
- Configuration is stored locally for the current project

## Example Usage

```bash
# From any project directory:
/add-serena-mcp

# With optional confirmation:
/add-serena-mcp verify
```

$ARGUMENTS
