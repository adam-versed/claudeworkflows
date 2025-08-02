#!/usr/bin/env python3
"""
Platform detection header for Claude Code Workflows analysis scripts.
Auto-detects Python command and sets up cross-platform execution.

Import this at the top of every analysis script to ensure cross-platform compatibility.
"""

import sys
import platform
from pathlib import Path


def setup_python_path():
    """Add utils directory to Python path for imports."""
    script_dir = Path(__file__).parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))


def get_platform_info():
    """Get platform information for debugging."""
    return {
        "system": platform.system(),
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "script_directory": str(Path(__file__).parent),
    }


def detect_python_command():
    """
    Detect the correct Python command for this platform.
    Returns the command that should be used to run Python scripts.
    Exits with critical error if Python is not found.
    """
    import subprocess

    # Current running interpreter
    current_python = sys.executable
    if current_python:
        return current_python

    # Try common Python commands
    for cmd in ["python3", "python"]:
        try:
            result = subprocess.run(
                [cmd, "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    # Critical blocking error - Python not found
    print("CRITICAL ERROR: Python not found on system", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "Claude Code Workflows scriptable analysis requires Python 3.8+",
        file=sys.stderr,
    )
    print("", file=sys.stderr)

    platform_name = platform.system()
    if platform_name == "Windows":
        print("Windows installation options:", file=sys.stderr)
        print("  1. Download from https://python.org/downloads/", file=sys.stderr)
        print("  2. Install from Microsoft Store: 'python'", file=sys.stderr)
        print(
            "  3. Use package manager: 'winget install Python.Python.3'",
            file=sys.stderr,
        )
    elif platform_name == "Darwin":  # macOS
        print("macOS installation options:", file=sys.stderr)
        print(
            "  1. Install Xcode Command Line Tools: 'xcode-select --install'",
            file=sys.stderr,
        )
        print("  2. Use Homebrew: 'brew install python'", file=sys.stderr)
        print("  3. Download from https://python.org/downloads/", file=sys.stderr)
    else:  # Linux and others
        print("Linux installation options:", file=sys.stderr)
        print(
            "  1. Ubuntu/Debian: 'sudo apt update && sudo apt install python3'",
            file=sys.stderr,
        )
        print("  2. CentOS/RHEL: 'sudo yum install python3'", file=sys.stderr)
        print("  3. Use package manager for your distribution", file=sys.stderr)

    print("", file=sys.stderr)
    print("After installing Python, verify with:", file=sys.stderr)
    print("  python --version  (or python3 --version)", file=sys.stderr)
    print("", file=sys.stderr)

    sys.exit(1)


def print_usage_info(script_name):
    """Print cross-platform usage information."""
    python_cmd = detect_python_command()
    platform_name = platform.system()

    print(f"# Claude Code Workflows Analysis Script: {script_name}")
    print(f"# Platform: {platform_name}")
    print(f"# Python: {python_cmd}")
    print("#")

    if platform_name == "Windows":
        print("# Windows Usage:")
        print(f"#   {python_cmd} {script_name} [directory]")
        print(f"#   python {script_name} [directory]")
    else:
        print("# macOS/Linux Usage:")
        print(f"#   {python_cmd} {script_name} [directory]")
        print(f"#   ./{script_name} [directory]  # if executable")
    print("#")


def validate_python_version(min_version=(3, 8)):
    """
    Validate that Python version meets minimum requirements.
    Exits with critical error if version is too old.
    """
    current_version = sys.version_info[:2]

    if current_version < min_version:
        print(
            f"CRITICAL ERROR: Python version {current_version[0]}.{current_version[1]} is too old",
            file=sys.stderr,
        )
        print(
            f"Claude Code Workflows requires Python {min_version[0]}.{min_version[1]}+",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print("Current Python version:", sys.version, file=sys.stderr)
        print("Python executable:", sys.executable, file=sys.stderr)
        print("", file=sys.stderr)
        print("Please upgrade Python to continue:", file=sys.stderr)

        platform_name = platform.system()
        if platform_name == "Windows":
            print(
                "  - Download latest from https://python.org/downloads/",
                file=sys.stderr,
            )
            print("  - Or update via Microsoft Store", file=sys.stderr)
        elif platform_name == "Darwin":  # macOS
            print("  - Use Homebrew: 'brew upgrade python'", file=sys.stderr)
            print(
                "  - Or download latest from https://python.org/downloads/",
                file=sys.stderr,
            )
        else:  # Linux
            print("  - Use your package manager to upgrade python3", file=sys.stderr)

        sys.exit(1)


def ensure_compatible_environment():
    """
    Ensure Python environment is compatible with Claude Code Workflows.
    Validates Python version and sets up paths.
    Call this at the start of every analysis script.
    """
    validate_python_version()
    setup_python_path()

    # Verify we can detect Python command
    try:
        detect_python_command()
    except SystemExit:
        # detect_python_command already printed error and exited
        pass


# Auto-setup when imported
setup_python_path()

# Export commonly used functions
__all__ = [
    "setup_python_path",
    "get_platform_info",
    "detect_python_command",
    "print_usage_info",
    "validate_python_version",
    "ensure_compatible_environment",
]
