#!/usr/bin/env python3
"""
Output formatting utilities for Claude Code Workflows scriptable workflows.
Provides standardized JSON output format for all analysis scripts.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class Severity(Enum):
    """Severity levels for findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AnalysisType(Enum):
    """Types of analysis."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    CODE_QUALITY = "code_quality"
    ARCHITECTURE = "architecture"


class Finding:
    """Represents a single analysis finding."""

    def __init__(
        self,
        finding_id: str,
        title: str,
        description: str,
        severity: Severity,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        recommendation: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ):
        self.finding_id = finding_id
        self.title = title
        self.description = description
        self.severity = severity
        self.file_path = file_path
        self.line_number = line_number
        self.recommendation = recommendation
        self.evidence = evidence or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "id": self.finding_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "recommendation": self.recommendation,
            "evidence": self.evidence,
        }


class AnalysisResult:
    """Standardized analysis result format."""

    def __init__(
        self,
        analysis_type: AnalysisType,
        script_name: str,
        target_path: str,
        findings: List[Finding] = None,
        metadata: Dict[str, Any] = None,
    ):
        self.analysis_type = analysis_type
        self.script_name = script_name
        self.target_path = target_path
        self.findings = findings or []
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.execution_time = 0.0
        self.success = True
        self.error_message = None

    def add_finding(self, finding: Finding):
        """Add a finding to the result."""
        self.findings.append(finding)

    def set_error(self, error_message: str):
        """Mark result as failed with error message."""
        self.success = False
        self.error_message = error_message

    def set_execution_time(self, start_time: float):
        """Set execution time based on start time."""
        self.execution_time = time.time() - start_time

    def get_summary(self) -> Dict[str, int]:
        """Get summary of findings by severity."""
        summary = {severity.value: 0 for severity in Severity}
        for finding in self.findings:
            summary[finding.severity.value] += 1
        return summary

    def to_dict(
        self, summary_mode: bool = False, min_severity: str = "low"
    ) -> Dict[str, Any]:
        """
        Convert result to dictionary.

        Args:
            summary_mode: If True, limit findings to top 10 critical/high severity
            min_severity: Minimum severity level to include (critical|high|medium|low)
        """
        # Filter by minimum severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

        min_severity_level = severity_order.get(min_severity, 3)
        filtered_findings = [
            f
            for f in self.findings
            if severity_order.get(f.severity.value, 4) <= min_severity_level
        ]

        findings_to_include = filtered_findings

        if summary_mode and len(filtered_findings) > 10:
            # Sort by severity priority and take top 10
            severity_priority = {
                Severity.CRITICAL: 0,
                Severity.HIGH: 1,
                Severity.MEDIUM: 2,
                Severity.LOW: 3,
                Severity.INFO: 4,
            }

            sorted_findings = sorted(
                filtered_findings, key=lambda f: severity_priority.get(f.severity, 5)
            )
            findings_to_include = sorted_findings[:10]

        result = {
            "analysis_type": self.analysis_type.value,
            "script_name": self.script_name,
            "target_path": self.target_path,
            "timestamp": self.timestamp,
            "execution_time": round(self.execution_time, 3),
            "success": self.success,
            "error_message": self.error_message,
            "summary": self.get_summary(),
            "findings": [finding.to_dict() for finding in findings_to_include],
            "metadata": self.metadata,
        }

        # Add filtering/truncation info
        if min_severity != "low":
            result["min_severity_filter"] = min_severity
            result["total_findings_before_filter"] = len(self.findings)
            result["total_findings_after_filter"] = len(filtered_findings)

        if summary_mode and len(filtered_findings) > 10:
            result["summary_mode"] = True
            result["showing_top"] = len(findings_to_include)
            result[
                "truncated_note"
            ] = f"Showing top {len(findings_to_include)} findings out of {len(filtered_findings)} filtered results"

        return result

    def to_json(
        self, indent: int = 2, summary_mode: bool = False, min_severity: str = "low"
    ) -> str:
        """Convert result to JSON string."""
        return json.dumps(
            self.to_dict(summary_mode=summary_mode, min_severity=min_severity),
            indent=indent,
            ensure_ascii=False,
        )


class ResultFormatter:
    """Utility class for formatting analysis results."""

    @staticmethod
    def create_security_result(script_name: str, target_path: str) -> AnalysisResult:
        """Create a security analysis result."""
        return AnalysisResult(AnalysisType.SECURITY, script_name, target_path)

    @staticmethod
    def create_performance_result(script_name: str, target_path: str) -> AnalysisResult:
        """Create a performance analysis result."""
        return AnalysisResult(AnalysisType.PERFORMANCE, script_name, target_path)

    @staticmethod
    def create_code_quality_result(
        script_name: str, target_path: str
    ) -> AnalysisResult:
        """Create a code quality analysis result."""
        return AnalysisResult(AnalysisType.CODE_QUALITY, script_name, target_path)

    @staticmethod
    def create_architecture_result(
        script_name: str, target_path: str
    ) -> AnalysisResult:
        """Create an architecture analysis result."""
        return AnalysisResult(AnalysisType.ARCHITECTURE, script_name, target_path)

    @staticmethod
    def create_finding(
        finding_id: str,
        title: str,
        description: str,
        severity: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        recommendation: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> Finding:
        """Create a finding with string severity."""
        severity_enum = Severity(severity.lower())
        return Finding(
            finding_id,
            title,
            description,
            severity_enum,
            file_path,
            line_number,
            recommendation,
            evidence,
        )

    @staticmethod
    def merge_results(results: List[AnalysisResult]) -> Dict[str, Any]:
        """Merge multiple analysis results into a combined report."""
        if not results:
            return {"error": "No results to merge"}

        combined = {
            "timestamp": datetime.now().isoformat(),
            "target_path": results[0].target_path,
            "total_execution_time": sum(r.execution_time for r in results),
            "scripts_run": len(results),
            "overall_success": all(r.success for r in results),
            "analysis_types": [r.analysis_type.value for r in results],
            "combined_summary": {},
            "results": [r.to_dict() for r in results],
        }

        # Combine summaries
        all_severities = {severity.value: 0 for severity in Severity}
        for result in results:
            summary = result.get_summary()
            for severity, count in summary.items():
                all_severities[severity] += count
        combined["combined_summary"] = all_severities

        return combined

    @staticmethod
    def format_console_output(result: AnalysisResult) -> str:
        """Format result for console display."""
        lines = []
        lines.append(
            f"=== {result.analysis_type.value.upper()} ANALYSIS: {result.script_name} ==="
        )
        lines.append(f"Target: {result.target_path}")
        lines.append(f"Executed: {result.timestamp}")
        lines.append(f"Duration: {result.execution_time:.3f}s")

        if not result.success:
            lines.append(f"❌ FAILED: {result.error_message}")
            return "\n".join(lines)

        summary = result.get_summary()
        lines.append("✅ SUCCESS")
        lines.append(f"Findings: {sum(summary.values())} total")

        for severity in ["critical", "high", "medium", "low", "info"]:
            count = summary.get(severity, 0)
            if count > 0:
                emoji = {
                    "critical": "🚨",
                    "high": "⚠️",
                    "medium": "📋",
                    "low": "💡",
                    "info": "ℹ️",
                }
                lines.append(
                    f"  {emoji.get(severity, '•')} {severity.upper()}: {count}"
                )

        return "\n".join(lines)


def main():
    """Test output formatting utilities."""
    print("=== Output Formatter Test ===")

    # Create test result
    result = ResultFormatter.create_security_result("test_script.py", "/test/path")

    # Add test findings
    finding1 = ResultFormatter.create_finding(
        "SEC001",
        "Hardcoded Password",
        "Password found in source code",
        "critical",
        "/test/path/config.py",
        42,
        "Use environment variables for sensitive data",
        {"pattern": "password = 'secret123'"},
    )

    finding2 = ResultFormatter.create_finding(
        "SEC002",
        "Missing Input Validation",
        "User input not validated",
        "medium",
        "/test/path/api.py",
        15,
        "Add input validation and sanitization",
    )

    result.add_finding(finding1)
    result.add_finding(finding2)
    result.set_execution_time(time.time() - 1.5)  # Simulate 1.5s execution

    # Test JSON output
    print("JSON Output:")
    print(result.to_json())

    print("\nConsole Output:")
    print(ResultFormatter.format_console_output(result))

    # Test merge functionality
    result2 = ResultFormatter.create_performance_result("perf_script.py", "/test/path")
    finding3 = ResultFormatter.create_finding(
        "PERF001",
        "Slow Database Query",
        "Query takes > 1s to execute",
        "high",
        recommendation="Add database index",
    )
    result2.add_finding(finding3)

    merged = ResultFormatter.merge_results([result, result2])
    print("\nMerged Results:")
    print(json.dumps(merged, indent=2))


if __name__ == "__main__":
    main()
