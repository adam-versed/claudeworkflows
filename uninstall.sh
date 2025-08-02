#!/bin/bash
# Claude Code Workflows Uninstall Script
# Removes Claude Code Workflows components while preserving .claude directory structure

set -euo pipefail

# Script configuration
SCRIPT_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/claude-workflows-uninstall.log"

# Default settings
DRY_RUN="false"
VERBOSE="false"
TARGET_PATH=""

# Global arrays for installation log tracking
PRE_EXISTING_PYTHON=()
NEWLY_INSTALLED_PYTHON=()
PRE_EXISTING_MCP=()
NEWLY_INSTALLED_MCP=()

# Usage and help
show_usage() {
    cat << 'EOF'
Claude Code Workflows Uninstaller

USAGE:
    ./uninstall.sh [TARGET_PATH] [OPTIONS]

ARGUMENTS:
    TARGET_PATH     Directory containing .claude/ to uninstall from
                   Examples:
                     ~/                    (User global: ~/.claude/)
                     ./myproject           (Project local: ./myproject/.claude/)
                     /path/to/project      (Custom path: /path/to/project/.claude/)
                   Default: current directory

OPTIONS:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -n, --dry-run   Show what would be removed without making changes

EXAMPLES:
    # Uninstall from current project
    ./uninstall.sh

    # Uninstall from user global installation
    ./uninstall.sh ~

    # Dry run to see what would be removed
    ./uninstall.sh --dry-run

DESCRIPTION:
    This script removes Claude Code Workflows components while preserving
    the .claude directory structure and any user-added files:

    - Removes workflow command files
    - Removes analysis scripts
    - Removes rule files
    - Removes sections from claude.md
    - Optionally removes Python packages (interactive)
    - Optionally removes MCP servers (interactive)

    Creates backup of MCP configuration before making changes.
EOF
}

# Initialize log file
init_log() {
    echo "" > "$LOG_FILE"
    log "Claude Code Workflows Uninstaller (v$SCRIPT_VERSION) started"
    log "Current directory: $(pwd)"
    log "Script directory: $SCRIPT_DIR"
    log "Command line: $0 $*"
}

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        log "$@"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
    fi
}

log_error() {
    echo "[ERROR] $*" | tee -a "$LOG_FILE" >&2
}

# Platform detection
detect_platform() {
    case "$(uname -s)" in
        Darwin*)
            PLATFORM="macos"
            ;;
        Linux*)
            PLATFORM="linux"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            PLATFORM="windows"
            ;;
        *)
            log_error "Unsupported platform: $(uname -s)"
            exit 1
            ;;
    esac
    log_verbose "Detected platform: $PLATFORM"
}

# Find and validate .claude installation
find_claude_installation() {
    # Set target path for .claude directory
    if [[ -z "$TARGET_PATH" ]]; then
        TARGET_PATH="$(pwd)"
    fi

    # Handle path ending with .claude
    if [[ "$TARGET_PATH" == */.claude ]]; then
        CLAUDE_DIR="$TARGET_PATH"
        log_verbose "Target path already ends with .claude, using it directly"
    else
        CLAUDE_DIR="$TARGET_PATH/.claude"
        log_verbose "Looking for .claude in target path"
    fi

    log "Checking for Claude Code Workflows installation at: $CLAUDE_DIR"

    if [[ ! -d "$CLAUDE_DIR" ]]; then
        log_error "No .claude directory found at: $CLAUDE_DIR"
        echo "Please specify the correct path containing your .claude installation"
        exit 1
    fi

    # Check if this looks like our installation
    local our_files_found=0

    # Check for our command files
    if [[ -f "$CLAUDE_DIR/commands/analyze-security.md" ]]; then
        ((our_files_found++))
    fi

    # Check for our scripts
    if [[ -d "$CLAUDE_DIR/scripts/analyze" ]]; then
        ((our_files_found++))
    fi

    # Check for our rules
    if [[ -f "$CLAUDE_DIR/rules/prototype.md" ]]; then
        ((our_files_found++))
    fi

    if [[ $our_files_found -eq 0 ]]; then
        log_error "No Claude Code Workflows components found at: $CLAUDE_DIR"
        echo "This doesn't appear to be a Claude Code Workflows installation"
        exit 1
    fi

    log "Found Claude Code Workflows installation ($our_files_found components detected)"
}

# Remove workflow command files
remove_command_files() {
    log "Checking for workflow command files..."

    if [[ ! -d "$CLAUDE_DIR/commands" ]]; then
        log_verbose "No commands directory found"
        return 0
    fi

    # List of our command files
    local our_commands=(
        "analyze-architecture.md"
        "analyze-code-quality.md"
        "analyze-performance.md"
        "analyze-root-cause.md"
        "analyze-security.md"
        "analyze-ux.md"
        "fix-bug.md"
        "fix-performance.md"
        "fix-test.md"
        "plan-refactor.md"
        "plan-solution.md"
        "plan-ux-prd.md"
    )

    local files_to_remove=()

    # Check which of our files exist
    for cmd in "${our_commands[@]}"; do
        if [[ -f "$CLAUDE_DIR/commands/$cmd" ]]; then
            files_to_remove+=("$cmd")
        fi
    done

    if [[ ${#files_to_remove[@]} -eq 0 ]]; then
        log "No workflow command files found to remove"
        return 0
    fi

    echo ""
    echo "Found ${#files_to_remove[@]} workflow command files:"
    for file in "${files_to_remove[@]}"; do
        echo "  - $file"
    done
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would remove ${#files_to_remove[@]} command files"
        return 0
    fi

    read -p "Remove these command files? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        local removed_count=0
        for file in "${files_to_remove[@]}"; do
            if rm "$CLAUDE_DIR/commands/$file" 2>/dev/null; then
                log_verbose "Removed command file: $file"
                ((removed_count++))
            else
                log_error "Failed to remove command file: $file"
            fi
        done
        log "Removed $removed_count command files"
    else
        log "Skipped removing command files"
    fi
}

# Remove script directories
remove_script_directories() {
    log "Checking for analysis script directories..."

    if [[ ! -d "$CLAUDE_DIR/scripts" ]]; then
        log_verbose "No scripts directory found"
        return 0
    fi

    # List of our script directories and files
    local our_scripts=(
        "scripts/analyze/"
        "scripts/setup/"
        "scripts/utils/"
        "scripts/run_all_analysis.py"
    )

    local items_to_remove=()

    # Check which of our script items exist
    for item in "${our_scripts[@]}"; do
        if [[ -e "$CLAUDE_DIR/$item" ]]; then
            items_to_remove+=("$item")
        fi
    done

    if [[ ${#items_to_remove[@]} -eq 0 ]]; then
        log "No workflow script directories found to remove"
        return 0
    fi

    echo ""
    echo "Found ${#items_to_remove[@]} script directories/files:"
    for item in "${items_to_remove[@]}"; do
        if [[ -d "$CLAUDE_DIR/$item" ]]; then
            echo "  - $item (directory)"
        else
            echo "  - $item (file)"
        fi
    done
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would remove ${#items_to_remove[@]} script items"
        return 0
    fi

    read -p "Remove these script directories and files? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        local removed_count=0
        for item in "${items_to_remove[@]}"; do
            if rm -rf "$CLAUDE_DIR/$item" 2>/dev/null; then
                log_verbose "Removed script item: $item"
                ((removed_count++))
            else
                log_error "Failed to remove script item: $item"
            fi
        done

        # Clean up __pycache__ folders in scripts directory
        if [[ -d "$CLAUDE_DIR/scripts" ]]; then
            find "$CLAUDE_DIR/scripts" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
            log_verbose "Cleaned up __pycache__ folders"
        fi

        # Remove scripts directory if it's empty or only contains __pycache__
        if [[ -d "$CLAUDE_DIR/scripts" ]]; then
            # Remove any remaining __pycache__ folders
            find "$CLAUDE_DIR/scripts" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

            # Check if scripts directory is empty or only contains empty subdirectories
            if [[ -z "$(find "$CLAUDE_DIR/scripts" -type f)" ]]; then
                rm -rf "$CLAUDE_DIR/scripts" 2>/dev/null && log_verbose "Removed empty scripts directory"
            fi
        fi

        log "Removed $removed_count script items"
    else
        log "Skipped removing script directories"
    fi
}

# Remove rule files
remove_rule_files() {
    log "Checking for rule files..."

    if [[ ! -d "$CLAUDE_DIR/rules" ]]; then
        log_verbose "No rules directory found"
        return 0
    fi

    # List of our rule files
    local our_rules=(
        "prototype.md"
        "tdd.md"
    )

    local files_to_remove=()

    # Check which of our rule files exist
    for rule in "${our_rules[@]}"; do
        if [[ -f "$CLAUDE_DIR/rules/$rule" ]]; then
            files_to_remove+=("$rule")
        fi
    done

    if [[ ${#files_to_remove[@]} -eq 0 ]]; then
        log "No rule files found to remove"
        return 0
    fi

    echo ""
    echo "Found ${#files_to_remove[@]} rule files:"
    for file in "${files_to_remove[@]}"; do
        echo "  - rules/$file"
    done
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would remove ${#files_to_remove[@]} rule files"
        return 0
    fi

    read -p "Remove these rule files? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        local removed_count=0
        for file in "${files_to_remove[@]}"; do
            if rm "$CLAUDE_DIR/rules/$file" 2>/dev/null; then
                log_verbose "Removed rule file: $file"
                ((removed_count++))
            else
                log_error "Failed to remove rule file: $file"
            fi
        done
        log "Removed $removed_count rule files"

        # Remove rules directory if it's empty
        if [[ -d "$CLAUDE_DIR/rules" ]] && [[ -z "$(ls -A "$CLAUDE_DIR/rules")" ]]; then
            rmdir "$CLAUDE_DIR/rules" 2>/dev/null && log_verbose "Removed empty rules directory"
        fi
    else
        log "Skipped removing rule files"
    fi
}

# Remove sections from claude.md
remove_claude_md_sections() {
    log "Checking for our sections in claude.md..."

    if [[ ! -f "$CLAUDE_DIR/claude.md" ]]; then
        log_verbose "No claude.md file found"
        return 0
    fi

    # Check if our "Build Approach Flags" section exists
    if ! grep -q "## Build Approach Flags for claude enhanced workflows" "$CLAUDE_DIR/claude.md"; then
        log "No Claude Code Workflows sections found in claude.md"
        return 0
    fi

    echo ""
    echo "Found Claude Code Workflows sections in claude.md:"
    echo "  - Build Approach Flags section"
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would remove sections from claude.md"
        return 0
    fi

    read -p "Remove our sections from claude.md? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Create backup of claude.md
        local backup_file="${CLAUDE_DIR}/claude.md.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$CLAUDE_DIR/claude.md" "$backup_file"
        log_verbose "Created backup: $(basename "$backup_file")"

        # Remove our section using sed
        # Remove from "## Build Approach Flags" to the next "##" or end of file
        sed -i.tmp '/^## Build Approach Flags for claude enhanced workflows$/,/^## /{
            /^## Build Approach Flags for claude enhanced workflows$/d
            /^## /!d
        }' "$CLAUDE_DIR/claude.md"

        # Clean up sed backup file
        rm -f "$CLAUDE_DIR/claude.md.tmp"

        log "Removed Claude Code Workflows sections from claude.md"
        echo "Backup saved as: $(basename "$backup_file")"
    else
        log "Skipped removing claude.md sections"
    fi
}

# Backup MCP server configuration
backup_mcp_config() {
    log "Creating backup of MCP server configuration..."

    # Check if Claude CLI is available
    if ! command -v claude &> /dev/null; then
        log_verbose "Claude CLI not found, skipping MCP backup"
        return 0
    fi

    # Create backup of MCP server list
    local backup_file="/tmp/claude-mcp-servers-backup-$(date +%Y%m%d_%H%M%S).txt"

    if claude mcp list > "$backup_file" 2>/dev/null; then
        log "MCP server configuration backed up to: $backup_file"
        echo "MCP backup saved at: $backup_file"
    else
        log_verbose "Failed to backup MCP configuration (this is non-critical)"
    fi
}

# Read installation log for better removal warnings
read_installation_log() {
    local log_file="$CLAUDE_DIR/installation-log.txt"

    # Initialize arrays
    PRE_EXISTING_PYTHON=()
    NEWLY_INSTALLED_PYTHON=()
    PRE_EXISTING_MCP=()
    NEWLY_INSTALLED_MCP=()

    if [[ ! -f "$log_file" ]]; then
        log_verbose "No installation log found, using default warnings"
        return 0
    fi

    log_verbose "Reading installation log for safer removal..."

    # Read pre-existing Python packages
    local in_section=""
    while IFS= read -r line; do
        case "$line" in
            "[PRE_EXISTING_PYTHON_PACKAGES]")
                in_section="pre_python"
                ;;
            "[NEWLY_INSTALLED_PYTHON_PACKAGES]")
                in_section="new_python"
                ;;
            "[PRE_EXISTING_MCP_SERVERS]")
                in_section="pre_mcp"
                ;;
            "[NEWLY_INSTALLED_MCP_SERVERS]")
                in_section="new_mcp"
                ;;
            "["*"]")
                in_section=""
                ;;
            *)
                if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
                    case "$in_section" in
                        "pre_python")
                            PRE_EXISTING_PYTHON+=("$line")
                            ;;
                        "new_python")
                            NEWLY_INSTALLED_PYTHON+=("$line")
                            ;;
                        "pre_mcp")
                            PRE_EXISTING_MCP+=("$line")
                            ;;
                        "new_mcp")
                            NEWLY_INSTALLED_MCP+=("$line")
                            ;;
                    esac
                fi
                ;;
        esac
    done < "$log_file"

    log_verbose "Found installation log: ${#PRE_EXISTING_PYTHON[@]} pre-existing Python packages, ${#NEWLY_INSTALLED_PYTHON[@]} newly installed"
    log_verbose "Found installation log: ${#PRE_EXISTING_MCP[@]} pre-existing MCP servers, ${#NEWLY_INSTALLED_MCP[@]} newly installed"
}

# Interactive Python package removal
remove_python_packages() {
    log "Checking for Python packages to remove..."

    # Check if requirements.txt exists in our script directory
    local requirements_file="$SCRIPT_DIR/claude/scripts/setup/requirements.txt"
    if [[ ! -f "$requirements_file" ]]; then
        log_verbose "No requirements.txt found, skipping Python package removal"
        return 0
    fi

    # Extract package names from requirements.txt (remove version constraints)
    local packages=()
    while IFS= read -r line; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        # Extract package name (everything before ==, >=, etc.)
        local pkg=$(echo "$line" | sed 's/[>=<].*//' | tr -d ' ')
        [[ -n "$pkg" ]] && packages+=("$pkg")
    done < "$requirements_file"

    if [[ ${#packages[@]} -eq 0 ]]; then
        log "No Python packages found in requirements.txt"
        return 0
    fi

    # Check which packages are actually installed
    local installed_packages=()
    for pkg in "${packages[@]}"; do
        if python3 -m pip show "$pkg" &>/dev/null; then
            installed_packages+=("$pkg")
        fi
    done

    if [[ ${#installed_packages[@]} -eq 0 ]]; then
        log "No installed Python packages found to remove"
        return 0
    fi

    echo ""
    echo "Found ${#installed_packages[@]} Python packages that could be removed:"

    # Categorize packages based on installation log
    local pre_existing=()
    local newly_installed=()
    local unknown=()

    for pkg in "${installed_packages[@]}"; do
        if [[ ${#PRE_EXISTING_PYTHON[@]} -gt 0 ]] && [[ " ${PRE_EXISTING_PYTHON[*]} " =~ " $pkg " ]]; then
            pre_existing+=("$pkg")
        elif [[ ${#NEWLY_INSTALLED_PYTHON[@]} -gt 0 ]] && [[ " ${NEWLY_INSTALLED_PYTHON[*]} " =~ " $pkg " ]]; then
            newly_installed+=("$pkg")
        else
            unknown+=("$pkg")
        fi
    done

    # Show packages with appropriate warnings
    if [[ ${#newly_installed[@]} -gt 0 ]]; then
        echo ""
        echo "📦 Newly installed by Claude Code Workflows (safer to remove):"
        for pkg in "${newly_installed[@]}"; do
            echo "  - $pkg"
        done
    fi

    if [[ ${#pre_existing[@]} -gt 0 ]]; then
        echo ""
        echo "⚠️  Pre-existing packages (likely used by other projects - CAUTION advised):"
        for pkg in "${pre_existing[@]}"; do
            echo "  - $pkg"
        done
    fi

    if [[ ${#unknown[@]} -gt 0 ]]; then
        echo ""
        echo "❓ Unknown status packages (no installation log available):"
        for pkg in "${unknown[@]}"; do
            echo "  - $pkg"
        done
    fi

    echo ""
    echo "⚠️  WARNING: Only remove packages you're certain aren't needed by other projects!"
    echo "    Pre-existing packages were already installed before Claude Code Workflows."
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would prompt to remove ${#installed_packages[@]} Python packages"
        return 0
    fi

    local removed_count=0
    for pkg in "${installed_packages[@]}"; do
        # Show appropriate warning based on package status
        local warning=""
        if [[ ${#PRE_EXISTING_PYTHON[@]} -gt 0 ]] && [[ " ${PRE_EXISTING_PYTHON[*]} " =~ " $pkg " ]]; then
            warning=" (⚠️  PRE-EXISTING - likely used elsewhere)"
        elif [[ ${#NEWLY_INSTALLED_PYTHON[@]} -gt 0 ]] && [[ " ${NEWLY_INSTALLED_PYTHON[*]} " =~ " $pkg " ]]; then
            warning=" (📦 newly installed by workflows)"
        fi

        echo -n "Remove Python package '$pkg'$warning? (y/n): "
        read -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if python3 -m pip uninstall -y "$pkg" &>/dev/null; then
                log_verbose "Removed Python package: $pkg"
                ((removed_count++))
            else
                log_error "Failed to remove Python package: $pkg"
            fi
        else
            log_verbose "Skipped Python package: $pkg"
        fi
    done

    if [[ $removed_count -gt 0 ]]; then
        log "Removed $removed_count Python packages"
    else
        log "No Python packages were removed"
    fi
}

# Interactive MCP server removal
remove_mcp_servers() {
    log "Checking for MCP servers to remove..."

    # Check if Claude CLI is available
    if ! command -v claude &> /dev/null; then
        log_verbose "Claude CLI not found, skipping MCP server removal"
        return 0
    fi

    # List of MCP servers we install
    local our_mcp_servers=(
        "sequential-thinking"
        "grep"
    )

    # Check which of our servers are installed
    local installed_servers=()
    for server in "${our_mcp_servers[@]}"; do
        if claude mcp list 2>/dev/null | grep -q "^$server"; then
            installed_servers+=("$server")
        fi
    done

    if [[ ${#installed_servers[@]} -eq 0 ]]; then
        log "No Claude Code Workflows MCP servers found to remove"
        return 0
    fi

    echo ""
    echo "Found ${#installed_servers[@]} MCP servers that were installed by Claude Code Workflows:"

    # Categorize servers based on installation log
    local pre_existing_servers=()
    local newly_installed_servers=()
    local unknown_servers=()

    for server in "${installed_servers[@]}"; do
        if [[ ${#PRE_EXISTING_MCP[@]} -gt 0 ]] && [[ " ${PRE_EXISTING_MCP[*]} " =~ " $server " ]]; then
            pre_existing_servers+=("$server")
        elif [[ ${#NEWLY_INSTALLED_MCP[@]} -gt 0 ]] && [[ " ${NEWLY_INSTALLED_MCP[*]} " =~ " $server " ]]; then
            newly_installed_servers+=("$server")
        else
            unknown_servers+=("$server")
        fi
    done

    # Show servers with appropriate warnings
    if [[ ${#newly_installed_servers[@]} -gt 0 ]]; then
        echo ""
        echo "🔧 Newly installed by Claude Code Workflows (safer to remove):"
        for server in "${newly_installed_servers[@]}"; do
            echo "  - $server"
        done
    fi

    if [[ ${#pre_existing_servers[@]} -gt 0 ]]; then
        echo ""
        echo "⚠️  Pre-existing servers (likely used by other projects - CAUTION advised):"
        for server in "${pre_existing_servers[@]}"; do
            echo "  - $server"
        done
    fi

    if [[ ${#unknown_servers[@]} -gt 0 ]]; then
        echo ""
        echo "❓ Unknown status servers (no installation log available):"
        for server in "${unknown_servers[@]}"; do
            echo "  - $server"
        done
    fi

    echo ""
    echo "⚠️  WARNING: These MCP servers may be used by other projects or workflows!"
    echo "    Pre-existing servers were already installed before Claude Code Workflows."
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would prompt to remove ${#installed_servers[@]} MCP servers"
        return 0
    fi

    local removed_count=0
    for server in "${installed_servers[@]}"; do
        # Show appropriate warning based on server status
        local warning=""
        if [[ ${#PRE_EXISTING_MCP[@]} -gt 0 ]] && [[ " ${PRE_EXISTING_MCP[*]} " =~ " $server " ]]; then
            warning=" (⚠️  PRE-EXISTING - likely used elsewhere)"
        elif [[ ${#NEWLY_INSTALLED_MCP[@]} -gt 0 ]] && [[ " ${NEWLY_INSTALLED_MCP[*]} " =~ " $server " ]]; then
            warning=" (🔧 newly installed by workflows)"
        fi

        echo -n "Remove MCP server '$server'$warning? (y/n): "
        read -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if claude mcp remove "$server" &>/dev/null; then
                log_verbose "Removed MCP server: $server"
                ((removed_count++))
            else
                log_error "Failed to remove MCP server: $server"
            fi
        else
            log_verbose "Skipped MCP server: $server"
        fi
    done

    if [[ $removed_count -gt 0 ]]; then
        log "Removed $removed_count MCP servers"
    else
        log "No MCP servers were removed"
    fi
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -n|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                if [[ -z "$TARGET_PATH" ]]; then
                    TARGET_PATH="$1"
                else
                    log_error "Multiple target paths specified"
                    exit 1
                fi
                shift
                ;;
        esac
    done
}

# Show uninstall summary
show_summary() {
    echo ""
    echo "🧹 Claude Code Workflows uninstall completed!"
    echo ""
    echo "Installation location: $CLAUDE_DIR"
    echo ""
    echo "What was processed:"
    echo "  ✓ Workflow command files checked/removed"
    echo "  ✓ Analysis script directories checked/removed"
    echo "  ✓ Rule files checked/removed"
    echo "  ✓ claude.md sections checked/removed"
    echo "  ✓ Python packages offered for removal"
    echo "  ✓ MCP servers offered for removal"
    echo ""
    echo "The .claude directory structure has been preserved."
    echo "Check the log for details: $LOG_FILE"
    echo ""
}

# Main execution function
main() {
    init_log
    parse_arguments "$@"
    detect_platform

    log "Starting Claude Code Workflows uninstall (v$SCRIPT_VERSION)"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🔍 DRY RUN MODE - No changes will be made"
        echo ""
    fi

    # Find and validate installation
    find_claude_installation

    # Read installation log for better removal warnings
    read_installation_log

    # Backup MCP configuration first
    backup_mcp_config

    echo ""
    echo "🧹 Claude Code Workflows Uninstaller"
    echo "===================================="
    echo ""
    echo "This will selectively remove Claude Code Workflows components from:"
    echo "  $CLAUDE_DIR"
    echo ""
    echo "The .claude directory and any user-added files will be preserved."
    echo ""

    if [[ "$DRY_RUN" != "true" ]]; then
        read -p "Continue with uninstall? (y/n): " -n 1 -r
        echo
        echo ""

        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Uninstall cancelled by user"
            echo "Uninstall cancelled."
            exit 0
        fi
    fi

    # Remove components
    remove_command_files
    remove_script_directories
    remove_rule_files
    remove_claude_md_sections
    remove_python_packages
    remove_mcp_servers

    if [[ "$DRY_RUN" != "true" ]]; then
        show_summary
    else
        echo ""
        echo "Dry run completed - no changes were made"
        echo "Run without --dry-run to perform the actual uninstall"
    fi
}

# Run main function with all arguments
main "$@"
