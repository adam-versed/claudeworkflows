#!/usr/bin/env python3
"""
Language-agnostic performance baseline analyzer.
Establishes performance benchmarks before refactoring for comparison validation.
"""

import os
import sys
import json
import time
import psutil
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
    )
    from tech_stack_detector import TechStackDetector
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class PerformanceBaseliner:
    """Language-agnostic performance baseline analyzer."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()
        # Initialize tech stack detector for smart filtering
        self.tech_detector = TechStackDetector()

        # Language-specific performance testing commands
        self.perf_commands = {
            "python": {
                "test_runner": [
                    "python",
                    "-m",
                    "pytest",
                    "--benchmark-only",
                    "--json-report",
                ],
                "profiler": ["python", "-m", "cProfile", "-o"],
                "memory_profiler": ["python", "-m", "memory_profiler"],
                "time_command": ["python", "-m", "timeit"],
            },
            "javascript": {
                "test_runner": ["npm", "run", "test:perf"],
                "benchmark": ["npm", "run", "benchmark"],
                "profiler": ["node", "--prof"],
                "memory_usage": ["node", "--trace-gc"],
            },
            "typescript": {
                "test_runner": ["npm", "run", "test:perf"],
                "benchmark": ["npm", "run", "benchmark"],
                "profiler": ["node", "--prof"],
                "build_time": ["npm", "run", "build"],
            },
            "java": {
                "test_runner": ["mvn", "test", "-Dtest=**/*PerfTest"],
                "benchmark": ["java", "-jar", "target/benchmarks.jar"],
                "profiler": ["java", "-XX:+FlightRecorder"],
                "gradle_perf": ["gradle", "test", "--profile"],
            },
            "go": {
                "test_runner": ["go", "test", "-bench=.", "-benchmem"],
                "profiler": ["go", "test", "-cpuprofile=cpu.prof"],
                "memory_prof": ["go", "test", "-memprofile=mem.prof"],
                "race_detector": ["go", "test", "-race"],
            },
            "rust": {
                "test_runner": ["cargo", "bench"],
                "profiler": ["cargo", "flamegraph"],
                "criterion": ["cargo", "test", "--release", "--", "--bench"],
            },
            "csharp": {
                "test_runner": ["dotnet", "test", "--configuration", "Release"],
                "benchmark": [
                    "dotnet",
                    "run",
                    "--configuration",
                    "Release",
                    "--project",
                    "Benchmarks",
                ],
            },
            "ruby": {
                "test_runner": ["bundle", "exec", "rspec", "--format", "json"],
                "benchmark": ["ruby", "-r", "benchmark"],
                "profiler": ["ruby-prof"],
                "memory_profiler": ["ruby", "-r", "memory_profiler"],
            },
            "php": {
                "test_runner": ["vendor/bin/phpunit", "--log-json"],
                "benchmark": ["php", "-d", "memory_limit=-1"],
                "profiler": ["xdebug"],
                "memory_usage": ["php", "-d", "xdebug.profiler_enable=1"],
            },
            "cpp": {
                "test_runner": ["ctest", "--output-on-failure"],
                "benchmark": ["cmake", "--build", "build", "--target", "benchmark"],
                "profiler": ["perf", "record"],
                "memory_profiler": ["valgrind", "--tool=massif"],
            },
            "swift": {
                "test_runner": ["swift", "test", "--enable-code-coverage"],
                "benchmark": ["swift", "run", "--configuration", "release"],
                "profiler": ["instruments", "-t", "Time Profiler"],
                "memory_profiler": ["instruments", "-t", "Allocations"],
            },
            "kotlin": {
                "test_runner": ["gradle", "test", "--info"],
                "benchmark": ["gradle", "jmh"],
                "profiler": ["gradle", "profileTest"],
                "memory_profiler": [
                    "gradle",
                    "test",
                    "-Dorg.gradle.jvmargs=-XX:+HeapDumpOnOutOfMemoryError",
                ],
            },
        }

        # Performance metrics to capture
        self.baseline_metrics = [
            "execution_time",
            "memory_usage",
            "cpu_utilization",
            "build_time",
            "startup_time",
            "throughput",
            "latency",
            "file_sizes",
            "dependency_count",
        ]

    def detect_project_languages(self, target_path: Path) -> Dict[str, int]:
        """Detect programming languages and their prevalence in the project."""
        language_counts = defaultdict(int)

        for file_path in target_path.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix.lower()

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
                    ".c": "cpp",
                    ".h": "cpp",
                    ".hpp": "cpp",
                    ".swift": "swift",
                    ".kt": "kotlin",
                    ".kts": "kotlin",
                }

                if suffix in ext_map:
                    language_counts[ext_map[suffix]] += 1

        return dict(language_counts)

    def analyze_project_structure(self, target_path: Path) -> Dict[str, Any]:
        """Analyze project structure for baseline metrics."""
        structure_metrics = {
            "total_files": 0,
            "total_size_bytes": 0,
            "directory_count": 0,
            "max_depth": 0,
            "largest_files": [],
            "file_type_distribution": defaultdict(int),
        }

        # Get exclusion directories using universal exclusion system
        exclude_dirs = self.tech_detector.get_simple_exclusions(target_path)[
            "directories"
        ]

        for root, dirs, files in os.walk(target_path):
            # Filter directories using universal exclusion system
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            depth = len(Path(root).relative_to(target_path).parts)
            structure_metrics["max_depth"] = max(structure_metrics["max_depth"], depth)
            structure_metrics["directory_count"] += len(dirs)

            for file in files:
                file_path = Path(root) / file
                try:
                    file_size = file_path.stat().st_size
                    structure_metrics["total_files"] += 1
                    structure_metrics["total_size_bytes"] += file_size
                    structure_metrics["file_type_distribution"][
                        file_path.suffix.lower()
                    ] += 1

                    # Track largest files
                    structure_metrics["largest_files"].append(
                        {
                            "path": str(file_path.relative_to(target_path)),
                            "size": file_size,
                        }
                    )
                except (OSError, PermissionError):
                    continue

        # Keep only top 10 largest files
        structure_metrics["largest_files"] = sorted(
            structure_metrics["largest_files"], key=lambda x: x["size"], reverse=True
        )[:10]

        return structure_metrics

    def capture_system_baseline(self) -> Dict[str, Any]:
        """Capture current system performance baseline."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_used_percent": memory.percent,
                "disk_total": disk.total,
                "disk_free": disk.free,
                "disk_used_percent": (disk.used / disk.total) * 100,
                "cpu_count": psutil.cpu_count(),
                "platform": self.platform.get_platform_info(),
            }
        except Exception as e:
            return {"error": f"Failed to capture system metrics: {str(e)}"}

    def measure_build_performance(
        self, target_path: Path, languages: List[str]
    ) -> Dict[str, Any]:
        """Measure build performance for detected languages."""
        build_metrics = {}

        for lang in languages:
            if lang not in self.perf_commands:
                continue

            self.perf_commands[lang]
            build_results = {}

            # Try common build commands for each language
            build_commands = {
                "python": [
                    ["python", "-m", "py_compile"],
                    ["pip", "install", "-e", "."],
                ],
                "javascript": [["npm", "install"], ["npm", "run", "build"]],
                "typescript": [
                    ["npm", "install"],
                    ["npm", "run", "build"],
                    ["tsc", "--noEmit"],
                ],
                "java": [["mvn", "compile"], ["gradle", "build"]],
                "go": [["go", "build", "./..."], ["go", "mod", "tidy"]],
                "rust": [["cargo", "check"], ["cargo", "build", "--release"]],
                "csharp": [["dotnet", "build"], ["dotnet", "restore"]],
                "ruby": [["bundle", "install"], ["bundle", "exec", "rake"]],
                "php": [["composer", "install"], ["composer", "dump-autoload"]],
                "cpp": [
                    ["cmake", "-S", ".", "-B", "build"],
                    ["cmake", "--build", "build"],
                ],
                "swift": [["swift", "build"], ["swift", "package", "resolve"]],
                "kotlin": [["gradle", "build"], ["gradle", "assemble"]],
            }

            if lang in build_commands:
                for cmd in build_commands[lang]:
                    cmd_name = " ".join(cmd)
                    build_results[cmd_name] = self._measure_command_performance(
                        cmd, target_path
                    )

            if build_results:
                build_metrics[lang] = build_results

        return build_metrics

    def _measure_command_performance(
        self, command: List[str], cwd: Path
    ) -> Dict[str, Any]:
        """Measure performance of a single command."""
        try:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss if psutil else 0

            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss if psutil else 0

            return {
                "success": result.returncode == 0,
                "execution_time": end_time - start_time,
                "memory_delta": end_memory - start_memory,
                "return_code": result.returncode,
                "stdout_lines": len(result.stdout.splitlines()) if result.stdout else 0,
                "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "execution_time": 300,
            }
        except FileNotFoundError:
            return {"success": False, "error": "Command not found", "execution_time": 0}
        except Exception as e:
            return {"success": False, "error": str(e), "execution_time": 0}

    def analyze_dependencies(self, target_path: Path) -> Dict[str, Any]:
        """Analyze project dependencies for baseline metrics."""
        dependency_files = {
            "package.json": "javascript/typescript",
            "requirements.txt": "python",
            "Pipfile": "python",
            "pom.xml": "java",
            "build.gradle": "java",
            "go.mod": "go",
            "Cargo.toml": "rust",
            "*.csproj": "csharp",
            "Gemfile": "ruby",
            "composer.json": "php",
            "CMakeLists.txt": "cpp",
            "Package.swift": "swift",
            "build.gradle.kts": "kotlin",
        }

        found_dependencies = {}

        for dep_file, language in dependency_files.items():
            if "*" in dep_file:
                # Handle glob patterns
                matches = list(target_path.rglob(dep_file))
                if matches:
                    found_dependencies[language] = [
                        str(m.relative_to(target_path)) for m in matches
                    ]
            else:
                dep_path = target_path / dep_file
                if dep_path.exists():
                    try:
                        content = dep_path.read_text(encoding="utf-8")
                        found_dependencies[language] = {
                            "file": dep_file,
                            "size": len(content),
                            "lines": len(content.splitlines()),
                        }
                    except Exception:
                        found_dependencies[language] = {
                            "file": dep_file,
                            "error": "Could not read",
                        }

        return found_dependencies

    def generate_performance_recommendations(
        self, baseline_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate performance improvement recommendations based on baseline."""
        recommendations = []

        # Analyze build performance
        build_metrics = baseline_data.get("build_performance", {})
        for lang, commands in build_metrics.items():
            for cmd, metrics in commands.items():
                if metrics.get("execution_time", 0) > 60:  # > 1 minute
                    recommendations.append(
                        {
                            "type": "build_performance",
                            "priority": "medium",
                            "issue": f"Slow build time for {cmd}",
                            "details": f'Build takes {metrics["execution_time"]:.1f}s',
                            "suggestion": f"Consider build optimization for {lang} project",
                        }
                    )

        # Analyze project structure
        structure = baseline_data.get("structure_metrics", {})
        if structure.get("total_files", 0) > 10000:
            recommendations.append(
                {
                    "type": "project_structure",
                    "priority": "low",
                    "issue": "Large number of files",
                    "details": f'{structure["total_files"]} files in project',
                    "suggestion": "Consider modularization or cleanup of unused files",
                }
            )

        # Analyze large files
        large_files = structure.get("largest_files", [])
        if large_files and large_files[0]["size"] > 1024 * 1024:  # > 1MB
            recommendations.append(
                {
                    "type": "file_size",
                    "priority": "medium",
                    "issue": "Large source files detected",
                    "details": f'Largest file: {large_files[0]["path"]} ({large_files[0]["size"] / 1024 / 1024:.1f}MB)',
                    "suggestion": "Consider splitting large files for better maintainability",
                }
            )

        return recommendations

    def analyze(self, target_path: str) -> AnalysisResult:
        """Main analysis method for performance baseline."""
        try:
            start_time = time.time()
            target = Path(target_path).resolve()

            if not target.exists():
                result = self.formatter.create_performance_result(
                    "performance_baseline.py", target_path
                )
                result.set_error(f"Target path does not exist: {target_path}")
                return result.to_dict()

            # Detect languages
            languages = self.detect_project_languages(target)

            # Capture baseline metrics
            baseline_data = {
                "languages_detected": languages,
                "system_baseline": self.capture_system_baseline(),
                "structure_metrics": self.analyze_project_structure(target),
                "dependency_analysis": self.analyze_dependencies(target),
                "build_performance": self.measure_build_performance(
                    target, list(languages.keys())
                ),
                "timestamp": time.time(),
                "analysis_duration": 0,
            }

            # Generate findings and recommendations
            findings = []
            recommendations = self.generate_performance_recommendations(baseline_data)

            for rec in recommendations:
                severity = "medium" if rec["priority"] == "medium" else "low"
                finding = self.formatter.create_finding(
                    finding_id=f"PERF_BASELINE_{rec['type'].upper()}",
                    title=rec["issue"],
                    description=rec["suggestion"],
                    severity=severity,
                    file_path=str(target),
                    line_number=None,
                    evidence={
                        "details": rec["details"],
                        "type": rec["type"],
                        "baseline_impact": "pre_refactoring",
                    },
                )
                findings.append(finding)

            execution_time = time.time() - start_time
            baseline_data["analysis_duration"] = execution_time

            result = self.formatter.create_performance_result(
                "performance_baseline.py", target_path
            )
            for finding in findings:
                result.add_finding(finding)
            result.set_execution_time(start_time)
            result.metadata = {
                "baseline_established": True,
                "metrics_captured": self.baseline_metrics,
                "languages_analyzed": list(languages.keys()),
                "baseline_data": baseline_data,
                "recommendations_count": len(recommendations),
                "next_steps": [
                    "Store baseline data for post-refactoring comparison",
                    "Run performance tests before refactoring",
                    "Establish monitoring for key metrics during refactoring",
                    "Plan performance validation checkpoints",
                ],
            }
            return result.to_dict()

        except Exception as e:
            result = self.formatter.create_performance_result(
                "performance_baseline.py", target_path
            )
            result.set_error(str(e))
            result.set_execution_time(start_time)
            return result.to_dict()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Establish performance benchmarks before refactoring for comparison validation"
    )
    parser.add_argument("target_path", help="Path to analyze")
    parser.add_argument(
        "--output-format",
        choices=["json", "console"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--benchmark-current",
        action="store_true",
        help="Benchmark current performance state",
    )

    args = parser.parse_args()

    baseliner = PerformanceBaseliner()
    result_dict = baseliner.analyze(args.target_path)

    if args.output_format == "console":
        # Simple console output
        if result_dict.get("success", False):
            print(f"Performance Baseline Results for: {args.target_path}")
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
