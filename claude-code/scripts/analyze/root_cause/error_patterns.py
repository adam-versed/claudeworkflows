#!/usr/bin/env python3
"""
Root cause analysis script: Error pattern matching for known failure modes.
Part of Claude Code Workflows.
"""

import os
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
    from output_formatter import (
        ResultFormatter,
        Severity,
        AnalysisType,
        Finding,
        AnalysisResult,
    )
    from tech_stack_detector import TechStackDetector
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class ErrorPatternAnalyzer:
    """Analyze code for known error patterns and failure modes."""

    def __init__(self):
        self.error_patterns = {
            # Memory and Resource Patterns
            "memory_leak": {
                "patterns": [
                    r"(?:new|malloc|alloc).*without.*(?:delete|free)",
                    r"addEventListener.*without.*removeEventListener",
                    r"setInterval|setTimeout.*without.*clear",
                    r"open\([^)]*\).*without.*close\(\)",
                ],
                "severity": "high",
                "category": "resource_management",
                "description": "Potential memory leak or resource not properly released",
            },
            # Null/Undefined Access Patterns (refined to reduce false positives)
            "null_pointer": {
                "patterns": [
                    r"(?:user_input|request\.|params\.|query\.)\w+(?:\.\w+)*(?!\s*(?:and|or|if|is|==|!=))",  # unsafe user input access
                    r"(?:JSON\.parse|parseInt|parseFloat)\([^)]*\)(?!\s*(?:try|catch|\}|\)))",  # parsing without error handling
                ],
                "severity": "medium",
                "category": "null_safety",
                "description": "Potential null/undefined access or missing error handling",
            },
            # Concurrency and Racing Patterns
            "race_condition": {
                "patterns": [
                    r"(?:async|await).*(?:for|while).*(?:async|await)",  # async in loops
                    r"Promise\.all.*(?:await|then).*(?:await|then)",  # chained async
                    r"(?:setTimeout|setInterval).*(?:state|this\.)",  # timer with state access
                    r"(?:global|window|document)\.\w+\s*=.*(?:async|setTimeout)",  # global state in async
                ],
                "severity": "high",
                "category": "concurrency",
                "description": "Potential race condition or unsafe concurrent access",
            },
            # Input Validation Patterns (more precise)
            "injection_vulnerability": {
                "patterns": [
                    r"(?:query|cursor\.execute).*\+.*(?:user_input|request\.|params\.|input\()",  # SQL injection via concatenation
                    r"eval\s*\(\s*(?:user_input|request\.|params\.|input\()",  # direct eval of user input
                    r"exec\s*\(\s*(?:user_input|request\.|params\.|input\()",  # direct exec of user input
                    r"(?:subprocess|os\.system|os\.popen)\s*\(\s*.*(?:user_input|request\.|params\.|input\()",  # command injection
                ],
                "severity": "critical",
                "category": "security",
                "description": "Potential injection vulnerability",
            },
            # Error Handling Patterns
            "poor_error_handling": {
                "patterns": [
                    r"catch\s*\([^)]*\)\s*\{\s*\}",  # empty catch
                    r"catch.*console\.log",  # logging without proper handling
                    r"try\s*\{[^}]*\}\s*catch\s*\([^)]*\)\s*\{\s*return",  # silent failure
                    r'throw\s+(?:new\s+)?Error\(\s*["\']["\']\s*\)',  # empty error message
                ],
                "severity": "medium",
                "category": "error_handling",
                "description": "Poor error handling that may hide issues",
            },
            # Performance Anti-patterns
            "performance_issue": {
                "patterns": [
                    r"for.*for.*for",  # nested loops (O(n³))
                    r"(?:forEach|map|filter).*(?:forEach|map|filter).*(?:forEach|map|filter)",  # nested iterations
                    r"(?:getElementById|querySelector).*(?:for|while)",  # DOM queries in loops
                    r"(?:JSON\.parse|JSON\.stringify).*(?:for|while)",  # JSON ops in loops
                    r"(?:split|replace|match).*(?:for|while)",  # string ops in loops
                ],
                "severity": "medium",
                "category": "performance",
                "description": "Performance anti-pattern that may cause bottlenecks",
            },
            # State Management Patterns
            "state_mutation": {
                "patterns": [
                    r"(?:state|props)\.\w+\s*=",  # direct state mutation
                    r"(?:push|pop|splice|sort|reverse)\s*\(.*(?:state|props)",  # mutating state arrays
                    r"Object\.assign\s*\(\s*(?:state|props)",  # mutating state objects
                    r"(?:state|props)\[\w+\]\s*=",  # bracket notation state mutation
                ],
                "severity": "medium",
                "category": "state_management",
                "description": "Direct state mutation that may cause rendering issues",
            },
            # Authentication/Authorization Patterns
            "auth_bypass": {
                "patterns": [
                    r'(?:admin|role|permission)\s*==?\s*["\'](?:true|1)["\']',  # string comparison
                    r"(?:if|while)\s*\(\s*true\s*\).*(?:auth|login|permission)",  # hardcoded true
                    r"(?:auth|token|session)\s*=\s*null.*continue",  # auth bypass
                    r"(?:localStorage|sessionStorage)\.(?:token|auth).*without.*verify",  # client-side auth
                ],
                "severity": "critical",
                "category": "security",
                "description": "Potential authentication or authorization bypass",
            },
            # Data Handling Patterns
            "data_corruption": {
                "patterns": [
                    r"(?:parseInt|parseFloat)\([^)]*\)(?!\s*(?:isNaN|\|\||&&))",  # parsing without validation
                    r"(?:slice|substring|substr)\([^)]*\)(?!\s*(?:length|check))",  # string manipulation without bounds
                    r"(?:push|unshift).*(?:splice|pop|shift)",  # conflicting array operations
                    r"(?:JSON\.parse).*(?:JSON\.stringify).*(?:JSON\.parse)",  # excessive serialization
                ],
                "severity": "medium",
                "category": "data_integrity",
                "description": "Potential data corruption or invalid transformation",
            },
        }

        # Common error keywords to search for in files
        self.error_keywords = [
            "error",
            "exception",
            "fail",
            "crash",
            "bug",
            "issue",
            "problem",
            "todo",
            "fixme",
            "hack",
            "workaround",
            "temporary",
        ]

        # File extensions and their specific patterns
        self.language_patterns = {
            ".py": {
                "patterns": [
                    r"except\s*:(?!\s*(?:pass|raise))",  # bare except
                    r"import\s+\*",  # wildcard imports
                    r"exec\s*\(",  # exec usage
                    r"eval\s*\(",  # eval usage
                ],
                "severity": "medium",
            },
            ".js": {
                "patterns": [
                    r"==\s*(?:null|undefined)",  # loose equality
                    r'typeof.*==\s*["\']undefined["\']',  # typeof check
                    r"var\s+",  # var usage (prefer let/const)
                ],
                "severity": "low",
            },
            ".java": {
                "patterns": [
                    r"catch\s*\([^)]*\)\s*\{\s*e\.printStackTrace\(\)",  # stack trace in catch
                    r"System\.out\.print",  # System.out usage
                    r"Thread\.sleep",  # Thread.sleep usage
                ],
                "severity": "medium",
            },
        }

    def analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a single file for error patterns."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.split("\n")

            # Check general error patterns
            findings.extend(self._check_error_patterns(content, lines, file_path))

            # Check language-specific patterns
            findings.extend(self._check_language_patterns(content, lines, file_path))

            # Check for error keywords in comments
            findings.extend(self._check_error_keywords(lines, file_path))

        except Exception as e:
            findings.append(
                {
                    "type": "analysis_error",
                    "file_path": str(file_path),
                    "error": str(e),
                    "severity": "low",
                }
            )

        return findings

    def _check_error_patterns(
        self, content: str, lines: List[str], file_path: Path
    ) -> List[Dict[str, Any]]:
        """Check for general error patterns."""
        findings = []

        for pattern_name, pattern_info in self.error_patterns.items():
            for pattern in pattern_info["patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    findings.append(
                        {
                            "type": "error_pattern",
                            "pattern_name": pattern_name,
                            "category": pattern_info["category"],
                            "file_path": str(file_path),
                            "line": line_num,
                            "severity": pattern_info["severity"],
                            "description": pattern_info["description"],
                            "code_snippet": (
                                lines[line_num - 1].strip()
                                if line_num <= len(lines)
                                else ""
                            ),
                            "matched_text": match.group(0),
                        }
                    )

        return findings

    def _check_language_patterns(
        self, content: str, lines: List[str], file_path: Path
    ) -> List[Dict[str, Any]]:
        """Check for language-specific patterns."""
        findings = []

        file_ext = file_path.suffix.lower()
        if file_ext in self.language_patterns:
            lang_config = self.language_patterns[file_ext]

            for pattern in lang_config["patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    findings.append(
                        {
                            "type": "language_pattern",
                            "language": file_ext,
                            "file_path": str(file_path),
                            "line": line_num,
                            "severity": lang_config["severity"],
                            "description": f"Language-specific anti-pattern for {file_ext}",
                            "code_snippet": (
                                lines[line_num - 1].strip()
                                if line_num <= len(lines)
                                else ""
                            ),
                            "matched_text": match.group(0),
                        }
                    )

        return findings

    def _check_error_keywords(
        self, lines: List[str], file_path: Path
    ) -> List[Dict[str, Any]]:
        """Check for error-related keywords in comments."""
        findings = []
        comment_patterns = [
            r"#.*",  # Python, shell comments
            r"//.*",  # C++, Java, JavaScript comments
            r"/\*.*?\*/",  # Multi-line comments
            r"<!--.*?-->",  # HTML comments
        ]

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()

            # Check if line is a comment
            is_comment = any(re.search(pattern, line) for pattern in comment_patterns)

            if is_comment:
                for keyword in self.error_keywords:
                    if keyword in line_lower:
                        findings.append(
                            {
                                "type": "error_keyword",
                                "keyword": keyword,
                                "file_path": str(file_path),
                                "line": line_num,
                                "severity": "low",
                                "description": f"Error-related keyword '{keyword}' found in comment",
                                "code_snippet": line.strip(),
                            }
                        )

        return findings

    def analyze_error_clusters(
        self, all_findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze clusters of errors that might indicate systemic issues."""
        clusters = []

        # Group by file and category
        file_categories = defaultdict(lambda: defaultdict(list))

        for finding in all_findings:
            if finding.get("type") == "error_pattern":
                file_path = finding.get("file_path", "")
                category = finding.get("category", "unknown")
                file_categories[file_path][category].append(finding)

        # Find files with multiple issues in same category
        for file_path, categories in file_categories.items():
            for category, findings in categories.items():
                if len(findings) >= 3:  # 3+ issues in same category
                    clusters.append(
                        {
                            "type": "error_cluster",
                            "file_path": file_path,
                            "category": category,
                            "issue_count": len(findings),
                            "severity": "high",
                            "description": f"Multiple {category} issues clustered in {Path(file_path).name}",
                            "findings": findings,
                        }
                    )

        return clusters


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze error patterns and debug traces in codebase"
    )
    parser.add_argument(
        "target_path",
        nargs="?",
        default=os.getcwd(),
        help="Directory path to analyze (default: current directory)",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "console"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()
    start_time = time.time()

    # Get target directory
    target_dir = Path(args.target_path)

    # Initialize analyzer
    analyzer = ErrorPatternAnalyzer()
    result = AnalysisResult(
        AnalysisType.ARCHITECTURE, "error_patterns.py", str(target_dir)
    )

    # Configuration for analysis
    max_files = int(os.environ.get("MAX_FILES", "50"))  # Configurable via environment
    max_file_size = int(os.environ.get("MAX_FILE_SIZE", "1048576"))  # 1MB default

    # File extensions to analyze
    extensions = {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".php",
        ".rb",
        ".go",
    }

    # Initialize tech stack detector for smart filtering
    tech_detector = TechStackDetector()

    # Analyze all relevant files with limits using universal exclusion
    all_findings = []
    files_analyzed = 0

    for ext in extensions:
        for file_path in target_dir.rglob(f"*{ext}"):
            # Break if we've analyzed enough files
            if files_analyzed >= max_files:
                break

            # Use universal exclusion system
            if not tech_detector.should_analyze_file(str(file_path), str(target_dir)):
                continue

            # Skip files that are too large
            try:
                if file_path.stat().st_size > max_file_size:
                    continue
            except OSError:
                continue

            try:
                findings = analyzer.analyze_file(file_path)
                all_findings.extend(findings)
                files_analyzed += 1
            except Exception:
                # Continue processing other files if one fails
                continue

        # Break outer loop if we've reached file limit
        if files_analyzed >= max_files:
            break

    # Analyze error clusters
    clusters = analyzer.analyze_error_clusters(all_findings)
    all_findings.extend(clusters)

    # Convert findings to formatter format
    for finding in all_findings:
        severity_map = {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
        }

        finding_title = (
            finding.get("pattern_name", finding.get("type", "Unknown"))
            .replace("_", " ")
            .title()
        )

        finding_obj = Finding(
            finding_id=f"{finding.get('type', 'unknown')}_{hash(str(finding)) % 10000}",
            title=finding_title,
            description=finding.get("description", "Error pattern detected"),
            severity=severity_map.get(finding.get("severity", "low"), Severity.LOW),
            file_path=finding.get("file_path"),
            line_number=finding.get("line"),
            evidence=finding,
        )
        result.add_finding(finding_obj)

    # Set execution time and add metadata
    result.set_execution_time(start_time)
    result.metadata.update(
        {
            "files_analyzed": files_analyzed,
            "error_patterns_found": len(
                [f for f in all_findings if f.get("type") == "error_pattern"]
            ),
            "error_clusters_found": len(
                [f for f in all_findings if f.get("type") == "error_cluster"]
            ),
            "critical_issues": len(
                [f for f in all_findings if f.get("severity") == "critical"]
            ),
            "high_issues": len(
                [f for f in all_findings if f.get("severity") == "high"]
            ),
        }
    )

    # Output based on format choice
    if args.output_format == "console":
        print(ResultFormatter.format_console_output(result))
    else:  # json (default)
        print(result.to_json())


if __name__ == "__main__":
    main()
