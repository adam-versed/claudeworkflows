#!/usr/bin/env python3
"""
Test script for make-dev system setup validation
Tests that Makefile targets work correctly and required dependencies are present
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_makefile_targets():
    """Test that Makefile targets are properly defined"""
    print("🧪 Testing Makefile targets...")
    
    # Check if Makefile exists
    if not os.path.exists("Makefile"):
        print("❌ Makefile not found")
        return False
    
    # Test each target without actually running dev services
    targets_to_test = ["help", "status", "clean"]
    
    for target in targets_to_test:
        success, stdout, stderr = run_command(f"make {target}")
        if success:
            print(f"✅ make {target} - OK")
        else:
            print(f"❌ make {target} - FAILED: {stderr}")
            return False
    
    return True

def test_procfile_format():
    """Test that Procfile is properly formatted"""
    print("🧪 Testing Procfile format...")
    
    if not os.path.exists("Procfile"):
        print("❌ Procfile not found")
        return False
    
    with open("Procfile", "r") as f:
        content = f.read()
    
    required_services = ["web:", "native:", "backend:"]
    for service in required_services:
        if service not in content:
            print(f"❌ Missing service definition: {service}")
            return False
        else:
            print(f"✅ Found service: {service.rstrip(':')}")
    
    return True

def test_dependencies():
    """Test that required dependencies are available"""
    print("🧪 Testing dependencies...")
    
    dependencies = {
        "make": "make --version",
        "node": "node --version", 
        "npm": "npm --version"
    }
    
    optional_deps = {
        "watchexec": "watchexec --version",
        "shoreman": "shoreman --version"
    }
    
    all_good = True
    
    # Required dependencies
    for dep, cmd in dependencies.items():
        success, stdout, stderr = run_command(cmd)
        if success:
            version = stdout.strip().split('\n')[0]
            print(f"✅ {dep}: {version}")
        else:
            print(f"❌ {dep}: Not found")
            all_good = False
    
    # Optional dependencies
    for dep, cmd in optional_deps.items():
        success, stdout, stderr = run_command(cmd)
        if success:
            version = stdout.strip().split('\n')[0] 
            print(f"✅ {dep}: {version}")
        else:
            print(f"⚠️  {dep}: Not found (optional - install with: brew install {dep})")
    
    return all_good

def test_project_structure():
    """Test that this is a valid Turborepo project"""
    print("🧪 Testing project structure...")
    
    required_files = [
        "turbo.json",
        "package.json",
        "apps/web/package.json",
        "apps/native/package.json"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing make-dev setup for Turborepo...")
    print("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Dependencies", test_dependencies), 
        ("Makefile Targets", test_makefile_targets),
        ("Procfile Format", test_procfile_format)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Make-dev setup is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())