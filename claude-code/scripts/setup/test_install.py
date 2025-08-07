#!/usr/bin/env python3
"""
Test installation script - non-interactive version for validation.
"""

import sys
from pathlib import Path

# Add the setup directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from install_dependencies import DependencyInstaller
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


def test_installation():
    """Test installation process without user interaction."""
    print("🧪 Testing Claude Code Workflows dependency installation...")

    installer = DependencyInstaller()

    # Test platform detection
    installer.print_platform_info()

    # Test prerequisites
    print("\n🔍 Testing prerequisites...")
    python_ok = installer.check_python_version()
    pip_ok = installer.check_pip_available()

    if not python_ok or not pip_ok:
        print("❌ Prerequisites not met")
        return False

    # Test package verification (without installing)
    print("\n🔍 Testing package verification...")
    verified, missing = installer.verify_installation()

    print("✅ Installation test completed")
    print(f"Prerequisites: {'✅' if python_ok and pip_ok else '❌'}")
    print(f"Current packages verified: {'✅' if verified else f'❌ Missing: {missing}'}")

    return True


if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)
