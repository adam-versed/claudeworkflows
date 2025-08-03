# install_monitoring_dependencies.py v0.1
"""
install_monitoring_dependencies.py v0.1

Simplified cross-platform installer for monitoring dependencies: make, watchexec, and foreman.
Checks for tool presence, asks user consent, and installs using platform-specific package managers.
"""

import os
import sys
import subprocess
import platform


def run_command(cmd, shell=False):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def check_tool_installed(tool_name):
    """Check if a tool is installed and available in PATH."""
    system = platform.system().lower()

    if system == "windows":
        success, _, _ = run_command(["where", tool_name], shell=True)
    else:
        success, _, _ = run_command(["which", tool_name])

    return success


def detect_platform_and_package_manager():
    """Detect the current platform and available package manager."""
    system = platform.system().lower()

    if system == "darwin":  # macOS
        if run_command(["which", "brew"])[0]:
            return "macos", "brew"
        else:
            return "macos", None

    elif system == "linux":
        # Check for common Linux package managers
        for pm in ["apt", "dnf", "yum", "pacman"]:
            if run_command(["which", pm])[0]:
                return "linux", pm
        return "linux", None

    elif system == "windows":
        # Check for Windows package managers
        for pm in ["winget", "choco", "scoop"]:
            if run_command(["where", pm], shell=True)[0]:
                return "windows", pm
        return "windows", None

    return system, None


def get_user_consent(missing_tools):
    """Ask user for consent to install missing tools."""
    print(f"\nMissing tools detected: {', '.join(missing_tools)}")
    print("These tools are required for development monitoring.")

    while True:
        response = input("\nWould you like to install them? (y/n): ").lower().strip()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def install_make(platform_name, package_manager):
    """Install make based on platform and package manager."""
    print("Installing make...")

    if package_manager == "brew":
        return run_command(["brew", "install", "make"])
    elif package_manager == "apt":
        run_command(["sudo", "apt", "update"])
        return run_command(["sudo", "apt", "install", "-y", "build-essential"])
    elif package_manager in ["dnf", "yum"]:
        return run_command(["sudo", package_manager, "install", "-y", "make"])
    elif package_manager == "pacman":
        return run_command(["sudo", "pacman", "-S", "--noconfirm", "make"])
    elif package_manager == "winget":
        return run_command(["winget", "install", "GnuWin32.Make"], shell=True)
    elif package_manager == "choco":
        return run_command(["choco", "install", "make", "-y"], shell=True)
    elif package_manager == "scoop":
        return run_command(["scoop", "install", "make"], shell=True)

    return False, "", f"Unsupported package manager: {package_manager}"


def install_watchexec(platform_name, package_manager):
    """Install watchexec based on platform and package manager."""
    print("Installing watchexec...")

    if package_manager == "brew":
        return run_command(["brew", "install", "watchexec"])
    elif package_manager == "apt":
        return run_command(["sudo", "apt", "install", "-y", "watchexec"])
    elif package_manager in ["dnf", "yum"]:
        return run_command(["sudo", package_manager, "install", "-y", "watchexec"])
    elif package_manager == "pacman":
        return run_command(["sudo", "pacman", "-S", "--noconfirm", "watchexec"])
    elif package_manager == "winget":
        return run_command(["winget", "install", "watchexec"], shell=True)
    elif package_manager == "choco":
        return run_command(["choco", "install", "watchexec", "-y"], shell=True)
    elif package_manager == "scoop":
        return run_command(["scoop", "install", "watchexec"], shell=True)

    return False, "", f"Unsupported package manager: {package_manager}"


def install_foreman_from_github(platform_name):
    """Install foreman (shoreman) from GitHub for all platforms."""
    print("Installing foreman (shoreman) from GitHub...")

    if platform_name == "windows":
        # For Windows, we'll download to a different location
        target_path = os.path.expanduser("~/.local/bin/shoreman")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
    else:
        target_path = "/usr/local/bin/shoreman"

    try:
        # Download shoreman script
        success, stdout, stderr = run_command(
            [
                "curl",
                "-L",
                "-o",
                target_path,
                "https://github.com/chrismytton/shoreman/raw/master/shoreman.sh",
            ]
        )

        if not success:
            return False, "", f"Failed to download shoreman: {stderr}"

        # Make it executable (Unix-like systems)
        if platform_name != "windows":
            success, stdout, stderr = run_command(["chmod", "+x", target_path])
            if not success:
                return False, "", f"Failed to make shoreman executable: {stderr}"

        return True, f"Foreman (shoreman) installed to {target_path}", ""

    except Exception as e:
        return False, "", f"Installation failed: {str(e)}"


def main():
    """Main function to check and install monitoring dependencies."""
    print("Checking monitoring dependencies...")
    print("Required tools: make, watchexec, foreman")

    # Detect platform and package manager
    platform_name, package_manager = detect_platform_and_package_manager()

    if not package_manager:
        print(f"\nError: No supported package manager found on {platform_name}")
        if platform_name == "macos":
            print("Please install Homebrew: https://brew.sh")
        elif platform_name == "linux":
            print(
                "Please install a supported package manager (apt, dnf, yum, or pacman)"
            )
        elif platform_name == "windows":
            print("Please install winget, chocolatey, or scoop")
        return 1

    print(f"Detected: {platform_name} with {package_manager}")

    # Check which tools are missing
    tools_to_check = ["make", "watchexec", "shoreman"]
    missing_tools = []

    for tool in tools_to_check:
        # Special case: check for both shoreman and foreman for process manager
        if tool == "shoreman":
            if not (
                check_tool_installed("shoreman") or check_tool_installed("foreman")
            ):
                missing_tools.append("foreman")
        elif not check_tool_installed(tool):
            missing_tools.append(tool)

    if not missing_tools:
        print("\n✓ All required tools are already installed!")
        return 0

    # Ask for user consent
    if not get_user_consent(missing_tools):
        print("Installation cancelled by user.")
        return 1

    # Install missing tools
    print(f"\nInstalling tools using {package_manager}...")
    failed_installations = []

    for tool in missing_tools:
        if tool == "make":
            success, stdout, stderr = install_make(platform_name, package_manager)
        elif tool == "watchexec":
            success, stdout, stderr = install_watchexec(platform_name, package_manager)
        elif tool == "foreman":
            success, stdout, stderr = install_foreman_from_github(platform_name)

        if success:
            print(f"  ✓ {tool} installed successfully")
        else:
            print(f"  ✗ Failed to install {tool}: {stderr}")
            failed_installations.append(tool)

    # Summary
    if failed_installations:
        print(f"\n⚠️  Failed to install: {', '.join(failed_installations)}")
        return 1
    else:
        print("\n✓ All monitoring dependencies installed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
