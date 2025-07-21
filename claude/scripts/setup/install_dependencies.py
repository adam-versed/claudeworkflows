"""
Dependency installer for claudeworkflows scriptable workflows.
Handles cross-platform installation of required Python packages.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

# Add utils to path for imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "utils"))

from cross_platform import PlatformDetector, CommandExecutor, DependencyChecker

class DependencyInstaller:
    """Handle installation of Python dependencies."""
    
    def __init__(self):
        self.platform = PlatformDetector.get_platform()
        self.python_cmd = PlatformDetector.get_python_command()
        self.requirements_file = Path(__file__).parent / "requirements.txt"
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        if not DependencyChecker.check_python_version():
            print("❌ Python 3.7 or higher is required")
            print(f"Current version: {sys.version}")
            return False
        
        print(f"✅ Python version OK: {sys.version.split()[0]}")
        return True
    
    def check_pip_available(self) -> bool:
        """Check if pip is available."""
        try:
            returncode, stdout, stderr = CommandExecutor.run_command([
                self.python_cmd, "-m", "pip", "--version"
            ])
            if returncode == 0:
                print(f"✅ Pip available: {stdout.strip().split()[1]}")
                return True
            else:
                print("❌ Pip not available")
                return False
        except Exception as e:
            print(f"❌ Error checking pip: {e}")
            return False
    
    def install_package(self, package: str) -> Tuple[bool, str]:
        """
        Install a single package.
        
        Args:
            package: Package specification (e.g., "requests>=2.25.0")
            
        Returns:
            Tuple of (success, message)
        """
        print(f"📦 Installing {package}...")
        
        returncode, stdout, stderr = CommandExecutor.run_command([
            self.python_cmd, "-m", "pip", "install", package
        ], timeout=300)  # 5 minute timeout for installations
        
        if returncode == 0:
            print(f"✅ Successfully installed {package}")
            return True, "Success"
        else:
            error_msg = stderr or stdout or "Unknown error"
            print(f"❌ Failed to install {package}: {error_msg}")
            return False, error_msg
    
    def install_from_requirements(self) -> Tuple[bool, List[str]]:
        """
        Install all packages from requirements.txt.
        
        Returns:
            Tuple of (all_success, failed_packages)
        """
        if not self.requirements_file.exists():
            print(f"❌ Requirements file not found: {self.requirements_file}")
            return False, ["requirements.txt not found"]
        
        print(f"📋 Installing from {self.requirements_file}")
        
        returncode, stdout, stderr = CommandExecutor.run_command([
            self.python_cmd, "-m", "pip", "install", "-r", str(self.requirements_file)
        ], timeout=600)  # 10 minute timeout
        
        if returncode == 0:
            print("✅ All packages installed successfully")
            return True, []
        else:
            error_msg = stderr or stdout or "Unknown error"
            print(f"❌ Installation failed: {error_msg}")
            return False, [error_msg]
    
    def upgrade_pip(self) -> bool:
        """Upgrade pip to latest version."""
        print("🔄 Upgrading pip...")
        
        returncode, stdout, stderr = CommandExecutor.run_command([
            self.python_cmd, "-m", "pip", "install", "--upgrade", "pip"
        ], timeout=300)
        
        if returncode == 0:
            print("✅ Pip upgraded successfully")
            return True
        else:
            print(f"⚠️ Pip upgrade failed (continuing anyway): {stderr}")
            return False
    
    def verify_installation(self) -> Tuple[bool, List[str]]:
        """
        Verify that critical packages are installed and working.
        
        Returns:
            Tuple of (all_verified, missing_packages)
        """
        print("\n🔍 Verifying installations...")
        
        critical_packages = [
            "bandit",      # Security analysis
            "psutil",      # System utilities
            "flake8",      # Code quality
            "requests",    # HTTP requests
        ]
        
        missing = []
        for package in critical_packages:
            if DependencyChecker.check_package_installed(package):
                print(f"✅ {package} - OK")
            else:
                print(f"❌ {package} - MISSING")
                missing.append(package)
        
        return len(missing) == 0, missing
    
    def install_all(self) -> bool:
        """
        Complete installation process.
        
        Returns:
            True if installation successful, False otherwise
        """
        print("🚀 SuperCopilot Scriptable Workflows - Dependency Installation")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_python_version():
            return False
        
        if not self.check_pip_available():
            print("💡 Try installing pip with: python -m ensurepip --upgrade")
            return False
        
        # Upgrade pip first
        self.upgrade_pip()
        
        # Install dependencies
        success, failures = self.install_from_requirements()
        
        if not success:
            print(f"\n❌ Installation failed with errors:")
            for failure in failures:
                print(f"  - {failure}")
            return False
        
        # Verify installation
        verified, missing = self.verify_installation()
        
        if verified:
            print(f"\n🎉 Installation completed successfully!")
            print("All required packages are installed and ready to use.")
            return True
        else:
            print(f"\n⚠️ Installation completed but some packages are missing:")
            for package in missing:
                print(f"  - {package}")
            print("You may need to install these manually.")
            return False
    
    def print_platform_info(self):
        """Print platform-specific information."""
        print(f"\n🖥️ Platform Information:")
        print(f"  OS: {self.platform}")
        print(f"  Python: {self.python_cmd}")
        print(f"  Python version: {sys.version.split()[0]}")
        
        # Platform-specific notes
        if self.platform == "windows":
            print("\n📝 Windows Notes:")
            print("  - Some packages may require Microsoft Visual C++ Build Tools")
            print("  - py-spy is not available on Windows")
        elif self.platform == "macos":
            print("\n📝 macOS Notes:")
            print("  - All packages should install without issues")
            print("  - Xcode Command Line Tools may be required for some packages")
        elif self.platform == "linux":
            print("\n📝 Linux Notes:")
            print("  - Some packages may require system dependencies (e.g., gcc, python3-dev)")

def main():
    """Main installation function."""
    installer = DependencyInstaller()
    
    # Print platform info
    installer.print_platform_info()
    
    # Confirm installation
    print("\n❓ Do you want to install SuperCopilot analysis dependencies? (y/n): ", end="")
    response = input().strip().lower()
    
    if response not in ['y', 'yes']:
        print("Installation cancelled.")
        return False
    
    # Run installation
    success = installer.install_all()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Run analysis scripts from .github/scripts/analyze/")
        print("2. Check the workflow files in .github/workflows/analyze/")
        print("3. See documentation for usage examples")
        return True
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Ensure Python 3.7+ is installed")
        print("2. Check internet connectivity")
        print("3. Try running: python -m pip install --upgrade pip")
        print("4. Install system dependencies if needed")
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)