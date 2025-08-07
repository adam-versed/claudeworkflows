# Claude Code Workflows Installation Script for Windows
# Installs the complete workflow system with commands, scripts, and dependencies

param(
    [Parameter(Position=0)]
    [string]$TargetPath = "",

    [switch]$Help,
    [switch]$Verbose,
    [switch]$DryRun,
    [switch]$SkipMcp,
    [switch]$SkipPython
)

# Script configuration
$VERSION = "1.0.0"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$LOG_FILE = "$env:TEMP\claude-workflows-install.log"

# Colors for output
$Colors = @{
    Green = [System.ConsoleColor]::Green
    Yellow = [System.ConsoleColor]::Yellow
    Red = [System.ConsoleColor]::Red
    Blue = [System.ConsoleColor]::Blue
    White = [System.ConsoleColor]::White
    Cyan = [System.ConsoleColor]::Cyan
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::White
    )
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Output $Message
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LOG_FILE -Value $logEntry

    if ($Verbose) {
        Write-ColorOutput "$logEntry" -Color $Colors.Cyan
    }
}

function Show-Usage {
    Write-ColorOutput "Claude Code Workflows Installer v$VERSION" -Color $Colors.Green
    Write-Output ""
    Write-Output "USAGE:"
    Write-Output "    .\install.ps1 [TARGET_PATH] [OPTIONS]"
    Write-Output ""
    Write-Output "ARGUMENTS:"
    Write-Output "    TARGET_PATH     Directory where .claude\ will be created"
    Write-Output "                   Examples:"
    Write-Output "                     ~\                    (User global: ~\.claude\)"
    Write-Output "                     .\myproject           (Project local: .\myproject\.claude\)"
    Write-Output "                     C:\path\to\project    (Custom path: C:\path\to\project\.claude\)"
    Write-Output "                   Default: current directory"
    Write-Output ""
    Write-Output "OPTIONS:"
    Write-Output "    -Help           Show this help message"
    Write-Output "    -Verbose        Enable verbose output"
    Write-Output "    -DryRun         Show what would be done without making changes"
    Write-Output "    -SkipMcp        Skip MCP tools installation"
    Write-Output "    -SkipPython     Skip Python dependencies installation"
    Write-Output ""
    Write-Output "EXAMPLES:"
    Write-Output "    # Install in current project (creates .\.claude\)"
    Write-Output "    .\install.ps1"
    Write-Output ""
    Write-Output "    # Install globally for user (creates ~\.claude\)"
    Write-Output "    .\install.ps1 ~"
    Write-Output ""
    Write-Output "    # Install in specific project"
    Write-Output "    .\install.ps1 C:\path\to\my-project"
    Write-Output ""
    Write-Output "    # Dry run to see what would happen"
    Write-Output "    .\install.ps1 -DryRun"
    Write-Output ""
    Write-Output "    # Install without MCP tools"
    Write-Output "    .\install.ps1 -SkipMcp"
    Write-Output ""
    Write-Output "REQUIREMENTS:"
    Write-Output "    - Python 3.7+"
    Write-Output "    - Node.js (for MCP tools)"
    Write-Output "    - Claude CLI (for MCP tools)"
    Write-Output "    - Internet connection for dependencies"
}

function Test-Prerequisites {
    Write-Output ""
    Write-ColorOutput "Checking prerequisites..." -Color $Colors.Yellow
    Write-Log "Starting prerequisite checks"

    $errors = 0

    # Check Python
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)"
            if ($versionMatch -and $matches.Count -ge 3) {
                $major = [int]$matches[1]
                $minor = [int]$matches[2]
                if (($major -eq 3 -and $minor -ge 7) -or $major -gt 3) {
                    Write-ColorOutput "[OK] $pythonVersion found" -Color $Colors.Green
                    Write-Log "Python check passed: $pythonVersion"
                } else {
                    Write-ColorOutput "[ERROR] $pythonVersion found, but Python 3.7+ required" -Color $Colors.Red
                    Write-Output "  Install: https://www.python.org/downloads/"
                    Write-Log "Python version too old: $pythonVersion" -Level "ERROR"
                    $errors++
                }
            } else {
                Write-ColorOutput "[ERROR] Could not parse Python version: $pythonVersion" -Color $Colors.Red
                Write-Log "Could not parse Python version: $pythonVersion" -Level "ERROR"
                $errors++
            }
        } else {
            throw "Python not found"
        }
    } catch {
        Write-ColorOutput "[ERROR] Python not found or not accessible" -Color $Colors.Red
        Write-Output "  Install: https://www.python.org/downloads/"
        Write-Output "  Make sure Python is in your PATH"
        Write-Log "Python not found: $($_.Exception.Message)" -Level "ERROR"
        $errors++
    }

    # Check pip
    try {
        $pipVersion = & pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "[OK] pip found" -Color $Colors.Green
            Write-Log "pip check passed: $pipVersion"
        } else {
            throw "pip not found"
        }
    } catch {
        Write-ColorOutput "[ERROR] pip not found" -Color $Colors.Red
        Write-Output "  pip should be included with Python 3.7+"
        Write-Output "  If missing, install with: python -m ensurepip --upgrade"
        Write-Log "pip not found: $($_.Exception.Message)" -Level "ERROR"
        $errors++
    }

    # Check Node.js (only if MCP tools not skipped)
    if (-not $SkipMcp) {
        try {
            $nodeVersion = & node --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $versionNumber = $nodeVersion -replace '^v', ''
                $major = [int]($versionNumber.Split('.')[0])
                if ($major -ge 14) {
                    Write-ColorOutput "[OK] Node.js $nodeVersion found" -Color $Colors.Green
                    Write-Log "Node.js check passed: $nodeVersion"
                } else {
                    Write-ColorOutput "[ERROR] Node.js $nodeVersion found, but 14+ required for MCP tools" -Color $Colors.Red
                    Write-Output "  Install: https://nodejs.org/"
                    Write-Output "  Or use -SkipMcp to skip MCP tools installation"
                    Write-Log "Node.js version too old: $nodeVersion" -Level "ERROR"
                    $errors++
                }
            } else {
                throw "Node.js not found"
            }
        } catch {
            Write-ColorOutput "[WARNING] Node.js not found - MCP tools will be skipped" -Color $Colors.Yellow
            Write-Output "  To enable MCP tools, install Node.js: https://nodejs.org/"
            Write-Log "Node.js not found, will skip MCP tools: $($_.Exception.Message)" -Level "WARNING"
            $SkipMcp = $true
        }

        # Check Claude CLI (only if MCP tools not skipped)
        if (-not $SkipMcp) {
            try {
                $claudeVersion = & claude --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "[OK] Claude CLI found" -Color $Colors.Green
                    Write-Log "Claude CLI check passed: $claudeVersion"
                } else {
                    throw "Claude CLI not found"
                }
            } catch {
                Write-ColorOutput "[WARNING] Claude CLI not found - MCP tools will be skipped" -Color $Colors.Yellow
                Write-Output "  To enable MCP tools, install Claude CLI"
                Write-Output "  Or use -SkipMcp to skip MCP tools installation"
                Write-Log "Claude CLI not found, will skip MCP tools: $($_.Exception.Message)" -Level "WARNING"
                $SkipMcp = $true
            }
        }
    } else {
        Write-ColorOutput "[INFO] MCP tools installation skipped" -Color $Colors.Yellow
        Write-Log "MCP tools installation skipped by user"
    }

    if ($errors -gt 0) {
        Write-Output ""
        Write-ColorOutput "[ERROR] Installation blocked: $errors prerequisite(s) missing" -Color $Colors.Red
        Write-Output ""
        Write-Output "Please install missing prerequisites and run again."
        Write-Log "Installation blocked due to $errors missing prerequisites" -Level "ERROR"
        exit 1
    }

    Write-Output ""
    Write-ColorOutput "[OK] All prerequisites satisfied" -Color $Colors.Green
    Write-Log "All prerequisites satisfied"
}

function Resolve-TargetPath {
    param([string]$Path)

    if ([string]::IsNullOrEmpty($Path)) {
        $resolvedPath = Get-Location
    } elseif ($Path -eq "~") {
        $resolvedPath = $env:USERPROFILE
    } else {
        # Convert to absolute path if relative
        if (-not [System.IO.Path]::IsPathRooted($Path)) {
            $resolvedPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
        } else {
            $resolvedPath = $Path
        }
    }

    return $resolvedPath
}

function Test-WritePermissions {
    param([string]$Path)

    try {
        $testFile = Join-Path $Path "test_write_permissions.tmp"
        New-Item -ItemType File -Path $testFile -Force | Out-Null
        Remove-Item -Path $testFile -Force
        return $true
    } catch {
        return $false
    }
}

function Backup-ExistingInstallation {
    param([string]$ClaudePath)

    if (Test-Path $ClaudePath) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = "$ClaudePath.backup.$timestamp"

        Write-ColorOutput "Existing .claude directory found" -Color $Colors.Yellow

        if ($DryRun) {
            Write-ColorOutput "[DRY RUN] Would backup existing installation to: $backupPath" -Color $Colors.Blue
            return $backupPath
        }

        Write-Output "Creating backup of existing installation..."
        Copy-Item -Path $ClaudePath -Destination $backupPath -Recurse -Force
        Write-ColorOutput "Backup created: $backupPath" -Color $Colors.Green
        Write-Log "Created backup: $backupPath"
        return $backupPath
    }

    return $null
}

function Install-PythonDependencies {
    if ($SkipPython) {
        Write-ColorOutput "[INFO] Python dependencies installation skipped" -Color $Colors.Yellow
        Write-Log "Python dependencies installation skipped by user"
        return
    }

    Write-Output ""
    Write-ColorOutput "Installing Python dependencies..." -Color $Colors.Yellow
    Write-Log "Starting Python dependencies installation"

    $setupDir = Join-Path $SCRIPT_DIR "scripts\setup"
    $requirementsPath = Join-Path $setupDir "requirements.txt"

    if (-not (Test-Path $requirementsPath)) {
        Write-ColorOutput "[ERROR] Requirements file not found: $requirementsPath" -Color $Colors.Red
        Write-Log "Requirements file not found: $requirementsPath" -Level "ERROR"
        exit 1
    }

    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Would install Python dependencies from: $requirementsPath" -Color $Colors.Blue
        return
    }

    try {
        Write-Output "Installing packages from requirements.txt..."
        & pip install -r $requirementsPath --user

        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "[OK] Python dependencies installed successfully" -Color $Colors.Green
            Write-Log "Python dependencies installed successfully"
        } else {
            Write-ColorOutput "[ERROR] Failed to install Python dependencies" -Color $Colors.Red
            Write-Log "Failed to install Python dependencies, exit code: $LASTEXITCODE" -Level "ERROR"
            exit 1
        }
    } catch {
        Write-ColorOutput "[ERROR] Error installing Python dependencies: $($_.Exception.Message)" -Color $Colors.Red
        Write-Log "Error installing Python dependencies: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}

function Install-McpTools {
    param([string]$ClaudePath)

    if ($SkipMcp) {
        Write-ColorOutput "[INFO] MCP tools installation skipped" -Color $Colors.Yellow
        Write-Log "MCP tools installation skipped"
        return
    }

    Write-Output ""
    Write-ColorOutput "Installing MCP tools..." -Color $Colors.Yellow
    Write-Log "Starting MCP tools installation"

    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Would install MCP tools via Claude CLI" -Color $Colors.Blue
        return
    }

    try {
        # Install sequential-thinking MCP server
        Write-Output "Installing sequential-thinking MCP server..."
        Start-Sleep -Seconds 1  # Small delay to ensure claude mcp list is ready
        $mcpListOutput = & claude mcp list 2>&1
        if ($mcpListOutput -match "^sequential-thinking:") {
            Write-ColorOutput "[INFO] sequential-thinking already installed, skipping" -Color $Colors.Yellow
            Write-Log "sequential-thinking already installed, skipping"
        } else {
            # Try to install, capturing the actual output
            $installOutput = & claude mcp add sequential-thinking -s user -- npx -y "@modelcontextprotocol/server-sequential-thinking" 2>&1
            $installExitCode = $LASTEXITCODE

            if ($installExitCode -eq 0) {
                Write-ColorOutput "[OK] sequential-thinking MCP server installed" -Color $Colors.Green
                Write-Log "sequential-thinking MCP server installed successfully"
            } elseif ($installOutput -match "already exists") {
                Write-ColorOutput "[INFO] sequential-thinking already exists, marking as successful" -Color $Colors.Yellow
                Write-Log "sequential-thinking already exists (detected during install)"
            } else {
                Write-ColorOutput "[WARNING] Failed to install sequential-thinking MCP server: $installOutput" -Color $Colors.Yellow
                Write-Log "Failed to install sequential-thinking MCP server: $installOutput" -Level "WARNING"
            }
        }

        # Install grep MCP server
        Write-Output "Installing grep MCP server..."
        $mcpListOutput = & claude mcp list 2>&1
        if ($mcpListOutput -match "^grep:") {
            Write-ColorOutput "[INFO] grep already installed, skipping" -Color $Colors.Yellow
            Write-Log "grep already installed, skipping"
        } else {
            # Try to install, capturing the actual output
            $installOutput = & claude mcp add --transport http grep https://mcp.grep.app 2>&1
            $installExitCode = $LASTEXITCODE

            if ($installExitCode -eq 0) {
                Write-ColorOutput "[OK] grep MCP server installed" -Color $Colors.Green
                Write-Log "grep MCP server installed successfully"
            } elseif ($installOutput -match "already exists") {
                Write-ColorOutput "[INFO] grep already exists, marking as successful" -Color $Colors.Yellow
                Write-Log "grep already exists (detected during install)"
            } else {
                Write-ColorOutput "[WARNING] Failed to install grep MCP server: $installOutput" -Color $Colors.Yellow
                Write-Log "Failed to install grep MCP server: $installOutput" -Level "WARNING"
            }
        }

    } catch {
        Write-ColorOutput "[WARNING] Error installing MCP tools: $($_.Exception.Message)" -Color $Colors.Yellow
        Write-Log "Error installing MCP tools: $($_.Exception.Message)" -Level "WARNING"
    }
}

function Copy-WorkflowFiles {
    param([string]$ClaudePath)

    Write-Output ""
    Write-ColorOutput "Copying workflow files..." -Color $Colors.Yellow
    Write-Log "Starting workflow files copy"

    # Source directory is the script directory itself
    $sourceClaudeDir = $SCRIPT_DIR

    if (-not (Test-Path $sourceClaudeDir)) {
        Write-ColorOutput "[ERROR] Source claude directory not found: $sourceClaudeDir" -Color $Colors.Red
        Write-Log "Source claude directory not found: $sourceClaudeDir" -Level "ERROR"
        exit 1
    }

    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Would copy workflow files from: $sourceClaudeDir" -Color $Colors.Blue
        Write-ColorOutput "[DRY RUN] Would copy to: $ClaudePath" -Color $Colors.Blue
        return
    }

    try {
        # Create target directory
        if (-not (Test-Path $ClaudePath)) {
            New-Item -ItemType Directory -Path $ClaudePath -Force | Out-Null
        }

        # Copy all files and directories to target/.claude/, excluding docs folder and install scripts
        $items = Get-ChildItem $sourceClaudeDir -Recurse | Where-Object {
            $relativePath = [System.IO.Path]::GetRelativePath($sourceClaudeDir, $_.FullName)
            -not ($relativePath -like "docs\*" -or $relativePath -eq "docs" -or $relativePath -eq "install.sh" -or $relativePath -eq "install.ps1")
        }
        foreach ($item in $items) {
            $relativePath = [System.IO.Path]::GetRelativePath($sourceClaudeDir, $item.FullName)
            $targetPath = Join-Path $ClaudePath $relativePath
            $targetDir = Split-Path $targetPath -Parent

            if (-not (Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }

            if ($item.PSIsContainer) {
                if (-not (Test-Path $targetPath)) {
                    New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
                }
            } else {
                Copy-Item -Path $item.FullName -Destination $targetPath -Force
            }
        }

        # Copy CLAUDE.md if it exists in root, otherwise copy claude.md as CLAUDE.md
        $rootClaudeFile = Join-Path $SCRIPT_DIR "CLAUDE.md"
        $nestedClaudeFile = Join-Path $SCRIPT_DIR "claude.md"
        $targetClaudeFile = Join-Path $ClaudePath "CLAUDE.md"

        if (Test-Path $rootClaudeFile) {
            Copy-Item -Path $rootClaudeFile -Destination $targetClaudeFile -Force
        } elseif (Test-Path $nestedClaudeFile) {
            Copy-Item -Path $nestedClaudeFile -Destination $targetClaudeFile -Force
        }

        # Create installation log
        $installLog = Join-Path $ClaudePath "installation-log.txt"
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $mcpStatus = if ($SkipMcp) { "Skipped" } else { "Installed" }
        $pythonStatus = if ($SkipPython) { "Skipped" } else { "Installed" }
        @"
Claude Code Workflows Installation Log
=====================================
Installation Date: $timestamp
Installer Version: $VERSION
Target Path: $ClaudePath
MCP Tools: $mcpStatus
Python Dependencies: $pythonStatus
"@ | Set-Content -Path $installLog

        Write-ColorOutput "[OK] Workflow files copied successfully" -Color $Colors.Green
        Write-Log "Workflow files copied successfully to: $ClaudePath"

    } catch {
        Write-ColorOutput "[ERROR] Error copying workflow files: $($_.Exception.Message)" -Color $Colors.Red
        Write-Log "Error copying workflow files: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}

function Test-Installation {
    param([string]$ClaudePath)

    Write-Output ""
    Write-ColorOutput "Verifying installation..." -Color $Colors.Yellow
    Write-Log "Starting installation verification"

    $errors = 0

    # Check main directories
    $requiredDirs = @("commands", "scripts", "rules", "templates", "agents")
    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $ClaudePath $dir
        if (Test-Path $dirPath) {
            Write-ColorOutput "[OK] Directory $dir found" -Color $Colors.Green
        } else {
            Write-ColorOutput "[ERROR] Directory $dir missing" -Color $Colors.Red
            $errors++
        }
    }

    # Check key files
    $requiredFiles = @("claude.md", "CLAUDE.md")
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $ClaudePath $file
        if (Test-Path $filePath) {
            Write-ColorOutput "[OK] File $file found" -Color $Colors.Green
        } else {
            Write-ColorOutput "[WARNING] File $file missing" -Color $Colors.Yellow
        }
    }

    # Count command files
    $commandsPath = Join-Path $ClaudePath "commands"
    if (Test-Path $commandsPath) {
        $commandCount = (Get-ChildItem $commandsPath -Filter "*.md" | Measure-Object).Count
        Write-ColorOutput "[INFO] Commands found: $commandCount" -Color $Colors.Green
    }

    # Count script files
    $scriptsPath = Join-Path $ClaudePath "scripts"
    if (Test-Path $scriptsPath) {
        $scriptCount = (Get-ChildItem $scriptsPath -Filter "*.py" -Recurse | Measure-Object).Count
        Write-ColorOutput "[INFO] Python scripts found: $scriptCount" -Color $Colors.Green
    }

    # Count template files
    $templatesPath = Join-Path $ClaudePath "templates"
    if (Test-Path $templatesPath) {
        $templateCount = (Get-ChildItem $templatesPath -Filter "*.md" | Measure-Object).Count
        Write-ColorOutput "[INFO] Templates found: $templateCount" -Color $Colors.Green
    }

    if ($errors -gt 0) {
        Write-ColorOutput "[ERROR] Installation verification failed: $errors errors found" -Color $Colors.Red
        Write-Log "Installation verification failed: $errors errors found" -Level "ERROR"
        return $false
    } else {
        Write-ColorOutput "[OK] Installation verification successful" -Color $Colors.Green
        Write-Log "Installation verification successful"
        return $true
    }
}

function Show-CompletionMessage {
    param([string]$ClaudePath, [string]$BackupPath)

    Write-Output ""
    Write-ColorOutput "==================================" -Color $Colors.Green
    Write-ColorOutput "Installation completed successfully!" -Color $Colors.Green
    Write-ColorOutput "==================================" -Color $Colors.Green
    Write-Output ""

    Write-ColorOutput "Claude Code Workflows v$VERSION installed to:" -Color $Colors.Yellow
    Write-Output "  $ClaudePath"
    Write-Output ""

    if ($BackupPath) {
        Write-ColorOutput "Previous installation backed up to:" -Color $Colors.Yellow
        Write-Output "  $BackupPath"
        Write-Output ""
    }

    Write-ColorOutput "Available commands:" -Color $Colors.Yellow
    $commandsPath = Join-Path $ClaudePath "commands"
    if (Test-Path $commandsPath) {
        $commands = Get-ChildItem $commandsPath -Filter "*.md" | ForEach-Object { $_.BaseName }
        $commandCount = $commands.Count
        Write-Output "  Total commands: $commandCount"
        foreach ($command in $commands | Select-Object -First 5) {
            Write-Output "  • $command"
        }
        if ($commandCount -gt 5) {
            Write-Output "  • ... and $($commandCount - 5) more"
        }
    }
    Write-Output ""

    Write-ColorOutput "Next steps:" -Color $Colors.Yellow
    Write-Output "  1. Read documentation: $ClaudePath\CLAUDE.md"
    Write-Output "  2. Try a command: claude /analyze-security"
    Write-Output "  3. Use build flags: --prototype or --tdd"
    Write-Output ""

    if (-not $SkipMcp) {
        Write-ColorOutput "MCP Tools configured:" -Color $Colors.Yellow
        Write-Output "  • sequential-thinking - Complex analysis workflows"
        Write-Output "  • grep - GitHub repository code search"
        Write-Output ""
    }

    Write-ColorOutput "For help and support:" -Color $Colors.Yellow
    Write-Output "  • Documentation: $ClaudePath\README.md"
    Write-Output "  • Log file: $LOG_FILE"
    Write-Output ""
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Initialize logging
Write-Log "Starting Claude Code Workflows installation v$VERSION"
Write-Log "Command line: $($MyInvocation.Line)"

# Main installation process
try {
    Write-ColorOutput "Claude Code Workflows Installer v$VERSION" -Color $Colors.Green
    Write-ColorOutput "===========================================" -Color $Colors.Green
    Write-Output ""

    # Resolve target path
    $resolvedTargetPath = Resolve-TargetPath $TargetPath
    $claudePath = Join-Path $resolvedTargetPath ".claude"

    Write-ColorOutput "Target directory: $resolvedTargetPath" -Color $Colors.Yellow
    Write-ColorOutput "Installation path: $claudePath" -Color $Colors.Yellow
    Write-Output ""

    # Check write permissions
    if (-not (Test-WritePermissions $resolvedTargetPath)) {
        Write-ColorOutput "[ERROR] No write permission for: $resolvedTargetPath" -Color $Colors.Red
        Write-Log "No write permissions for target path: $resolvedTargetPath" -Level "ERROR"
        exit 1
    }

    # Check prerequisites
    Test-Prerequisites

    # Backup existing installation if present
    $backupPath = Backup-ExistingInstallation $claudePath

    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Installation preview completed" -Color $Colors.Blue
        Write-Output "All operations would succeed. Run without -DryRun to perform actual installation."
        exit 0
    }

    # Copy workflow files
    Copy-WorkflowFiles $claudePath

    # Install Python dependencies
    Install-PythonDependencies

    # Install MCP tools
    Install-McpTools $claudePath

    # Verify installation
    if (Test-Installation $claudePath) {
        Show-CompletionMessage $claudePath $backupPath
        Write-Log "Installation completed successfully"
    } else {
        Write-ColorOutput "[ERROR] Installation verification failed" -Color $Colors.Red
        Write-Log "Installation verification failed" -Level "ERROR"
        exit 1
    }

} catch {
    Write-ColorOutput "[ERROR] Installation failed: $($_.Exception.Message)" -Color $Colors.Red
    Write-Log "Installation failed: $($_.Exception.Message)" -Level "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" -Level "ERROR"
    exit 1
}
