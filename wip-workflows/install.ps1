# SuperCopilot Framework Installer Script for Windows
# Installs SuperCopilot workflow-driven development framework for GitHub Copilot

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$ProjectDirectory,
    
    [switch]$Force,
    [switch]$Update,
    [switch]$Uninstall,
    [switch]$InstallMcp,
    [switch]$DryRun,
    [switch]$Help
)

# Version
$VERSION = "1.0.0"

# Colors for output
$Colors = @{
    Green = [System.ConsoleColor]::Green
    Yellow = [System.ConsoleColor]::Yellow
    Red = [System.ConsoleColor]::Red
    Blue = [System.ConsoleColor]::Blue
    White = [System.ConsoleColor]::White
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

function Show-Usage {
    Write-ColorOutput "SuperCopilot Framework Installer v$VERSION" -Color $Colors.Green
    Write-Output "Switch-based AI development with minimal context and maximum capability"
    Write-Output ""
    Write-Output "Usage: .\install.ps1 <project_directory> [OPTIONS]"
    Write-Output ""
    Write-Output "Arguments:"
    Write-Output "  <project_directory>      Target project directory to install SuperCopilot"
    Write-Output ""
    Write-Output "Options:"
    Write-Output "  -Force                   Skip confirmation prompts (for automation)"
    Write-Output "  -Update                  Update existing installation (preserves customisations)"
    Write-Output "  -Uninstall               Remove SuperCopilot from specified directory"
    Write-Output "  -InstallMcp              Install and configure MCP tools in VS Code"
    Write-Output "  -DryRun                  Show what would be done without making changes"
    Write-Output "  -Help                    Show this help message"
    Write-Output ""
    Write-Output "Examples:"
    Write-Output "  .\install.ps1 C:\path\to\my-project                    # Install to my-project"
    Write-Output "  .\install.ps1 .\my-app -Force                         # Install without prompts"
    Write-Output "  .\install.ps1 C:\opt\project -Update                   # Update existing installation"
    Write-Output "  .\install.ps1 C:\dev\app -Uninstall                    # Remove SuperCopilot"
    Write-Output "  .\install.ps1 .\test-project -DryRun                   # Preview installation"
    Write-Output ""
    Write-Output "Features:"
    Write-Output "  • Specialized Chat Modes for VS Code with GitHub Copilot"
    Write-Output "  • Structured workflows for rapid prototyping and PRD creation"
    Write-Output "  • MCP tool integration for enhanced capabilities"
    Write-Output "  • Prerequisites validation (Node.js, MCP servers)"
}

function Test-SuperCopilotDirectory {
    # Check if we're in the SuperCopilot directory
    $requiredFiles = @("README.md", "github\chatmodes", "github\copilot-instructions.md")
    $missingFiles = @()
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-ColorOutput "Error: This script must be run from the SuperCopilot directory" -Color $Colors.Red
        Write-Output ""
        Write-Output "Expected files not found. Please ensure you are in the root SuperCopilot directory."
        Write-Output "Missing: $($missingFiles -join ', ')"
        Write-Output ""
        Write-Output "Solution: cd to the SuperCopilot directory and run: .\install.ps1 <target_directory>"
        exit 1
    }
}

function Test-Prerequisites {
    Write-Output ""
    Write-Output "Checking prerequisites for SuperCopilot framework..."
    
    $errors = 0
    
    # Check Node.js (required for MCP servers)
    if (Get-Command node -ErrorAction SilentlyContinue) {
        try {
            $nodeVersion = (& node --version).TrimStart('v')
            $nodeMajor = [int]($nodeVersion.Split('.')[0])
            if ($nodeMajor -ge 14) {
                Write-ColorOutput "[OK] Node.js $nodeVersion found" -Color $Colors.Green
            } else {
                Write-ColorOutput "[ERROR] Node.js $nodeVersion found, but 14+ required" -Color $Colors.Red
                Write-Output "  Install: https://nodejs.org"
                $errors++
            }
        } catch {
            Write-ColorOutput "[ERROR] Node.js version check failed" -Color $Colors.Red
            Write-Output "  Install: https://nodejs.org"
            $errors++
        }
    } else {
        Write-ColorOutput "[ERROR] Node.js not found" -Color $Colors.Red
        Write-Output "  Install: https://nodejs.org"
        $errors++
    }
    
    # Check for MCP tools in VS Code settings
    $settingsPath = "$env:APPDATA\Code\User\settings.json"
    
    if (Test-Path $settingsPath) {
        try {
            $settingsContent = Get-Content -Path $settingsPath -Raw
            $settings = $settingsContent | ConvertFrom-Json
            
            $context7Configured = $false
            $sequentialConfigured = $false
            
            if ($settings.mcp -and $settings.mcp.servers) {
                $context7Configured = $settings.mcp.servers.PSObject.Properties.Name -contains "context7"
                $sequentialConfigured = $settings.mcp.servers.PSObject.Properties.Name -contains "sequential-thinking"
            }
            
            if ($context7Configured) {
                Write-ColorOutput "[OK] Context7 MCP Server configured" -Color $Colors.Green
            } else {
                Write-ColorOutput "[INFO] Context7 MCP Server not configured" -Color $Colors.Yellow
                Write-Output "  Configure with: .\install.ps1 <dir> -InstallMcp"
            }
            
            if ($sequentialConfigured) {
                Write-ColorOutput "[OK] Sequential Thinking MCP Server configured" -Color $Colors.Green
            } else {
                Write-ColorOutput "[INFO] Sequential Thinking MCP Server not configured" -Color $Colors.Yellow
                Write-Output "  Configure with: .\install.ps1 <dir> -InstallMcp"
            }
        } catch {
            Write-ColorOutput "[INFO] VS Code settings found but could not parse - MCP tools not configured" -Color $Colors.Yellow
            Write-Output "  Configure with: .\install.ps1 <dir> -InstallMcp"
        }
    } else {
        Write-ColorOutput "[INFO] VS Code settings not found - MCP tools not configured" -Color $Colors.Yellow
        Write-Output "  Configure with: .\install.ps1 <dir> -InstallMcp (after VS Code setup)"
    }
    
    # Block installation if prerequisites missing
    if ($errors -gt 0) {
        Write-Output ""
        Write-ColorOutput "[ERROR] Installation blocked: $errors prerequisite(s) missing" -Color $Colors.Red
        Write-Output ""
        Write-Output "Please install missing prerequisites and run again."
        Write-Output "See README.md Prerequisites section for details."
        exit 1
    }
    
    Write-Output ""
    Write-ColorOutput "[OK] All prerequisites satisfied" -Color $Colors.Green
}

function Install-McpTools {
    Write-Output ""
    Write-Output "Installing MCP tools for VS Code..."
    
    # Get current user
    $userId = $env:USERNAME
    Write-Output "[INFO] Detected user: $userId"
    
    # Define VS Code settings path for Windows
    $settingsPath = "$env:APPDATA\Code\User\settings.json"
    Write-Output "[INFO] VS Code settings path: $settingsPath"
    
    # Check if settings.json exists
    if (-not (Test-Path $settingsPath)) {
        Write-ColorOutput "[ERROR] VS Code settings.json not found at $settingsPath" -Color $Colors.Red
        Write-Output "   Please ensure VS Code is installed and has been run at least once."
        return $false
    }
    
    # Backup existing settings
    Write-Output "[INFO] Creating backup of existing settings..."
    $backupPath = "$settingsPath.backup.$((Get-Date).ToString('yyyyMMdd_HHmmss'))"
    Copy-Item -Path $settingsPath -Destination $backupPath
    
    try {
        # Read and parse existing settings
        $settingsContent = Get-Content -Path $settingsPath -Raw
        $settings = $settingsContent | ConvertFrom-Json
        
        # Check if MCP tools are already configured
        $context7Configured = $false
        $sequentialConfigured = $false
        
        if ($settings.mcp -and $settings.mcp.servers) {
            $context7Configured = $settings.mcp.servers.PSObject.Properties.Name -contains "context7"
            $sequentialConfigured = $settings.mcp.servers.PSObject.Properties.Name -contains "sequential-thinking"
        }
        
        if ($context7Configured -and $sequentialConfigured) {
            Write-ColorOutput "[WARNING] Both MCP tools are already configured in settings.json" -Color $Colors.Yellow
            return $true
        }
        
        # Ensure mcp structure exists
        if (-not $settings.mcp) {
            $settings | Add-Member -NotePropertyName "mcp" -NotePropertyValue ([PSCustomObject]@{})
        }
        if (-not $settings.mcp.servers) {
            $settings.mcp | Add-Member -NotePropertyName "servers" -NotePropertyValue ([PSCustomObject]@{})
        }
        if (-not $settings.mcp.inputs) {
            $settings.mcp | Add-Member -NotePropertyName "inputs" -NotePropertyValue @()
        }
        
            # Add Context7 if not present
        if (-not $context7Configured) {
            $context7Config = [PSCustomObject]@{
                command = "npx"
                args = @("-y", "@upstash/context7-mcp")
                env = [PSCustomObject]@{}
            }
            $settings.mcp.servers | Add-Member -NotePropertyName "context7" -NotePropertyValue $context7Config
            Write-ColorOutput "✅ Added Context7 MCP server configuration" -Color $Colors.Green
        }
        
            # Add Sequential Thinking if not present
        if (-not $sequentialConfigured) {
            $sequentialConfig = [PSCustomObject]@{
                command = "npx"
                args = @("-y", "@modelcontextprotocol/server-sequential-thinking")
                env = [PSCustomObject]@{}
            }
            $settings.mcp.servers | Add-Member -NotePropertyName "sequential-thinking" -NotePropertyValue $sequentialConfig
            Write-ColorOutput "✅ Added Sequential Thinking MCP server configuration" -Color $Colors.Green
        }
        
        # Write updated settings back to file
        $settings | ConvertTo-Json -Depth 10 | Set-Content -Path $settingsPath
        
        Write-Output ""
        Write-ColorOutput "[SUCCESS] MCP tools installation completed successfully!" -Color $Colors.Green
        Write-Output ""
        Write-Output "[INFO] Next steps:"
        Write-Output "   1. Restart VS Code completely"
        Write-Output "   2. The MCP tools should now be available in your chat interface"
        Write-Output "   3. Test with documentation queries and complex problem analysis"
        
        return $true
        
    } catch {
        Write-ColorOutput "[ERROR] Error installing MCP tools: $($_.Exception.Message)" -Color $Colors.Red
        # Restore backup if something went wrong
        if (Test-Path $backupPath) {
            Copy-Item -Path $backupPath -Destination $settingsPath -Force
            Write-Output "   Settings restored from backup"
        }
        return $false
    }
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Remove trailing slash if present
$ProjectDirectory = $ProjectDirectory.TrimEnd('\', '/')

# Convert to absolute path if relative
if (-not [System.IO.Path]::IsPathRooted($ProjectDirectory)) {
    $ProjectDirectory = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $ProjectDirectory))
}

# Create target directory if it doesn't exist
if (-not (Test-Path $ProjectDirectory)) {
    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Would create directory: $ProjectDirectory" -Color $Colors.Blue
    } else {
        Write-ColorOutput "Creating project directory: $ProjectDirectory" -Color $Colors.Yellow
        New-Item -ItemType Directory -Path $ProjectDirectory -Force | Out-Null
    }
}

# SuperCopilot target path
$SuperCopilotDir = Join-Path $ProjectDirectory ".github"

# Handle uninstall mode
if ($Uninstall) {
    Write-ColorOutput "SuperCopilot Framework Uninstaller" -Color $Colors.Green
    Write-Output "===================================="
    Write-ColorOutput "Target directory: $ProjectDirectory" -Color $Colors.Yellow
    Write-Output ""
    
    if (-not (Test-Path $SuperCopilotDir)) {
        Write-ColorOutput "Error: SuperCopilot not found at $ProjectDirectory" -Color $Colors.Red
        exit 1
    }
    
    # Check if it's actually SuperCopilot
    $instructionsFile = Join-Path $SuperCopilotDir "copilot-instructions.md"
    if (-not (Test-Path $instructionsFile) -or -not (Select-String -Path $instructionsFile -Pattern "SuperCopilot" -Quiet)) {
        Write-ColorOutput "Error: Directory doesn't appear to contain SuperCopilot" -Color $Colors.Red
        exit 1
    }
    
    if (-not $Force) {
        Write-ColorOutput "This will remove SuperCopilot from $ProjectDirectory" -Color $Colors.Yellow
        $confirmUninstall = Read-Host "Are you sure you want to continue? (y/n)"
        if ($confirmUninstall -ne "y") {
            Write-Output "Uninstall cancelled."
            exit 0
        }
    }
    
    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Would remove SuperCopilot files from: $SuperCopilotDir" -Color $Colors.Blue
    } else {
        Write-Output "Removing SuperCopilot..."
        Remove-Item -Path $SuperCopilotDir -Recurse -Force
        Write-ColorOutput "[SUCCESS] SuperCopilot uninstalled successfully!" -Color $Colors.Green
    }
    exit 0
}

Write-ColorOutput "SuperCopilot Framework Installer v$VERSION" -Color $Colors.Green
Write-Output "=============================================="
Write-ColorOutput "Target project: $ProjectDirectory" -Color $Colors.Yellow
Write-ColorOutput "Installation path: $SuperCopilotDir" -Color $Colors.Yellow
Write-ColorOutput "Framework: Switch-based Chat Modes with Just-In-Time Loading" -Color $Colors.Yellow
Write-Output ""

# Check write permissions
try {
    $testFile = Join-Path $ProjectDirectory "test_write_permissions.tmp"
    New-Item -ItemType File -Path $testFile -Force | Out-Null
    Remove-Item -Path $testFile -Force
} catch {
    Write-ColorOutput "Error: No write permission for $ProjectDirectory" -Color $Colors.Red
    exit 1
}

# Check prerequisites
Test-SuperCopilotDirectory
Test-Prerequisites

# Backup existing .github directory if it exists
$backupDir = ""
if ((Test-Path $SuperCopilotDir) -and ((Get-ChildItem $SuperCopilotDir -Force | Measure-Object).Count -gt 0)) {
    Write-ColorOutput "Existing .github directory found" -Color $Colors.Yellow
    
    if ($Update -or $Force) {
        $backupChoice = "y"
    } else {
        $backupChoice = Read-Host "Backup existing .github directory? (y/n)"
    }
    
    if ($backupChoice -eq "y") {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupDir = "$ProjectDirectory\.github.backup.$timestamp"
        
        if ($DryRun) {
            Write-ColorOutput "[DRY RUN] Would backup existing .github to: $backupDir" -Color $Colors.Blue
        } else {
            Write-Output "Backing up existing .github directory..."
            Copy-Item -Path $SuperCopilotDir -Destination $backupDir -Recurse -Force
            Write-ColorOutput "Backed up to: $backupDir" -Color $Colors.Green
        }
    }
} elseif (Test-Path $SuperCopilotDir) {
    Write-ColorOutput "Directory $SuperCopilotDir exists but is empty" -Color $Colors.Yellow
}

# Confirmation prompt (skip if -Force)
if (-not $Force -and -not $DryRun) {
    Write-Output ""
    if ($Update) {
        Write-ColorOutput "This will update SuperCopilot Framework in $ProjectDirectory" -Color $Colors.Yellow
    } else {
        Write-ColorOutput "This will install SuperCopilot Framework in $ProjectDirectory" -Color $Colors.Yellow
        Write-Output "Features: Specialized Chat Modes, Rapid Prototyping, PRD Creation, MCP Tool Integration"
    }
    $confirmInstall = Read-Host "Are you sure you want to continue? (y/n)"
    if ($confirmInstall -ne "y") {
        Write-Output "Installation cancelled."
        exit 0
    }
}

Write-Output ""
if ($Update) {
    Write-Output "Updating SuperCopilot Framework..."
} elseif ($DryRun) {
    Write-ColorOutput "DRY RUN: Showing what would be installed..." -Color $Colors.Blue
} else {
    Write-Output "Installing SuperCopilot Framework..."
}

# Create SuperCopilot directory structure
Write-Output "Creating SuperCopilot base directory..."
if ($DryRun) {
    Write-ColorOutput "[DRY RUN] Would create: $SuperCopilotDir\" -Color $Colors.Blue
} else {
    New-Item -ItemType Directory -Path $SuperCopilotDir -Force | Out-Null
}

# Copy entire github directory structure to .github
Write-Output "Copying SuperCopilot framework files..."
if ($DryRun) {
    Write-ColorOutput "[DRY RUN] Would copy: entire github\ directory to .github\ preserving structure" -Color $Colors.Blue
} else {
    if ($Update -and (Test-Path (Join-Path $SuperCopilotDir "copilot-instructions.md"))) {
        # In update mode, check if copilot-instructions.md was customized
        $sourceFile = "github\copilot-instructions.md"
        $targetFile = Join-Path $SuperCopilotDir "copilot-instructions.md"
        
        if ((Get-FileHash $sourceFile).Hash -ne (Get-FileHash $targetFile).Hash) {
            Write-Output "  Preserving customised copilot-instructions.md (new version: copilot-instructions.md.new)"
            # Copy everything except copilot-instructions.md
            $githubItems = Get-ChildItem "github" -Recurse
            foreach ($item in $githubItems) {
                if ($item.Name -ne "copilot-instructions.md" -or $item.Directory.Name -ne "github") {
                    $relativePath = $item.FullName.Substring((Resolve-Path "github").Path.Length + 1)
                    $targetPath = Join-Path $SuperCopilotDir $relativePath
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
            }
            Copy-Item -Path $sourceFile -Destination "$targetFile.new" -Force
        } else {
            # No customization, copy everything
            Copy-Item -Path "github\*" -Destination $SuperCopilotDir -Recurse -Force
        }
    } else {
        # Fresh install, copy everything
        Copy-Item -Path "github\*" -Destination $SuperCopilotDir -Recurse -Force
    }
}


# Copy documentation files
Write-Output "Copying documentation..."
if ($DryRun) {
    Write-ColorOutput "[DRY RUN] Would copy: README.md" -Color $Colors.Blue
} else {
    $docFiles = @("README.md")
    foreach ($file in $docFiles) {
        if (Test-Path $file) {
            Copy-Item -Path $file -Destination $SuperCopilotDir -Force -ErrorAction SilentlyContinue
        }
    }
}

# Copy scriptable workflows (if available)
if (Test-Path ".github\scripts") {
    Write-Output "Copying scriptable workflows..."
    if ($DryRun) {
        Write-ColorOutput "[DRY RUN] Would copy: .github\scripts directory" -Color $Colors.Blue
        Write-ColorOutput "[DRY RUN] Note: Windows uses file associations for Python scripts" -Color $Colors.Blue
    } else {
        Copy-Item -Path ".github\scripts" -Destination $SuperCopilotDir -Recurse -Force -ErrorAction SilentlyContinue
        
        # Windows note: No execute permissions needed, uses file association
        Write-Output "Python scripts ready (Windows uses file associations for execution)"
    }
}


# Check prerequisites before proceeding
if (-not $DryRun) {
    Test-Prerequisites
} elseif ($DryRun) {
    Write-Output ""
    Write-ColorOutput "[DRY RUN] Would check prerequisites (Python 3.8+, Node.js 18+, Lizard, MCP servers)" -Color $Colors.Blue
}

# Verify installation
if (-not $DryRun) {
    Write-Output ""
    Write-Output "Verifying installation..."

    # Count installed files
    $mainConfig = if (Test-Path (Join-Path $SuperCopilotDir "copilot-instructions.md")) { 1 } else { 0 }
    $chatmodeFiles = (Get-ChildItem (Join-Path $SuperCopilotDir "chatmodes") -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object).Count
    $instructionsFiles = (Get-ChildItem (Join-Path $SuperCopilotDir "instructions") -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object).Count

    Write-ColorOutput "Main config: $mainConfig (expected: 1)" -Color $Colors.Green
    Write-ColorOutput "Chat modes: $chatmodeFiles (expected: 3)" -Color $Colors.Green
    Write-ColorOutput "Instructions: $instructionsFiles (expected: 10)" -Color $Colors.Green

    # Calculate success criteria
    $successCriteria = ($mainConfig -ge 1) -and ($chatmodeFiles -ge 3) -and ($instructionsFiles -ge 10)

    if ($successCriteria) {
        Write-Output ""
        Write-ColorOutput "[SUCCESS] SuperCopilot Framework installed successfully!" -Color $Colors.Green
        Write-Output ""
        Write-ColorOutput "🚀 Getting Started:" -Color $Colors.Yellow
        Write-Output "  1. Open your project in VS Code with GitHub Copilot"
        Write-Output "  2. Select a chat mode from the dropdown"
        Write-Output "  3. Use MCP tools for enhanced capabilities"
        Write-Output "  4. Leverage structured workflows for rapid development"
        Write-Output "  5. Create prototypes and PRDs efficiently"
        Write-Output ""
        Write-ColorOutput "📖 Available Chat Modes:" -Color $Colors.Yellow
        Write-Output "  • prototype-web.chatmode.md - Web app rapid prototyping with 5-phase workflow"
        Write-Output "  • prototype-mobile.chatmode.md - Mobile app rapid prototyping with 6-phase workflow"
        Write-Output "  • ux-prd.chatmode.md - Product requirements documentation"
        Write-Output ""
        Write-ColorOutput "📝 File Creation Instructions:" -Color $Colors.Yellow
        Write-Output "  • 10 VS Code .instructions.md files for consistent web prototype patterns"
        Write-Output "  • Covers React components, pages, services, styling, and configuration"
        Write-Output ""
        Write-ColorOutput "🛠️ MCP Tools:" -Color $Colors.Yellow
        Write-Output "  • Context7 - Documentation lookup (install: npx @upstash/context7-mcp)"
        Write-Output "  • Sequential Thinking - Complex problem analysis (install: npx @modelcontextprotocol/server-sequential-thinking)"
        Write-Output ""
        if ($Update) {
            $newFiles = Get-ChildItem $SuperCopilotDir -Filter "*.new" -Recurse -ErrorAction SilentlyContinue
            if ($newFiles.Count -gt 0) {
                Write-ColorOutput "Updates available:" -Color $Colors.Yellow
                foreach ($file in $newFiles) {
                    Write-Output "  - $($file.FullName)"
                }
                Write-Output "Review: Compare-Object (Get-Content file) (Get-Content file.new)"
                Write-Output ""
            }
        }
        if ($backupDir -and (Test-Path $backupDir)) {
            Write-ColorOutput "Backup: $backupDir" -Color $Colors.Yellow
            Write-Output ""
        }
        Write-Output "Documentation: $SuperCopilotDir\README.md"
        
        # Install MCP tools if requested
        if ($InstallMcp) {
            Install-McpTools
        }
    } else {
        Write-Output ""
        Write-ColorOutput "[ERROR] Installation may be incomplete" -Color $Colors.Red
        Write-Output ""
        Write-Output "Component status:"
        Write-Output "  Main config: $mainConfig/1$(if ($mainConfig -lt 1) { ' [FAIL]' } else { ' [OK]' })"
        Write-Output "  Chat modes: $chatmodeFiles/3$(if ($chatmodeFiles -lt 3) { ' [FAIL]' } else { ' [OK]' })"
        Write-Output "  Instructions: $instructionsFiles/10$(if ($instructionsFiles -lt 10) { ' [FAIL]' } else { ' [OK]' })"
        Write-Output ""
        Write-Output "Debugging installation:"
        Write-Output "1. Check write permissions to $ProjectDirectory"
        Write-Output "2. Verify source files exist in current directory"
        Write-Output "3. Run from SuperCopilot root directory"
        Write-Output ""
        exit 1
    }
} else {
    Write-Output ""
    Write-ColorOutput "[SUCCESS] DRY RUN COMPLETE" -Color $Colors.Blue
    Write-Output "All operations would succeed. Run without -DryRun to perform actual installation."
}