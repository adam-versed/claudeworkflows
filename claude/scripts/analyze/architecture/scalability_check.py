#!/usr/bin/env python3
"""
Scalability Analysis Script
Analyzes code for potential scalability bottlenecks and architectural constraints.
"""

import os
import sys
import re
import json
import ast
import time
from typing import Dict, List, Any
from collections import defaultdict

# Add utils to path for cross-platform and output_formatter imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "utils"))

try:
    from cross_platform import PlatformDetector
    from output_formatter import ResultFormatter
    from tech_stack_detector import TechStackDetector
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class ScalabilityAnalyzer:
    """Analyzes code for scalability bottlenecks and architectural constraints."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()
        self.tech_detector = TechStackDetector()

        # Database scalability patterns
        self.db_patterns = {
            "n_plus_one": {
                "indicators": [
                    r"for\s+\w+\s+in\s+\w+.*:\s*\n.*\.(get|find|query)\(",
                    r"\.all\(\).*for\s+",
                    r"while\s+.*:\s*\n.*\.(get|find|query)\(",
                    r"forEach.*\.(get|find|query)\(",
                ],
                "severity": "high",
                "description": "Potential N+1 query problem",
            },
            "missing_indexes": {
                "indicators": [
                    r"WHERE\s+\w+\s*=",
                    r"ORDER\s+BY\s+\w+",
                    r"\.filter\(\w+\s*=",
                    r"\.where\(\w+\s*=",
                ],
                "severity": "medium",
                "description": "Query without explicit index consideration",
            },
            "large_result_sets": {
                "indicators": [
                    r"\.all\(\)",
                    r"SELECT\s+\*\s+FROM",
                    r"fetchall\(\)",
                    r"find\(\{\}\)",
                ],
                "severity": "medium",
                "description": "Potentially unbounded result set",
            },
            "no_pagination": {
                "indicators": [
                    r"\.all\(\)",
                    r"fetchall\(\)",
                    r"SELECT.*FROM.*(?!LIMIT)",
                    r"find\(\)(?!\.limit)",
                ],
                "severity": "medium",
                "description": "Query without pagination",
            },
        }

        # Performance bottleneck patterns
        self.performance_patterns = {
            "synchronous_io": {
                "indicators": [
                    r"requests\.get\(",
                    r"urllib\.request\.",
                    r"httplib\.",
                    r'open\(.*[\'"]r[\'"]',
                    r"sleep\(",
                    r"time\.sleep\(",
                ],
                "severity": "high",
                "description": "Synchronous I/O operation",
            },
            "nested_loops": {
                "indicators": [
                    r"for\s+.*:\s*\n.*for\s+.*:\s*\n.*for\s+",  # Triple nested
                    r"while\s+.*:\s*\n.*while\s+.*:\s*\n.*while\s+",
                ],
                "severity": "high",
                "description": "Deep nested loops (O(n³) or worse)",
            },
            "inefficient_algorithms": {
                "indicators": [
                    r"\.sort\(\).*\.sort\(\)",  # Multiple sorts
                    r"in\s+range\(len\(",  # Inefficient iteration
                    r"list\(.*\)\[0\]",  # Inefficient first element access
                ],
                "severity": "medium",
                "description": "Potentially inefficient algorithm",
            },
            "memory_leaks": {
                "indicators": [
                    r"global\s+\w+.*=.*\[\]",  # Global collections
                    r"while\s+True:.*append\(",  # Unbounded growth
                    r"cache\s*=\s*\{\}",  # Unbounded cache
                ],
                "severity": "high",
                "description": "Potential memory leak",
            },
        }

        # Concurrency and scaling patterns
        self.concurrency_patterns = {
            "thread_safety": {
                "indicators": [
                    r"global\s+\w+",
                    r"class\s+\w+.*:\s*\n.*\w+\s*=\s*\[\]",  # Shared mutable state
                    r"threading\.Thread",
                    r"multiprocessing\.",
                ],
                "severity": "high",
                "description": "Potential thread safety issue",
            },
            "blocking_operations": {
                "indicators": [
                    r"\.join\(\)",
                    r"\.wait\(\)",
                    r"input\(\)",
                    r"raw_input\(\)",
                    r"time\.sleep\(",
                ],
                "severity": "medium",
                "description": "Blocking operation that may affect scalability",
            },
            "resource_contention": {
                "indicators": [
                    r"lock\s*=\s*",
                    r"Lock\(\)",
                    r"RLock\(\)",
                    r"Semaphore\(",
                    r"mutex",
                ],
                "severity": "medium",
                "description": "Resource locking that may limit scalability",
            },
        }

        # Architecture scalability patterns
        self.architecture_patterns = {
            "tight_coupling": {
                "indicators": [
                    r"import\s+\w+\.\w+\.\w+\.\w+",  # Deep imports
                    r"from\s+\w+\.\w+\.\w+\.\w+",
                    r"\w+\.\w+\.\w+\.\w+\(",  # Deep method chaining
                ],
                "severity": "medium",
                "description": "Tight coupling that may hinder scaling",
            },
            "hardcoded_config": {
                "indicators": [
                    r'host\s*=\s*[\'"]localhost[\'"]',
                    r"port\s*=\s*\d+",
                    r'password\s*=\s*[\'"]',
                    r'url\s*=\s*[\'"]http://',
                    r'database\s*=\s*[\'"]',
                ],
                "severity": "high",
                "description": "Hardcoded configuration limits scalability",
            },
            "single_responsibility": {
                "indicators": [
                    r"class\s+\w+.*:\s*(?:\n.*){50,}",  # Very large classes
                    r"def\s+\w+.*:\s*(?:\n.*){30,}",  # Very large methods
                ],
                "severity": "medium",
                "description": "Violation of single responsibility principle",
            },
        }

    def analyze_scalability(
        self, target_path: str, min_severity: str = "low"
    ) -> Dict[str, Any]:
        """Analyze scalability bottlenecks in the target path."""

        start_time = time.time()
        result = ResultFormatter.create_architecture_result(
            "scalability_check.py", target_path
        )

        if not os.path.exists(target_path):
            result.set_error(f"Path does not exist: {target_path}")
            result.set_execution_time(start_time)
            return result.to_dict()

        bottleneck_summary = defaultdict(int)
        file_count = 0

        try:
            # Get tech stack-aware filtering rules
            exclusion_patterns = self.tech_detector.get_exclusion_patterns(target_path)

            # Walk through all files
            for root, dirs, files in os.walk(target_path):
                # Skip directories based on tech stack detection
                dirs[:] = [
                    d
                    for d in dirs
                    if not self._should_skip_directory_smart(
                        d, root, target_path, exclusion_patterns
                    )
                ]

                for file in files:
                    if self._should_analyze_file_smart(
                        file, root, target_path, exclusion_patterns
                    ):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, target_path)

                        try:
                            file_findings = self._analyze_file_scalability(
                                file_path, relative_path
                            )
                            file_count += 1

                            # Convert findings to Finding objects
                            for finding_data in file_findings:
                                finding = ResultFormatter.create_finding(
                                    finding_id=f"SCALE_{bottleneck_summary[finding_data['bottleneck_type']] + 1:03d}",
                                    title=finding_data["bottleneck_type"]
                                    .replace("_", " ")
                                    .title(),
                                    description=finding_data["message"],
                                    severity=finding_data["severity"],
                                    file_path=finding_data["file"],
                                    line_number=finding_data["line"],
                                    recommendation=finding_data.get(
                                        "recommendation",
                                        "Review for scalability improvements",
                                    ),
                                    evidence={
                                        "context": finding_data.get("context", ""),
                                        "category": finding_data.get(
                                            "category", "unknown"
                                        ),
                                    },
                                )
                                result.add_finding(finding)
                                bottleneck_summary[finding_data["bottleneck_type"]] += 1

                        except Exception as e:
                            error_finding = ResultFormatter.create_finding(
                                finding_id=f"ERROR_{file_count:03d}",
                                title="Analysis Error",
                                description=f"Error analyzing file: {str(e)}",
                                severity="low",
                                file_path=relative_path,
                                line_number=0,
                            )
                            result.add_finding(error_finding)

            # Generate analysis summary
            analysis_summary = self._generate_scalability_summary(
                bottleneck_summary, file_count
            )
            result.metadata = analysis_summary

            result.set_execution_time(start_time)
            return result.to_dict(min_severity=min_severity)

        except Exception as e:
            result.set_error(f"Scalability analysis failed: {str(e)}")
            result.set_execution_time(start_time)
            return result.to_dict()

    def _analyze_file_scalability(
        self, file_path: str, relative_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze scalability issues in a single file."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

            # Check database scalability patterns
            findings.extend(
                self._check_scalability_patterns(
                    content, lines, relative_path, self.db_patterns, "database"
                )
            )

            # Check performance patterns
            findings.extend(
                self._check_scalability_patterns(
                    content,
                    lines,
                    relative_path,
                    self.performance_patterns,
                    "performance",
                )
            )

            # Check concurrency patterns
            findings.extend(
                self._check_scalability_patterns(
                    content,
                    lines,
                    relative_path,
                    self.concurrency_patterns,
                    "concurrency",
                )
            )

            # Check architecture patterns
            findings.extend(
                self._check_scalability_patterns(
                    content,
                    lines,
                    relative_path,
                    self.architecture_patterns,
                    "architecture",
                )
            )

            # Additional complexity analysis
            if file_path.endswith(".py"):
                findings.extend(
                    self._analyze_python_complexity(content, lines, relative_path)
                )

        except Exception as e:
            findings.append(
                {
                    "file": relative_path,
                    "line": 0,
                    "bottleneck_type": "file_error",
                    "severity": "low",
                    "message": f"Could not analyze file: {str(e)}",
                }
            )

        return findings

    def _check_scalability_patterns(
        self,
        content: str,
        lines: List[str],
        file_path: str,
        pattern_dict: Dict,
        category: str,
    ) -> List[Dict[str, Any]]:
        """Check for specific scalability patterns in file content."""
        findings = []

        for pattern_name, pattern_info in pattern_dict.items():
            for indicator in pattern_info["indicators"]:
                matches = re.finditer(indicator, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    findings.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "bottleneck_type": f"{category}_{pattern_name}",
                            "severity": pattern_info["severity"],
                            "message": f"{pattern_info['description']} ({pattern_name})",
                            "context": lines[line_num - 1].strip()
                            if line_num <= len(lines)
                            else "",
                            "category": category,
                            "recommendation": self._get_recommendation(
                                pattern_name, category
                            ),
                        }
                    )

        return findings

    def _analyze_python_complexity(
        self, content: str, lines: List[str], file_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze Python-specific complexity that affects scalability."""
        findings = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Check for deeply nested loops
                if isinstance(node, (ast.For, ast.While)):
                    nesting_level = self._count_nesting_level(node, tree)
                    if nesting_level >= 3:
                        line_num = getattr(node, "lineno", 0)
                        findings.append(
                            {
                                "file": file_path,
                                "line": line_num,
                                "bottleneck_type": "algorithmic_complexity",
                                "severity": "high",
                                "message": f"Deeply nested loop (level {nesting_level}) - O(n^{nesting_level}) complexity",
                                "context": lines[line_num - 1].strip()
                                if line_num <= len(lines)
                                else "",
                                "category": "performance",
                                "recommendation": "Consider algorithm optimization or caching",
                            }
                        )

                # Check for large list comprehensions
                if isinstance(node, ast.ListComp):
                    if len(node.generators) > 2:  # Multiple generators
                        line_num = getattr(node, "lineno", 0)
                        findings.append(
                            {
                                "file": file_path,
                                "line": line_num,
                                "bottleneck_type": "complex_comprehension",
                                "severity": "medium",
                                "message": "Complex list comprehension may impact performance",
                                "context": lines[line_num - 1].strip()
                                if line_num <= len(lines)
                                else "",
                                "category": "performance",
                                "recommendation": "Consider breaking into simpler operations",
                            }
                        )

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            findings.append(
                {
                    "file": file_path,
                    "line": 0,
                    "bottleneck_type": "ast_analysis_error",
                    "severity": "low",
                    "message": f"AST analysis failed: {str(e)}",
                    "context": "",
                    "category": "analysis",
                    "recommendation": "Manual review required",
                }
            )

        return findings

    def _count_nesting_level(self, target_node, tree) -> int:
        """Count the nesting level of loops."""
        level = 0

        def count_parent_loops(node):
            nonlocal level
            for child in ast.iter_child_nodes(node):
                if child == target_node:
                    return True
                if isinstance(child, (ast.For, ast.While)):
                    level += 1
                    if count_parent_loops(child):
                        return True
                    level -= 1
                elif count_parent_loops(child):
                    return True
            return False

        count_parent_loops(tree)
        return level

    def _get_recommendation(self, pattern_name: str, category: str) -> str:
        """Get specific recommendations for scalability issues."""
        recommendations = {
            "n_plus_one": "Use eager loading, batch queries, or caching",
            "missing_indexes": "Add database indexes for frequently queried columns",
            "large_result_sets": "Implement pagination or result limiting",
            "no_pagination": "Add LIMIT clauses and pagination support",
            "synchronous_io": "Use async/await or threading for I/O operations",
            "nested_loops": "Optimize algorithm complexity or use caching",
            "inefficient_algorithms": "Review algorithm choice and data structures",
            "memory_leaks": "Implement proper cleanup and bounded collections",
            "thread_safety": "Use thread-safe data structures and proper synchronization",
            "blocking_operations": "Use non-blocking alternatives or background processing",
            "resource_contention": "Minimize lock scope and consider lock-free algorithms",
            "tight_coupling": "Implement dependency injection and interface abstraction",
            "hardcoded_config": "Use environment variables or configuration files",
            "single_responsibility": "Refactor into smaller, focused components",
        }
        return recommendations.get(pattern_name, "Review and optimize this pattern")

    def _generate_scalability_summary(
        self, bottleneck_summary: Dict, file_count: int
    ) -> Dict[str, Any]:
        """Generate summary of scalability analysis."""

        # Categorize bottlenecks
        categories = {
            "database": [
                k for k in bottleneck_summary.keys() if k.startswith("database_")
            ],
            "performance": [
                k for k in bottleneck_summary.keys() if k.startswith("performance_")
            ],
            "concurrency": [
                k for k in bottleneck_summary.keys() if k.startswith("concurrency_")
            ],
            "architecture": [
                k for k in bottleneck_summary.keys() if k.startswith("architecture_")
            ],
        }

        total_issues = sum(bottleneck_summary.values())
        severity_counts = self._count_by_severity(bottleneck_summary)

        return {
            "total_files_analyzed": file_count,
            "total_scalability_issues": total_issues,
            "issues_by_category": {
                category: {
                    "count": sum(bottleneck_summary.get(issue, 0) for issue in issues),
                    "issues": {
                        issue.replace(f"{category}_", ""): bottleneck_summary.get(
                            issue, 0
                        )
                        for issue in issues
                        if bottleneck_summary.get(issue, 0) > 0
                    },
                }
                for category, issues in categories.items()
            },
            "severity_breakdown": severity_counts,
            "scalability_score": self._calculate_scalability_score(
                total_issues, file_count
            ),
            "top_concerns": self._get_top_concerns(bottleneck_summary),
            "recommendations": self._generate_priority_recommendations(
                bottleneck_summary
            ),
        }

    def _count_by_severity(self, bottleneck_summary: Dict) -> Dict[str, int]:
        """Count issues by severity level."""
        # This is a simplified mapping - in reality, we'd need to track severity per finding
        severity_mapping = {
            "high": [
                "n_plus_one",
                "synchronous_io",
                "nested_loops",
                "memory_leaks",
                "thread_safety",
                "hardcoded_config",
            ],
            "medium": [
                "missing_indexes",
                "large_result_sets",
                "no_pagination",
                "inefficient_algorithms",
                "blocking_operations",
                "resource_contention",
                "tight_coupling",
                "single_responsibility",
            ],
            "low": ["analysis_error", "file_error"],
        }

        counts = {"high": 0, "medium": 0, "low": 0}
        for issue, count in bottleneck_summary.items():
            issue_name = issue.split("_", 1)[-1]  # Remove category prefix
            for severity, patterns in severity_mapping.items():
                if issue_name in patterns:
                    counts[severity] += count
                    break

        return counts

    def _calculate_scalability_score(self, total_issues: int, file_count: int) -> float:
        """Calculate a scalability score (0-100, higher is better)."""
        if file_count == 0:
            return 100.0

        issue_density = total_issues / file_count
        # Score decreases with issue density, floor at 0
        score = max(0, 100 - (issue_density * 10))
        return round(score, 1)

    def _get_top_concerns(self, bottleneck_summary: Dict) -> List[Dict[str, Any]]:
        """Get the top scalability concerns."""
        sorted_issues = sorted(
            bottleneck_summary.items(), key=lambda x: x[1], reverse=True
        )
        return [
            {
                "issue": issue.replace("_", " ").title(),
                "count": count,
                "category": issue.split("_")[0] if "_" in issue else "unknown",
            }
            for issue, count in sorted_issues[:5]
            if count > 0
        ]

    def _generate_priority_recommendations(self, bottleneck_summary: Dict) -> List[str]:
        """Generate priority recommendations based on findings."""
        recommendations = []

        # High priority issues
        high_priority = [
            "n_plus_one",
            "synchronous_io",
            "memory_leaks",
            "hardcoded_config",
        ]
        for issue in high_priority:
            if any(issue in k for k in bottleneck_summary.keys()):
                if "n_plus_one" in issue:
                    recommendations.append(
                        "HIGH: Implement query optimization and eager loading"
                    )
                elif "synchronous_io" in issue:
                    recommendations.append(
                        "HIGH: Convert to asynchronous I/O operations"
                    )
                elif "memory_leaks" in issue:
                    recommendations.append("HIGH: Implement proper resource cleanup")
                elif "hardcoded_config" in issue:
                    recommendations.append(
                        "HIGH: Externalize configuration for environment scalability"
                    )

        # Medium priority issues
        medium_priority = ["nested_loops", "missing_indexes", "thread_safety"]
        for issue in medium_priority:
            if any(issue in k for k in bottleneck_summary.keys()):
                if "nested_loops" in issue:
                    recommendations.append("MEDIUM: Optimize algorithmic complexity")
                elif "missing_indexes" in issue:
                    recommendations.append(
                        "MEDIUM: Add database indexes for performance"
                    )
                elif "thread_safety" in issue:
                    recommendations.append("MEDIUM: Review concurrency safety")

        # General recommendations
        total_issues = sum(bottleneck_summary.values())
        if total_issues > 20:
            recommendations.append("Consider architectural review for scalability")

        return recommendations[:5]  # Limit to top 5 recommendations

    def _should_skip_directory_smart(
        self,
        directory: str,
        current_root: str,
        target_path: str,
        exclusion_patterns: set,
    ) -> bool:
        """Smart directory filtering based on tech stack detection."""
        # Create relative path for pattern matching
        rel_path = os.path.relpath(os.path.join(current_root, directory), target_path)

        # Check against exclusion patterns
        for pattern in exclusion_patterns:
            if self._matches_exclusion_pattern(rel_path, pattern):
                return True

        # Fallback to basic skip logic
        return self._should_skip_directory(directory)

    def _should_analyze_file_smart(
        self,
        filename: str,
        current_root: str,
        target_path: str,
        exclusion_patterns: set,
    ) -> bool:
        """Smart file filtering based on tech stack detection."""
        # Create relative path for pattern matching
        rel_path = os.path.relpath(os.path.join(current_root, filename), target_path)

        # Check against exclusion patterns
        for pattern in exclusion_patterns:
            if self._matches_exclusion_pattern(rel_path, pattern):
                return False

        # Check if it's a source file we should analyze
        return self._should_analyze_file(filename)

    def _matches_exclusion_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches exclusion pattern."""
        import fnmatch

        # Handle glob patterns
        if "**" in pattern:
            # Convert ** to * for fnmatch
            pattern = pattern.replace("**", "*")

        return fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            file_path, pattern.replace("/", os.sep)
        )

    def _should_skip_directory(self, directory: str) -> bool:
        """Check if directory should be skipped (legacy method)."""
        skip_dirs = {
            "node_modules",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "build",
            "dist",
            ".next",
            ".nuxt",
            "coverage",
            "venv",
            "env",
            ".env",
            "vendor",
            "logs",
        }
        return directory in skip_dirs or directory.startswith(".")

    def _should_analyze_file(self, filename: str) -> bool:
        """Check if file should be analyzed (legacy method)."""
        analyze_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cs",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".swift",
            ".kt",
            ".scala",
            ".sql",
        }
        return any(filename.endswith(ext) for ext in analyze_extensions)


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze scalability bottlenecks in codebase"
    )
    parser.add_argument("target_path", help="Path to analyze")
    parser.add_argument(
        "--min-severity",
        choices=["low", "medium", "high", "critical"],
        default="low",
        help="Minimum severity level to report",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "console"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    analyzer = ScalabilityAnalyzer()
    result = analyzer.analyze_scalability(args.target_path, args.min_severity)

    if args.output_format == "console":
        # Simple console output
        if result.get("success", False):
            print(f"Scalability Analysis Results for: {args.target_path}")
            print(f"Analysis Type: {result.get('analysis_type', 'unknown')}")
            print(f"Execution Time: {result.get('execution_time', 0)}s")
            print(f"\nFindings: {len(result.get('findings', []))}")
            for finding in result.get("findings", []):
                file_path = finding.get("file_path", "unknown")
                line = finding.get("line_number", 0)
                desc = finding.get("description", "No description")
                severity = finding.get("severity", "unknown")
                print(f"  {file_path}:{line} - {desc} [{severity}]")
        else:
            error_msg = result.get("error_message", "Unknown error")
            print(f"Error: {error_msg}")
    else:  # json (default)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
