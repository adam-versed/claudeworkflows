#!/usr/bin/env python3
"""
Cross-platform system dependency checker for development monitoring setup.
Detects OS, package managers, and verifies monitoring tool availability.
"""

import os
import sys
import subprocess
import platform
import argparse
import json
from pathlib import Path

def detect_platform():
    """Detect the current platform and available package managers."""
    system = platform.system().lower()
    
    managers = []
    
    if system == "darwin":  # macOS
        if subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
            managers.append("brew")
        if subprocess.run(["which", "port"], capture_output=True).returncode == 0:
            managers.append("macports")
    elif system == "linux":
        if subprocess.run(["which", "apt"], capture_output=True).returncode == 0:
            managers.append("apt")
        if subprocess.run(["which", "yum"], capture_output=True).returncode == 0:
            managers.append("yum")
        if subprocess.run(["which", "dnf"], capture_output=True).returncode == 0:
            managers.append("dnf")
        if subprocess.run(["which", "pacman"], capture_output=True).returncode == 0:
            managers.append("pacman")
        if subprocess.run(["which", "zypper"], capture_output=True).returncode == 0:
            managers.append("zypper")
    elif system == "windows":
        if subprocess.run(["where", "choco"], capture_output=True, shell=True).returncode == 0:
            managers.append("chocolatey")
        if subprocess.run(["where", "winget"], capture_output=True, shell=True).returncode == 0:
            managers.append("winget")
        if subprocess.run(["where", "scoop"], capture_output=True, shell=True).returncode == 0:
            managers.append("scoop")
    
    return {
        "platform": system,
        "package_managers": managers
    }

def check_monitoring_dependencies():
    """Check for monitoring-related system dependencies."""
    dependencies = {
        "required": {
            "make": "Build automation tool",
            "python3": "Python interpreter for scripts",
            "node": "Node.js runtime (if Node.js project detected)",
            "git": "Version control system"
        },
        "monitoring": {
            "watchexec": "File watching for auto-reload",
            "htop": "Process monitoring",
            "curl": "HTTP health checks", 
            "jq": "JSON processing for log analysis"
        },
        "optional": {
            "docker": "Container monitoring",
            "docker-compose": "Multi-service orchestration",
            "tmux": "Terminal multiplexing for service management",
            "screen": "Terminal session management"
        }
    }
    
    results = {
        "required": {},
        "monitoring": {},
        "optional": {}
    }
    
    for category, deps in dependencies.items():
        for tool, description in deps.items():
            try:
                if platform.system().lower() == "windows":
                    cmd = ["where", tool]
                    result = subprocess.run(cmd, capture_output=True, shell=True)
                else:
                    cmd = ["which", tool]
                    result = subprocess.run(cmd, capture_output=True)
                
                available = result.returncode == 0
                results[category][tool] = {
                    "available": available,
                    "description": description,
                    "path": result.stdout.decode().strip() if available else None
                }
            except Exception as e:
                results[category][tool] = {
                    "available": False,
                    "description": description,
                    "error": str(e)
                }
    
    return results

def generate_installation_commands(platform_info, missing_deps):
    """Generate installation commands for missing dependencies."""
    platform = platform_info["platform"]
    managers = platform_info["package_managers"]
    
    commands = []
    
    if not managers:
        return ["No package manager detected. Manual installation required."]
    
    primary_manager = managers[0]  # Use first available manager
    
    # Map package names across different managers
    package_maps = {
        "brew": {
            "make": "make",
            "python3": "python@3.11",
            "node": "node",
            "git": "git",
            "watchexec": "watchexec",
            "htop": "htop",
            "curl": "curl",
            "jq": "jq",
            "docker": "docker",
            "docker-compose": "docker-compose",
            "tmux": "tmux",
            "screen": "screen"
        },
        "apt": {
            "make": "build-essential",
            "python3": "python3",
            "node": "nodejs npm",
            "git": "git",
            "watchexec": "watchexec",
            "htop": "htop",
            "curl": "curl",
            "jq": "jq",
            "docker": "docker.io",
            "docker-compose": "docker-compose",
            "tmux": "tmux",
            "screen": "screen"
        },
        "yum": {
            "make": "make gcc",
            "python3": "python3",
            "node": "nodejs npm",
            "git": "git",
            "htop": "htop",
            "curl": "curl",
            "jq": "jq",
            "docker": "docker",
            "tmux": "tmux",
            "screen": "screen"
        },
        "chocolatey": {
            "make": "make",
            "python3": "python3",
            "node": "nodejs",
            "git": "git",
            "curl": "curl",
            "jq": "jq",
            "docker": "docker-desktop",
            "tmux": "msys2"
        }
    }
    
    package_map = package_maps.get(primary_manager, {})
    
    for dep in missing_deps:
        package_name = package_map.get(dep, dep)
        if primary_manager == "brew":
            commands.append(f"brew install {package_name}")
        elif primary_manager == "apt":
            commands.append(f"sudo apt update && sudo apt install -y {package_name}")
        elif primary_manager in ["yum", "dnf"]:
            commands.append(f"sudo {primary_manager} install -y {package_name}")
        elif primary_manager == "chocolatey":
            commands.append(f"choco install {package_name}")
        elif primary_manager == "winget":
            commands.append(f"winget install {package_name}")
        else:
            commands.append(f"# Install {dep} using {primary_manager}")
    
    return commands

def main():
    parser = argparse.ArgumentParser(description="Check system dependencies for monitoring setup")
    parser.add_argument("--monitoring", action="store_true", help="Include monitoring-specific tools")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--install-commands", action="store_true", help="Generate installation commands")
    
    args = parser.parse_args()
    
    # Detect platform and package managers
    platform_info = detect_platform()
    
    # Check dependencies
    dep_results = check_monitoring_dependencies()
    
    # Identify missing dependencies
    missing_required = []
    missing_monitoring = []
    missing_optional = []
    
    for tool, info in dep_results["required"].items():
        if not info["available"]:
            missing_required.append(tool)
    
    if args.monitoring:
        for tool, info in dep_results["monitoring"].items():
            if not info["available"]:
                missing_monitoring.append(tool)
        
        for tool, info in dep_results["optional"].items():
            if not info["available"]:
                missing_optional.append(tool)
    
    # Generate results
    results = {
        "platform": platform_info,
        "dependencies": dep_results,
        "missing": {
            "required": missing_required,
            "monitoring": missing_monitoring,
            "optional": missing_optional
        }
    }
    
    if args.install_commands:
        all_missing = missing_required + missing_monitoring + missing_optional
        results["installation_commands"] = generate_installation_commands(platform_info, all_missing)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Human-readable output
        print(f"Platform: {platform_info['platform']}")
        print(f"Package Managers: {', '.join(platform_info['package_managers']) if platform_info['package_managers'] else 'None detected'}")
        print()
        
        if missing_required:
            print("Missing Required Dependencies:")
            for dep in missing_required:
                print(f"  - {dep}: {dep_results['required'][dep]['description']}")
            print()
        
        if args.monitoring and missing_monitoring:
            print("Missing Monitoring Tools:")
            for dep in missing_monitoring:
                print(f"  - {dep}: {dep_results['monitoring'][dep]['description']}")
            print()
        
        if args.monitoring and missing_optional:
            print("Missing Optional Tools:")
            for dep in missing_optional:
                print(f"  - {dep}: {dep_results['optional'][dep]['description']}")
            print()
        
        if args.install_commands and "installation_commands" in results:
            print("Installation Commands:")
            for cmd in results["installation_commands"]:
                print(f"  {cmd}")
    
    # Exit with error code if required dependencies are missing
    return 1 if missing_required else 0

if __name__ == "__main__":
    sys.exit(main())