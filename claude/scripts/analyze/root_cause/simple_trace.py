#!/usr/bin/env python3
"""
Simple root cause analysis script: Basic execution tracing.
Part of Claude Code Workflows.
"""

import os
import sys
import time
from pathlib import Path

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
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Simple execution tracing for root cause analysis"
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

    # Initialize result
    result = AnalysisResult(
        AnalysisType.ARCHITECTURE, "simple_trace.py", str(target_dir)
    )

    # Simple analysis - just count files and basic info
    python_files = list(target_dir.rglob("*.py"))

    # Filter out common excludes
    python_files = [
        f
        for f in python_files
        if not any(
            exclude in str(f)
            for exclude in [
                "node_modules",
                ".git",
                "__pycache__",
                ".pytest_cache",
                "venv",
                "env",
                "build",
                "dist",
            ]
        )
    ]

    # Basic analysis
    for i, file_path in enumerate(python_files[:5]):  # Limit to 5 files
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                line_count = len(content.split("\n"))

            finding_obj = Finding(
                finding_id=f"file_info_{i}",
                title="Python File Analysis",
                description=f"File {file_path.name} has {line_count} lines",
                severity=Severity.INFO,
                file_path=str(file_path),
                evidence={"line_count": line_count, "file_size": len(content)},
            )
            result.add_finding(finding_obj)

        except Exception:
            continue

    # Set execution time and add metadata
    result.set_execution_time(start_time)
    result.metadata.update(
        {
            "python_files_found": len(python_files),
            "files_analyzed": min(5, len(python_files)),
        }
    )

    # Output based on format choice
    if args.output_format == "console":
        print(ResultFormatter.format_console_output(result))
    else:  # json (default)
        print(result.to_json())


if __name__ == "__main__":
    main()
