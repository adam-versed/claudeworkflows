#!/usr/bin/env python3
"""
Architecture analysis script: Coupling analysis and dependency mapping.
Part of Claude Code Workflows.
"""

import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

# Add utils to path for imports
script_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(script_dir / "utils"))

try:
    from output_formatter import ResultFormatter, AnalysisResult
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class CouplingAnalyzer:
    """Analyze coupling and dependencies in codebase architecture."""

    def __init__(self):
        # Import/dependency patterns for different languages
        self.import_patterns = {
            "python": {
                "pattern": r"(?:from\s+(\S+)\s+import|import\s+(\S+))",
                "groups": [1, 2],
            },
            "javascript": {
                "pattern": r'(?:import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\))',
                "groups": [1, 2],
            },
            "typescript": {
                "pattern": r'(?:import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\))',
                "groups": [1, 2],
            },
            "java": {"pattern": r"import\s+([^;]+);", "groups": [1]},
            "csharp": {"pattern": r"using\s+([^;]+);", "groups": [1]},
            "go": {
                "pattern": r'import\s+(?:"([^"]+)"|`([^`]+)`)',
                "groups": [1, 2],
            },
            "rust": {
                "pattern": r"use\s+([^;]+);",
                "groups": [1],
            },
            "php": {
                "pattern": r"(?:use\s+([^;]+);|require_once\s+['\"]([^'\"]+)['\"]|include_once\s+['\"]([^'\"]+)['\"])",
                "groups": [1, 2, 3],
            },
            "ruby": {
                "pattern": r"(?:require\s+['\"]([^'\"]+)['\"]|require_relative\s+['\"]([^'\"]+)['\"])",
                "groups": [1, 2],
            },
            "swift": {
                "pattern": r"import\s+(\w+)",
                "groups": [1],
            },
            "kotlin": {
                "pattern": r"import\s+([^;]+)",
                "groups": [1],
            },
            "cpp": {
                "pattern": r"#include\s+[<\"]([^>\"]+)[>\"]",
                "groups": [1],
            },
            "c": {
                "pattern": r"#include\s+[<\"]([^>\"]+)[>\"]",
                "groups": [1],
            },
        }

        # Coupling anti-patterns
        self.coupling_patterns = {
            "circular_dependency": {
                "severity": "high",
                "description": "Circular dependency detected",
            },
            "high_fan_out": {
                "severity": "medium",
                "description": "Module has too many outgoing dependencies",
            },
            "high_fan_in": {
                "severity": "medium",
                "description": "Module is depended on by too many others",
            },
            "deep_dependency": {
                "severity": "medium",
                "description": "Deep dependency chain detected",
            },
            "unstable_dependency": {
                "severity": "medium",
                "description": "Dependency on unstable/concrete module",
            },
        }

        # File extension mapping
        self.extension_language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".h": "cpp",
            ".hpp": "cpp",
        }

        # Files to skip
        self.skip_patterns = {
            "node_modules",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "venv",
            "env",
            ".venv",
            "dist",
            "build",
            ".next",
            "coverage",
            ".nyc_output",
            "target",
            "vendor",
        }

        # Dependency graph
        self.dependency_graph = defaultdict(set)
        self.reverse_graph = defaultdict(set)
        self.module_info = {}

    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned."""
        # Skip directories in skip_patterns
        for part in file_path.parts:
            if part in self.skip_patterns:
                return False

        # Check if we support this file type
        suffix = file_path.suffix.lower()
        return suffix in self.extension_language_map

    def extract_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from a file."""
        dependencies = []
        suffix = file_path.suffix.lower()
        language = self.extension_language_map.get(suffix)

        if not language or language not in self.import_patterns:
            return dependencies

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

                pattern_info = self.import_patterns[language]
                pattern = pattern_info["pattern"]
                groups = pattern_info["groups"]

                matches = re.finditer(pattern, content, re.MULTILINE)

                for match in matches:
                    for group_idx in groups:
                        if group_idx <= len(match.groups()) and match.group(group_idx):
                            dep = match.group(group_idx).strip()
                            # Clean up dependency name
                            dep = dep.split(".")[0]  # Take first part of dotted imports
                            dep = dep.split("/")[0]  # Take first part of path imports
                            if dep and not dep.startswith(
                                "."
                            ):  # Skip relative imports for now
                                dependencies.append(dep)

        except Exception:
            # Continue on error
            pass

        return list(set(dependencies))  # Remove duplicates

    def build_dependency_graph(self, target_path: str) -> Dict[str, Any]:
        """Build dependency graph for the codebase."""
        target = Path(target_path)
        file_count = 0

        if target.is_file():
            if self.should_scan_file(target):
                file_count = 1
                module_name = self._get_module_name(target)
                dependencies = self.extract_dependencies(target)
                self.dependency_graph[module_name] = set(dependencies)
                self.module_info[module_name] = {
                    "file_path": str(target),
                    "dependencies": dependencies,
                    "language": self.extension_language_map.get(target.suffix.lower()),
                }
        elif target.is_dir():
            for file_path in target.rglob("*"):
                if file_path.is_file() and self.should_scan_file(file_path):
                    file_count += 1
                    module_name = self._get_module_name(file_path)
                    dependencies = self.extract_dependencies(file_path)
                    self.dependency_graph[module_name] = set(dependencies)
                    self.module_info[module_name] = {
                        "file_path": str(file_path),
                        "dependencies": dependencies,
                        "language": self.extension_language_map.get(
                            file_path.suffix.lower()
                        ),
                    }

        # Build reverse graph
        for module, deps in self.dependency_graph.items():
            for dep in deps:
                self.reverse_graph[dep].add(module)

        return {
            "total_modules": len(self.dependency_graph),
            "total_files": file_count,
            "total_dependencies": sum(
                len(deps) for deps in self.dependency_graph.values()
            ),
        }

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        # Use relative path from project root as module name
        return str(file_path.stem)

    def analyze_coupling_metrics(self) -> List[Dict[str, Any]]:
        """Analyze coupling metrics and find issues."""
        findings = []

        for module, dependencies in self.dependency_graph.items():
            module_info = self.module_info.get(module, {})
            file_path = module_info.get("file_path", "")

            # Fan-out (efferent coupling) - number of dependencies
            fan_out = len(dependencies)
            if fan_out > 10:  # High fan-out threshold
                findings.append(
                    {
                        "category": "Coupling",
                        "pattern_type": "high_fan_out",
                        "module": module,
                        "file_path": file_path,
                        "severity": "high" if fan_out > 20 else "medium",
                        "description": f"Module has {fan_out} outgoing dependencies (recommended: <10)",
                        "metric_value": fan_out,
                        "dependencies": list(dependencies),
                    }
                )

            # Fan-in (afferent coupling) - number of modules depending on this one
            fan_in = len(self.reverse_graph.get(module, set()))
            if fan_in > 15:  # High fan-in threshold
                findings.append(
                    {
                        "category": "Coupling",
                        "pattern_type": "high_fan_in",
                        "module": module,
                        "file_path": file_path,
                        "severity": "medium",
                        "description": f"Module is used by {fan_in} other modules (high coupling)",
                        "metric_value": fan_in,
                        "dependents": list(self.reverse_graph.get(module, set())),
                    }
                )

        # Check for circular dependencies
        circular_deps = self.find_circular_dependencies()
        for cycle in circular_deps:
            findings.append(
                {
                    "category": "Coupling",
                    "pattern_type": "circular_dependency",
                    "module": " -> ".join(cycle),
                    "file_path": "",
                    "severity": "high",
                    "description": f"Circular dependency: {' -> '.join(cycle)}",
                    "cycle": cycle,
                }
            )

        return findings

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor in self.dependency_graph:  # Only internal dependencies
                    dfs(neighbor, path + [node])

            rec_stack.remove(node)

        for module in self.dependency_graph:
            if module not in visited:
                dfs(module, [])

        return cycles

    def analyze(self, target_path: str) -> AnalysisResult:
        """
        Main analysis function.

        Args:
            target_path: Path to analyze

        Returns:
            AnalysisResult object
        """
        start_time = time.time()
        result = ResultFormatter.create_architecture_result(
            "coupling_analysis.py", target_path
        )

        try:
            # Build dependency graph
            graph_stats = self.build_dependency_graph(target_path)

            # Analyze coupling issues
            coupling_findings = self.analyze_coupling_metrics()

            # Convert to Finding objects
            finding_id = 1
            for finding_data in coupling_findings:
                recommendation = self._get_recommendation(finding_data["pattern_type"])

                finding = ResultFormatter.create_finding(
                    f"ARCH{finding_id:03d}",
                    f"{finding_data['category']}: {finding_data['pattern_type']}",
                    finding_data["description"],
                    finding_data["severity"],
                    finding_data.get("file_path"),
                    None,  # No specific line number for architecture issues
                    recommendation,
                    {
                        "category": finding_data["category"],
                        "pattern_type": finding_data["pattern_type"],
                        "module": finding_data.get("module"),
                        "metric_value": finding_data.get("metric_value"),
                        "dependencies": finding_data.get("dependencies"),
                        "dependents": finding_data.get("dependents"),
                        "cycle": finding_data.get("cycle"),
                    },
                )
                result.add_finding(finding)
                finding_id += 1

            # Add metadata
            result.metadata = {
                **graph_stats,
                "patterns_checked": len(self.coupling_patterns),
                "circular_dependencies": len(
                    [
                        f
                        for f in coupling_findings
                        if f["pattern_type"] == "circular_dependency"
                    ]
                ),
                "high_coupling_modules": len(
                    [f for f in coupling_findings if "fan_" in f["pattern_type"]]
                ),
            }

        except Exception as e:
            result.set_error(f"Analysis failed: {str(e)}")

        result.set_execution_time(start_time)
        return result

    def _get_recommendation(self, pattern_type: str) -> str:
        """Get recommendation for specific pattern type."""
        recommendations = {
            "circular_dependency": "Break circular dependencies using dependency inversion or intermediary modules",
            "high_fan_out": "Reduce dependencies by using dependency injection or facade patterns",
            "high_fan_in": "Consider breaking large modules into smaller, focused components",
            "deep_dependency": "Flatten dependency chains and reduce coupling layers",
            "unstable_dependency": "Depend on abstractions rather than concrete implementations",
        }
        return recommendations.get(
            pattern_type, "Review architecture for coupling reduction opportunities"
        )


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze code coupling and dependency patterns"
    )
    parser.add_argument("target_path", help="Path to analyze")
    parser.add_argument(
        "--output-format",
        choices=["json", "console", "summary"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Limit output to top 10 critical/high findings for large codebases",
    )
    parser.add_argument(
        "--min-severity",
        choices=["critical", "high", "medium", "low"],
        default="low",
        help="Minimum severity level (default: low)",
    )

    args = parser.parse_args()

    analyzer = CouplingAnalyzer()
    result = analyzer.analyze(args.target_path)

    # Auto-enable summary mode for large result sets
    if len(result.findings) > 50 and not args.summary:
        print(
            f"⚠️ Large result set detected ({len(result.findings)} findings). Consider using --summary flag.",
            file=sys.stderr,
        )

    # Output based on format choice
    if args.output_format == "console":
        print(ResultFormatter.format_console_output(result))
    elif args.output_format == "summary":
        print(result.to_json(summary_mode=True, min_severity=args.min_severity))
    else:  # json (default)
        print(result.to_json(summary_mode=args.summary, min_severity=args.min_severity))
        # Also print console summary to stderr for human readability
        print(ResultFormatter.format_console_output(result), file=sys.stderr)


if __name__ == "__main__":
    main()
