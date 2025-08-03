#!/usr/bin/env python3
"""
Authentication Security Analysis Script
Analyzes authentication and authorization patterns for security vulnerabilities.
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


class AuthSecurityAnalyzer:
    """Analyzes authentication and authorization security patterns."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()

        # Authentication vulnerabilities
        self.auth_patterns = {
            "weak_password_policy": {
                "indicators": [
                    r"password.*length.*<\s*[1-7]",  # Very short passwords
                    r"min.*password.*[1-7]",
                    r"password.*simple",
                    r"no.*password.*requirement",
                ],
                "severity": "high",
                "description": "Weak password policy detected",
            },
            "missing_password_hash": {
                "indicators": [
                    r"password\s*=\s*.*\.encode\(\)",
                    r'password\s*==\s*[\'"]',
                    r"plaintext.*password",
                    r"password.*plain",
                    r"password\s*=\s*input\(",
                ],
                "severity": "critical",
                "description": "Password stored in plaintext or weakly encoded",
            },
            "session_fixation": {
                "indicators": [
                    r"session_id\s*=\s*request",
                    r"session.*fixed",
                    r"session_regenerate.*false",
                    r"session\.id\s*=\s*",
                ],
                "severity": "high",
                "description": "Potential session fixation vulnerability",
            },
            "missing_csrf_protection": {
                "indicators": [
                    r"@app\.route.*methods.*POST.*(?!.*csrf)",
                    r"<form.*method.*post.*(?!.*csrf)",
                    r"POST.*(?!.*csrf_token)",
                    r"forms.*(?!.*CSRFProtect)",
                ],
                "severity": "high",
                "description": "Missing CSRF protection on state-changing operations",
            },
            "insecure_session_config": {
                "indicators": [
                    r"session.*secure.*false",
                    r"session.*httponly.*false",
                    r"session.*samesite.*none",
                    r"cookie.*secure.*false",
                ],
                "severity": "medium",
                "description": "Insecure session cookie configuration",
            },
        }

        # Authorization vulnerabilities
        self.authz_patterns = {
            "missing_authorization": {
                "indicators": [
                    r"@app\.route.*(?!.*@.*auth)",
                    r"def\s+\w+.*(?!.*auth.*check)",
                    r"sensitive.*(?!.*permission)",
                    r"admin.*(?!.*role.*check)",
                ],
                "severity": "high",
                "description": "Potential missing authorization checks",
            },
            "privilege_escalation": {
                "indicators": [
                    r'user\.role\s*=\s*[\'"]admin[\'"]',
                    r"is_admin\s*=\s*True",
                    r"permission.*override",
                    r"role.*elevation",
                ],
                "severity": "critical",
                "description": "Potential privilege escalation vulnerability",
            },
            "insecure_direct_object_reference": {
                "indicators": [
                    r"user_id\s*=\s*request\.",
                    r"id\s*=\s*params\[",
                    r"get.*by.*id.*request",
                    r"user.*request\.args",
                ],
                "severity": "high",
                "description": "Potential insecure direct object reference",
            },
            "role_confusion": {
                "indicators": [
                    r"if.*user.*==.*admin",
                    r"role.*string.*comparison",
                    r"permission.*hardcoded",
                    r"access.*level.*\d+",
                ],
                "severity": "medium",
                "description": "Role-based access control implementation issues",
            },
        }

        # JWT and token vulnerabilities
        self.token_patterns = {
            "weak_jwt_secret": {
                "indicators": [
                    r'jwt.*secret.*[\'"].*[\'"]',
                    r'JWT_SECRET.*=.*[\'"][^\'\"]{1,10}[\'"]',
                    r"token.*key.*simple",
                    r'secret.*=.*[\'"]password[\'"]',
                ],
                "severity": "critical",
                "description": "Weak JWT secret or hardcoded token key",
            },
            "jwt_algorithm_confusion": {
                "indicators": [
                    r"algorithm.*none",
                    r"jwt.*verify.*false",
                    r"algorithm.*HS256.*RS256",
                    r"verify_signature.*false",
                ],
                "severity": "critical",
                "description": "JWT algorithm confusion or verification bypass",
            },
            "missing_token_expiration": {
                "indicators": [
                    r"jwt\.encode.*(?!.*exp)",
                    r"token.*(?!.*expir)",
                    r"access_token.*(?!.*timeout)",
                    r"session.*(?!.*timeout)",
                ],
                "severity": "medium",
                "description": "Missing token expiration",
            },
            "token_in_url": {
                "indicators": [
                    r"token.*=.*request\.args",
                    r"access_token.*query",
                    r"token.*GET.*parameter",
                    r"url.*token.*=",
                ],
                "severity": "medium",
                "description": "Authentication token exposed in URL parameters",
            },
        }

    def analyze_auth_security(
        self, target_path: str, min_severity: str = "low"
    ) -> Dict[str, Any]:
        """Analyze authentication security in the target path."""

        start_time = time.time()
        result = ResultFormatter.create_security_result("check_auth.py", target_path)

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
                            file_findings = self._analyze_file_auth(
                                file_path, relative_path
                            )
                            file_count += 1

                            # Convert findings to Finding objects
                            for finding_data in file_findings:
                                finding = ResultFormatter.create_finding(
                                    finding_id=f"AUTH_{vulnerability_summary[finding_data['vuln_type']] + 1:03d}",
                                    title=finding_data["vuln_type"]
                                    .replace("_", " ")
                                    .title(),
                                    description=finding_data["message"],
                                    severity=finding_data["severity"],
                                    file_path=finding_data["file"],
                                    line_number=finding_data["line"],
                                    recommendation=self._get_auth_recommendation(
                                        finding_data["vuln_type"]
                                    ),
                                    evidence={
                                        "context": finding_data.get("context", ""),
                                        "category": finding_data.get(
                                            "category", "authentication"
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
            analysis_summary = self._generate_auth_summary(
                vulnerability_summary, file_count
            )
            result.metadata = analysis_summary

            result.set_execution_time(start_time)
            return result.to_dict(min_severity=min_severity)

        except Exception as e:
            result.set_error(f"Authentication security analysis failed: {str(e)}")
            result.set_execution_time(start_time)
            return result.to_dict()

    def _analyze_file_auth(
        self, file_path: str, relative_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze authentication security in a single file."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

            # Check authentication vulnerabilities
            findings.extend(
                self._check_auth_patterns(
                    content, lines, relative_path, self.auth_patterns, "authentication"
                )
            )

            # Check authorization vulnerabilities
            findings.extend(
                self._check_auth_patterns(
                    content, lines, relative_path, self.authz_patterns, "authorization"
                )
            )

            # Check token vulnerabilities
            findings.extend(
                self._check_auth_patterns(
                    content, lines, relative_path, self.token_patterns, "token"
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
                }
            )

        return findings

    def _check_auth_patterns(
        self,
        content: str,
        lines: List[str],
        file_path: str,
        pattern_dict: Dict,
        category: str,
    ) -> List[Dict[str, Any]]:
        """Check for specific authentication patterns in file content."""
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
                        }
                    )

        return findings

    def _get_auth_recommendation(self, vuln_type: str) -> str:
        """Get specific recommendations for authentication vulnerabilities."""
        recommendations = {
            "authentication_weak_password_policy": "Implement strong password requirements (min 12 chars, complexity)",
            "authentication_missing_password_hash": "Use bcrypt, scrypt, or Argon2 for password hashing",
            "authentication_session_fixation": "Regenerate session ID after authentication",
            "authentication_missing_csrf_protection": "Implement CSRF tokens for state-changing operations",
            "authentication_insecure_session_config": "Set secure, httpOnly, and sameSite cookie flags",
            "authorization_missing_authorization": "Add proper authorization checks to sensitive endpoints",
            "authorization_privilege_escalation": "Validate user permissions before role changes",
            "authorization_insecure_direct_object_reference": "Implement access control checks for object access",
            "authorization_role_confusion": "Use enum-based roles and centralized permission checking",
            "token_weak_jwt_secret": "Use cryptographically strong, randomly generated JWT secrets",
            "token_jwt_algorithm_confusion": "Explicitly specify and validate JWT algorithms",
            "token_missing_token_expiration": "Set appropriate expiration times for all tokens",
            "token_token_in_url": "Use Authorization header instead of URL parameters for tokens",
        }
        return recommendations.get(
            vuln_type,
            "Review authentication implementation for security best practices",
        )

    def _generate_auth_summary(
        self, vulnerability_summary: Dict, file_count: int
    ) -> Dict[str, Any]:
        """Generate summary of authentication security analysis."""

        # Categorize vulnerabilities
        categories = {
            "authentication": [
                k
                for k in vulnerability_summary.keys()
                if k.startswith("authentication_")
            ],
            "authorization": [
                k
                for k in vulnerability_summary.keys()
                if k.startswith("authorization_")
            ],
            "token": [
                k for k in vulnerability_summary.keys() if k.startswith("token_")
            ],
        }

        total_issues = sum(vulnerability_summary.values())
        severity_counts = self._count_by_severity(vulnerability_summary)

        return {
            "total_files_analyzed": file_count,
            "total_auth_vulnerabilities": total_issues,
            "vulnerabilities_by_category": {
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
                for category, vulns in categories.items()
            },
            "severity_breakdown": severity_counts,
            "security_score": self._calculate_security_score(total_issues, file_count),
            "top_vulnerabilities": self._get_top_vulnerabilities(vulnerability_summary),
            "recommendations": self._generate_priority_recommendations(
                vulnerability_summary
            ),
        }

    def _count_by_severity(self, vulnerability_summary: Dict) -> Dict[str, int]:
        """Count vulnerabilities by severity level."""
        # Simplified mapping based on pattern definitions
        severity_mapping = {
            "critical": [
                "missing_password_hash",
                "privilege_escalation",
                "weak_jwt_secret",
                "jwt_algorithm_confusion",
            ],
            "high": [
                "weak_password_policy",
                "session_fixation",
                "missing_csrf_protection",
                "missing_authorization",
                "insecure_direct_object_reference",
            ],
            "medium": [
                "insecure_session_config",
                "role_confusion",
                "missing_token_expiration",
                "token_in_url",
            ],
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
        # Score decreases with issue density, with critical issues having more impact
        score = max(0, 100 - (issue_density * 15))
        return round(score, 1)

    def _get_top_vulnerabilities(
        self, vulnerability_summary: Dict
    ) -> List[Dict[str, Any]]:
        """Get the top authentication vulnerabilities."""
        sorted_vulns = sorted(
            vulnerability_summary.items(), key=lambda x: x[1], reverse=True
        )
        return [
            {
                "vulnerability": vuln.replace("_", " ").title(),
                "count": count,
                "category": vuln.split("_")[0] if "_" in vuln else "unknown",
            }
            for vuln, count in sorted_vulns[:5]
            if count > 0
        ]

    def _generate_priority_recommendations(
        self, vulnerability_summary: Dict
    ) -> List[str]:
        """Generate priority recommendations based on findings."""
        recommendations = []

        # Critical issues first
        critical_patterns = [
            "missing_password_hash",
            "privilege_escalation",
            "weak_jwt_secret",
            "jwt_algorithm_confusion",
        ]
        for pattern in critical_patterns:
            if any(pattern in k for k in vulnerability_summary.keys()):
                if "missing_password_hash" in pattern:
                    recommendations.append(
                        "CRITICAL: Implement proper password hashing (bcrypt/Argon2)"
                    )
                elif "privilege_escalation" in pattern:
                    recommendations.append(
                        "CRITICAL: Add authorization checks for privilege changes"
                    )
                elif "weak_jwt_secret" in pattern:
                    recommendations.append(
                        "CRITICAL: Use cryptographically strong JWT secrets"
                    )
                elif "jwt_algorithm_confusion" in pattern:
                    recommendations.append("CRITICAL: Fix JWT algorithm verification")

        # High priority issues
        high_patterns = [
            "weak_password_policy",
            "missing_csrf_protection",
            "missing_authorization",
        ]
        for pattern in high_patterns:
            if any(pattern in k for k in vulnerability_summary.keys()):
                if "weak_password_policy" in pattern:
                    recommendations.append("HIGH: Strengthen password requirements")
                elif "missing_csrf_protection" in pattern:
                    recommendations.append("HIGH: Implement CSRF protection")
                elif "missing_authorization" in pattern:
                    recommendations.append(
                        "HIGH: Add authorization checks to endpoints"
                    )

        # General recommendations
        total_issues = sum(vulnerability_summary.values())
        if total_issues > 15:
            recommendations.append(
                "Consider security code review and penetration testing"
            )

        return recommendations[:5]  # Limit to top 5 recommendations

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
        }
        return any(filename.endswith(ext) for ext in analyze_extensions)


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze authentication security in codebase"
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

    analyzer = AuthSecurityAnalyzer()
    result = analyzer.analyze_auth_security(args.target_path, args.min_severity)

    if args.output_format == "console":
        # Simple console output
        if result.get("success", False):
            print(f"Authentication Security Analysis Results for: {args.target_path}")
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
