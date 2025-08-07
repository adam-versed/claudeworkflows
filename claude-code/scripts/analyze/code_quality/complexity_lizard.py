#!/usr/bin/env python3
"""
Code complexity analysis using Lizard - a multi-language complexity analyzer.
Supports: C/C++/C#, Java, JavaScript, Python, Ruby, PHP, Swift, Go, Rust, TypeScript, etc.
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List

# Add utils to path
script_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(script_dir / "utils"))

from output_formatter import ResultFormatter  # noqa: E402
from tech_stack_detector import TechStackDetector  # noqa: E402


class LizardComplexityAnalyzer:
    """Wrapper around Lizard for code complexity analysis."""

    def __init__(self):
        # Initialize tech stack detector for smart filtering
        self.tech_detector = TechStackDetector()

        # Thresholds based on industry standards
        self.thresholds = {
            "cyclomatic_complexity": {
                "high": 20,  # Very complex
                "medium": 10,  # Complex
                "low": 5,  # Moderate
            },
            "function_length": {
                "high": 100,  # Very long
                "medium": 50,  # Long
                "low": 25,  # Getting long
            },
            "parameter_count": {
                "high": 7,  # Too many
                "medium": 5,  # Many
                "low": 4,  # Starting to be many
            },
        }

    def check_lizard_installed(self) -> bool:
        """Check if lizard is installed."""
        try:
            subprocess.run(["lizard", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_filtered_files(self, target_path: str) -> List[str]:
        """Get list of files to analyze using universal exclusion system."""
        import os

        files_to_analyze = []

        # Walk through directory structure and apply universal filtering
        for root, dirs, files in os.walk(target_path):
            for file in files:
                file_path = os.path.join(root, file)

                # Use universal exclusion system
                if self.tech_detector.should_analyze_file(file_path, target_path):
                    # Only include supported file extensions
                    if any(
                        file.endswith(ext)
                        for ext in [
                            ".py",
                            ".js",
                            ".ts",
                            ".tsx",
                            ".jsx",
                            ".java",
                            ".cpp",
                            ".c",
                            ".h",
                            ".go",
                            ".rs",
                            ".swift",
                            ".kt",
                            ".cs",
                            ".rb",
                            ".php",
                        ]
                    ):
                        files_to_analyze.append(file_path)

        return files_to_analyze

    def run_lizard(self, target_path: str) -> Dict[str, Any]:
        """Run lizard on filtered files with smart filtering."""
        try:
            # Get filtered list of files to analyze
            files_to_analyze = self.get_filtered_files(target_path)

            if not files_to_analyze:
                return {"files": []}

            all_output = ""
            batch_size = (
                100  # Process files in batches to avoid "Argument list too long"
            )

            # Process files in batches
            for i in range(0, len(files_to_analyze), batch_size):
                batch = files_to_analyze[i : i + batch_size]

                # Run lizard on this batch
                cmd = [
                    "lizard",
                    "-C",
                    "999",  # Set high to get all results
                    "-L",
                    "999",  # Set high to get all results
                    "-a",
                    "999",  # Set high to get all results
                ] + batch

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    all_output += result.stdout + "\n"
                elif result.stderr:
                    # Continue with other batches even if one fails
                    continue

            # Parse combined output (no additional filtering needed since we pre-filtered)
            return self.parse_default_output(all_output, [], target_path)

        except Exception as e:
            return {"error": str(e)}

    def parse_default_output(
        self, output: str, exclusion_patterns: list = None, target_path: str = ""
    ) -> Dict[str, Any]:
        """Parse Lizard default output into structured data with filtering."""
        import re

        if exclusion_patterns is None:
            exclusion_patterns = []

        lines = output.strip().split("\n")
        files_data = {}

        # Skip header lines and summary lines
        data_lines = []
        for line in lines:
            if (
                not line.startswith("=")
                and not line.startswith("-")
                and "NLOC" not in line
                and "file analyzed" not in line
                and "No thresholds" not in line
                and "Total nloc" not in line
                and line.strip()
                and "@" in line
            ):  # Only lines with function@location format
                data_lines.append(line)

        for line in data_lines:
            # Parse format: NLOC CCN token PARAM length location
            # Example: 19 3 75 2 20 authorize@103-122@/path/to/file.ts
            parts = line.strip().split()
            if len(parts) < 6:
                continue

            try:
                nloc = int(parts[0])
                ccn = int(parts[1])
                token_count = int(parts[2])
                param_count = int(parts[3])
                length = int(parts[4])
                location = " ".join(parts[5:])  # Join remaining parts for location

                # Parse location: function_name@start-end@filepath
                match = re.match(r"(.+)@(\d+)-(\d+)@(.+)", location)
                if not match:
                    continue

                func_name = match.group(1)
                start_line = int(match.group(2))
                end_line = int(match.group(3))
                filepath = match.group(4)

                # Apply smart filtering - skip files that should be excluded
                if not self.tech_detector.should_analyze_file(
                    filepath, target_path or ""
                ):
                    continue

                if filepath not in files_data:
                    files_data[filepath] = {"filename": filepath, "functions": []}

                func_data = {
                    "name": func_name,
                    "cyclomatic_complexity": ccn,
                    "nloc": nloc,
                    "parameter_count": param_count,
                    "start_line": start_line,
                    "end_line": end_line,
                    "token_count": token_count,
                    "length": length,
                }
                files_data[filepath]["functions"].append(func_data)

            except (ValueError, IndexError):
                # Skip lines that don't match expected format
                continue

        return {"files": list(files_data.values())}

    def get_severity(self, metric_type: str, value: float) -> str:
        """Determine severity based on thresholds."""
        thresholds = self.thresholds.get(metric_type, {})

        if value >= thresholds.get("high", float("inf")):
            return "high"
        elif value >= thresholds.get("medium", float("inf")):
            return "medium"
        elif value >= thresholds.get("low", float("inf")):
            return "low"
        else:
            return "info"

    def analyze(self, target_path: str):
        """Main analysis function."""
        start_time = time.time()
        result = ResultFormatter.create_code_quality_result(
            "complexity_lizard.py", target_path
        )

        try:
            # Check lizard is installed
            if not self.check_lizard_installed():
                result.set_error("Lizard is not installed. Run: pip install lizard")
                return result

            # Run lizard analysis
            lizard_output = self.run_lizard(target_path)

            if "error" in lizard_output:
                result.set_error(lizard_output["error"])
                return result

            # Process results
            finding_id = 1

            for file_data in lizard_output.get("files", []):
                file_path = file_data.get("filename", "")

                for func_data in file_data.get("functions", []):
                    func_name = func_data.get("name", "unknown")
                    ccn = func_data.get("cyclomatic_complexity", 0)
                    length = func_data.get("nloc", 0)  # lines of code
                    params = func_data.get("parameter_count", 0)
                    line_num = func_data.get("start_line", 1)

                    # Check cyclomatic complexity
                    ccn_severity = self.get_severity("cyclomatic_complexity", ccn)
                    if ccn_severity in ["high", "medium"]:
                        finding = ResultFormatter.create_finding(
                            f"CMPLX{finding_id:03d}",
                            "High Cyclomatic Complexity",
                            f"Function '{func_name}' has cyclomatic complexity of {ccn}",
                            ccn_severity,
                            file_path,
                            line_num,
                            "Consider breaking down this function. Aim for complexity < 10",
                            {
                                "function_name": func_name,
                                "cyclomatic_complexity": ccn,
                                "lines_of_code": length,
                                "parameters": params,
                            },
                        )
                        result.add_finding(finding)
                        finding_id += 1

                    # Check function length
                    length_severity = self.get_severity("function_length", length)
                    if length_severity in ["high", "medium"]:
                        finding = ResultFormatter.create_finding(
                            f"CMPLX{finding_id:03d}",
                            "Long Function",
                            f"Function '{func_name}' is {length} lines long",
                            length_severity,
                            file_path,
                            line_num,
                            "Consider breaking down this function. Aim for < 50 lines",
                            {
                                "function_name": func_name,
                                "lines_of_code": length,
                                "cyclomatic_complexity": ccn,
                            },
                        )
                        result.add_finding(finding)
                        finding_id += 1

                    # Check parameter count
                    param_severity = self.get_severity("parameter_count", params)
                    if param_severity in ["high", "medium"]:
                        finding = ResultFormatter.create_finding(
                            f"CMPLX{finding_id:03d}",
                            "Too Many Parameters",
                            f"Function '{func_name}' has {params} parameters",
                            param_severity,
                            file_path,
                            line_num,
                            "Consider using parameter objects or configuration classes",
                            {"function_name": func_name, "parameter_count": params},
                        )
                        result.add_finding(finding)
                        finding_id += 1

            # Add metadata
            result.metadata = {
                "total_files": len(lizard_output.get("files", [])),
                "total_functions": sum(
                    len(f.get("functions", [])) for f in lizard_output.get("files", [])
                ),
                "thresholds": self.thresholds,
            }

        except Exception as e:
            result.set_error(f"Analysis failed: {str(e)}")

        result.set_execution_time(start_time)
        return result


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze code complexity using Lizard")
    parser.add_argument("target_path", help="Path to analyze")
    parser.add_argument(
        "--output-format",
        choices=["json", "console", "summary"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show only high/critical findings"
    )
    parser.add_argument(
        "--min-severity",
        choices=["critical", "high", "medium", "low"],
        default="low",
        help="Minimum severity level (default: low)",
    )

    args = parser.parse_args()

    analyzer = LizardComplexityAnalyzer()
    result = analyzer.analyze(args.target_path)

    # Output based on format choice
    if args.output_format == "console":
        print(ResultFormatter.format_console_output(result))
    elif args.output_format == "summary":
        print(result.to_json(summary_mode=True, min_severity=args.min_severity))
    else:  # json (default)
        print(result.to_json(summary_mode=args.summary, min_severity=args.min_severity))
        # Print console summary to stderr for human readability
        print(ResultFormatter.format_console_output(result), file=sys.stderr)


if __name__ == "__main__":
    main()
