#!/usr/bin/env python3
"""
Architecture Pattern Evaluation Script
Analyzes design patterns and architectural decisions in codebases.
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
    from tech_stack_detector import TechStackDetector
    from architectural_pattern_detector import ArchitecturalPatternDetector
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class PatternEvaluator:
    """Evaluates design patterns and architectural decisions."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()
        self.tech_detector = TechStackDetector()
        self.pattern_detector = ArchitecturalPatternDetector()

        # Pattern detection delegated to architectural_pattern_detector
        # All pattern definitions moved to the dedicated detector

    def analyze_patterns(
        self, target_path: str, min_severity: str = "low"
    ) -> Dict[str, Any]:
        """Analyze design patterns in the target path."""

        start_time = time.time()
        result = ResultFormatter.create_architecture_result(
            "pattern_evaluation.py", target_path
        )

        if not os.path.exists(target_path):
            result.set_error(f"Path does not exist: {target_path}")
            result.set_execution_time(start_time)
            return result.to_dict()

        pattern_summary = defaultdict(int)
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
                            file_findings = self._analyze_file_patterns_improved(
                                file_path, relative_path
                            )
                            file_count += 1

                            # Convert findings to Finding objects
                            for finding_data in file_findings:
                                finding = ResultFormatter.create_finding(
                                    finding_id=f"PATTERN_{pattern_summary[finding_data['pattern']] + 1:03d}",
                                    title=finding_data["pattern"]
                                    .replace("_", " ")
                                    .title(),
                                    description=finding_data["message"],
                                    severity=finding_data["severity"],
                                    file_path=finding_data["file"],
                                    line_number=finding_data["line"],
                                    recommendation=self._get_pattern_recommendation(
                                        finding_data["pattern"]
                                    ),
                                    evidence={
                                        "context": finding_data.get("context", "")
                                    },
                                )
                                result.add_finding(finding)
                                pattern_summary[finding_data["pattern"]] += 1

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
            analysis_summary = self._generate_pattern_summary(
                pattern_summary, file_count
            )
            result.metadata = analysis_summary

            result.set_execution_time(start_time)
            return result.to_dict(min_severity=min_severity)

        except Exception as e:
            result.set_error(f"Pattern analysis failed: {str(e)}")
            result.set_execution_time(start_time)
            return result.to_dict()

    def _analyze_file_patterns(
        self, file_path: str, relative_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze patterns in a single file."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

            # Check design patterns
            findings.extend(
                self._check_patterns(
                    content, lines, relative_path, self.patterns, "design"
                )
            )

            # Check anti-patterns
            findings.extend(
                self._check_patterns(
                    content, lines, relative_path, self.antipatterns, "anti"
                )
            )

            # Check architectural patterns
            findings.extend(
                self._check_patterns(
                    content,
                    lines,
                    relative_path,
                    self.architectural_patterns,
                    "architectural",
                )
            )

            # Additional complexity-based checks
            findings.extend(
                self._check_complexity_patterns(content, lines, relative_path)
            )

        except Exception as e:
            findings.append(
                {
                    "file": relative_path,
                    "line": 0,
                    "pattern": "file_error",
                    "severity": "low",
                    "message": f"Could not analyze file: {str(e)}",
                }
            )

        return findings

    def _check_patterns(
        self,
        content: str,
        lines: List[str],
        file_path: str,
        pattern_dict: Dict,
        pattern_type: str,
    ) -> List[Dict[str, Any]]:
        """Check for specific patterns in file content."""
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
                            "pattern": f"{pattern_type}_{pattern_name}",
                            "severity": pattern_info["severity"],
                            "message": f"{pattern_info['description']}: {pattern_name}",
                            "context": lines[line_num - 1].strip()
                            if line_num <= len(lines)
                            else "",
                        }
                    )

        return findings

    def _check_complexity_patterns(
        self, content: str, lines: List[str], file_path: str
    ) -> List[Dict[str, Any]]:
        """Check for complexity-based pattern violations."""
        findings = []

        # Check for very long methods
        method_pattern = r"def\s+(\w+)\s*\([^)]*\):"
        for match in re.finditer(method_pattern, content):
            method_start = content[: match.start()].count("\n") + 1
            method_name = match.group(1)

            # Count lines in method (rough approximation)
            remaining_content = content[match.end() :]
            method_lines = 0
            indent_level = None

            for line in remaining_content.split("\n"):
                if line.strip():
                    current_indent = len(line) - len(line.lstrip())
                    if indent_level is None and current_indent > 0:
                        indent_level = current_indent
                    elif (
                        indent_level is not None
                        and current_indent <= indent_level
                        and line.strip()
                    ):
                        break
                method_lines += 1
                if method_lines > 50:  # Very long method
                    findings.append(
                        {
                            "file": file_path,
                            "line": method_start,
                            "pattern": "long_method",
                            "severity": "medium",
                            "message": f"Very long method detected: {method_name} ({method_lines}+ lines)",
                            "context": lines[method_start - 1].strip()
                            if method_start <= len(lines)
                            else "",
                        }
                    )
                    break

        # Check for high parameter count
        param_pattern = r"def\s+\w+\s*\(([^)]+)\):"
        for match in re.finditer(param_pattern, content):
            params = match.group(1)
            param_count = len(
                [
                    p.strip()
                    for p in params.split(",")
                    if p.strip() and p.strip() != "self"
                ]
            )

            if param_count > 6:  # Too many parameters
                line_num = content[: match.start()].count("\n") + 1
                findings.append(
                    {
                        "file": file_path,
                        "line": line_num,
                        "pattern": "too_many_parameters",
                        "severity": "medium",
                        "message": f"Method has too many parameters: {param_count}",
                        "context": lines[line_num - 1].strip()
                        if line_num <= len(lines)
                        else "",
                    }
                )

        return findings

    def _generate_pattern_summary(
        self, pattern_summary: Dict, file_count: int
    ) -> Dict[str, Any]:
        """Generate summary of pattern analysis."""

        # Categorize patterns
        design_patterns = {
            k: v for k, v in pattern_summary.items() if k.startswith("design_")
        }
        anti_patterns = {
            k: v for k, v in pattern_summary.items() if k.startswith("anti_")
        }
        architectural_patterns = {
            k: v for k, v in pattern_summary.items() if k.startswith("architectural_")
        }
        complexity_patterns = {
            k: v
            for k, v in pattern_summary.items()
            if k in ["long_method", "too_many_parameters"]
        }

        total_patterns = sum(pattern_summary.values())

        return {
            "total_files_analyzed": file_count,
            "total_patterns_found": total_patterns,
            "pattern_categories": {
                "design_patterns": {
                    "count": sum(design_patterns.values()),
                    "types": dict(design_patterns),
                },
                "anti_patterns": {
                    "count": sum(anti_patterns.values()),
                    "types": dict(anti_patterns),
                },
                "architectural_patterns": {
                    "count": sum(architectural_patterns.values()),
                    "types": dict(architectural_patterns),
                },
                "complexity_issues": {
                    "count": sum(complexity_patterns.values()),
                    "types": dict(complexity_patterns),
                },
            },
            "pattern_density": round(total_patterns / max(file_count, 1), 2),
            "recommendations": self._generate_recommendations(pattern_summary),
        }

    def _generate_recommendations(self, pattern_summary: Dict) -> List[str]:
        """Generate recommendations based on pattern analysis."""
        recommendations = []

        # Check for anti-patterns
        if any(k.startswith("anti_") for k in pattern_summary.keys()):
            recommendations.append(
                "Consider refactoring detected anti-patterns to improve code quality"
            )

        # Check for lack of patterns
        design_pattern_count = sum(
            v for k, v in pattern_summary.items() if k.startswith("design_")
        )
        if design_pattern_count == 0:
            recommendations.append(
                "Consider introducing design patterns to improve code structure"
            )

        # Check for complexity issues
        if pattern_summary.get("long_method", 0) > 0:
            recommendations.append(
                "Break down long methods into smaller, more focused functions"
            )

        if pattern_summary.get("too_many_parameters", 0) > 0:
            recommendations.append(
                "Consider using parameter objects or builder pattern for methods with many parameters"
            )

        # Check for singleton overuse
        if pattern_summary.get("design_singleton", 0) > 3:
            recommendations.append(
                "Review singleton usage - consider dependency injection instead"
            )

        return recommendations

    def _get_pattern_recommendation(self, pattern: str) -> str:
        """Get recommendation for a specific pattern."""
        recommendations = {
            "design_singleton": "Consider dependency injection instead of singleton pattern",
            "design_factory": "Good use of factory pattern for object creation",
            "design_observer": "Consider using event-driven architecture",
            "design_strategy": "Good separation of algorithms",
            "design_decorator": "Consider composition over inheritance",
            "anti_god_class": "Break down into smaller, focused classes",
            "anti_feature_envy": "Move functionality closer to the data it uses",
            "anti_data_class": "Add behavior to data classes or use records/structs",
            "architectural_mvc": "Good separation of concerns with MVC pattern",
            "architectural_repository": "Good data access abstraction",
            "architectural_service": "Consider domain-driven design principles",
            "architectural_dependency_injection": "Good use of inversion of control",
            "long_method": "Break method into smaller, focused functions",
            "too_many_parameters": "Use parameter objects or builder pattern",
        }
        return recommendations.get(
            pattern, "Review pattern usage and consider refactoring"
        )

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

    def _analyze_file_patterns_improved(
        self, file_path: str, relative_path: str
    ) -> List[Dict[str, Any]]:
        """Improved pattern analysis using enhanced detection."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Determine language
            language = self._detect_language(file_path)

            # Use improved pattern detection
            pattern_matches = self.pattern_detector.detect_patterns(
                content, file_path, language
            )

            # Convert to legacy format for compatibility
            for match in pattern_matches:
                findings.append(
                    {
                        "file": relative_path,
                        "line": match.line_number,
                        "pattern": f"{match.pattern_type}_{match.pattern_name}",
                        "severity": match.severity,
                        "message": f"{match.description} (confidence: {match.confidence:.2f})",
                        "context": match.context,
                        "confidence": match.confidence,
                    }
                )

            # For Python files, add AST analysis
            if language == "python":
                ast_matches = self.pattern_detector.analyze_python_ast(
                    content, file_path
                )
                for match in ast_matches:
                    findings.append(
                        {
                            "file": relative_path,
                            "line": match.line_number,
                            "pattern": f"{match.pattern_type}_{match.pattern_name}",
                            "severity": match.severity,
                            "message": f"{match.description} (AST analysis)",
                            "context": match.context,
                            "confidence": match.confidence,
                        }
                    )

        except Exception as e:
            findings.append(
                {
                    "file": relative_path,
                    "line": 0,
                    "pattern": "file_error",
                    "severity": "low",
                    "message": f"Could not analyze file: {str(e)}",
                    "context": "",
                    "confidence": 0.0,
                }
            )

        return findings

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
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
        return language_map.get(ext, "unknown")

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
        }
        return any(filename.endswith(ext) for ext in analyze_extensions)


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze design patterns in codebase")
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

    evaluator = PatternEvaluator()
    result = evaluator.analyze_patterns(args.target_path, args.min_severity)

    if args.output_format == "console":
        # Simple console output
        if result.get("success", False):
            print(f"Pattern Analysis Results for: {args.target_path}")
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
