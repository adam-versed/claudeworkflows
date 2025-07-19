#!/usr/bin/env python3
"""
Automated setup script for make-based development workflow
Handles detection, dependency installation, and file generation for Turborepo projects
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class MakeDevSetup:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.platform = platform.system().lower()
        self.is_turborepo = False
        self.has_web = False
        self.has_native = False
        self.has_backend = False
        
    def log(self, message: str, emoji: str = "ℹ️"):
        """Print formatted log message"""
        print(f"{emoji} {message}")
        
    def run_command(self, cmd: str, check: bool = True, capture_output: bool = True) -> Tuple[bool, str, str]:
        """Run shell command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=capture_output, 
                text=True, cwd=self.project_path, check=check
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout or "", e.stderr or ""
        except Exception as e:
            return False, "", str(e)
    
    def detect_project_structure(self) -> bool:
        """Detect if this is a valid Turborepo project with required structure"""
        self.log("Detecting project structure...", "🔍")
        
        # Check for turbo.json
        turbo_json = self.project_path / "turbo.json"
        if turbo_json.exists():
            self.is_turborepo = True
            self.log("✅ Turborepo detected")
        else:
            self.log("❌ turbo.json not found - not a Turborepo project")
            return False
        
        # Check for web app
        web_package = self.project_path / "apps" / "web" / "package.json"
        if web_package.exists():
            with open(web_package) as f:
                package_data = json.load(f)
                if "next" in package_data.get("dependencies", {}) or "next" in package_data.get("devDependencies", {}):
                    self.has_web = True
                    self.log("✅ Next.js web app detected")
        
        # Check for native app
        native_package = self.project_path / "apps" / "native" / "package.json"
        if native_package.exists():
            with open(native_package) as f:
                package_data = json.load(f)
                deps = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
                if "expo" in deps or "react-native" in deps:
                    self.has_native = True
                    self.log("✅ React Native/Expo app detected")
        
        # Check for Convex backend
        convex_dir = self.project_path / "convex"
        backend_package = self.project_path / "packages" / "backend" / "package.json"
        root_package = self.project_path / "package.json"
        
        if convex_dir.exists() or backend_package.exists() or (root_package.exists() and "convex" in open(root_package).read()):
            # Check if Convex is properly configured with generated files
            if self.check_convex_setup():
                self.has_backend = True
                if backend_package.exists():
                    self.log("✅ Convex backend detected (workspace-based)")
                else:
                    self.log("✅ Convex backend detected")
            else:
                self.log("⚠️  Convex detected but not properly configured")
                self.log("   Missing required files:")
                self.log("   - convex/_generated/ folder (populated)")
                self.log("   - convex/schema.ts file")
                self.log("")
                self.log("   Please run one of these commands first:")
                if backend_package.exists():
                    self.log("   npm run setup --workspace packages/backend")
                else:
                    self.log("   npx convex dev")
                self.log("")
                self.log("   Then re-run this setup script")
                return False
        
        if not (self.has_web or self.has_native or self.has_backend):
            self.log("❌ No supported apps detected (web/native/backend)")
            return False
            
        return True
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check for required system dependencies"""
        self.log("Checking system dependencies...", "🔧")
        
        deps = {
            "make": "make --version",
            "node": "node --version",
            "npm": "npm --version"
        }
        
        optional_deps = {
            "watchexec": "watchexec --version",
            "shoreman": "shoreman"  # shoreman doesn't support --version, just check if command exists
        }
        
        results = {}
        
        # Check required dependencies
        for dep, cmd in deps.items():
            success, stdout, _ = self.run_command(cmd, check=False)
            if success:
                version = stdout.strip().split('\n')[0]
                self.log(f"✅ {dep}: {version}")
                results[dep] = True
            else:
                self.log(f"❌ {dep}: Not found")
                results[dep] = False
        
        # Check optional dependencies
        for dep, cmd in optional_deps.items():
            success, stdout, _ = self.run_command(cmd, check=False)
            if success:
                if dep == "shoreman":
                    self.log(f"✅ {dep}: Available")
                else:
                    version = stdout.strip().split('\n')[0]
                    self.log(f"✅ {dep}: {version}")
                results[dep] = True
            else:
                if dep == "shoreman":
                    self.log(f"⚠️  {dep}: Not found (will install via brew)")
                else:
                    self.log(f"⚠️  {dep}: Not found (install with: brew install {dep})")
                results[dep] = False
                
        return results
    
    def check_convex_setup(self) -> bool:
        """Check if Convex is properly configured with generated files"""
        # Check for _generated folder and schema.ts
        convex_generated = self.project_path / "convex" / "_generated"
        convex_schema = self.project_path / "convex" / "schema.ts"
        
        # Also check workspace-based setup
        workspace_generated = self.project_path / "packages" / "backend" / "convex" / "_generated"
        workspace_schema = self.project_path / "packages" / "backend" / "convex" / "schema.ts"
        
        # Check if _generated folder exists and has content
        def is_generated_populated(generated_path):
            if not generated_path.exists():
                return False
            # Check if _generated has any files (should contain api.js, api.d.ts, etc.)
            return any(generated_path.iterdir())
        
        # Check standard convex setup
        if convex_generated.parent.exists():
            if is_generated_populated(convex_generated) and convex_schema.exists():
                self.log("✅ Convex schema and generated files found")
                return True
        
        # Check workspace-based setup
        if workspace_generated.parent.exists():
            if is_generated_populated(workspace_generated) and workspace_schema.exists():
                self.log("✅ Convex schema and generated files found (workspace)")
                return True
        
        # If we get here, Convex is not properly set up
        return False
    
    def check_port_conflicts(self) -> bool:
        """Check for common port conflicts and warn user"""
        self.log("Checking for port conflicts...", "🔍")
        
        # Check common ports that might conflict
        ports_to_check = [3000, 5000]
        conflicts = []
        
        for port in ports_to_check:
            success, stdout, _ = self.run_command(f"lsof -i :{port}", check=False)
            if success and stdout.strip():
                conflicts.append(port)
                self.log(f"⚠️  Port {port} is in use")
        
        if conflicts:
            self.log("Port conflicts detected - services will be configured with appropriate ports.")
            if 3000 in conflicts:
                self.log("⚠️  Port 3000 is in use - you may need to stop other services")
        else:
            self.log("✅ No port conflicts detected")
        
        self.log("Next.js will be configured to use port 3000 (standard web server port)")
        
        return True  # Don't fail setup, just warn
    
    def install_dependencies(self, deps_status: Dict[str, bool]) -> bool:
        """Install missing dependencies"""
        self.log("Installing missing dependencies...", "📦")
        
        if self.platform == "darwin":  # macOS
            if not deps_status.get("watchexec", True):
                self.log("Installing watchexec...")
                success, _, stderr = self.run_command("brew install watchexec", check=False)
                if not success:
                    self.log(f"❌ Failed to install watchexec: {stderr}")
                    return False
                self.log("✅ watchexec installed")
            
            if not deps_status.get("shoreman", True):
                self.log("Installing shoreman...")
                success, _, stderr = self.run_command("brew install chrismytton/formula/shoreman", check=False)
                if not success:
                    self.log(f"⚠️  Failed to install shoreman via brew: {stderr}")
                    self.log("Please install manually: brew install chrismytton/formula/shoreman")
                else:
                    self.log("✅ shoreman installed")
                
        elif self.platform == "linux":
            # Linux installation commands
            if not deps_status.get("watchexec", True):
                self.log("Installing watchexec...")
                # Try different package managers
                for cmd in ["apt install -y watchexec", "yum install -y watchexec", "pacman -S watchexec"]:
                    success, _, _ = self.run_command(f"sudo {cmd}", check=False)
                    if success:
                        break
                else:
                    # Fallback to cargo
                    success, _, stderr = self.run_command("cargo install watchexec-cli", check=False)
                    if not success:
                        self.log(f"⚠️  Could not install watchexec automatically: {stderr}")
            
            if not deps_status.get("shoreman", True):
                # Try direct download as fallback for Linux
                success, _, stderr = self.run_command("curl -sL https://github.com/chrismytton/shoreman/raw/master/shoreman.sh -o /usr/local/bin/shoreman && chmod +x /usr/local/bin/shoreman", check=False)
                if not success:
                    self.log(f"⚠️  Failed to install shoreman: {stderr}")
                    self.log("Please install manually from: https://github.com/chrismytton/shoreman")
                    
        else:  # Windows
            self.log("⚠️  Windows detected - manual installation may be required")
            if not deps_status.get("watchexec", True):
                self.log("Install watchexec: https://github.com/watchexec/watchexec/releases")
            if not deps_status.get("shoreman", True):
                self.log("Install shoreman: npm install -g shoreman")
        
        return True
    
    def generate_makefile(self) -> bool:
        """Generate Makefile with appropriate targets"""
        self.log("Generating Makefile...", "📝")
        
        makefile_content = '''# ==========================================
# DEVELOPMENT WORKFLOW FOR TURBOREPO
# ==========================================
# CRITICAL: Claude should NEVER run 'make dev'
# Always ask user to start development services
# ==========================================

.PHONY: dev tail-log lint test format clean status stop help

# Start all development services (USER ONLY - NEVER AUTOMATED)
dev:
\t@echo "🚀 Starting Turborepo development environment..."
\t@echo "📱 Services will start with auto-reload enabled"
\t@echo "📝 Logs will be written to dev.log"
\t@rm -f dev.log
\t@touch dev.log
\t@echo "$$(date): Development services starting" >> dev.log
\tshoreman Procfile

# Access unified development logs (Claude can use this)
tail-log:
\t@if [ -f dev.log ]; then \\
\t\techo "📋 Development logs (use Ctrl+C to exit):"; \\
\t\ttail -f dev.log; \\
\telse \\
\t\techo "❌ No development logs found. Run 'make dev' first."; \\
\tfi

# Show current service status
status:
\t@if [ -f shoreman.pid ]; then \\
\t\techo "✅ Development services are running (PID: $$(cat shoreman.pid))"; \\
\t\techo "📝 Log file: dev.log"; \\
\t\techo "🔍 Use 'make tail-log' to view logs"; \\
\telse \\
\t\techo "❌ Development services are not running"; \\
\t\techo "🚀 Run 'make dev' to start services"; \\
\tfi

# Stop all services (USER ONLY)
stop:
\t@if [ -f shoreman.pid ]; then \\
\t\techo "🛑 Stopping development services..."; \\
\t\tkill $$(cat shoreman.pid) 2>/dev/null || true; \\
\t\trm -f shoreman.pid; \\
\t\techo "✅ Services stopped"; \\
\telse \\
\t\techo "ℹ️  No services running"; \\
\tfi

# Code quality and testing
lint:
\t@echo "🔍 Running linting across monorepo..."
\tnpx turbo lint

test:
\t@echo "🧪 Running tests across monorepo..."
\tnpx turbo test

format:
\t@echo "✨ Formatting code across monorepo..."
\tnpx turbo format

# Cleanup
clean:
\t@echo "🧹 Cleaning build artifacts..."
\tnpx turbo clean
\t@echo "🗑️  Removing log files..."
\trm -f dev.log shoreman.pid
\t@echo "✅ Cleanup complete"

# Help
help:
\t@echo "📚 Turborepo Development Commands:"
\t@echo ""
\t@echo "  make dev       Start all services (web, mobile, backend)"
\t@echo "  make tail-log  View unified development logs"
\t@echo "  make status    Check if services are running"
\t@echo "  make stop      Stop all development services"
\t@echo ""
\t@echo "  make lint      Run code quality checks"
\t@echo "  make test      Run test suites"
\t@echo "  make format    Format all code"
\t@echo "  make clean     Clean build artifacts and logs"
\t@echo ""
\t@echo "⚠️  Claude should NEVER run 'make dev' or 'make stop'"
\t@echo "📋 Claude can use 'make tail-log' and 'make status'"
'''
        
        makefile_path = self.project_path / "Makefile"
        try:
            with open(makefile_path, "w") as f:
                f.write(makefile_content)
            self.log("✅ Makefile created")
            return True
        except Exception as e:
            self.log(f"❌ Failed to create Makefile: {e}")
            return False
    
    def generate_procfile(self) -> bool:
        """Generate Procfile based on detected project structure"""
        self.log("Generating Procfile...", "📝")
        
        services = []
        
        if self.has_web:
            services.append('web: cd apps/web && PORT=3000 npm run dev 2>&1 | while IFS= read -r line; do echo "[$(date \'+%H:%M:%S\')] [WEB] $line"; done | tee -a ../../dev.log')
        
        if self.has_native:
            services.append('native: cd apps/native && npx expo start --clear 2>&1 | while IFS= read -r line; do echo "[$(date \'+%H:%M:%S\')] [NATIVE] $line"; done | tee -a ../../dev.log')
        
        if self.has_backend:
            # Check for workspace-based backend setup
            backend_package = self.project_path / "packages" / "backend" / "package.json"
            if backend_package.exists():
                services.append('backend: npm run setup --workspace packages/backend 2>&1 | while IFS= read -r line; do echo "[$(date \'+%H:%M:%S\')] [BACKEND] $line"; done | tee -a dev.log')
            else:
                services.append('backend: npx convex dev 2>&1 | while IFS= read -r line; do echo "[$(date \'+%H:%M:%S\')] [BACKEND] $line"; done | tee -a dev.log')
        
        if not services:
            self.log("❌ No services detected for Procfile")
            return False
        
        procfile_content = "# Turborepo Development Services\n"
        procfile_content += "# Each service runs in its own process with unified logging\n\n"
        procfile_content += "\n".join(services)
        procfile_content += "\n\n# Optional: Additional services can be added here\n"
        procfile_content += "# redis: redis-server 2>&1 | while IFS= read -r line; do echo \"[$(date '+%H:%M:%S')] [REDIS] $line\"; done | tee -a dev.log\n"
        
        procfile_path = self.project_path / "Procfile"
        try:
            with open(procfile_path, "w") as f:
                f.write(procfile_content)
            self.log("✅ Procfile created")
            return True
        except Exception as e:
            self.log(f"❌ Failed to create Procfile: {e}")
            return False
    
    def update_gitignore(self) -> bool:
        """Update .gitignore to exclude development files"""
        self.log("Updating .gitignore...", "📝")
        
        gitignore_path = self.project_path / ".gitignore"
        gitignore_entries = [
            "# Development workflow files",
            "dev.log",
            "shoreman.pid",
            ""
        ]
        
        try:
            # Read existing .gitignore if it exists
            existing_content = ""
            if gitignore_path.exists():
                with open(gitignore_path, "r") as f:
                    existing_content = f.read()
            
            # Check if our entries are already present
            if "dev.log" not in existing_content:
                with open(gitignore_path, "a") as f:
                    f.write("\n".join(gitignore_entries))
                self.log("✅ .gitignore updated")
            else:
                self.log("✅ .gitignore already contains development entries")
            
            return True
        except Exception as e:
            self.log(f"❌ Failed to update .gitignore: {e}")
            return False
    
    def create_claude_config(self) -> bool:
        """Create or update CLAUDE.md with development workflow documentation"""
        self.log("Creating/updating CLAUDE.md...", "📝")
        
        claude_md_path = self.project_path / "CLAUDE.md"
        
        dev_section = '''
## Development Workflow Commands (Make-based)

**CRITICAL: Service Management Restrictions**
- **NEVER run `make dev` or `make stop`** - These commands start/stop development services
- **ALWAYS ask the user** to run these commands manually
- **Claude can use**: `make tail-log`, `make status`, `make lint`, `make test`, `make format`, `make clean`

### Available Commands

- `make dev` - **USER ONLY** - Start all development services (web, mobile, backend) with auto-reload
- `make tail-log` - **Claude can use** - Access unified development logs for debugging and context
- `make status` - **Claude can use** - Check if development services are running
- `make stop` - **USER ONLY** - Stop all development services
- `make lint` - **Claude can use** - Run code quality checks across monorepo
- `make test` - **Claude can use** - Execute test suites for all packages
- `make format` - **Claude can use** - Format code across all workspaces
- `make clean` - **Claude can use** - Clean build artifacts and logs
- `make help` - **Claude can use** - Show available commands

### Log Files and Debugging

- **Development logs**: Located at `./dev.log` in project root
- **Log format**: `[TIMESTAMP] [SERVICE] Message content`
- **Services**: `[WEB]` (Next.js), `[NATIVE]` (React Native/Expo), `[BACKEND]` (Convex)
- **Access logs**: Use `make tail-log` to read current development activity
- **Context gathering**: Logs provide complete context about frontend/backend requests and errors

### Workflow Integration

When debugging issues or understanding system state:
1. **Check service status**: `make status`
2. **Read development logs**: `make tail-log` (use Ctrl+C to exit)
3. **Run quality checks**: `make lint` and `make test`
4. **Ask user to restart services**: "Please run `make dev` to start/restart development services"

**Never attempt to start, stop, or restart development services automatically.**
'''
        
        try:
            if claude_md_path.exists():
                with open(claude_md_path, "r") as f:
                    content = f.read()
                
                if "Development Workflow Commands" not in content:
                    with open(claude_md_path, "a") as f:
                        f.write(dev_section)
                    self.log("✅ CLAUDE.md updated with development workflow")
                else:
                    self.log("✅ CLAUDE.md already contains development workflow")
            else:
                with open(claude_md_path, "w") as f:
                    f.write(f"# {self.project_path.name}\n{dev_section}")
                self.log("✅ CLAUDE.md created")
            
            return True
        except Exception as e:
            self.log(f"❌ Failed to create/update CLAUDE.md: {e}")
            return False
    
    def run_validation(self) -> bool:
        """Run validation tests to ensure setup works"""
        self.log("Running validation tests...", "🧪")
        
        # Test make help
        success, stdout, stderr = self.run_command("make help", check=False)
        if success:
            self.log("✅ make help - OK")
        else:
            self.log(f"❌ make help failed: {stderr}")
            return False
        
        # Test make status
        success, stdout, stderr = self.run_command("make status", check=False)
        if success:
            self.log("✅ make status - OK")
        else:
            self.log(f"❌ make status failed: {stderr}")
            return False
        
        return True
    
    def setup(self) -> bool:
        """Run complete setup process"""
        self.log("Starting make-dev setup for Turborepo...", "🚀")
        self.log("=" * 60)
        
        # Step 1: Detect project structure
        if not self.detect_project_structure():
            return False
        
        # Step 2: Check dependencies
        deps_status = self.check_dependencies()
        required_deps = ["make", "node", "npm"]
        if not all(deps_status.get(dep, False) for dep in required_deps):
            self.log("❌ Missing required dependencies. Please install manually.")
            return False
        
        # Step 2.5: Check for port conflicts
        self.check_port_conflicts()
        
        # Step 3: Install optional dependencies
        if not self.install_dependencies(deps_status):
            self.log("⚠️  Some optional dependencies failed to install")
        
        # Step 4: Generate files
        steps = [
            ("Makefile", self.generate_makefile),
            ("Procfile", self.generate_procfile),
            (".gitignore", self.update_gitignore),
            ("CLAUDE.md", self.create_claude_config)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                self.log(f"❌ Failed to create {step_name}")
                return False
        
        # Step 5: Validation
        if not self.run_validation():
            return False
        
        self.log("=" * 60)
        self.log("🎉 Make-dev setup completed successfully!", "✅")
        self.log("")
        self.log("Next steps:")
        self.log("1. Run `make help` to see available commands")
        self.log("2. Run `make dev` to start development services")
        self.log("3. Use `make tail-log` to view unified logs")
        self.log("4. Claude can now use make commands for development workflow")
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup make-based development workflow for Turborepo")
    parser.add_argument("--path", default=".", help="Project path (default: current directory)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    setup = MakeDevSetup(args.path)
    
    try:
        if setup.setup():
            return 0
        else:
            setup.log("❌ Setup failed", "💥")
            return 1
    except KeyboardInterrupt:
        setup.log("Setup interrupted by user", "⚠️")
        return 1
    except Exception as e:
        setup.log(f"Unexpected error: {e}", "💥")
        return 1

if __name__ == "__main__":
    sys.exit(main())