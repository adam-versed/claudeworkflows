#!/usr/bin/env python3
"""
Root cause analysis script: High-level execution path and dependency pointers.
Part of Claude Code Workflows.
"""

import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Any
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
    from validation import (
        validate_target_directory,
        validate_environment_config,
        log_debug,
    )
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class HighLevelTracer:
    """Provide high-level execution and dependency pointers for LLM investigation."""

    def __init__(self):
        # Simple patterns for basic component identification
        self.patterns = {
            "main_functions": [r"def main\(", r'if __name__ == ["\']__main__["\']'],
            "classes": [r"class \w+"],
            "functions": [r"def \w+\("],
            "imports": [r"import \w+", r"from \w+ import"],
            "try_blocks": [r"try:"],
            "for_loops": [r"for \w+ in"],
            "api_routes": [r"@app\.route", r"app\.(get|post|put|delete)"],
        }

    def analyze_codebase_structure(self, target_dir: Path) -> Dict[str, Any]:
        """Analyze high-level codebase structure rapidly."""
        structure = {
            "file_summary": {},
            "investigation_pointers": [],
            "language_distribution": defaultdict(int),
            "total_metrics": defaultdict(int),
        }

        # Limit analysis to prevent timeouts
        max_files = 20
        files_processed = 0

        # Focus on Python files for initial implementation
        for file_path in target_dir.rglob("*.py"):
            if files_processed >= max_files:
                break

            # Skip common excludes
            if any(
                exclude in str(file_path)
                for exclude in ["__pycache__", ".git", "venv", "env", "build", "dist"]
            ):
                continue

            try:
                file_info = self._analyze_single_file(file_path)
                if file_info:
                    structure["file_summary"][str(file_path)] = file_info
                    structure["language_distribution"]["python"] += 1

                    # Aggregate metrics
                    for key, value in file_info.items():
                        if isinstance(value, int):
                            structure["total_metrics"][key] += value

                    files_processed += 1

            except Exception:
                continue

        # Generate investigation pointers
        self._generate_pointers(structure)

        return structure

    def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Quickly analyze a single file."""
        try:
            # Skip large files
            if file_path.stat().st_size > 100000:  # 100KB limit
                return {"skipped": True, "reason": "file_too_large"}

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.split("\n")
            file_info = {
                "total_lines": len(lines),
                "code_lines": len(
                    [line for line in lines if line.strip() and not line.strip().startswith("#")]
                ),
                "blank_lines": len([line for line in lines if not line.strip()]),
                "comment_lines": len([line for line in lines if line.strip().startswith("#")]),
            }

            # Count basic patterns
            for pattern_name, patterns in self.patterns.items():
                count = 0
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    count += len(matches)
                file_info[pattern_name] = count

            return file_info

        except Exception:
            return None

    def _generate_pointers(self, structure: Dict[str, Any]):
        """Generate investigation pointers based on analysis."""
        pointers = []
        metrics = structure["total_metrics"]
        files = structure["file_summary"]

        # Check for missing main functions
        if metrics.get("main_functions", 0) == 0:
            pointers.append(
                {
                    "type": "no_entry_points",
                    "severity": "medium",
                    "description": "No main functions or entry points found",
                    "investigation_focus": "Identify application startup and entry points",
                    "files_to_investigate": list(files.keys())[:3],
                }
            )

        # Check for error handling coverage
        total_functions = metrics.get("functions", 0)
        try_blocks = metrics.get("try_blocks", 0)
        if total_functions > 5 and try_blocks < (total_functions * 0.2):
            pointers.append(
                {
                    "type": "low_error_handling",
                    "severity": "high",
                    "description": f"Only {try_blocks} try blocks for {total_functions} functions",
                    "investigation_focus": "Review error handling and exception management",
                    "files_to_investigate": list(files.keys())[:3],
                }
            )

        # Check for complex files
        complex_files = []
        for file_path, info in files.items():
            if info.get("code_lines", 0) > 200:
                complex_files.append(file_path)

        if complex_files:
            pointers.append(
                {
                    "type": "complex_files",
                    "severity": "medium",
                    "description": f"Found {len(complex_files)} files with >200 lines of code",
                    "investigation_focus": "Review complex files for potential issues",
                    "files_to_investigate": complex_files[:3],
                }
            )

        # Check for API endpoints
        if metrics.get("api_routes", 0) > 0:
            pointers.append(
                {
                    "type": "web_application_detected",
                    "severity": "info",
                    "description": f"Found {metrics['api_routes']} API routes",
                    "investigation_focus": "Review web application structure and routing",
                    "files_to_investigate": [
                        f for f, info in files.items() if info.get("api_routes", 0) > 0
                    ][:3],
                }
            )

        structure["investigation_pointers"] = pointers


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze execution patterns and dependencies for debugging"
    )
    parser.add_argument(
        "target_path",
        nargs="?",
        default=os.getcwd(),
        help="Path to analyze (default: current directory)",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "console"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()
    start_time = time.time()

    try:
        # Get configuration
        config = validate_environment_config()
        log_debug("Starting trace execution analysis", config)

        # Get and validate target directory
        target_path = args.target_path
        is_valid, error_msg, target_dir = validate_target_directory(target_path)

        if not is_valid:
            # Create error result
            result = AnalysisResult(
                AnalysisType.ARCHITECTURE, "trace_execution.py", target_path
            )
            result.set_error(f"Directory validation failed: {error_msg}")
            print(result.to_json())
            return

        log_debug(f"Analyzing target directory: {target_dir}", config)

        # Initialize tracer
        tracer = HighLevelTracer()
        result = AnalysisResult(
            AnalysisType.ARCHITECTURE, "trace_execution.py", str(target_dir)
        )

        # Analyze codebase structure
        structure = tracer.analyze_codebase_structure(target_dir)
        log_debug(
            f"Analysis complete: {len(structure['investigation_pointers'])} pointers found",
            config,
        )

        # Convert investigation pointers to findings
        for pointer in structure["investigation_pointers"]:
            severity_map = {
                "critical": Severity.CRITICAL,
                "high": Severity.HIGH,
                "medium": Severity.MEDIUM,
                "low": Severity.LOW,
                "info": Severity.INFO,
            }

            finding_obj = Finding(
                finding_id=f"execution_pointer_{hash(pointer['type']) % 10000}",
                title=pointer["type"].replace("_", " ").title(),
                description=pointer["description"],
                severity=severity_map.get(pointer["severity"], Severity.MEDIUM),
                evidence={
                    "investigation_focus": pointer["investigation_focus"],
                    "files_to_investigate": pointer["files_to_investigate"],
                    "pointer_type": pointer["type"],
                },
            )
            result.add_finding(finding_obj)

        # Add file metrics summary
        metrics = structure["total_metrics"]
        if metrics:
            finding_obj = Finding(
                finding_id="codebase_metrics",
                title="Codebase Metrics Summary",
                description=f"Analyzed {len(structure['file_summary'])} Python files",
                severity=Severity.INFO,
                evidence={
                    "total_files": len(structure["file_summary"]),
                    "total_code_lines": metrics.get("code_lines", 0),
                    "total_functions": metrics.get("functions", 0),
                    "total_classes": metrics.get("classes", 0),
                    "language_distribution": dict(structure["language_distribution"]),
                },
            )
            result.add_finding(finding_obj)

        # Set execution time and add metadata
        result.set_execution_time(start_time)
        result.metadata.update(
            {
                "files_analyzed": len(structure["file_summary"]),
                "investigation_pointers": len(structure["investigation_pointers"]),
                "languages_detected": len(structure["language_distribution"]),
                "analysis_scope": "python_files_only",
                "configuration": config,
            }
        )

    except Exception as e:
        # Handle any unexpected errors
        if "result" not in locals():
            result = AnalysisResult(
                AnalysisType.ARCHITECTURE,
                "trace_execution.py",
                str(target_path if "target_path" in locals() else "unknown"),
            )

        result.set_error(f"Analysis failed: {str(e)}")
        if "config" in locals():
            log_debug(f"Error during analysis: {str(e)}", config)

    # Output based on format choice
    if args.output_format == "console":
        print(ResultFormatter.format_console_output(result))
    else:  # json (default)
        print(result.to_json())


if __name__ == "__main__":
    main()
