#!/usr/bin/env python3
"""
Performance Bottleneck Analysis Script
Analyzes code for CPU/memory performance bottlenecks and resource usage patterns.
"""

import os
import sys
import re
import json
import time
import ast
from typing import Dict, List, Any
from collections import defaultdict

# Add utils to path for cross-platform and output_formatter imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "utils"))

try:
    from cross_platform import PlatformDetector
    from output_formatter import ResultFormatter
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class BottleneckAnalyzer:
    """Analyzes performance bottlenecks and resource usage patterns."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()

        # CPU bottleneck patterns
        self.cpu_patterns = {
            "inefficient_loops": {
                "indicators": [
                    r"for\s+.*in\s+range\(len\(",
                    r"while\s+.*:\s*\n.*for\s+.*:",
                    r"for\s+.*:\s*\n.*for\s+.*:\s*\n.*for\s+.*:",  # Triple nested loops
                    r"forEach\(.*forEach\(.*forEach\(",
                    r"map\(.*map\(.*map\(",
                ],
                "severity": "high",
                "description": "Inefficient nested loops causing CPU bottlenecks",
            },
            "redundant_computations": {
                "indicators": [
                    r"for\s+.*:\s*\n.*len\(",
                    r"while\s+.*len\(",
                    r"sort\(.*\).*sort\(",
                    r"reverse\(.*\).*reverse\(",
                    r"Math\.(sin|cos|tan|sqrt)\(.*\).*Math\.(sin|cos|tan|sqrt)\(",
                ],
                "severity": "medium",
                "description": "Redundant computations in loops",
            },
            "expensive_operations_in_loops": {
                "indicators": [
                    r"for\s+.*:\s*\n.*re\.compile\(",
                    r"while\s+.*:\s*\n.*datetime\.now\(",
                    r"for\s+.*:\s*\n.*json\.loads\(",
                    r"forEach\(.*new\s+Date\(",
                    r"map\(.*JSON\.parse\(",
                ],
                "severity": "high",
                "description": "Expensive operations inside loops",
            },
            "blocking_io_operations": {
                "indicators": [
                    r"requests\.get\((?!.*async)",
                    r"urllib\.request\.urlopen\(",
                    r'open\(.*[\'"]r[\'"].*\)(?!.*async)',
                    r"file\.read\(\)(?!.*async)",
                    r"fetch\(.*\)(?!.*\.then|await)",
                ],
                "severity": "high",
                "description": "Blocking I/O operations on main thread",
            },
        }

        # Memory bottleneck patterns
        self.memory_patterns = {
            "memory_leaks": {
                "indicators": [
                    r"global\s+\w+\s*=\s*\[\]",
                    r"cache\s*=\s*\{\}",
                    r"setInterval\(.*(?!.*clearInterval)",
                    r"addEventListener\(.*(?!.*removeEventListener)",
                    r"new\s+.*Observer\(.*(?!.*disconnect)",
                ],
                "severity": "critical",
                "description": "Potential memory leaks from uncleaned resources",
            },
            "large_object_creation": {
                "indicators": [
                    r"new\s+Array\(\s*\d{6,}\s*\)",
                    r"\[\s*\]\s*\*\s*\d{6,}",
                    r"Buffer\.alloc\(\s*\d{6,}\s*\)",
                    r"new\s+.*\(\s*\d{6,}\s*\)",
                    r"range\(\s*\d{6,}\s*\)",
                ],
                "severity": "medium",
                "description": "Large object creation that may cause memory pressure",
            },
            "inefficient_data_structures": {
                "indicators": [
                    r"for\s+.*in\s+.*:\s*\n.*list\.append\(",
                    r"while\s+.*:\s*\n.*dict\[.*\]\s*=",
                    r"for\s+.*:\s*\n.*array\.push\(",
                    r"forEach\(.*array\.push\(",
                    r"map\(.*\{\.\.\.",
                ],
                "severity": "medium",
                "description": "Inefficient data structure usage",
            },
            "string_concatenation_loops": {
                "indicators": [
                    r'for\s+.*:\s*\n.*\+\s*[\'"]',
                    r'while\s+.*:\s*\n.*\+=\s*[\'"]',
                    r"forEach\(.*\+=.*string",
                    r'map\(.*\+.*[\'"`]',
                ],
                "severity": "medium",
                "description": "String concatenation in loops causing memory allocations",
            },
        }

        # Algorithm complexity patterns
        self.algorithm_patterns = {
            "quadratic_complexity": {
                "indicators": [
                    r"for\s+.*:\s*\n.*for\s+.*:\s*\n.*if\s+.*==",
                    r"forEach\(.*forEach\(",
                    r"for\s+.*in\s+.*:\s*\n.*for\s+.*in\s+.*:",
                    r"while\s+.*:\s*\n.*while\s+.*:",
                ],
                "severity": "high",
                "description": "O(n²) algorithm complexity",
            },
            "inefficient_search": {
                "indicators": [
                    r"for\s+.*in\s+.*:\s*\n.*if\s+.*==.*break",
                    r"while\s+.*:\s*\n.*if\s+.*==.*return",
                    r"indexOf\(.*\)\s*!==\s*-1",
                    r"includes\(.*\)",
                ],
                "severity": "medium",
                "description": "Inefficient linear search where better alternatives exist",
            },
            "repeated_sorting": {
                "indicators": [
                    r"for\s+.*:\s*\n.*sort\(",
                    r"while\s+.*:\s*\n.*sort\(",
                    r"forEach\(.*sort\(",
                    r"map\(.*sort\(",
                ],
                "severity": "medium",
                "description": "Repeated sorting operations",
            },
        }

        # Database bottleneck patterns
        self.database_patterns = {
            "n_plus_one_queries": {
                "indicators": [
                    r"for\s+.*:\s*\n.*\.get\(",
                    r"for\s+.*:\s*\n.*\.find\(",
                    r"forEach\(.*\.query\(",
                    r"map\(.*\.execute\(",
                    r"for\s+.*:\s*\n.*SELECT",
                ],
                "severity": "critical",
                "description": "N+1 query problem",
            },
            "missing_pagination": {
                "indicators": [
                    r"\.all\(\)",
                    r"SELECT\s+\*\s+FROM.*(?!LIMIT)",
                    r"find\(\{\}\)(?!\.limit)",
                    r"query\(.*\)(?!\.limit)",
                ],
                "severity": "medium",
                "description": "Queries without pagination",
            },
            "inefficient_queries": {
                "indicators": [
                    r"SELECT\s+\*\s+FROM",
                    r'WHERE.*LIKE\s+[\'"]%.*%[\'"]',
                    r"ORDER\s+BY.*(?!.*INDEX)",
                    r"JOIN.*(?!.*INDEX)",
                ],
                "severity": "medium",
                "description": "Potentially inefficient database queries",
            },
        }

        # Concurrency bottleneck patterns
        self.concurrency_patterns = {
            "race_conditions": {
                "indicators": [
                    r"global\s+\w+\s*=.*(?!.*lock)",
                    r"shared.*variable.*(?!.*mutex)",
                    r"counter\s*\+=.*(?!.*atomic)",
                    r"threading.*(?!.*Lock)",
                ],
                "severity": "high",
                "description": "Potential race conditions in concurrent code",
            },
            "deadlock_risk": {
                "indicators": [
                    r"lock.*lock",
                    r"acquire.*acquire",
                    r"synchronized.*synchronized",
                    r"mutex.*mutex",
                ],
                "severity": "high",
                "description": "Potential deadlock from multiple locks",
            },
            "thread_pool_exhaustion": {
                "indicators": [
                    r"ThreadPoolExecutor\(.*\d+.*\)",
                    r"thread.*pool.*size.*\d+",
                    r"concurrent\.futures.*max_workers=\d+",
                    r"asyncio.*Semaphore\(\d+\)",
                ],
                "severity": "medium",
                "description": "Fixed thread pool sizes that may cause exhaustion",
            },
        }

    def analyze_bottlenecks(
        self, target_path: str, min_severity: str = "low"
    ) -> Dict[str, Any]:
        """Analyze performance bottlenecks in the target path."""

        start_time = time.time()
        result = ResultFormatter.create_performance_result(
            "check_bottlenecks.py", target_path
        )

        if not os.path.exists(target_path):
            result.set_error(f"Path does not exist: {target_path}")
            result.set_execution_time(start_time)
            return result.to_dict()

        bottleneck_summary = defaultdict(int)
        file_count = 0

        try:
            # Walk through all files
            for root, dirs, files in os.walk(target_path):
                # Skip common build/dependency directories
                dirs[:] = [d for d in dirs if not self._should_skip_directory(d)]

                for file in files:
                    if self._should_analyze_file(file):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, target_path)

                        try:
                            file_findings = self._analyze_file_bottlenecks(
                                file_path, relative_path
                            )
                            file_count += 1

                            # Convert findings to Finding objects
                            for finding_data in file_findings:
                                finding = ResultFormatter.create_finding(
                                    finding_id=f"BOTTLENECK_{bottleneck_summary[finding_data['bottleneck_type']] + 1:03d}",
                                    title=finding_data["bottleneck_type"]
                                    .replace("_", " ")
                                    .title(),
                                    description=finding_data["message"],
                                    severity=finding_data["severity"],
                                    file_path=finding_data["file"],
                                    line_number=finding_data["line"],
                                    recommendation=self._get_bottleneck_recommendation(
                                        finding_data["bottleneck_type"]
                                    ),
                                    evidence={
                                        "context": finding_data.get("context", ""),
                                        "category": finding_data.get(
                                            "category", "performance_bottleneck"
                                        ),
                                        "performance_impact": finding_data.get(
                                            "performance_impact", "unknown"
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
            analysis_summary = self._generate_bottleneck_summary(
                bottleneck_summary, file_count
            )
            result.metadata = analysis_summary

            result.set_execution_time(start_time)
            return result.to_dict(min_severity=min_severity)

        except Exception as e:
            result.set_error(f"Bottleneck analysis failed: {str(e)}")
            result.set_execution_time(start_time)
            return result.to_dict()

    def _analyze_file_bottlenecks(
        self, file_path: str, relative_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze performance bottlenecks in a single file."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

            # Check CPU bottleneck patterns
            findings.extend(
                self._check_bottleneck_patterns(
                    content,
                    lines,
                    relative_path,
                    self.cpu_patterns,
                    "cpu",
                    "cpu_performance",
                )
            )

            # Check memory bottleneck patterns
            findings.extend(
                self._check_bottleneck_patterns(
                    content,
                    lines,
                    relative_path,
                    self.memory_patterns,
                    "memory",
                    "memory_usage",
                )
            )

            # Check algorithm complexity patterns
            findings.extend(
                self._check_bottleneck_patterns(
                    content,
                    lines,
                    relative_path,
                    self.algorithm_patterns,
                    "algorithm",
                    "algorithm_efficiency",
                )
            )

            # Check database bottleneck patterns
            findings.extend(
                self._check_bottleneck_patterns(
                    content,
                    lines,
                    relative_path,
                    self.database_patterns,
                    "database",
                    "database_performance",
                )
            )

            # Check concurrency bottleneck patterns
            findings.extend(
                self._check_bottleneck_patterns(
                    content,
                    lines,
                    relative_path,
                    self.concurrency_patterns,
                    "concurrency",
                    "concurrency_performance",
                )
            )

            # Additional Python-specific analysis
            if file_path.endswith(".py"):
                findings.extend(
                    self._analyze_python_bottlenecks(content, lines, relative_path)
                )

        except Exception as e:
            findings.append(
                {
                    "file": relative_path,
                    "line": 0,
                    "bottleneck_type": "file_error",
                    "severity": "low",
                    "message": f"Could not analyze file: {str(e)}",
                    "category": "analysis",
                    "performance_impact": "unknown",
                }
            )

        return findings

    def _check_bottleneck_patterns(
        self,
        content: str,
        lines: List[str],
        file_path: str,
        pattern_dict: Dict,
        category: str,
        performance_impact: str,
    ) -> List[Dict[str, Any]]:
        """Check for specific bottleneck patterns in file content."""
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
                            "performance_impact": performance_impact,
                        }
                    )

        return findings

    def _analyze_python_bottlenecks(
        self, content: str, lines: List[str], file_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze Python-specific performance bottlenecks."""
        findings = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Check for global variables in loops
                if isinstance(node, (ast.For, ast.While)):
                    loop_line = getattr(node, "lineno", 0)
                    for child in ast.walk(node):
                        if isinstance(child, ast.Global):
                            findings.append(
                                {
                                    "file": file_path,
                                    "line": loop_line,
                                    "bottleneck_type": "python_global_in_loop",
                                    "severity": "medium",
                                    "message": "Global variable access in loop may impact performance",
                                    "context": lines[loop_line - 1].strip()
                                    if loop_line <= len(lines)
                                    else "",
                                    "category": "python",
                                    "performance_impact": "cpu_performance",
                                }
                            )

                # Check for list comprehensions with side effects
                if isinstance(node, ast.ListComp):
                    for generator in node.generators:
                        for if_clause in generator.ifs:
                            if isinstance(if_clause, ast.Call):
                                line_num = getattr(node, "lineno", 0)
                                findings.append(
                                    {
                                        "file": file_path,
                                        "line": line_num,
                                        "bottleneck_type": "python_complex_comprehension",
                                        "severity": "low",
                                        "message": "Complex list comprehension may impact performance",
                                        "context": lines[line_num - 1].strip()
                                        if line_num <= len(lines)
                                        else "",
                                        "category": "python",
                                        "performance_impact": "cpu_performance",
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
                    "bottleneck_type": "python_analysis_error",
                    "severity": "low",
                    "message": f"Python AST analysis failed: {str(e)}",
                    "context": "",
                    "category": "analysis",
                    "performance_impact": "unknown",
                }
            )

        return findings

    def _get_bottleneck_recommendation(self, bottleneck_type: str) -> str:
        """Get specific recommendations for performance bottlenecks."""
        recommendations = {
            "cpu_inefficient_loops": "Optimize nested loops with better algorithms or caching",
            "cpu_redundant_computations": "Cache expensive computations outside loops",
            "cpu_expensive_operations_in_loops": "Move expensive operations outside loops",
            "cpu_blocking_io_operations": "Use async/await or threading for I/O operations",
            "memory_memory_leaks": "Implement proper cleanup of resources and event listeners",
            "memory_large_object_creation": "Use streaming or chunked processing for large data",
            "memory_inefficient_data_structures": "Use appropriate data structures (sets, deques, etc.)",
            "memory_string_concatenation_loops": "Use join() or StringBuilder for string concatenation",
            "algorithm_quadratic_complexity": "Replace with O(n log n) or O(n) algorithms",
            "algorithm_inefficient_search": "Use hash tables, binary search, or indexed lookups",
            "algorithm_repeated_sorting": "Sort once and maintain order, or use appropriate data structures",
            "database_n_plus_one_queries": "Use eager loading, joins, or batch queries",
            "database_missing_pagination": "Implement LIMIT/OFFSET or cursor-based pagination",
            "database_inefficient_queries": "Add indexes, optimize WHERE clauses, avoid SELECT *",
            "concurrency_race_conditions": "Use locks, atomic operations, or thread-safe data structures",
            "concurrency_deadlock_risk": "Implement lock ordering or use lock-free algorithms",
            "concurrency_thread_pool_exhaustion": "Use dynamic thread pools or rate limiting",
            "python_global_in_loop": "Use local variables or pass globals as parameters",
            "python_complex_comprehension": "Break complex comprehensions into simpler operations",
        }
        return recommendations.get(
            bottleneck_type, "Review code for performance optimization opportunities"
        )

    def _generate_bottleneck_summary(
        self, bottleneck_summary: Dict, file_count: int
    ) -> Dict[str, Any]:
        """Generate summary of bottleneck analysis."""

        # Categorize bottlenecks by type
        categories = {
            "cpu": [k for k in bottleneck_summary.keys() if k.startswith("cpu_")],
            "memory": [k for k in bottleneck_summary.keys() if k.startswith("memory_")],
            "algorithm": [
                k for k in bottleneck_summary.keys() if k.startswith("algorithm_")
            ],
            "database": [
                k for k in bottleneck_summary.keys() if k.startswith("database_")
            ],
            "concurrency": [
                k for k in bottleneck_summary.keys() if k.startswith("concurrency_")
            ],
            "python": [k for k in bottleneck_summary.keys() if k.startswith("python_")],
        }

        total_issues = sum(bottleneck_summary.values())
        severity_counts = self._count_by_severity(bottleneck_summary)

        return {
            "total_files_analyzed": file_count,
            "total_bottlenecks": total_issues,
            "bottlenecks_by_category": {
                category: {
                    "count": sum(
                        bottleneck_summary.get(bottleneck, 0)
                        for bottleneck in bottlenecks
                    ),
                    "bottlenecks": {
                        bottleneck.replace(f"{category}_", ""): bottleneck_summary.get(
                            bottleneck, 0
                        )
                        for bottleneck in bottlenecks
                        if bottleneck_summary.get(bottleneck, 0) > 0
                    },
                }
                for category, bottlenecks in categories.items()
            },
            "severity_breakdown": severity_counts,
            "performance_score": self._calculate_performance_score(
                total_issues, file_count
            ),
            "critical_bottlenecks": self._get_critical_bottlenecks(bottleneck_summary),
            "recommendations": self._generate_priority_recommendations(
                bottleneck_summary
            ),
        }

    def _count_by_severity(self, bottleneck_summary: Dict) -> Dict[str, int]:
        """Count bottlenecks by severity level."""
        severity_mapping = {
            "critical": ["memory_leaks", "n_plus_one_queries"],
            "high": [
                "inefficient_loops",
                "expensive_operations_in_loops",
                "blocking_io_operations",
                "quadratic_complexity",
                "race_conditions",
                "deadlock_risk",
            ],
            "medium": [
                "redundant_computations",
                "large_object_creation",
                "inefficient_data_structures",
                "string_concatenation_loops",
                "inefficient_search",
                "repeated_sorting",
                "missing_pagination",
                "inefficient_queries",
                "thread_pool_exhaustion",
                "global_in_loop",
            ],
            "low": ["complex_comprehension", "file_error", "analysis_error"],
        }

        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for bottleneck, count in bottleneck_summary.items():
            bottleneck_name = bottleneck.split("_", 1)[-1]  # Remove category prefix
            for severity, patterns in severity_mapping.items():
                if bottleneck_name in patterns:
                    counts[severity] += count
                    break

        return counts

    def _calculate_performance_score(self, total_issues: int, file_count: int) -> float:
        """Calculate a performance score (0-100, higher is better)."""
        if file_count == 0:
            return 100.0

        issue_density = total_issues / file_count
        # Score decreases with issue density, with critical bottlenecks having heavy impact
        score = max(0, 100 - (issue_density * 18))
        return round(score, 1)

    def _get_critical_bottlenecks(
        self, bottleneck_summary: Dict
    ) -> List[Dict[str, Any]]:
        """Get critical bottlenecks requiring immediate attention."""
        critical_patterns = [
            "memory_leaks",
            "n_plus_one_queries",
            "inefficient_loops",
            "blocking_io_operations",
        ]
        critical_bottlenecks = []

        for bottleneck, count in bottleneck_summary.items():
            bottleneck_name = bottleneck.split("_", 1)[-1]
            if bottleneck_name in critical_patterns and count > 0:
                critical_bottlenecks.append(
                    {
                        "bottleneck": bottleneck.replace("_", " ").title(),
                        "count": count,
                        "severity": "critical"
                        if bottleneck_name in ["memory_leaks", "n_plus_one_queries"]
                        else "high",
                        "category": bottleneck.split("_")[0],
                    }
                )

        return critical_bottlenecks

    def _generate_priority_recommendations(self, bottleneck_summary: Dict) -> List[str]:
        """Generate priority recommendations based on findings."""
        recommendations = []

        # Critical bottlenecks first
        if any("memory_leaks" in k for k in bottleneck_summary.keys()):
            recommendations.append(
                "CRITICAL: Fix memory leaks to prevent application crashes"
            )
        if any("n_plus_one_queries" in k for k in bottleneck_summary.keys()):
            recommendations.append(
                "CRITICAL: Optimize N+1 query problems with batch loading"
            )

        # High impact bottlenecks
        if any("inefficient_loops" in k for k in bottleneck_summary.keys()):
            recommendations.append("HIGH: Optimize nested loops with better algorithms")
        if any("blocking_io_operations" in k for k in bottleneck_summary.keys()):
            recommendations.append(
                "HIGH: Convert blocking I/O to asynchronous operations"
            )
        if any("quadratic_complexity" in k for k in bottleneck_summary.keys()):
            recommendations.append(
                "HIGH: Replace O(n²) algorithms with more efficient alternatives"
            )

        # General recommendations
        total_issues = sum(bottleneck_summary.values())
        if total_issues > 20:
            recommendations.append("Consider performance profiling and load testing")

        return recommendations[:5]

    def _should_skip_directory(self, directory: str) -> bool:
        """Check if directory should be skipped."""
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
        """Check if file should be analyzed."""
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
        description="Analyze performance bottlenecks in codebase"
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
        help="Output format",
    )

    args = parser.parse_args()

    analyzer = BottleneckAnalyzer()
    result = analyzer.analyze_bottlenecks(args.target_path, args.min_severity)

    if args.output_format == "console":
        # Simple console output
        if result.get("success", False):
            print(f"Performance Bottleneck Analysis Results for: {args.target_path}")
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
