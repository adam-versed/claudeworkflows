#!/usr/bin/env python3
"""
Demo script: Run all analysis scripts and combine results.
Demonstrates the complete hybrid workflow system.
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Add utils to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir / "utils"))

try:
    from cross_platform import CommandExecutor
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class AnalysisRunner:
    """Run all analysis scripts and combine results."""

    def __init__(self):
        # Use the current script's location to find the analyze directory
        current_script_dir = Path(__file__).parent
        self.script_dir = current_script_dir / "analyze"
        self.scripts = {
            # Security analysis
            "security_auth": "security/check_auth.py",
            "security_vulnerabilities": "security/scan_vulnerabilities.py",
            "security_input_validation": "security/validate_inputs.py",
            "security_secrets": "security/detect_secrets.py",
            # Performance analysis
            "performance_frontend": "performance/analyze_frontend.py",
            "performance_bottlenecks": "performance/check_bottlenecks.py",
            "performance_baseline": "performance/performance_baseline.py",
            "performance_database": "performance/profile_database.py",
            # Code quality analysis
            "code_quality": "code_quality/complexity_lizard.py",
            "code_quality_metrics": "code_quality/complexity_metrics.py",
            "code_quality_coverage": "code_quality/test_coverage_analysis.py",
            # Architecture analysis
            "architecture_patterns": "architecture/pattern_evaluation.py",
            "architecture_scalability": "architecture/scalability_check.py",
            "architecture_coupling": "architecture/coupling_analysis.py",
            # Root cause analysis
            "root_cause_errors": "root_cause/error_patterns.py",
            "root_cause_changes": "root_cause/recent_changes.py",
            "root_cause_trace": "root_cause/simple_trace.py",
            "root_cause_execution": "root_cause/trace_execution.py",
        }

    def run_script(
        self,
        script_name: str,
        target_path: str,
        summary_mode: bool = True,
        min_severity: str = "low",
    ) -> Dict[str, Any]:
        """Run a single analysis script."""
        script_path = Path(self.script_dir) / self.scripts[script_name]

        print(f"🔄 Running {script_name} analysis...", file=sys.stderr)

        args = [str(script_path), target_path]
        # Only lizard script supports --summary flag
        if summary_mode and script_name == "code_quality":
            args.append("--summary")

        # Only certain scripts support --min-severity flag
        scripts_with_severity = [
            "security_auth",
            "security_vulnerabilities",
            "security_input_validation",
            "security_secrets",
            "performance_frontend",
            "performance_bottlenecks",
            "performance_database",
            "code_quality",
            "code_quality_metrics",
            "architecture_patterns",
            "architecture_scalability",
            "architecture_coupling",
        ]

        if min_severity != "low" and script_name in scripts_with_severity:
            args.extend(["--min-severity", min_severity])

        start_time = time.time()
        returncode, stdout, stderr = CommandExecutor.run_python_script(
            str(script_path), args[1:]
        )
        duration = time.time() - start_time

        if returncode == 0:
            try:
                result = json.loads(stdout)
                result["runner_duration"] = round(duration, 3)
                print(f"✅ {script_name} completed in {duration:.3f}s", file=sys.stderr)
                return result
            except json.JSONDecodeError as e:
                print(f"❌ {script_name} - JSON decode error: {e}", file=sys.stderr)
                return {"error": f"JSON decode error: {e}", "stderr": stderr}
        else:
            print(f"❌ {script_name} failed: {stderr}", file=sys.stderr)
            return {"error": f"Script failed (code {returncode})", "stderr": stderr}

    def run_all_analyses(
        self, target_path: str, summary_mode: bool = True, min_severity: str = "low"
    ) -> Dict[str, Any]:
        """Run all analysis scripts and combine results."""
        print("🚀 Claude Code Workflows Analysis - Running All Scripts", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        start_time = time.time()
        results = {}

        for script_name in self.scripts.keys():
            results[script_name] = self.run_script(
                script_name, target_path, summary_mode, min_severity
            )

        total_duration = time.time() - start_time

        # Generate combined report
        combined_report = self.generate_combined_report(
            results, target_path, total_duration
        )

        print(f"\n🎉 All analyses completed in {total_duration:.3f}s", file=sys.stderr)

        return combined_report

    def generate_combined_report(
        self, results: Dict[str, Any], target_path: str, total_duration: float
    ) -> Dict[str, Any]:
        """Generate a combined analysis report."""
        report = {
            "combined_analysis": {
                "target_path": target_path,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_duration": round(total_duration, 3),
                "scripts_run": len(self.scripts),
                "summary_mode": True,
                "overall_success": all(
                    not result.get("error") for result in results.values()
                ),
            },
            "executive_summary": self.generate_executive_summary(results),
            "detailed_results": results,
        }

        return report

    def generate_executive_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of all findings."""
        summary = {
            "total_findings": 0,
            "by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
            "by_category": {},
            "top_issues": [],
            "recommendations": [],
        }

        # Aggregate findings
        for script_name, result in results.items():
            if result.get("error"):
                continue

            findings = result.get("findings", [])

            # Add to totals - use actual findings count
            script_total = len(findings)
            summary["total_findings"] += script_total

            # Count severities from actual findings
            script_severity_counts = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }
            for finding in findings:
                severity = finding.get("severity", "info")
                if severity in script_severity_counts:
                    script_severity_counts[severity] += 1
                    summary["by_severity"][severity] += 1

            # Track by category
            summary["by_category"][script_name] = {
                "total": script_total,
                "summary": script_severity_counts,
            }

            # Collect critical/high issues for top issues
            for finding in findings:
                if finding.get("severity") in ["critical", "high"]:
                    summary["top_issues"].append(
                        {
                            "category": script_name,
                            "title": finding.get("title", ""),
                            "severity": finding.get("severity", ""),
                            "file": finding.get("file_path", ""),
                            "line": finding.get("line_number"),
                        }
                    )

        # Sort top issues by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        summary["top_issues"].sort(key=lambda x: severity_order.get(x["severity"], 5))

        # Limit top issues to 20
        summary["top_issues"] = summary["top_issues"][:20]

        # Generate recommendations
        summary["recommendations"] = self.generate_recommendations(summary)

        return summary

    def generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate high-level recommendations based on findings."""
        recommendations = []

        # Security recommendations
        security_critical = 0
        security_high = 0
        for category in [
            "security_auth",
            "security_vulnerabilities",
            "security_input_validation",
            "security_secrets",
        ]:
            if category in summary["by_category"]:
                security_critical += (
                    summary["by_category"][category]
                    .get("summary", {})
                    .get("critical", 0)
                )
                security_high += (
                    summary["by_category"][category].get("summary", {}).get("high", 0)
                )

        if security_critical > 0:
            recommendations.append(
                f"🚨 URGENT: Address {security_critical} critical security vulnerabilities immediately"
            )
        elif security_high > 3:
            recommendations.append(
                f"🔒 HIGH: Fix {security_high} high-severity security issues"
            )

        # Performance recommendations
        perf_critical = 0
        perf_high = 0
        for category in [
            "performance_frontend",
            "performance_bottlenecks",
            "performance_baseline",
            "performance_database",
        ]:
            if category in summary["by_category"]:
                perf_critical += (
                    summary["by_category"][category]
                    .get("summary", {})
                    .get("critical", 0)
                )
                perf_high += (
                    summary["by_category"][category].get("summary", {}).get("high", 0)
                )

        if perf_critical > 0:
            recommendations.append(
                f"🚨 CRITICAL: Fix {perf_critical} critical performance issues"
            )
        elif perf_high > 3:
            recommendations.append(
                f"⚡ HIGH: Optimize {perf_high} performance bottlenecks affecting user experience"
            )

        # Code quality recommendations
        quality_total = 0
        for category in [
            "code_quality",
            "code_quality_metrics",
            "code_quality_coverage",
        ]:
            quality_total += summary["by_category"].get(category, {}).get("total", 0)

        if quality_total > 50:
            recommendations.append(
                f"🏗 MEDIUM: Address code complexity issues to improve maintainability ({quality_total} findings)"
            )

        # Architecture recommendations
        arch_critical = 0
        arch_high = 0
        for category in [
            "architecture_patterns",
            "architecture_scalability",
            "architecture_coupling",
        ]:
            if category in summary["by_category"]:
                arch_critical += (
                    summary["by_category"][category]
                    .get("summary", {})
                    .get("critical", 0)
                )
                arch_high += (
                    summary["by_category"][category].get("summary", {}).get("high", 0)
                )

        if arch_critical > 0:
            recommendations.append(
                f"🚨 CRITICAL: Fix {arch_critical} critical architectural issues"
            )
        elif arch_high > 2:
            recommendations.append(
                f"🔗 HIGH: Resolve {arch_high} architectural design issues"
            )

        # Root cause analysis recommendations
        root_cause_total = 0
        for category in [
            "root_cause_errors",
            "root_cause_changes",
            "root_cause_trace",
            "root_cause_execution",
        ]:
            root_cause_total += summary["by_category"].get(category, {}).get("total", 0)

        if root_cause_total > 10:
            recommendations.append(
                f"🔍 MEDIUM: Investigate {root_cause_total} potential root cause indicators"
            )

        if not recommendations:
            recommendations.append(
                "✅ Overall code health appears good - continue with regular monitoring"
            )

        return recommendations


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run comprehensive code analysis across multiple dimensions"
    )
    parser.add_argument("target_path", help="Path to analyze")
    parser.add_argument(
        "--output-format",
        choices=["json", "console"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include detailed results (default is summary mode)",
    )
    parser.add_argument(
        "--min-severity",
        choices=["critical", "high", "medium", "low"],
        default="low",
        help="Minimum severity level (default: low)",
    )

    args = parser.parse_args()

    summary_mode = (
        not args.verbose
    )  # Inverse logic: verbose=False means summary_mode=True

    runner = AnalysisRunner()
    report = runner.run_all_analyses(args.target_path, summary_mode, args.min_severity)

    # Output based on format choice
    if args.output_format == "console":
        # Simple console output for the combined report
        print("=== COMPREHENSIVE ANALYSIS REPORT ===")
        print(f"Target: {args.target_path}")
        print(f"Timestamp: {report.get('timestamp', 'unknown')}")
        print(f"Scripts run: {report.get('scripts_run', 0)}")
        print(f"Success: {report.get('overall_success', False)}")

        # Show combined summary
        summary = report.get("combined_summary", {})
        total_findings = sum(summary.values())
        print(f"Total findings: {total_findings}")
        for severity in ["critical", "high", "medium", "low", "info"]:
            count = summary.get(severity, 0)
            if count > 0:
                print(f"  {severity.upper()}: {count}")
    else:  # json (default)
        # Output combined report with proper error handling for broken pipe
        try:
            print(json.dumps(report, indent=2))
            sys.stdout.flush()
        except BrokenPipeError:
            # Handle broken pipe gracefully (e.g., when output is piped to head)
            try:
                sys.stdout.close()
            except (OSError, ValueError):
                pass
            try:
                sys.stderr.close()
            except (OSError, ValueError):
                pass


if __name__ == "__main__":
    main()
