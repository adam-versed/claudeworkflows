#!/usr/bin/env python3
"""
Security analysis script: Detect hardcoded secrets and credentials.
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


class SecretDetector:
    """Detect hardcoded secrets and credentials in source code."""

    def __init__(self):
        # Common secret patterns (simplified for prototype)
        self.patterns = {
            "password": {
                "pattern": r'(?i)(password|pwd|pass)\s*[=:]\s*["\']([^"\']{3,})["\']',
                "severity": "critical",
                "description": "Hardcoded password found",
            },
            "api_key": {
                "pattern": r'(?i)(api[_-]?key|apikey|secret[_-]?key)\s*[=:]\s*["\']([^"\']{10,})["\']',
                "severity": "critical",
                "description": "Hardcoded API key found",
            },
            "database_url": {
                "pattern": r'(?i)(database[_-]?url|db[_-]?url|connection[_-]?string)\s*[=:]\s*["\']([^"\']*://[^"\']+)["\']',
                "severity": "high",
                "description": "Database connection string found",
            },
            "jwt_secret": {
                "pattern": r'(?i)(jwt[_-]?secret|token[_-]?secret)\s*[=:]\s*["\']([^"\']{10,})["\']',
                "severity": "critical",
                "description": "JWT secret found",
            },
            "aws_key": {
                "pattern": r'(?i)(aws[_-]?access[_-]?key[_-]?id|access[_-]?key)\s*[=:]\s*["\']([A-Z0-9]{20})["\']',
                "severity": "critical",
                "description": "AWS access key found",
            },
            "private_key": {
                "pattern": r"-----BEGIN[A-Z\s]+PRIVATE KEY-----",
                "severity": "critical",
                "description": "Private key found",
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
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".rs",
            ".swift",
            ".kt",
        }

        # Config file extensions
        self.config_extensions = {
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".conf",
            ".xml",
            ".env",
            ".properties",
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

    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned."""
        # Skip directories in skip_patterns
        for part in file_path.parts:
            if part in self.skip_patterns:
                return False

        # Check file extension
        suffix = file_path.suffix.lower()
        return suffix in self.code_extensions or suffix in self.config_extensions

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Scan a single file for secrets.

        Returns:
            List of findings dictionaries
        """
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

                for pattern_name, pattern_info in self.patterns.items():
                    matches = re.finditer(
                        pattern_info["pattern"], content, re.MULTILINE
                    )

                    for match in matches:
                        # Find line number
                        line_start = content[: match.start()].count("\n") + 1

                        # Get matched secret (group 2 for most patterns)
                        if match.groups() and len(match.groups()) >= 2:
                            secret_value = match.group(2)
                        else:
                            secret_value = match.group(0)

                        # Create finding
                        finding = {
                            "pattern_type": pattern_name,
                            "file_path": str(file_path),
                            "line_number": line_start,
                            "line_content": lines[line_start - 1].strip()
                            if line_start <= len(lines)
                            else "",
                            "matched_value": secret_value[:20] + "..."
                            if len(secret_value) > 20
                            else secret_value,
                            "severity": pattern_info["severity"],
                            "description": pattern_info["description"],
                        }
                        findings.append(finding)

        except Exception:
            # Log error but continue scanning
            pass

        return findings

    def scan_directory(self, target_path: str) -> List[Dict[str, Any]]:
        """
        Scan directory recursively for secrets.

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
        result = ResultFormatter.create_security_result(
            "detect_secrets.py", target_path
        )

        try:
            # Scan for secrets
            findings = self.scan_directory(target_path)

            # Convert to Finding objects
            finding_id = 1
            for finding_data in findings:
                finding = ResultFormatter.create_finding(
                    f"SEC{finding_id:03d}",
                    f"Hardcoded Secret: {finding_data['pattern_type']}",
                    finding_data["description"],
                    finding_data["severity"],
                    finding_data["file_path"],
                    finding_data["line_number"],
                    "Remove hardcoded secrets and use environment variables or secure vaults",
                    {
                        "pattern_type": finding_data["pattern_type"],
                        "line_content": finding_data["line_content"],
                        "matched_value": finding_data["matched_value"],
                    },
                )
                result.add_finding(finding)
                finding_id += 1

            # Add metadata
            result.metadata = {
                "files_scanned": len(set(f["file_path"] for f in findings)),
                "patterns_checked": len(self.patterns),
            }

        except Exception as e:
            result.set_error(f"Analysis failed: {str(e)}")

        result.set_execution_time(start_time)
        return result


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect hardcoded secrets and credentials in source code"
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

    detector = SecretDetector()
    result = detector.analyze(args.target_path)

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
