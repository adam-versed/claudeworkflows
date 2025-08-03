#!/usr/bin/env python3
"""
Input Validation Analysis Script
Analyzes code for input validation vulnerabilities and injection attack vectors.
"""

import os
import sys
import re
import json
import time
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


class InputValidationAnalyzer:
    """Analyzes input validation and injection vulnerabilities."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()

        # Input validation patterns
        self.validation_patterns = {
            "missing_input_validation": {
                "indicators": [
                    r"request\.(args|form|json).*(?!.*validat)",
                    r"input\(.*\).*(?!.*validat)",
                    r"params\[.*\].*(?!.*check)",
                    r"query\[.*\].*(?!.*sanitiz)",
                    r"POST.*data.*(?!.*validat)",
                ],
                "severity": "high",
                "description": "Missing input validation",
            },
            "insufficient_sanitization": {
                "indicators": [
                    r"user.*input.*(?!.*escape|.*sanitiz|.*clean)",
                    r"request.*data.*(?!.*filter|.*validat)",
                    r"form.*data.*(?!.*sanitiz)",
                    r"query.*param.*(?!.*escape)",
                ],
                "severity": "medium",
                "description": "Insufficient input sanitization",
            },
            "direct_user_input": {
                "indicators": [
                    r"eval\(.*request",
                    r"exec\(.*user",
                    r"system\(.*input",
                    r"shell_exec\(.*user",
                ],
                "severity": "critical",
                "description": "Direct execution of user input",
            },
            "regex_injection": {
                "indicators": [
                    r"re\.compile\(.*user",
                    r"regex\(.*input",
                    r"pattern.*=.*request",
                    r"match\(.*user.*input",
                ],
                "severity": "medium",
                "description": "Potential regex injection vulnerability",
            },
        }

        # SQL injection patterns
        self.sql_injection_patterns = {
            "string_concatenation": {
                "indicators": [
                    r"SELECT.*\+.*request",
                    r"INSERT.*\+.*user",
                    r"UPDATE.*\+.*input",
                    r"DELETE.*\+.*param",
                    r'query.*=.*[\'"].*\+.*[\'"]',
                ],
                "severity": "critical",
                "description": "SQL query built with string concatenation",
            },
            "format_string_sql": {
                "indicators": [
                    r"query.*%.*user",
                    r"execute.*%.*request",
                    r"cursor\.execute.*%",
                    r"sql.*format.*input",
                ],
                "severity": "critical",
                "description": "SQL query using format strings with user input",
            },
            "dynamic_query_building": {
                "indicators": [
                    r"WHERE.*\+.*user",
                    r"ORDER.*BY.*\+.*input",
                    r"GROUP.*BY.*\+.*param",
                    r"HAVING.*\+.*request",
                ],
                "severity": "high",
                "description": "Dynamic SQL query building with user input",
            },
        }

        # NoSQL injection patterns
        self.nosql_injection_patterns = {
            "mongodb_injection": {
                "indicators": [
                    r"find\(.*user.*input",
                    r"collection\..*request",
                    r"db\..*\$.*user",
                    r"mongo.*query.*input",
                ],
                "severity": "high",
                "description": "Potential NoSQL injection in MongoDB queries",
            },
            "json_injection": {
                "indicators": [
                    r"json\.loads.*request.*(?!.*validat)",
                    r"eval.*json.*user",
                    r"JSON\.parse.*user.*(?!.*validat)",
                    r"json.*decode.*input.*(?!.*check)",
                ],
                "severity": "high",
                "description": "JSON injection through unsafe parsing",
            },
        }

        # Path traversal patterns
        self.path_traversal_patterns = {
            "directory_traversal": {
                "indicators": [
                    r"open\(.*user.*input",
                    r"file.*=.*request",
                    r"path.*=.*input.*(?!.*validat)",
                    r"filename.*=.*param.*(?!.*check)",
                    r"\.\./.*user",
                ],
                "severity": "high",
                "description": "Potential directory traversal vulnerability",
            },
            "file_inclusion": {
                "indicators": [
                    r"include.*user.*input",
                    r"require.*request",
                    r"import.*user.*file",
                    r"load.*file.*input",
                ],
                "severity": "high",
                "description": "Potential file inclusion vulnerability",
            },
        }

        # Command injection patterns
        self.command_injection_patterns = {
            "os_command_injection": {
                "indicators": [
                    r"os\.system\(.*user",
                    r"subprocess.*user.*input",
                    r"shell_exec.*request",
                    r"exec\(.*input",
                    r"popen\(.*user",
                ],
                "severity": "critical",
                "description": "OS command injection vulnerability",
            },
            "shell_metacharacters": {
                "indicators": [
                    r"shell=True.*user",
                    r"system.*input.*[;&|`]",
                    r"command.*user.*[<>]",
                    r"exec.*param.*[$]",
                ],
                "severity": "critical",
                "description": "Shell metacharacters in user input",
            },
        }

        # LDAP injection patterns
        self.ldap_injection_patterns = {
            "ldap_filter_injection": {
                "indicators": [
                    r"ldap.*filter.*user",
                    r"search.*base.*input",
                    r"ldap.*query.*request",
                    r"directory.*search.*param",
                ],
                "severity": "high",
                "description": "LDAP injection in search filters",
            }
        }

    def analyze_input_validation(
        self, target_path: str, min_severity: str = "low"
    ) -> Dict[str, Any]:
        """Analyze input validation vulnerabilities in the target path."""

        start_time = time.time()
        result = ResultFormatter.create_security_result(
            "validate_inputs.py", target_path
        )

        if not os.path.exists(target_path):
            result.set_error(f"Path does not exist: {target_path}")
            result.set_execution_time(start_time)
            return result.to_dict()

        vulnerability_summary = defaultdict(int)
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
                            file_findings = self._analyze_file_input_validation(
                                file_path, relative_path
                            )
                            file_count += 1

                            # Convert findings to Finding objects
                            for finding_data in file_findings:
                                finding = ResultFormatter.create_finding(
                                    finding_id=f"INPUT_{vulnerability_summary[finding_data['vuln_type']] + 1:03d}",
                                    title=finding_data["vuln_type"]
                                    .replace("_", " ")
                                    .title(),
                                    description=finding_data["message"],
                                    severity=finding_data["severity"],
                                    file_path=finding_data["file"],
                                    line_number=finding_data["line"],
                                    recommendation=self._get_input_validation_recommendation(
                                        finding_data["vuln_type"]
                                    ),
                                    evidence={
                                        "context": finding_data.get("context", ""),
                                        "category": finding_data.get(
                                            "category", "input_validation"
                                        ),
                                        "injection_type": finding_data.get(
                                            "injection_type", "unknown"
                                        ),
                                    },
                                )
                                result.add_finding(finding)
                                vulnerability_summary[finding_data["vuln_type"]] += 1

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
            analysis_summary = self._generate_input_validation_summary(
                vulnerability_summary, file_count
            )
            result.metadata = analysis_summary

            result.set_execution_time(start_time)
            return result.to_dict(min_severity=min_severity)

        except Exception as e:
            result.set_error(f"Input validation analysis failed: {str(e)}")
            result.set_execution_time(start_time)
            return result.to_dict()

    def _analyze_file_input_validation(
        self, file_path: str, relative_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze input validation vulnerabilities in a single file."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

            # Check general input validation patterns
            findings.extend(
                self._check_input_patterns(
                    content,
                    lines,
                    relative_path,
                    self.validation_patterns,
                    "validation",
                    "input_validation",
                )
            )

            # Check SQL injection patterns
            findings.extend(
                self._check_input_patterns(
                    content,
                    lines,
                    relative_path,
                    self.sql_injection_patterns,
                    "sql_injection",
                    "sql_injection",
                )
            )

            # Check NoSQL injection patterns
            findings.extend(
                self._check_input_patterns(
                    content,
                    lines,
                    relative_path,
                    self.nosql_injection_patterns,
                    "nosql_injection",
                    "nosql_injection",
                )
            )

            # Check path traversal patterns
            findings.extend(
                self._check_input_patterns(
                    content,
                    lines,
                    relative_path,
                    self.path_traversal_patterns,
                    "path_traversal",
                    "path_traversal",
                )
            )

            # Check command injection patterns
            findings.extend(
                self._check_input_patterns(
                    content,
                    lines,
                    relative_path,
                    self.command_injection_patterns,
                    "command_injection",
                    "command_injection",
                )
            )

            # Check LDAP injection patterns
            findings.extend(
                self._check_input_patterns(
                    content,
                    lines,
                    relative_path,
                    self.ldap_injection_patterns,
                    "ldap_injection",
                    "ldap_injection",
                )
            )

        except Exception as e:
            findings.append(
                {
                    "file": relative_path,
                    "line": 0,
                    "vuln_type": "file_error",
                    "severity": "low",
                    "message": f"Could not analyze file: {str(e)}",
                    "category": "analysis",
                    "injection_type": "N/A",
                }
            )

        return findings

    def _check_input_patterns(
        self,
        content: str,
        lines: List[str],
        file_path: str,
        pattern_dict: Dict,
        category: str,
        injection_type: str,
    ) -> List[Dict[str, Any]]:
        """Check for specific input validation patterns in file content."""
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
                            "vuln_type": f"{category}_{pattern_name}",
                            "severity": pattern_info["severity"],
                            "message": f"{pattern_info['description']} ({pattern_name})",
                            "context": lines[line_num - 1].strip()
                            if line_num <= len(lines)
                            else "",
                            "category": category,
                            "injection_type": injection_type,
                        }
                    )

        return findings

    def _get_input_validation_recommendation(self, vuln_type: str) -> str:
        """Get specific recommendations for input validation vulnerabilities."""
        recommendations = {
            "validation_missing_input_validation": "Implement comprehensive input validation for all user inputs",
            "validation_insufficient_sanitization": "Add proper input sanitization and encoding",
            "validation_direct_user_input": "Never directly execute user input - use safe alternatives",
            "validation_regex_injection": "Validate regex patterns and use safe regex compilation",
            "sql_injection_string_concatenation": "Use parameterized queries instead of string concatenation",
            "sql_injection_format_string_sql": "Use prepared statements instead of format strings",
            "sql_injection_dynamic_query_building": "Use query builders or ORM with parameterized queries",
            "nosql_injection_mongodb_injection": "Use parameterized queries and input validation for NoSQL",
            "nosql_injection_json_injection": "Validate JSON structure and content before parsing",
            "path_traversal_directory_traversal": "Validate and sanitize file paths, use whitelisting",
            "path_traversal_file_inclusion": "Use safe file inclusion methods and path validation",
            "command_injection_os_command_injection": "Avoid system calls with user input, use safe APIs",
            "command_injection_shell_metacharacters": "Sanitize shell metacharacters or avoid shell execution",
            "ldap_injection_ldap_filter_injection": "Use parameterized LDAP queries and input validation",
        }
        return recommendations.get(
            vuln_type, "Implement proper input validation and sanitization"
        )

    def _generate_input_validation_summary(
        self, vulnerability_summary: Dict, file_count: int
    ) -> Dict[str, Any]:
        """Generate summary of input validation analysis."""

        # Categorize vulnerabilities by injection type
        injection_categories = {
            "input_validation": [
                k for k in vulnerability_summary.keys() if k.startswith("validation_")
            ],
            "sql_injection": [
                k
                for k in vulnerability_summary.keys()
                if k.startswith("sql_injection_")
            ],
            "nosql_injection": [
                k
                for k in vulnerability_summary.keys()
                if k.startswith("nosql_injection_")
            ],
            "path_traversal": [
                k
                for k in vulnerability_summary.keys()
                if k.startswith("path_traversal_")
            ],
            "command_injection": [
                k
                for k in vulnerability_summary.keys()
                if k.startswith("command_injection_")
            ],
            "ldap_injection": [
                k
                for k in vulnerability_summary.keys()
                if k.startswith("ldap_injection_")
            ],
        }

        total_issues = sum(vulnerability_summary.values())
        severity_counts = self._count_by_severity(vulnerability_summary)

        return {
            "total_files_analyzed": file_count,
            "total_input_validation_issues": total_issues,
            "issues_by_injection_type": {
                category: {
                    "count": sum(vulnerability_summary.get(vuln, 0) for vuln in vulns),
                    "vulnerabilities": {
                        vuln.replace(f"{category}_", ""): vulnerability_summary.get(
                            vuln, 0
                        )
                        for vuln in vulns
                        if vulnerability_summary.get(vuln, 0) > 0
                    },
                }
                for category, vulns in injection_categories.items()
            },
            "severity_breakdown": severity_counts,
            "security_score": self._calculate_security_score(total_issues, file_count),
            "critical_injection_vectors": self._get_critical_injection_vectors(
                vulnerability_summary
            ),
            "recommendations": self._generate_priority_recommendations(
                vulnerability_summary
            ),
        }

    def _count_by_severity(self, vulnerability_summary: Dict) -> Dict[str, int]:
        """Count vulnerabilities by severity level."""
        severity_mapping = {
            "critical": [
                "direct_user_input",
                "string_concatenation",
                "format_string_sql",
                "os_command_injection",
                "shell_metacharacters",
            ],
            "high": [
                "missing_input_validation",
                "dynamic_query_building",
                "mongodb_injection",
                "json_injection",
                "directory_traversal",
                "file_inclusion",
                "ldap_filter_injection",
            ],
            "medium": ["insufficient_sanitization", "regex_injection"],
            "low": ["file_error"],
        }

        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for vuln, count in vulnerability_summary.items():
            vuln_name = vuln.split("_", 1)[-1]  # Remove category prefix
            for severity, patterns in severity_mapping.items():
                if vuln_name in patterns:
                    counts[severity] += count
                    break

        return counts

    def _calculate_security_score(self, total_issues: int, file_count: int) -> float:
        """Calculate a security score (0-100, higher is better)."""
        if file_count == 0:
            return 100.0

        issue_density = total_issues / file_count
        # Score decreases with issue density, with critical injection flaws having heavy impact
        score = max(0, 100 - (issue_density * 25))
        return round(score, 1)

    def _get_critical_injection_vectors(
        self, vulnerability_summary: Dict
    ) -> List[Dict[str, Any]]:
        """Get critical injection vectors requiring immediate attention."""
        critical_patterns = [
            "direct_user_input",
            "string_concatenation",
            "format_string_sql",
            "os_command_injection",
            "shell_metacharacters",
        ]
        critical_vectors = []

        for vuln, count in vulnerability_summary.items():
            vuln_name = vuln.split("_", 1)[-1]
            if vuln_name in critical_patterns and count > 0:
                critical_vectors.append(
                    {
                        "injection_vector": vuln.replace("_", " ").title(),
                        "count": count,
                        "severity": "critical",
                        "category": vuln.split("_")[0],
                    }
                )

        return critical_vectors

    def _generate_priority_recommendations(
        self, vulnerability_summary: Dict
    ) -> List[str]:
        """Generate priority recommendations based on findings."""
        recommendations = []

        # Critical injection vulnerabilities first
        if any("direct_user_input" in k for k in vulnerability_summary.keys()):
            recommendations.append(
                "CRITICAL: Never directly execute user input - implement safe alternatives"
            )
        if any(
            "string_concatenation" in k or "format_string_sql" in k
            for k in vulnerability_summary.keys()
        ):
            recommendations.append(
                "CRITICAL: Replace SQL string concatenation with parameterized queries"
            )
        if any(
            "os_command_injection" in k or "shell_metacharacters" in k
            for k in vulnerability_summary.keys()
        ):
            recommendations.append(
                "CRITICAL: Fix command injection by avoiding system calls with user input"
            )

        # High priority validation issues
        if any("missing_input_validation" in k for k in vulnerability_summary.keys()):
            recommendations.append(
                "HIGH: Implement comprehensive input validation for all user inputs"
            )
        if any(
            "directory_traversal" in k or "file_inclusion" in k
            for k in vulnerability_summary.keys()
        ):
            recommendations.append(
                "HIGH: Add path validation to prevent directory traversal attacks"
            )

        # General recommendations
        total_issues = sum(vulnerability_summary.values())
        if total_issues > 10:
            recommendations.append(
                "Consider implementing a centralized input validation framework"
            )

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
        description="Analyze input validation vulnerabilities in codebase"
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

    analyzer = InputValidationAnalyzer()
    result = analyzer.analyze_input_validation(args.target_path, args.min_severity)

    if args.output_format == "console":
        # Simple console output
        if result.get("success", False):
            print(f"Input Validation Analysis Results for: {args.target_path}")
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
