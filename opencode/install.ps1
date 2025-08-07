# AI Assisted Workflows Installation Script for Windows
# Installs the complete workflow system with agents, scripts, and dependencies

param(
    [Parameter(Position=0)]
    [string]$TargetPath = "",

    [switch]$Help,
    [switch]$Verbose,
    [switch]$DryRun,
    [switch]$SkipPython
)

# Script configuration
$VERSION = "1.0.0"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$LOG_FILE = "$env:TEMP\opencode-workflows-install.log"

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
    Write-ColorOutput "AI Assisted Workflows Installer v$VERSION" -Color $Colors.Green
    Write-Output ""
    Write-Output "USAGE:"
    Write-Output "    .\install.ps1 [TARGET_PATH] [OPTIONS]"
    Write-Output ""
    Write-Output "ARGUMENTS:"
    Write-Output "    TARGET_PATH     Directory where .opencode\ will be created"
    Write-Output "                   Examples:"
    Write-Output "                     ~\.config\opencode    (User global: ~\.config\opencode\)"
    Write-Output "                     .\myproject           (Project local: .\myproject\.opencode\)"
    Write-Output "                     C:\path\to\project    (Custom path: C:\path\to\project\.opencode\)"
    Write-Output "                   Default: current directory"
    Write-Output ""
    Write-Output "OPTIONS:"
    Write-Output "    -Help           Show this help message"
    Write-Output "    -Verbose        Enable verbose output"
    Write-Output "    -DryRun         Show what would be done without making changes"
    Write-Output "    -SkipPython     Skip Python dependencies installation"
    Write-Output ""
    Write-Output "EXAMPLES:"
    Write-Output "    # Install in current project (creates .\.opencode\)"
    Write-Output "    .\install.ps1"
    Write-Output ""
    Write-Output "    # Install globally for user (creates ~\.config\opencode\)"
    Write-Output "    .\install.ps1 ~\.config\opencode"
    Write-Output ""
    Write-Output "    # Install in specific project"
    Write-Output "    .\install.ps1 C:\path\to\my-project"
    Write-Output ""
    Write-Output "    # Dry run to see what would happen"
    Write-Output "    .\install.ps1 -DryRun"
    Write-Output ""
    Write-Output "REQUIREMENTS:"
    Write-Output "    - Python 3.7+"
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
        $resolvedPath = Join-Path $env:USERPROFILE ".config\opencode"
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
    param([string]$OpenCodePath)

    if (Test-Path $OpenCodePath) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = "$OpenCodePath.backup.$timestamp"

        Write-ColorOutput "Existing .opencode directory found" -Color $Colors.Yellow

        if ($DryRun) {
            Write-ColorOutput "[DRY RUN] Would backup existing installation to: $backupPath" -Color $Colors.Blue
            return $backupPath
        }

        Write-Output "Creating backup of existing installation..."
        Copy-Item -Path $OpenCodePath -Destination $backupPath -Recurse -Force
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

    # Scripts are now in shared/lib/scripts
    $sharedScriptsDir = Join-Path (Split-Path $SCRIPT_DIR -Parent) "shared\lib\scripts"
    $setupDir = Join-Path $sharedScriptsDir "setup"
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


function Copy-WorkflowFiles {
    param([string]$OpenCodePath)

    Write-Output ""
    Write-ColorOutput "Copying workflow files..." -Color $Colors.Yellow
    Write-Log "Starting workflow files copy"

    # Source directory is the script directory itself
    $sourceOpenCodeDir = $SCRIPT_DIR

    if (-not (Test-Path $sourceOpenCodeDir)) {
        Write-ColorOutput "[ERROR] Source opencode directory not found: $sourceOpenCodeDir" -Color $Colors.Red
        Write-Log "Source opencode directory not found: $sourceOpenCodeDir" -Level "ERROR"
        exit 1
    }

    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Would copy workflow files from: $sourceOpenCodeDir" -Color $Colors.Blue
        Write-ColorOutput "[DRY RUN] Would copy to: $OpenCodePath" -Color $Colors.Blue
        return
    }

    try {
        # Create target directory
        if (-not (Test-Path $OpenCodePath)) {
            New-Item -ItemType Directory -Path $OpenCodePath -Force | Out-Null
        }

        # Copy all files and directories, excluding docs folder and install scripts
        $items = Get-ChildItem $sourceOpenCodeDir -Recurse | Where-Object {
            $relativePath = [System.IO.Path]::GetRelativePath($sourceOpenCodeDir, $_.FullName)
            -not ($relativePath -like "docs\*" -or $relativePath -eq "docs" -or $relativePath -eq "install.sh" -or $relativePath -eq "install.ps1")
        }
        foreach ($item in $items) {
            $relativePath = [System.IO.Path]::GetRelativePath($sourceOpenCodeDir, $item.FullName)
            $targetPath = Join-Path $OpenCodePath $relativePath
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

        # Copy scripts from shared/lib to root of OpenCodePath
        $sharedScriptsDir = Join-Path (Split-Path $SCRIPT_DIR -Parent) "shared\lib\scripts"
        if (Test-Path $sharedScriptsDir) {
            $targetScriptsDir = Join-Path $OpenCodePath "scripts"
            Write-Log "Copying scripts from shared/lib/scripts to $targetScriptsDir"
            Copy-Item -Path $sharedScriptsDir -Destination $targetScriptsDir -Recurse -Force
        }

        # Copy formatter from shared/config to root of OpenCodePath
        $sharedFormatterDir = Join-Path (Split-Path $SCRIPT_DIR -Parent) "shared\config\formatter"
        if (Test-Path $sharedFormatterDir) {
            $targetFormatterDir = Join-Path $OpenCodePath "formatter"
            Write-Log "Copying formatter from shared/config/formatter to $targetFormatterDir"
            Copy-Item -Path $sharedFormatterDir -Destination $targetFormatterDir -Recurse -Force
        }

        # Create installation log
        $installLog = Join-Path $OpenCodePath "installation-log.txt"
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $pythonStatus = if ($SkipPython) { "Skipped" } else { "Installed" }
        @"
AI Assisted Workflows Installation Log
======================================
Installation Date: $timestamp
Installer Version: $VERSION
Target Path: $OpenCodePath
Python Dependencies: $pythonStatus
"@ | Set-Content -Path $installLog

        Write-ColorOutput "[OK] Workflow files copied successfully" -Color $Colors.Green
        Write-Log "Workflow files copied successfully to: $OpenCodePath"

    } catch {
        Write-ColorOutput "[ERROR] Error copying workflow files: $($_.Exception.Message)" -Color $Colors.Red
        Write-Log "Error copying workflow files: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}

function Test-Installation {
    param([string]$OpenCodePath)

    Write-Output ""
    Write-ColorOutput "Verifying installation..." -Color $Colors.Yellow
    Write-Log "Starting installation verification"

    $errors = 0

    # Check main directories
    $requiredDirs = @("agent", "scripts", "mode", "instructions")
    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $OpenCodePath $dir
        if (Test-Path $dirPath) {
            Write-ColorOutput "[OK] Directory $dir found" -Color $Colors.Green
        } else {
            Write-ColorOutput "[ERROR] Directory $dir missing" -Color $Colors.Red
            $errors++
        }
    }

    # Check key files
    $requiredFiles = @("agents.md", "opencode.json")
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $OpenCodePath $file
        if (Test-Path $filePath) {
            Write-ColorOutput "[OK] File $file found" -Color $Colors.Green
        } else {
            Write-ColorOutput "[WARNING] File $file missing" -Color $Colors.Yellow
        }
    }

    # Count agent files
    $agentsPath = Join-Path $OpenCodePath "agent"
    if (Test-Path $agentsPath) {
        $agentCount = (Get-ChildItem $agentsPath -Filter "*.md" | Measure-Object).Count
        Write-ColorOutput "[INFO] Agents found: $agentCount" -Color $Colors.Green
    }

    # Count script files
    $scriptsPath = Join-Path $OpenCodePath "scripts"
    if (Test-Path $scriptsPath) {
        $scriptCount = (Get-ChildItem $scriptsPath -Filter "*.py" -Recurse | Measure-Object).Count
        Write-ColorOutput "[INFO] Python scripts found: $scriptCount" -Color $Colors.Green
    }

    # Count mode files
    $modesPath = Join-Path $OpenCodePath "mode"
    if (Test-Path $modesPath) {
        $modeCount = (Get-ChildItem $modesPath -Filter "*.md" | Measure-Object).Count
        Write-ColorOutput "[INFO] Modes found: $modeCount" -Color $Colors.Green
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
    param([string]$OpenCodePath, [string]$BackupPath)

    Write-Output ""
    Write-ColorOutput "==================================" -Color $Colors.Green
    Write-ColorOutput "Installation completed successfully!" -Color $Colors.Green
    Write-ColorOutput "==================================" -Color $Colors.Green
    Write-Output ""

    Write-ColorOutput "AI Assisted Workflows v$VERSION installed to:" -Color $Colors.Yellow
    Write-Output "  $OpenCodePath"
    Write-Output ""

    if ($BackupPath) {
        Write-ColorOutput "Previous installation backed up to:" -Color $Colors.Yellow
        Write-Output "  $BackupPath"
        Write-Output ""
    }

    Write-ColorOutput "Available agents:" -Color $Colors.Yellow
    $agentsPath = Join-Path $OpenCodePath "agent"
    if (Test-Path $agentsPath) {
        $agents = Get-ChildItem $agentsPath -Filter "*.md" | ForEach-Object { $_.BaseName }
        $agentCount = $agents.Count
        Write-Output "  Total agents: $agentCount"
        foreach ($agent in $agents | Select-Object -First 5) {
            Write-Output "  • $agent"
        }
        if ($agentCount -gt 5) {
            Write-Output "  • ... and $($agentCount - 5) more"
        }
    }
    Write-Output ""

    Write-ColorOutput "Configuration files:" -Color $Colors.Yellow
    Write-Output "  • agents.md: $OpenCodePath\agents.md"
    Write-Output "  • opencode.json: $OpenCodePath\opencode.json"
    Write-Output ""

    Write-ColorOutput "Next steps:" -Color $Colors.Yellow
    Write-Output "  1. Agents are available through the Task tool in OpenCode"
    Write-Output "  2. Configure agents in opencode.json or via markdown files"
    Write-Output "  3. Use build flags: --prototype or --tdd"
    Write-Output ""

    Write-ColorOutput "For help and support:" -Color $Colors.Yellow
    Write-Output "  • View agents: ls $OpenCodePath\agent\"
    Write-Output "  • View modes: ls $OpenCodePath\mode\"
    Write-Output "  • Log file: $LOG_FILE"
    Write-Output ""
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Initialize logging
Write-Log "Starting AI Assisted Workflows installation v$VERSION"
Write-Log "Command line: $($MyInvocation.Line)"

# Main installation process
try {
    Write-ColorOutput "AI Assisted Workflows Installer v$VERSION" -Color $Colors.Green
    Write-ColorOutput "===========================================" -Color $Colors.Green
    Write-Output ""

    # Resolve target path and handle OpenCode path logic
    $resolvedTargetPath = Resolve-TargetPath $TargetPath

    # Apply the same logic as bash script for path handling
    if ($resolvedTargetPath -match "\\\.opencode$" -or $resolvedTargetPath -match "\\opencode$") {
        # User already specified opencode in the path
        $opencodePath = $resolvedTargetPath
        Write-Log "Target path already ends with opencode directory, using it directly"
    } else {
        # Append .opencode to the path for project installations
        $opencodePath = Join-Path $resolvedTargetPath ".opencode"
        Write-Log "Appending .opencode to target path"
    }

    Write-ColorOutput "Target directory: $resolvedTargetPath" -Color $Colors.Yellow
    Write-ColorOutput "Installation path: $opencodePath" -Color $Colors.Yellow
    Write-Output ""

    # Check write permissions
    if (-not (Test-WritePermissions $resolvedTargetPath)) {
        Write-ColorOutput "[ERROR] No write permission for: $resolvedTargetPath" -Color $Colors.Red
        Write-Log "No write permissions for target path: $resolvedTargetPath" -Level "ERROR"
        exit 1
    }

    # Check prerequisites (only Python now, no MCP)
    Test-Prerequisites

    # Backup existing installation if present
    $backupPath = Backup-ExistingInstallation $opencodePath

    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Installation preview completed" -Color $Colors.Blue
        Write-Output "All operations would succeed. Run without -DryRun to perform actual installation."
        exit 0
    }

    # Copy workflow files
    Copy-WorkflowFiles $opencodePath

    # Install Python dependencies
    Install-PythonDependencies

    # Verify installation
    if (Test-Installation $opencodePath) {
        Show-CompletionMessage $opencodePath $backupPath
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
