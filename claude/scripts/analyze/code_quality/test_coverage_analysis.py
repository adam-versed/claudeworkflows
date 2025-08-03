#!/usr/bin/env python3
"""
Language-agnostic test coverage analysis script.
Analyzes test coverage across multiple programming languages and frameworks.
"""

import os
import sys
import re
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Add utils to path for cross-platform and output_formatter imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "utils"))

try:
    from cross_platform import PlatformDetector
    from output_formatter import (
        ResultFormatter,
        AnalysisResult,
        Severity,
    )
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class TestCoverageAnalyzer:
    """Language-agnostic test coverage analyzer."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()

        # Language-specific test patterns and coverage tools
        self.language_configs = {
            "python": {
                "test_patterns": [r"test_.*\.py$", r".*_test\.py$", r"tests?/.*\.py$"],
                "source_patterns": [r".*\.py$"],
                "coverage_tools": ["coverage", "pytest-cov"],
                "coverage_files": [".coverage", "coverage.xml", "htmlcov/"],
                "exclude_dirs": ["__pycache__", ".pytest_cache", "venv", ".venv"],
            },
            "javascript": {
                "test_patterns": [
                    r".*\.test\.js$",
                    r".*\.spec\.js$",
                    r"__tests__/.*\.js$",
                    r"tests?/.*\.js$",
                ],
                "source_patterns": [r".*\.js$", r".*\.jsx$"],
                "coverage_tools": ["jest", "nyc", "c8"],
                "coverage_files": ["coverage/", ".nyc_output/", "coverage.json"],
                "exclude_dirs": ["node_modules", "coverage", "dist", "build"],
            },
            "typescript": {
                "test_patterns": [
                    r".*\.test\.ts$",
                    r".*\.spec\.ts$",
                    r"__tests__/.*\.ts$",
                ],
                "source_patterns": [r".*\.ts$", r".*\.tsx$"],
                "coverage_tools": ["jest", "nyc", "c8"],
                "coverage_files": ["coverage/", ".nyc_output/", "coverage.json"],
                "exclude_dirs": ["node_modules", "coverage", "dist", "build"],
            },
            "java": {
                "test_patterns": [
                    r".*Test\.java$",
                    r".*Tests\.java$",
                    r"src/test/.*\.java$",
                ],
                "source_patterns": [r".*\.java$"],
                "coverage_tools": ["jacoco", "cobertura"],
                "coverage_files": ["target/site/jacoco/", "target/cobertura/"],
                "exclude_dirs": ["target", ".gradle", "build"],
            },
            "go": {
                "test_patterns": [r".*_test\.go$"],
                "source_patterns": [r".*\.go$"],
                "coverage_tools": ["go test"],
                "coverage_files": ["coverage.out", "coverage.html"],
                "exclude_dirs": ["vendor/"],
            },
            "rust": {
                "test_patterns": [
                    r"tests/.*\.rs$",
                    r".*\.rs$",
                ],  # Rust tests can be in same file
                "source_patterns": [r".*\.rs$"],
                "coverage_tools": ["tarpaulin", "grcov"],
                "coverage_files": ["target/tarpaulin/", "target/debug/coverage/"],
                "exclude_dirs": ["target/"],
            },
            "csharp": {
                "test_patterns": [
                    r".*Test\.cs$",
                    r".*Tests\.cs$",
                    r".*\.Tests/.*\.cs$",
                ],
                "source_patterns": [r".*\.cs$"],
                "coverage_tools": ["coverlet", "dotcover"],
                "coverage_files": ["coverage.xml", "TestResults/"],
                "exclude_dirs": ["bin/", "obj/", "packages/"],
            },
            "ruby": {
                "test_patterns": [r".*_test\.rb$", r"test/.*\.rb$", r"spec/.*\.rb$"],
                "source_patterns": [r".*\.rb$"],
                "coverage_tools": ["simplecov"],
                "coverage_files": ["coverage/", ".resultset.json"],
                "exclude_dirs": ["vendor/", "coverage/"],
            },
            "php": {
                "test_patterns": [r".*Test\.php$", r"tests/.*\.php$"],
                "source_patterns": [r".*\.php$"],
                "coverage_tools": ["phpunit", "xdebug"],
                "coverage_files": ["coverage/", "clover.xml"],
                "exclude_dirs": ["vendor/", "coverage/"],
            },
            "cpp": {
                "test_patterns": [
                    r".*_test\.cpp$",
                    r".*_test\.cc$",
                    r"test.*\.cpp$",
                    r"tests/.*\.cpp$",
                ],
                "source_patterns": [
                    r".*\.cpp$",
                    r".*\.cc$",
                    r".*\.cxx$",
                    r".*\.c\+\+$",
                ],
                "coverage_tools": ["gcov", "lcov", "llvm-cov"],
                "coverage_files": ["coverage.info", "coverage/", "coverage.xml"],
                "exclude_dirs": [
                    "build/",
                    "cmake-build-*/",
                    ".vs/",
                    "Debug/",
                    "Release/",
                ],
            },
            "swift": {
                "test_patterns": [
                    r".*Tests\.swift$",
                    r".*Test\.swift$",
                    r"Tests/.*\.swift$",
                ],
                "source_patterns": [r".*\.swift$"],
                "coverage_tools": ["swift test", "xccov"],
                "coverage_files": [".build/debug/codecov/", "DerivedData/"],
                "exclude_dirs": [".build/", "DerivedData/", "Packages/"],
            },
            "kotlin": {
                "test_patterns": [r".*Test\.kt$", r".*Tests\.kt$", r"src/test/.*\.kt$"],
                "source_patterns": [r".*\.kt$", r".*\.kts$"],
                "coverage_tools": ["jacoco", "kover"],
                "coverage_files": ["build/reports/jacoco/", "build/reports/kover/"],
                "exclude_dirs": ["build/", ".gradle/", "out/"],
            },
        }

        # Generic test indicators (language-agnostic)
        self.generic_test_indicators = [
            r"test",
            r"spec",
            r"_test",
            r"Test",
            r"Tests",
            r"__tests__",
            r"assert",
            r"expect",
            r"should",
            r"describe",
            r"it\(",
            r"@Test",
            r"#[test]",
            r"func.*Test",
            r"def test_",
        ]

    def detect_languages(self, target_path: Path) -> Dict[str, int]:
        """Detect programming languages in the target directory."""
        language_counts = defaultdict(int)

        for file_path in target_path.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix.lower()

                # Map file extensions to languages
                ext_map = {
                    ".py": "python",
                    ".js": "javascript",
                    ".jsx": "javascript",
                    ".ts": "typescript",
                    ".tsx": "typescript",
                    ".java": "java",
                    ".go": "go",
                    ".rs": "rust",
                    ".cs": "csharp",
                    ".rb": "ruby",
                    ".php": "php",
                    ".cpp": "cpp",
                    ".cc": "cpp",
                    ".cxx": "cpp",
                    ".c++": "cpp",
                    ".c": "cpp",  # Treat C as C++ for simplicity
                    ".h": "cpp",
                    ".hpp": "cpp",
                    ".swift": "swift",
                    ".kt": "kotlin",
                    ".kts": "kotlin",
                }

                if suffix in ext_map:
                    language_counts[ext_map[suffix]] += 1

        return dict(language_counts)

    def find_test_files(
        self, target_path: Path, languages: List[str]
    ) -> Dict[str, List[Path]]:
        """Find test files for detected languages."""
        test_files = defaultdict(list)

        for lang in languages:
            config = self.language_configs.get(lang, {})
            patterns = config.get("test_patterns", [])
            exclude_dirs = config.get("exclude_dirs", [])

            for file_path in target_path.rglob("*"):
                if file_path.is_file():
                    # Skip excluded directories
                    if any(exc_dir in str(file_path) for exc_dir in exclude_dirs):
                        continue

                    # Check if file matches test patterns
                    for pattern in patterns:
                        if re.search(pattern, str(file_path)):
                            test_files[lang].append(file_path)
                            break

        return dict(test_files)

    def find_source_files(
        self, target_path: Path, languages: List[str]
    ) -> Dict[str, List[Path]]:
        """Find source files for detected languages."""
        source_files = defaultdict(list)

        for lang in languages:
            config = self.language_configs.get(lang, {})
            patterns = config.get("source_patterns", [])
            exclude_dirs = config.get("exclude_dirs", [])

            for file_path in target_path.rglob("*"):
                if file_path.is_file():
                    # Skip excluded directories
                    if any(exc_dir in str(file_path) for exc_dir in exclude_dirs):
                        continue

                    # Check if file matches source patterns
                    for pattern in patterns:
                        if re.search(pattern, str(file_path)):
                            source_files[lang].append(file_path)
                            break

        return dict(source_files)

    def detect_coverage_tools(self, target_path: Path) -> Dict[str, List[str]]:
        """Detect available coverage tools and existing coverage data."""
        detected_tools = defaultdict(list)

        # Check for configuration files that indicate coverage tools
        coverage_indicators = {
            ".coveragerc": "coverage.py",
            "pytest.ini": "pytest-cov",
            "jest.config.js": "jest",
            "jest.config.json": "jest",
            "package.json": "jest/nyc",
            "pom.xml": "jacoco",
            "build.gradle": "jacoco",
            "Cargo.toml": "tarpaulin",
            "tarpaulin.toml": "tarpaulin",
            "phpunit.xml": "phpunit",
            "Gemfile": "simplecov",
            "CMakeLists.txt": "gcov/lcov",
            "Package.swift": "swift test",
            "build.gradle.kts": "jacoco/kover",
            "gradle.properties": "jacoco/kover",
        }

        for config_file, tool in coverage_indicators.items():
            if (target_path / config_file).exists():
                detected_tools["config_files"].append(f"{config_file} ({tool})")

        # Check for existing coverage output directories/files
        coverage_outputs = [
            "coverage/",
            "htmlcov/",
            ".nyc_output/",
            "target/site/jacoco/",
            "coverage.xml",
            "coverage.json",
            ".coverage",
            "coverage.out",
        ]

        for output in coverage_outputs:
            output_path = target_path / output
            if output_path.exists():
                detected_tools["existing_coverage"].append(str(output))

        return dict(detected_tools)

    def analyze_test_coverage_ratio(
        self, test_files: Dict[str, List[Path]], source_files: Dict[str, List[Path]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze test-to-source file ratios for each language."""
        coverage_ratios = {}

        for lang in set(test_files.keys()) | set(source_files.keys()):
            test_count = len(test_files.get(lang, []))
            source_count = len(source_files.get(lang, []))

            if source_count > 0:
                ratio = test_count / source_count
                coverage_level = (
                    "excellent" if ratio >= 0.8 else "good" if ratio >= 0.5 else "poor"
                )
            else:
                ratio = 0
                coverage_level = "none"

            coverage_ratios[lang] = {
                "test_files": test_count,
                "source_files": source_count,
                "ratio": ratio,
                "coverage_level": coverage_level,
                "percentage": min(ratio * 100, 100),
            }

        return coverage_ratios

    def run_coverage_tools(
        self, target_path: Path, languages: List[str]
    ) -> Dict[str, Any]:
        """Attempt to run available coverage tools for detected languages."""
        coverage_results = {}

        for lang in languages:
            config = self.language_configs.get(lang, {})
            tools = config.get("coverage_tools", [])

            for tool in tools:
                try:
                    # Attempt to run coverage tool (safely)
                    if tool == "coverage" and lang == "python":
                        result = self._run_python_coverage(target_path)
                    elif tool == "go test" and lang == "go":
                        result = self._run_go_coverage(target_path)
                    elif tool in ["jest", "nyc"] and lang in [
                        "javascript",
                        "typescript",
                    ]:
                        result = self._run_js_coverage(target_path, tool)
                    else:
                        result = {
                            "available": False,
                            "reason": f"Tool {tool} execution not implemented",
                        }

                    coverage_results[f"{lang}_{tool}"] = result
                except Exception as e:
                    coverage_results[f"{lang}_{tool}"] = {
                        "available": False,
                        "error": str(e),
                    }

        return coverage_results

    def _run_python_coverage(self, target_path: Path) -> Dict[str, Any]:
        """Run Python coverage analysis if available."""
        try:
            # Check if coverage is available
            result = subprocess.run(
                ["coverage", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return {"available": True, "version": result.stdout.strip()}
            else:
                return {"available": False, "reason": "coverage command not found"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"available": False, "reason": "coverage tool not installed"}

    def _run_go_coverage(self, target_path: Path) -> Dict[str, Any]:
        """Check Go test coverage availability."""
        try:
            result = subprocess.run(
                ["go", "version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return {"available": True, "version": result.stdout.strip()}
            else:
                return {"available": False, "reason": "go command not found"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"available": False, "reason": "go not installed"}

    def _run_js_coverage(self, target_path: Path, tool: str) -> Dict[str, Any]:
        """Check JavaScript coverage tool availability."""
        try:
            cmd = "npm" if self.platform.is_windows() else "npm"
            result = subprocess.run(
                [cmd, "list", tool], capture_output=True, text=True, timeout=10
            )
            if tool in result.stdout:
                return {"available": True, "tool": tool}
            else:
                return {"available": False, "reason": f"{tool} not installed via npm"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"available": False, "reason": "npm not available"}

    def generate_recommendations(
        self, analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate coverage improvement recommendations."""
        recommendations = []

        coverage_ratios = analysis_results.get("coverage_ratios", {})
        detected_tools = analysis_results.get("detected_tools", {})

        for lang, ratio_data in coverage_ratios.items():
            if ratio_data["coverage_level"] == "poor":
                recommendations.append(
                    {
                        "language": lang,
                        "priority": "high",
                        "issue": f"Low test coverage ratio: {ratio_data['percentage']:.1f}%",
                        "recommendation": f"Add more test files for {lang}. Target ratio: 1 test file per source file.",
                        "current_ratio": f"{ratio_data['test_files']}:{ratio_data['source_files']}",
                    }
                )
            elif ratio_data["coverage_level"] == "none":
                recommendations.append(
                    {
                        "language": lang,
                        "priority": "critical",
                        "issue": f"No test files found for {lang}",
                        "recommendation": f"Create test suite for {lang} codebase.",
                        "suggested_tools": self.language_configs.get(lang, {}).get(
                            "coverage_tools", []
                        ),
                    }
                )

        # Recommend coverage tools if none detected
        if not detected_tools.get("config_files") and not detected_tools.get(
            "existing_coverage"
        ):
            recommendations.append(
                {
                    "priority": "medium",
                    "issue": "No coverage tools detected",
                    "recommendation": "Set up coverage measurement tools for better visibility",
                    "suggested_actions": [
                        "Add coverage configuration",
                        "Integrate with CI/CD",
                    ],
                }
            )

        return recommendations

    def analyze(self, target_path: str) -> AnalysisResult:
        """Main analysis method."""
        try:
            start_time = time.time()
            target = Path(target_path).resolve()

            if not target.exists():
                result = self.formatter.create_code_quality_result(
                    "test_coverage_analysis.py", target_path
                )
                result.set_error(f"Target path does not exist: {target_path}")
                return result.to_dict()

            # Detect languages
            languages = self.detect_languages(target)

            if not languages:
                result = self.formatter.create_code_quality_result(
                    "test_coverage_analysis.py", target_path
                )
                result.metadata = {
                    "message": "No recognized programming languages found"
                }
                result.set_execution_time(start_time)
                return result.to_dict()

            # Find test and source files
            test_files = self.find_test_files(target, list(languages.keys()))
            source_files = self.find_source_files(target, list(languages.keys()))

            # Detect coverage tools
            detected_tools = self.detect_coverage_tools(target)

            # Analyze coverage ratios
            coverage_ratios = self.analyze_test_coverage_ratio(test_files, source_files)

            # Run coverage tools (if available)
            tool_results = self.run_coverage_tools(target, list(languages.keys()))

            # Generate findings based on analysis
            findings = []

            for lang, ratio_data in coverage_ratios.items():
                severity = Severity.INFO
                if ratio_data["coverage_level"] == "poor":
                    severity = Severity.HIGH
                elif ratio_data["coverage_level"] == "none":
                    severity = Severity.CRITICAL
                elif ratio_data["coverage_level"] == "good":
                    severity = Severity.MEDIUM

                finding = self.formatter.create_finding(
                    finding_id=f"COVERAGE_{lang.upper()}_RATIO",
                    title=f"{lang.title()} Test Coverage Ratio",
                    description=f"Test-to-source file ratio: {ratio_data['ratio']:.2f} ({ratio_data['coverage_level']})",
                    severity=severity.value,
                    file_path=str(target),
                    line_number=None,
                    evidence={
                        "test_files": ratio_data["test_files"],
                        "source_files": ratio_data["source_files"],
                        "percentage": f"{ratio_data['percentage']:.1f}%",
                    },
                )
                findings.append(finding)

            # Generate recommendations
            recommendations = self.generate_recommendations(
                {"coverage_ratios": coverage_ratios, "detected_tools": detected_tools}
            )

            time.time() - start_time

            result = self.formatter.create_code_quality_result(
                "test_coverage_analysis.py", target_path
            )
            for finding in findings:
                result.add_finding(finding)
            result.set_execution_time(start_time)
            result.metadata = {
                "languages_detected": languages,
                "test_files_by_language": {k: len(v) for k, v in test_files.items()},
                "source_files_by_language": {
                    k: len(v) for k, v in source_files.items()
                },
                "coverage_tools_detected": detected_tools,
                "coverage_tool_availability": tool_results,
                "recommendations": recommendations,
                "total_test_files": sum(len(v) for v in test_files.values()),
                "total_source_files": sum(len(v) for v in source_files.values()),
            }
            return result.to_dict()

        except Exception as e:
            result = self.formatter.create_code_quality_result(
                "test_coverage_analysis.py", target_path
            )
            result.set_error(str(e))
            result.set_execution_time(start_time)
            return result.to_dict()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze test coverage across multiple programming languages and frameworks"
    )
    parser.add_argument("target_path", help="Path to analyze")
    parser.add_argument(
        "--output-format",
        choices=["json", "console"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    analyzer = TestCoverageAnalyzer()
    result_dict = analyzer.analyze(args.target_path)

    if args.output_format == "console":
        # Simple console output
        if result_dict.get("success", False):
            print(f"Test Coverage Analysis Results for: {args.target_path}")
            print(f"Analysis Type: {result_dict.get('analysis_type', 'unknown')}")
            print(f"Execution Time: {result_dict.get('execution_time', 0)}s")
            print(f"\nFindings: {len(result_dict.get('findings', []))}")
            for finding in result_dict.get("findings", []):
                title = finding.get("title", "Unknown")
                description = finding.get("description", "")
                severity = finding.get("severity", "unknown")
                print(f"  - {title}: {description} [{severity}]")
        else:
            error_msg = result_dict.get("error_message", "Unknown error")
            print(f"Error: {error_msg}")
    else:  # json (default)
        print(json.dumps(result_dict, indent=2, default=str))


if __name__ == "__main__":
    main()
