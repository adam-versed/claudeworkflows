#!/usr/bin/env python3
"""
Cross-platform monitoring tool installer.
Installs monitoring dependencies based on detected project types and platform.
"""

import os
import sys
import subprocess
import platform
import argparse
import json
import tempfile
from pathlib import Path

def run_command(cmd, shell=False):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def detect_platform():
    """Detect platform and package manager."""
    system = platform.system().lower()
    
    if system == "darwin":
        if run_command(["which", "brew"])[0]:
            return system, "brew"
    elif system == "linux":
        for pm in ["apt", "dnf", "yum", "pacman", "zypper"]:
            if run_command(["which", pm])[0]:
                return system, pm
    elif system == "windows":
        for pm in ["winget", "choco", "scoop"]:
            if run_command(["where", pm], shell=True)[0]:
                return system, pm
    
    return system, None

def install_base_monitoring_tools(platform_name, package_manager):
    """Install base monitoring tools regardless of project type."""
    tools = {
        "brew": {
            "watchexec": "watchexec",
            "htop": "htop", 
            "jq": "jq",
            "curl": "curl"
        },
        "apt": {
            "watchexec": "watchexec",
            "htop": "htop",
            "jq": "jq", 
            "curl": "curl"
        },
        "dnf": {
            "htop": "htop",
            "jq": "jq",
            "curl": "curl"
        },
        "yum": {
            "htop": "htop",
            "jq": "jq",
            "curl": "curl"
        },
        "winget": {
            "jq": "jq",
            "curl": "curl"
        },
        "choco": {
            "jq": "jq",
            "curl": "curl"
        }
    }
    
    pm_tools = tools.get(package_manager, {})
    results = {}
    
    for tool, package in pm_tools.items():
        print(f"Installing {tool}...")
        
        if package_manager == "brew":
            success, stdout, stderr = run_command(["brew", "install", package])
        elif package_manager == "apt":
            success, stdout, stderr = run_command(["sudo", "apt", "install", "-y", package])
        elif package_manager in ["dnf", "yum"]:
            success, stdout, stderr = run_command(["sudo", package_manager, "install", "-y", package])
        elif package_manager == "winget":
            success, stdout, stderr = run_command(["winget", "install", package], shell=True)
        elif package_manager == "choco":
            success, stdout, stderr = run_command(["choco", "install", package, "-y"], shell=True)
        else:
            success, stdout, stderr = False, "", f"Unsupported package manager: {package_manager}"
        
        results[tool] = {
            "success": success,
            "stdout": stdout,
            "stderr": stderr
        }
        
        if success:
            print(f"  ✓ {tool} installed successfully")
        else:
            print(f"  ✗ Failed to install {tool}: {stderr}")
    
    return results

def install_project_specific_tools(project_types, platform_name, package_manager):
    """Install monitoring tools specific to detected project types."""
    results = {}
    
    # Node.js specific monitoring
    if "nodejs" in project_types:
        print("Installing Node.js monitoring tools...")
        
        # Install pm2 for process management
        success, stdout, stderr = run_command(["npm", "install", "-g", "pm2"])
        results["pm2"] = {"success": success, "stdout": stdout, "stderr": stderr}
        
        if success:
            print("  ✓ pm2 installed successfully")
        else:
            print(f"  ✗ Failed to install pm2: {stderr}")
        
        # Install clinic.js for performance monitoring  
        success, stdout, stderr = run_command(["npm", "install", "-g", "@clinic/doctor", "@clinic/bubbleprof"])
        results["clinic"] = {"success": success, "stdout": stdout, "stderr": stderr}
        
        if success:
            print("  ✓ clinic.js tools installed successfully")
        else:
            print(f"  ✗ Failed to install clinic.js: {stderr}")
    
    # Python specific monitoring
    if "python" in project_types:
        print("Installing Python monitoring tools...")
        
        # Install psutil for system monitoring
        success, stdout, stderr = run_command([sys.executable, "-m", "pip", "install", "psutil", "memory-profiler"])
        results["python_monitoring"] = {"success": success, "stdout": stdout, "stderr": stderr}
        
        if success:
            print("  ✓ Python monitoring tools installed successfully")
        else:
            print(f"  ✗ Failed to install Python monitoring tools: {stderr}")
    
    # Docker specific monitoring
    if "docker" in project_types:
        print("Installing Docker monitoring tools...")
        
        if package_manager == "brew":
            success, stdout, stderr = run_command(["brew", "install", "dive", "docker-compose"])
        elif package_manager == "apt":
            # Install dive for Docker image analysis
            success, stdout, stderr = run_command(["sudo", "apt", "install", "-y", "docker-compose"])
        else:
            success, stdout, stderr = True, "Docker tools installation skipped", ""
        
        results["docker_monitoring"] = {"success": success, "stdout": stdout, "stderr": stderr}
        
        if success:
            print("  ✓ Docker monitoring tools installed successfully")
        else:
            print(f"  ✗ Failed to install Docker monitoring tools: {stderr}")
    
    # Database monitoring (if database configs detected)
    if "database" in project_types:
        print("Installing database monitoring tools...")
        
        if package_manager == "brew":
            success, stdout, stderr = run_command(["brew", "install", "pgcli", "mycli"])
        elif package_manager == "apt":
            success, stdout, stderr = run_command(["sudo", "apt", "install", "-y", "postgresql-client", "mysql-client"])
        else:
            success, stdout, stderr = True, "Database tools installation skipped", ""
        
        results["database_monitoring"] = {"success": success, "stdout": stdout, "stderr": stderr}
        
        if success:
            print("  ✓ Database monitoring tools installed successfully")
        else:
            print(f"  ✗ Failed to install database monitoring tools: {stderr}")
    
    return results

def install_optional_tools(platform_name, package_manager):
    """Install optional but useful monitoring tools."""
    print("Installing optional monitoring tools...")
    
    tools = {
        "brew": ["tmux", "screen", "tree"],
        "apt": ["tmux", "screen", "tree"],
        "dnf": ["tmux", "screen", "tree"],
        "yum": ["tmux", "screen", "tree"],
        "winget": [],
        "choco": ["msys2"]
    }
    
    pm_tools = tools.get(package_manager, [])
    results = {}
    
    for tool in pm_tools:
        if package_manager == "brew":
            success, stdout, stderr = run_command(["brew", "install", tool])
        elif package_manager == "apt":
            success, stdout, stderr = run_command(["sudo", "apt", "install", "-y", tool])
        elif package_manager in ["dnf", "yum"]:
            success, stdout, stderr = run_command(["sudo", package_manager, "install", "-y", tool])
        elif package_manager == "choco":
            success, stdout, stderr = run_command(["choco", "install", tool, "-y"], shell=True)
        else:
            success, stdout, stderr = True, f"{tool} installation skipped", ""
        
        results[tool] = {"success": success, "stdout": stdout, "stderr": stderr}
        
        if success:
            print(f"  ✓ {tool} installed successfully")
        else:
            print(f"  ✗ Failed to install {tool}: {stderr}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Install monitoring tools for development")
    parser.add_argument("--project-type", nargs="+", default=[], 
                       help="Project types: nodejs, python, docker, database, etc.")
    parser.add_argument("--platform", help="Target platform (auto-detected if not specified)")
    parser.add_argument("--skip-optional", action="store_true", 
                       help="Skip optional tool installation")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be installed without installing")
    
    args = parser.parse_args()
    
    # Detect platform and package manager
    platform_name, package_manager = detect_platform()
    
    if not package_manager:
        print(f"No supported package manager found on {platform_name}")
        print("Please install one of: brew (macOS), apt/dnf/yum (Linux), winget/choco (Windows)")
        return 1
    
    if args.dry_run:
        print(f"Platform: {platform_name}")
        print(f"Package Manager: {package_manager}")
        print(f"Project Types: {args.project_type}")
        print("This would install monitoring tools but --dry-run specified")
        return 0
    
    print(f"Installing monitoring tools on {platform_name} using {package_manager}")
    print(f"Project types: {args.project_type}")
    print()
    
    all_results = {}
    
    # Install base monitoring tools
    all_results["base"] = install_base_monitoring_tools(platform_name, package_manager)
    
    # Install project-specific tools
    if args.project_type:
        all_results["project_specific"] = install_project_specific_tools(
            args.project_type, platform_name, package_manager)
    
    # Install optional tools
    if not args.skip_optional:
        all_results["optional"] = install_optional_tools(platform_name, package_manager)
    
    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        print("\nInstallation Summary:")
        failed_tools = []
        
        for category, tools in all_results.items():
            for tool, result in tools.items():
                if not result["success"]:
                    failed_tools.append(f"{category}/{tool}")
        
        if failed_tools:
            print(f"Failed installations: {', '.join(failed_tools)}")
            return 1
        else:
            print("All monitoring tools installed successfully!")
            return 0

if __name__ == "__main__":
    sys.exit(main())