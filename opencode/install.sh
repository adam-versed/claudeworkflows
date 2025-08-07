#!/bin/bash
# AI Assisted Workflows Installation Script
# Installs the complete workflow system with agents, scripts, and dependencies

set -euo pipefail

# Script configuration
SCRIPT_VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/opencode-workflows-install.log"

# Usage and help
show_usage() {
    cat << 'EOF'
AI Assisted Workflows Installer

USAGE:
    ./install.sh [TARGET_PATH] [OPTIONS]

ARGUMENTS:
    TARGET_PATH     Directory where .opencode/ will be created
                   Examples:
                     ~                     (User global: ~/.config/opencode/)
                     ./myproject           (Project local: ./myproject/.opencode/)
                     /path/to/project      (Custom path: /path/to/project/.opencode/)
                   Default: current directory

OPTIONS:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -n, --dry-run   Show what would be done without making changes
    --skip-python   Skip Python dependencies installation

EXAMPLES:
    # Install in current project (creates ./.opencode/)
    ./install.sh

    # Install globally for user (creates ~/.config/opencode/)
    ./install.sh ~

    # Install in specific project
    ./install.sh /path/to/my-project

    # Dry run to see what would happen
    ./install.sh --dry-run

REQUIREMENTS:
    - Python 3.7+
    - Internet connection for dependencies

EOF
}

# Global variables
VERBOSE=false
DRY_RUN=false
SKIP_PYTHON=false

# Parse command line arguments
parse_args() {
    # Reset TARGET_PATH to empty to detect if user provided one
    TARGET_PATH=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-python)
                SKIP_PYTHON=true
                shift
                ;;
            -*)
                echo "Unknown option: $1" >&2
                show_usage
                exit 1
                ;;
            *)
                if [[ -z "$TARGET_PATH" ]]; then
                    TARGET_PATH="$1"
                else
                    echo "Error: Multiple target paths specified" >&2
                    exit 1
                fi
                shift
                ;;
        esac
    done

    # Set default if no target path provided
    if [[ -z "$TARGET_PATH" ]]; then
        TARGET_PATH="$(pwd)"
    fi
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

# Environment validation
check_python() {
    log_verbose "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        echo "Please install Python 3.7+ and try again"
        exit 1
    fi

    local python_version
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    log_verbose "Found Python $python_version"

    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)"; then
        log_error "Python 3.7+ is required, found Python $python_version"
        exit 1
    fi

    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not found"
        echo "Please install pip3 and try again"
        exit 1
    fi
}

# Directory setup with custom paths
setup_install_dir() {
    log_verbose "Setting up installation directory..."

    # Resolve and validate target path
    if [[ "$TARGET_PATH" == "~" ]]; then
        TARGET_PATH="$HOME"
    elif [[ "$TARGET_PATH" == ~* ]]; then
        TARGET_PATH="${TARGET_PATH/#\~/$HOME}"
    fi

    # Convert to absolute path
    TARGET_PATH=$(realpath "$TARGET_PATH" 2>/dev/null || echo "$TARGET_PATH")

    # Create target directory if it doesn't exist
    if [[ ! -d "$TARGET_PATH" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log "Would create directory: $TARGET_PATH"
        else
            log_verbose "Creating target directory: $TARGET_PATH"
            mkdir -p "$TARGET_PATH"
        fi
    fi

    # Set final installation path based on target
    # Special handling for home directory to use ~/.config/opencode
    if [[ "$TARGET_PATH" == "$HOME" ]]; then
        INSTALL_DIR="$HOME/.config/opencode"
        log_verbose "Home directory specified, using ~/.config/opencode"
    elif [[ "$TARGET_PATH" == */.opencode ]] || [[ "$TARGET_PATH" == */opencode ]]; then
        # User already specified .opencode or opencode in the path (for global installs)
        INSTALL_DIR="$TARGET_PATH"
        log_verbose "Target path already ends with opencode directory, using it directly"
    else
        # Append .opencode to the path for project installations
        INSTALL_DIR="$TARGET_PATH/.opencode"
        log_verbose "Appending .opencode to target path"
    fi

    log "Installation target: $INSTALL_DIR"

    # Handle existing installation
    if [[ -d "$INSTALL_DIR" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log "Would handle existing .opencode directory at: $INSTALL_DIR"
            log "Would create automatic backup before proceeding"
            log "Would prompt user for fresh install/merge/workflows-only/cancel choice"
        else
            # Always create a backup first
            local backup_dir="${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
            log "Creating automatic backup of existing installation to: $backup_dir"
            cp -r "$INSTALL_DIR" "$backup_dir"

            echo ""
            echo "Found existing .opencode directory at: $INSTALL_DIR"
            echo "Automatic backup created at: $backup_dir"
            echo ""
            echo "Choose an option:"
            echo "  1) Fresh install (replace existing)"
            echo "  2) Merge with existing (preserve user customizations)"
            echo "  3) Update workflows only (overwrite agents & scripts, preserve everything else)"
            echo "  4) Cancel installation (backup remains)"
            echo ""
            read -p "Enter choice [1-4]: " choice

            case $choice in
                1)
                    log "Proceeding with fresh installation"
                    rm -rf "$INSTALL_DIR"
                    ;;
                2)
                    log "Merging with existing installation"
                    MERGE_MODE=true
                    ;;
                3)
                    log "Updating workflows only (agents & scripts)"
                    UPDATE_WORKFLOWS_ONLY=true
                    ;;
                4)
                    log "Installation cancelled by user"
                    echo "Your backup is preserved at: $backup_dir"
                    exit 0
                    ;;
                *)
                    log_error "Invalid choice"
                    echo "Your backup is preserved at: $backup_dir"
                    exit 1
                    ;;
            esac
        fi
    fi

    # Create installation directory
    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would create installation directory: $INSTALL_DIR"
    else
        mkdir -p "$INSTALL_DIR"
    fi
}

# Handle agents.md file
handle_agents_md() {
    local source_dir="$1"
    local source_agents_md="$source_dir/agents.md"
    local target_agents_md="$INSTALL_DIR/agents.md"  # Note: agents.md goes to .opencode directory

    # Check if our source agents.md exists
    if [[ ! -f "$source_agents_md" ]]; then
        log_verbose "No agents.md found in source, skipping"
        return 0
    fi

    if [[ -f "$target_agents_md" ]]; then
        # Target agents.md exists, append our content as a new section
        log_verbose "Existing agents.md found, appending AI Assisted Workflows section..."

        # Check if our section already exists
        if grep -q "AI Assisted Workflow Agents" "$target_agents_md" 2>/dev/null; then
            log_verbose "AI Assisted Workflows section already exists, skipping merge"
            return 0
        fi

        # Append our content as a new section
        {
            echo ""
            echo "---"
            echo ""
            cat "$source_agents_md"
        } >> "$target_agents_md"

        log "Appended AI Assisted Workflows section to existing agents.md"
    else
        # No existing agents.md, copy ours
        log_verbose "No existing agents.md found, copying ours..."
        cp "$source_agents_md" "$target_agents_md"
        log "Copied agents.md to .opencode directory"
    fi
}

# Handle opencode.json file
handle_opencode_json() {
    local source_dir="$1"
    local source_json="$source_dir/opencode.json"
    local target_json="$INSTALL_DIR/opencode.json"  # Note: opencode.json goes to .opencode directory

    # Check if our source opencode.json exists
    if [[ ! -f "$source_json" ]]; then
        log_verbose "No opencode.json found in source, skipping"
        return 0
    fi

    if [[ -f "$target_json" ]]; then
        log_verbose "Existing opencode.json found, preserving user configuration"
        # Don't overwrite existing opencode.json as it contains user-specific configuration
    else
        # No existing opencode.json, copy ours
        log_verbose "No existing opencode.json found, copying default configuration..."
        cp "$source_json" "$target_json"
        log "Copied opencode.json to .opencode directory"
    fi
}

# File copy operations
copy_files() {
    log_verbose "Copying workflow files..."

    local source_dir="$SCRIPT_DIR"

    # Verify source files exist
    # Check if we have the expected subdirectories
    local scripts_dir="$(dirname "$source_dir")/shared/lib/scripts"
    if [[ ! -d "$source_dir/agent" ]] || [[ ! -d "$scripts_dir" ]]; then
        log_error "Source files not found"
        log_error "Expected to find: $source_dir/agent/ and $scripts_dir"
        exit 1
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would copy files from $source_dir to $INSTALL_DIR"
        return 0
    fi

    # Copy workflow files
    log_verbose "Copying workflow files..."
    if [[ "${MERGE_MODE:-false}" == "true" ]]; then
        # Merge mode: preserve existing files, copy new ones
        log "Merge mode: preserving existing files while adding new ones..."

        # Track what's being preserved vs added
        local preserved_count=0
        local added_count=0
        local custom_agents=()

        # Check for custom agents
        if [[ -d "$INSTALL_DIR/agent" ]]; then
            for agent in "$INSTALL_DIR/agent"/*; do
                if [[ -f "$agent" ]]; then
                    local agent_name=$(basename "$agent")
                    if ! [[ -f "$source_dir/agent/$agent_name" ]]; then
                        custom_agents+=("$agent_name")
                    fi
                fi
            done
        fi

        # Copy with no-clobber, excluding docs and install scripts
        find "$source_dir" -mindepth 1 -maxdepth 1 -not -name "docs" -not -name "install.sh" -not -name "install.ps1" -not -name "opencode.json" -not -name "agents.md" -exec cp -rn {} "$INSTALL_DIR/" \; 2>/dev/null || true

        # Copy scripts from shared/lib to root of INSTALL_DIR
        local scripts_source="$(dirname "$source_dir")/shared/lib/scripts"
        if [[ -d "$scripts_source" ]] && [[ ! -d "$INSTALL_DIR/scripts" ]]; then
            cp -r "$scripts_source" "$INSTALL_DIR/scripts"
        fi

        # Copy formatter from shared/config to root of INSTALL_DIR
        local formatter_source="$(dirname "$source_dir")/shared/config/formatter"
        if [[ -d "$formatter_source" ]] && [[ ! -d "$INSTALL_DIR/formatter" ]]; then
            cp -r "$formatter_source" "$INSTALL_DIR/formatter"
        fi

        # Report custom agents preserved
        if [[ ${#custom_agents[@]} -gt 0 ]]; then
            echo "  Preserved custom agents:"
            for agent in "${custom_agents[@]}"; do
                echo "    - $agent"
            done
        fi

        echo "  Merge complete. Existing files preserved, new files added."
    elif [[ "${UPDATE_WORKFLOWS_ONLY:-false}" == "true" ]]; then
        # Update workflows only: update built-in agents, scripts, modes, instructions, preserve custom agents
        log "Updating workflows only: built-in agents, scripts, modes, and instructions..."

        # Update built-in agents while preserving custom agents
        if [[ -d "$source_dir/agent" ]]; then
            log "  Updating agent directory (preserving custom agents)..."
            local custom_agents=()

            # Identify existing custom agents
            if [[ -d "$INSTALL_DIR/agent" ]]; then
                for agent in "$INSTALL_DIR/agent"/*; do
                    if [[ -f "$agent" ]]; then
                        local agent_name=$(basename "$agent")
                        if ! [[ -f "$source_dir/agent/$agent_name" ]]; then
                            custom_agents+=("$agent_name")
                        fi
                    fi
                done
            fi

            # Create agent directory if it doesn't exist
            mkdir -p "$INSTALL_DIR/agent"

            # Copy/overwrite built-in agents (this preserves any custom agents not in source)
            cp "$source_dir/agent"/* "$INSTALL_DIR/agent/"

            # Report preserved custom agents
            if [[ ${#custom_agents[@]} -gt 0 ]]; then
                echo "    Preserved custom agents:"
                for agent in "${custom_agents[@]}"; do
                    echo "      - $agent"
                done
            fi
        fi

        # Update scripts directory (preserve custom scripts)
        local scripts_source="$(dirname "$source_dir")/shared/lib/scripts"
        if [[ -d "$scripts_source" ]]; then
            log "  Updating scripts directory (preserving custom scripts)..."

            # Backup custom scripts if they exist
            local custom_scripts=()
            if [[ -d "$INSTALL_DIR/scripts" ]]; then
                # Find custom scripts that aren't in our source
                while IFS= read -r -d '' script_file; do
                    local rel_path="${script_file#$INSTALL_DIR/scripts/}"
                    if [[ ! -f "$scripts_source/$rel_path" ]]; then
                        custom_scripts+=("$rel_path")
                    fi
                done < <(find "$INSTALL_DIR/scripts" -type f -print0 2>/dev/null)

                # Create temp backup of custom scripts
                if [[ ${#custom_scripts[@]} -gt 0 ]]; then
                    local temp_backup=$(mktemp -d)
                    for script in "${custom_scripts[@]}"; do
                        local script_dir=$(dirname "$temp_backup/$script")
                        mkdir -p "$script_dir"
                        cp "$INSTALL_DIR/scripts/$script" "$temp_backup/$script"
                    done
                fi
            fi

            # Remove and recreate scripts directory
            rm -rf "$INSTALL_DIR/scripts"
            cp -r "$scripts_source" "$INSTALL_DIR/scripts"

            # Restore custom scripts
            if [[ ${#custom_scripts[@]} -gt 0 ]]; then
                echo "    Preserved custom scripts:"
                for script in "${custom_scripts[@]}"; do
                    local script_dir=$(dirname "$INSTALL_DIR/scripts/$script")
                    mkdir -p "$script_dir"
                    cp "$temp_backup/$script" "$INSTALL_DIR/scripts/$script"
                    echo "      - $script"
                done
                rm -rf "$temp_backup"
            fi
        fi

        # Update modes directory
        if [[ -d "$source_dir/mode" ]]; then
            log "  Updating mode directory..."
            rm -rf "$INSTALL_DIR/mode"
            cp -r "$source_dir/mode" "$INSTALL_DIR/"
        fi

        # Update instructions directory
        if [[ -d "$source_dir/instructions" ]]; then
            log "  Updating instructions directory..."
            rm -rf "$INSTALL_DIR/instructions"
            cp -r "$source_dir/instructions" "$INSTALL_DIR/"
        fi

        # Update formatter directory
        local formatter_source="$(dirname "$source_dir")/shared/config/formatter"
        if [[ -d "$formatter_source" ]]; then
            log "  Updating formatter directory..."
            rm -rf "$INSTALL_DIR/formatter"
            cp -r "$formatter_source" "$INSTALL_DIR/formatter"
        fi

        echo "  Workflow update complete. Built-in agents, scripts, modes, instructions, and formatter updated, custom agents and other files preserved."
    else
        # Fresh install: copy everything except docs, install scripts, opencode.json, and agents.md
        find "$source_dir" -mindepth 1 -maxdepth 1 -not -name "docs" -not -name "install.sh" -not -name "install.ps1" -not -name "opencode.json" -not -name "agents.md" -exec cp -r {} "$INSTALL_DIR/" \;

        # Copy scripts from shared/lib to root of INSTALL_DIR
        local scripts_source="$(dirname "$source_dir")/shared/lib/scripts"
        if [[ -d "$scripts_source" ]]; then
            cp -r "$scripts_source" "$INSTALL_DIR/scripts"
        fi

        # Copy formatter from shared/config to root of INSTALL_DIR
        local formatter_source="$(dirname "$source_dir")/shared/config/formatter"
        if [[ -d "$formatter_source" ]]; then
            cp -r "$formatter_source" "$INSTALL_DIR/formatter"
        fi
    fi

    # Handle agents.md and opencode.json separately (they go to TARGET_PATH root)
    handle_agents_md "$source_dir"
    handle_opencode_json "$source_dir"

    # Set proper permissions
    find "$INSTALL_DIR" -name "*.py" -exec chmod +x {} \;
    find "$INSTALL_DIR" -name "*.sh" -exec chmod +x {} \;

    log "Files copied successfully"
}

# Create installation log for uninstall tracking
create_installation_log() {
    log "Creating installation log for uninstall tracking..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would create installation log"
        return 0
    fi

    local log_file="$INSTALL_DIR/installation-log.txt"
    local requirements_file="$INSTALL_DIR/scripts/setup/requirements.txt"

    # Create log file with header
    cat > "$log_file" << EOF
# AI Assisted Workflows Installation Log
# DO NOT DELETE - Used by uninstall script to determine safe removal
# Generated on: $(date)
# Installation directory: $INSTALL_DIR

[PRE_EXISTING_PYTHON_PACKAGES]
EOF

    # Check which Python packages were already installed
    if [[ -f "$requirements_file" ]]; then
        while IFS= read -r line; do
            # Skip empty lines and comments
            [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
            # Extract package name (everything before ==, >=, etc.)
            local pkg=$(echo "$line" | sed 's/[>=<].*//' | tr -d ' ')
            if [[ -n "$pkg" ]] && python3 -m pip show "$pkg" &>/dev/null; then
                echo "$pkg" >> "$log_file"
                log_verbose "Pre-existing Python package: $pkg"
            fi
        done < "$requirements_file"
    fi

    # Initialize sections for newly installed items
    cat >> "$log_file" << EOF

[NEWLY_INSTALLED_PYTHON_PACKAGES]
EOF

    log_verbose "Installation log created: installation-log.txt"
}

# Update installation log with newly installed items
update_installation_log() {
    local item_type="$1"
    local item_name="$2"

    if [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    local log_file="$INSTALL_DIR/installation-log.txt"

    if [[ ! -f "$log_file" ]]; then
        return 0
    fi

    # Add item to appropriate section
    if [[ "$item_type" == "python" ]]; then
        echo "$item_name" >> "$log_file"
    fi

    log_verbose "Added to installation log: $item_type - $item_name"
}

# Python dependency installation
install_python_deps() {
    if [[ "$SKIP_PYTHON" == "true" ]]; then
        log "Skipping Python dependencies installation"
        return 0
    fi

    log "Installing Python dependencies..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would run Python dependency installation"
        return 0
    fi

    local setup_script="$INSTALL_DIR/scripts/setup/install_dependencies.py"

    if [[ ! -f "$setup_script" ]]; then
        log_error "Setup script not found: $setup_script"
        exit 1
    fi

    # Get list of packages that will be installed
    local requirements_file="$INSTALL_DIR/scripts/setup/requirements.txt"
    local packages_to_check=()

    if [[ -f "$requirements_file" ]]; then
        while IFS= read -r line; do
            # Skip empty lines and comments
            [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
            # Extract package name (everything before ==, >=, etc.)
            local pkg=$(echo "$line" | sed 's/[>=<].*//' | tr -d ' ')
            [[ -n "$pkg" ]] && packages_to_check+=("$pkg")
        done < "$requirements_file"
    fi

    log_verbose "Running installation script..."
    cd "$INSTALL_DIR"

    # Run Python dependency installation with automatic 'yes' response
    if echo "y" | python3 "$setup_script"; then
        log "Python dependencies installed successfully"

        # Check which packages are now installed and update log for newly installed ones
        for pkg in "${packages_to_check[@]}"; do
            if python3 -m pip show "$pkg" &>/dev/null; then
                # Check if this package was pre-existing by reading the installation log
                local log_file="$INSTALL_DIR/installation-log.txt"
                if [[ -f "$log_file" ]]; then
                    # Check if package is NOT in the pre-existing list
                    if ! grep -A 100 "^\[PRE_EXISTING_PYTHON_PACKAGES\]" "$log_file" | grep -q "^$pkg$"; then
                        update_installation_log "python" "$pkg"
                    fi
                else
                    # No log file, assume it's newly installed
                    update_installation_log "python" "$pkg"
                fi
            fi
        done
    else
        log_error "Python dependencies installation failed"
        exit 1
    fi
}

# Installation verification
verify_installation() {
    log "Verifying installation..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would verify installation"
        return 0
    fi

    if [[ "$DRY_RUN" != "true" ]]; then
        local test_script="$INSTALL_DIR/scripts/setup/test_install.py"

        # Test Python dependencies
        if [[ "$SKIP_PYTHON" != "true" ]] && [[ -f "$test_script" ]]; then
            log_verbose "Testing Python dependencies..."
            cd "$INSTALL_DIR"
            if python3 "$test_script" >> "$LOG_FILE" 2>&1; then
                log_verbose "Python dependencies verification passed"
            else
                log_error "Python dependencies verification failed"
                exit 1
            fi
        fi
    fi

    # Test file structure
    if [[ "$DRY_RUN" != "true" ]]; then
        local required_dirs=("agent" "scripts" "mode" "instructions")
        for dir in "${required_dirs[@]}"; do
            if [[ ! -d "$INSTALL_DIR/$dir" ]]; then
                log_error "Required directory missing: $INSTALL_DIR/$dir"
                exit 1
            fi
        done

        # Verify custom agents preservation if in merge mode
        if [[ "${MERGE_MODE:-false}" == "true" ]]; then
            log_verbose "Verifying custom agents preservation..."
            local custom_agents_found=0

            if [[ -d "$INSTALL_DIR/agent" ]]; then
                for agent in "$INSTALL_DIR/agent"/*; do
                    if [[ -f "$agent" ]]; then
                        local agent_name=$(basename "$agent")
                        # Check if this is a custom agent (not in source)
                        if ! [[ -f "$SCRIPT_DIR/agent/$agent_name" ]]; then
                            log_verbose "  Custom agent preserved: $agent_name"
                            ((custom_agents_found++))
                        fi
                    fi
                done
            fi

            if [[ $custom_agents_found -gt 0 ]]; then
                log "Verified: $custom_agents_found custom agent(s) preserved"
            fi
        fi
    fi

    log "Installation verification completed successfully"
}

# Display post-installation information
show_completion() {
    echo ""
    echo "🎉 AI Assisted Workflows installation completed successfully!"
    echo ""
    echo "Installation location: $INSTALL_DIR"
    echo ""
    echo "Available agents (14+ agents):"
    echo "  Analysis: analyze-security, analyze-architecture, analyze-performance, etc."
    echo "  Planning: plan-solution, plan-ux-prd, plan-refactor"
    echo "  Utilities: get-primer, create-session-notes, setup-dev-monitoring"
    echo "  Project: create-project"
    echo ""
    echo "Configuration files:"
    echo "  agents.md: $INSTALL_DIR/agents.md"
    echo "  opencode.json: $INSTALL_DIR/opencode.json"
    echo ""
    echo "Usage:"
    echo "  Agents are available through the Task tool in OpenCode"
    echo "  Configure agents in opencode.json or via markdown files"
    echo ""
    echo "For more information:"
    echo "  View agents: ls $INSTALL_DIR/agent/"
    echo "  View modes: ls $INSTALL_DIR/mode/"
    echo "  Log file: $LOG_FILE"
    echo ""
}

# Error handling and cleanup
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Installation failed with exit code $exit_code"
        echo ""
        echo "Installation failed. Check the log file for details: $LOG_FILE"
        echo ""
        echo "Common solutions:"
        echo "  1. Ensure Python 3.7+ is installed"
        echo "  2. Check internet connectivity"
        echo "  3. Run with --skip-python if Python deps are causing issues"
        echo ""
    fi
}

# Main installation function
main() {
    parse_args "$@"

    # Set up error handling
    trap cleanup EXIT

    # Initialize log file
    echo "AI Assisted Workflows Installation Log" > "$LOG_FILE"
    echo "Started: $(date)" >> "$LOG_FILE"
    echo "Arguments: $*" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    log "Starting AI Assisted Workflows installation (v$SCRIPT_VERSION)"

    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN MODE - no changes will be made"
    fi

    # Run installation steps
    detect_platform
    check_python
    setup_install_dir
    copy_files
    create_installation_log
    install_python_deps
    verify_installation

    if [[ "$DRY_RUN" != "true" ]]; then
        show_completion
    else
        log "Dry run completed - no changes were made"
    fi
}

# Run main function with all arguments
main "$@"
