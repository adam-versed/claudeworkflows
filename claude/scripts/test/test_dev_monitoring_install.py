#!/usr/bin/env python3
"""
Test script to verify dev-monitoring files are copied during install.sh execution.
Validates that all required dev-monitoring scripts and utilities are present in target directory.
"""

import os
import sys
from pathlib import Path


def test_dev_monitoring_install(target_dir):
    """
    Test that all dev-monitoring scripts are properly copied to target directory.
    
    Args:
        target_dir (str): Path to installation target directory
        
    Returns:
        bool: True if all files are present, False otherwise
    """
    target_path = Path(target_dir)
    
    if not target_path.exists():
        print(f"❌ Target directory does not exist: {target_dir}")
        return False
    
    # Define required dev-monitoring files
    required_files = [
        # Main command file
        "commands/setup-dev-monitoring.md",
        
        # Core dev-monitoring scripts
        "scripts/setup/dev-monitoring/check_system_dependencies.py",
        "scripts/setup/dev-monitoring/install_monitoring_tools.py",
        
        # Monitoring utility scripts
        "scripts/utils/generate_monitoring_templates.py",
        "scripts/utils/generate_makefile.py",
        "scripts/utils/generate_procfile.py",
    ]
    
    missing_files = []
    present_files = []
    
    print(f"🔍 Checking dev-monitoring files in: {target_dir}")
    print("=" * 60)
    
    for file_path in required_files:
        full_path = target_path / file_path
        if full_path.exists():
            present_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    print("=" * 60)
    print(f"📊 Results: {len(present_files)}/{len(required_files)} files present")
    
    if missing_files:
        print(f"❌ Missing {len(missing_files)} files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All dev-monitoring files are present!")
        return True


def main():
    """Main execution function."""
    if len(sys.argv) != 2:
        print("Usage: python test_dev_monitoring_install.py <target_directory>")
        print("Example: python test_dev_monitoring_install.py /tmp/test_install")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    success = test_dev_monitoring_install(target_dir)
    
    if success:
        print("\n🎉 Dev-monitoring install verification PASSED")
        sys.exit(0)
    else:
        print("\n💥 Dev-monitoring install verification FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()