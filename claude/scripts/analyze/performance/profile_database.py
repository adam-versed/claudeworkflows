#!/usr/bin/env python3
"""
Performance analysis script: Database query analysis and N+1 detection.
Part of Claude Code Workflows.
"""

import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add utils to path for imports
script_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(script_dir / "utils"))

try:
    from output_formatter import ResultFormatter, AnalysisResult
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class DatabaseProfiler:
    """Analyze database usage patterns for performance issues."""

    def __init__(self):
        # N+1 Query patterns
        self.n_plus_one_patterns = {
            "loop_query": {
                "pattern": r"for\s+\w+\s+in\s+.*?:\s*[\s\S]*?(?:\.query\(|\.get\(|\.filter\(|\.find\()",
                "severity": "high",
                "description": "Potential N+1 query in loop",
            },
            "foreach_query": {
                "pattern": r"(?:forEach|map|each)\s*\(\s*.*?(?:query|find|get|select)",
                "severity": "high",
                "description": "Potential N+1 query in iteration",
            },
            "nested_query": {
                "pattern": r"(?:\.query\(|\.find\(|\.get\()[\s\S]*?(?:\.query\(|\.find\(|\.get\()",
                "severity": "medium",
                "description": "Nested database queries detected",
            },
        }

        # Slow query patterns
        self.slow_query_patterns = {
            "missing_where": {
                "pattern": r"(?:SELECT|select)(?![^\'\"]*[\'\"]).+(?:FROM|from)\s+\w+(?![^\'\"]*[\'\"]\s*[;,)])(?!\s+(?:WHERE|where))",
                "severity": "high",
                "description": "Query without WHERE clause - potential table scan",
            },
            "select_all": {
                "pattern": r"(?:SELECT|select)\s+\*\s+(?:FROM|from)",
                "severity": "medium",
                "description": "SELECT * query - may fetch unnecessary data",
            },
            "no_limit": {
                "pattern": r"(?:SELECT|select)(?![^\'\"]*[\'\"]).+(?:FROM|from)\s+\w+(?![^\'\"]*[\'\"]\s*[;,)])(?!\s+(?:LIMIT|limit|TOP|top))",
                "severity": "medium",
                "description": "Query without LIMIT - may return large result set",
            },
            "like_prefix": {
                "pattern": r"(?:LIKE|like)\s+[\'\"]\%",
                "severity": "medium",
                "description": "LIKE query with leading wildcard - cannot use index",
            },
        }

        # ORM lazy loading patterns
        self.orm_patterns = {
            "eager_loading": {
                "pattern": r"\.include\(|\.populate\(|\.with\(|\.join\(",
                "severity": "info",
                "description": "Eager loading used - good practice",
            },
            "lazy_access": {
                "pattern": r"\w+\.\w+(?:\.\w+)*\.(?:count|length|size)\s*(?:\(\))?",
                "severity": "medium",
                "description": "Potential lazy loading access",
            },
        }

        # File extensions to scan
        self.code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".sql",
            ".prisma",
            ".kt",
            ".scala",
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
            "migrations",
        }

    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned."""
        # Skip directories in skip_patterns
        for part in file_path.parts:
            if part in self.skip_patterns:
                return False

        # Check file extension
        suffix = file_path.suffix.lower()
        return suffix in self.code_extensions

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Scan a single file for database performance issues.

        Returns:
            List of findings dictionaries
        """
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

                # Check N+1 patterns
                for pattern_name, pattern_info in self.n_plus_one_patterns.items():
                    findings.extend(
                        self._find_pattern_matches(
                            content,
                            lines,
                            file_path,
                            pattern_name,
                            pattern_info,
                            "N+1 Query",
                        )
                    )

                # Check slow query patterns
                for pattern_name, pattern_info in self.slow_query_patterns.items():
                    findings.extend(
                        self._find_pattern_matches(
                            content,
                            lines,
                            file_path,
                            pattern_name,
                            pattern_info,
                            "Slow Query",
                        )
                    )

                # Check ORM patterns
                for pattern_name, pattern_info in self.orm_patterns.items():
                    findings.extend(
                        self._find_pattern_matches(
                            content,
                            lines,
                            file_path,
                            pattern_name,
                            pattern_info,
                            "ORM Usage",
                        )
                    )

        except Exception:
            # Log error but continue scanning
            pass

        return findings

    def _find_pattern_matches(
        self,
        content: str,
        lines: List[str],
        file_path: Path,
        pattern_name: str,
        pattern_info: Dict[str, str],
        category: str,
    ) -> List[Dict[str, Any]]:
        """Find matches for a specific pattern."""
        findings = []

        matches = re.finditer(
            pattern_info["pattern"], content, re.MULTILINE | re.IGNORECASE
        )

        for match in matches:
            # Find line number
            line_start = content[: match.start()].count("\n") + 1

            # Get context lines
            context_start = max(0, line_start - 2)
            context_end = min(len(lines), line_start + 2)
            context_lines = lines[context_start:context_end]

            finding = {
                "category": category,
                "pattern_type": pattern_name,
                "file_path": str(file_path),
                "line_number": line_start,
                "line_content": lines[line_start - 1].strip()
                if line_start <= len(lines)
                else "",
                "context": "\n".join(context_lines),
                "matched_text": match.group(0)[:100],  # Limit length
                "severity": pattern_info["severity"],
                "description": pattern_info["description"],
            }
            findings.append(finding)

        return findings

    def scan_directory(self, target_path: str) -> List[Dict[str, Any]]:
        """
        Scan directory recursively for database performance issues.

        Args:
            target_path: Path to scan

        Returns:
            List of all findings
        """
        all_findings = []
        target = Path(target_path)

        if target.is_file():
            if self.should_scan_file(target):
                all_findings.extend(self.scan_file(target))
        elif target.is_dir():
            for file_path in target.rglob("*"):
                if file_path.is_file() and self.should_scan_file(file_path):
                    all_findings.extend(self.scan_file(file_path))

        return all_findings

    def analyze(self, target_path: str) -> AnalysisResult:
        """
        Main analysis function.

        Args:
            target_path: Path to analyze

        Returns:
            AnalysisResult object
        """
        start_time = time.time()
        result = ResultFormatter.create_performance_result(
            "profile_database.py", target_path
        )

        try:
            # Scan for database issues
            findings = self.scan_directory(target_path)

            # Convert to Finding objects
            finding_id = 1
            for finding_data in findings:
                # Determine severity and recommendation
                severity = finding_data["severity"]
                recommendation = self._get_recommendation(finding_data["pattern_type"])

                finding = ResultFormatter.create_finding(
                    f"PERF{finding_id:03d}",
                    f"{finding_data['category']}: {finding_data['pattern_type']}",
                    finding_data["description"],
                    severity,
                    finding_data["file_path"],
                    finding_data["line_number"],
                    recommendation,
                    {
                        "category": finding_data["category"],
                        "pattern_type": finding_data["pattern_type"],
                        "line_content": finding_data["line_content"],
                        "context": finding_data["context"],
                        "matched_text": finding_data["matched_text"],
                    },
                )
                result.add_finding(finding)
                finding_id += 1

            # Add metadata
            unique_files = set(f["file_path"] for f in findings)
            result.metadata = {
                "files_scanned": len(unique_files),
                "patterns_checked": len(self.n_plus_one_patterns)
                + len(self.slow_query_patterns)
                + len(self.orm_patterns),
                "categories": {
                    "n_plus_one": len(
                        [f for f in findings if f["category"] == "N+1 Query"]
                    ),
                    "slow_query": len(
                        [f for f in findings if f["category"] == "Slow Query"]
                    ),
                    "orm_usage": len(
                        [f for f in findings if f["category"] == "ORM Usage"]
                    ),
                },
            }

        except Exception as e:
            result.set_error(f"Analysis failed: {str(e)}")

        result.set_execution_time(start_time)
        return result

    def _get_recommendation(self, pattern_type: str) -> str:
        """Get recommendation for specific pattern type."""
        recommendations = {
            "loop_query": "Use eager loading or batch queries to avoid N+1 problem",
            "foreach_query": "Consider bulk operations or eager loading instead",
            "nested_query": "Refactor to use joins or single query with subqueries",
            "missing_where": "Add WHERE clause to filter results and use indexes",
            "select_all": "Select only necessary columns to reduce data transfer",
            "no_limit": "Add LIMIT clause to prevent large result sets",
            "like_prefix": "Avoid leading wildcards; consider full-text search",
            "eager_loading": "Good practice - continue using eager loading",
            "lazy_access": "Consider eager loading for frequently accessed relations",
        }
        return recommendations.get(
            pattern_type, "Review query performance and optimization opportunities"
        )


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze database usage patterns and performance issues"
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

    profiler = DatabaseProfiler()
    result = profiler.analyze(args.target_path)

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
