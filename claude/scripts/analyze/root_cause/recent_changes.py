#!/usr/bin/env python3
"""
Root cause analysis script: Git blame and recent changes analysis.
Part of Claude Code Workflows.
"""

import os
import re
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
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
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class ChangeAnalyzer:
    """Analyze recent code changes and correlate with potential issues."""

    def __init__(self, days_back: int = 30, max_commits: int = 100):
        self.days_back = days_back
        self.max_commits = max_commits
        self.change_patterns = {
            "auth_changes": {
                "patterns": [r"auth", r"login", r"session", r"token", r"permission"],
                "severity": "high",
                "description": "Authentication/authorization changes",
            },
            "database_changes": {
                "patterns": [r"database", r"query", r"sql", r"migration", r"schema"],
                "severity": "high",
                "description": "Database-related changes",
            },
            "api_changes": {
                "patterns": [r"api", r"endpoint", r"route", r"controller", r"handler"],
                "severity": "medium",
                "description": "API endpoint changes",
            },
            "config_changes": {
                "patterns": [
                    r"config",
                    r"settings",
                    r"environment",
                    r"\.env",
                    r"constants",
                ],
                "severity": "medium",
                "description": "Configuration changes",
            },
            "dependency_changes": {
                "patterns": [
                    r"package\.json",
                    r"requirements\.txt",
                    r"Gemfile",
                    r"pom\.xml",
                    r"Cargo\.toml",
                ],
                "severity": "medium",
                "description": "Dependency changes",
            },
            "critical_file_changes": {
                "patterns": [
                    r"main\.",
                    r"app\.",
                    r"index\.",
                    r"server\.",
                    r"__init__\.",
                ],
                "severity": "high",
                "description": "Critical application file changes",
            },
        }

    def run_git_command(
        self, command: List[str], cwd: Optional[Path] = None
    ) -> Optional[str]:
        """Run a git command and return output."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return None

    def get_recent_commits(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Get recent commits with details and file changes."""
        since_date = (datetime.now() - timedelta(days=self.days_back)).strftime(
            "%Y-%m-%d"
        )

        # Get commit log with details
        command = [
            "git",
            "log",
            "--oneline",
            "--since",
            since_date,
            "--pretty=format:%H|%an|%ad|%s",
            "--date=iso",
            f"--max-count={self.max_commits}",
        ]

        output = self.run_git_command(command, repo_path)
        if not output:
            return []

        commits = []
        for line in output.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    commit_data = {
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                        "files_changed": [],
                    }

                    # Get files changed in this commit
                    files_command = [
                        "git",
                        "show",
                        "--name-only",
                        "--pretty=format:",
                        parts[0],
                    ]
                    files_output = self.run_git_command(files_command, repo_path)
                    if files_output:
                        commit_data["files_changed"] = [
                            f.strip() for f in files_output.split("\n") if f.strip()
                        ]

                    commits.append(commit_data)

        return commits

    def get_file_blame_info(self, file_path: Path, repo_path: Path) -> Dict[str, Any]:
        """Get git blame information for a file."""
        relative_path = file_path.relative_to(repo_path)

        command = ["git", "blame", "--line-porcelain", str(relative_path)]
        output = self.run_git_command(command, repo_path)

        if not output:
            return {}

        blame_info = {
            "recent_changes": [],
            "authors": defaultdict(int),
            "commit_dates": [],
        }

        current_commit = {}
        line_number = 0

        for line in output.split("\n"):
            if line.startswith("\t"):
                # This is the actual code line
                line_number += 1
                if current_commit:
                    current_commit["line_number"] = line_number
                    current_commit["code"] = line[1:]  # Remove tab

                    # Check if this is a recent change
                    if "author-time" in current_commit:
                        commit_date = datetime.fromtimestamp(
                            int(current_commit["author-time"])
                        )
                        if commit_date > datetime.now() - timedelta(
                            days=self.days_back
                        ):
                            blame_info["recent_changes"].append(current_commit.copy())
                        blame_info["commit_dates"].append(commit_date)

                    if "author" in current_commit:
                        blame_info["authors"][current_commit["author"]] += 1

                current_commit = {}
            elif " " in line:
                key, value = line.split(" ", 1)
                current_commit[key] = value

        return blame_info

    def analyze_change_risk(
        self, commits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze commits for potential risk factors."""
        risk_findings = []

        for commit in commits:
            commit_risks = []
            message = commit["message"].lower()

            # Check for risky commit patterns
            risky_patterns = {
                "hotfix": r"\b(hotfix|urgent|emergency|critical)\b",
                "rollback": r"\b(rollback|revert|undo)\b",
                "temp_fix": r"\b(temp|temporary|quick|hack)\b",
                "major_change": r"\b(refactor|rewrite|major|breaking)\b",
                "merge_conflict": r"\b(merge|conflict|resolution)\b",
            }

            for risk_type, pattern in risky_patterns.items():
                if re.search(pattern, message):
                    commit_risks.append(risk_type)

            # Check for specific change categories
            for category, info in self.change_patterns.items():
                for pattern in info["patterns"]:
                    if re.search(pattern, message, re.IGNORECASE):
                        commit_risks.append(category)

            if commit_risks:
                risk_findings.append(
                    {
                        "commit": commit,
                        "risks": commit_risks,
                        "risk_level": self._calculate_risk_level(commit_risks),
                    }
                )

        return risk_findings

    def _calculate_risk_level(self, risks: List[str]) -> str:
        """Calculate overall risk level based on detected risks."""
        critical_risks = [
            "hotfix",
            "rollback",
            "temp_fix",
            "auth_changes",
            "database_changes",
        ]
        high_risks = ["major_change", "merge_conflict", "critical_file_changes"]

        if any(risk in critical_risks for risk in risks):
            return "critical"
        elif any(risk in high_risks for risk in risks):
            return "high"
        elif len(risks) > 2:
            return "medium"
        else:
            return "low"

    def get_changed_files(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Get files changed in recent commits."""
        since_date = (datetime.now() - timedelta(days=self.days_back)).strftime(
            "%Y-%m-%d"
        )

        command = [
            "git",
            "log",
            "--name-status",
            "--since",
            since_date,
            "--pretty=format:%H|%ad",
            "--date=iso",
        ]

        output = self.run_git_command(command, repo_path)
        if not output:
            return []

        changed_files = defaultdict(list)
        current_commit = None

        for line in output.split("\n"):
            if "|" in line and not line.startswith(("A\t", "M\t", "D\t", "R\t")):
                current_commit = line.split("|")[0]
            elif line.startswith(("A\t", "M\t", "D\t", "R\t")) and current_commit:
                parts = line.split("\t")
                if len(parts) >= 2:
                    change_type = parts[0]
                    file_path = parts[1]
                    changed_files[file_path].append(
                        {"commit": current_commit, "change_type": change_type}
                    )

        return dict(changed_files)

    def analyze_file_change_frequency(
        self, changed_files: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Analyze files that change frequently (potential hotspots)."""
        hotspots = []

        for file_path, changes in changed_files.items():
            change_count = len(changes)

            # Files changed more than threshold might be hotspots
            if change_count >= 5:
                # Analyze change types
                change_types = [change["change_type"] for change in changes]

                hotspots.append(
                    {
                        "file_path": file_path,
                        "change_count": change_count,
                        "change_types": change_types,
                        "recent_commits": [change["commit"] for change in changes[:5]],
                        "risk_level": "high" if change_count >= 10 else "medium",
                    }
                )

        return hotspots

    def analyze_commit_timing_patterns(
        self, commits: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze commit timing to detect emergency patterns."""
        timing_issues = []

        for i, commit in enumerate(commits):
            try:
                commit_time = datetime.fromisoformat(
                    commit["date"].replace(" ", "T").split("+")[0]
                )

                # Check for late night/weekend commits (potential emergency fixes)
                is_weekend = commit_time.weekday() >= 5  # Saturday = 5, Sunday = 6
                is_late_night = commit_time.hour < 6 or commit_time.hour > 22

                if is_weekend or is_late_night:
                    timing_issues.append(
                        {
                            "commit": commit,
                            "timing_concern": "weekend" if is_weekend else "late_night",
                            "risk_level": "medium",
                        }
                    )

                # Check for rapid consecutive commits (potential hotfix sequence)
                if i > 0:
                    prev_commit_time = datetime.fromisoformat(
                        commits[i - 1]["date"].replace(" ", "T").split("+")[0]
                    )
                    time_diff = abs((commit_time - prev_commit_time).total_seconds())

                    # Commits within 10 minutes might indicate emergency hotfixes
                    if time_diff < 600 and commit["author"] == commits[i - 1]["author"]:
                        timing_issues.append(
                            {
                                "commit": commit,
                                "timing_concern": "rapid_consecutive",
                                "time_diff_minutes": time_diff / 60,
                                "previous_commit": commits[i - 1]["hash"][:8],
                                "risk_level": "high",
                            }
                        )

            except (ValueError, KeyError, IndexError):
                continue

        return timing_issues


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze recent code changes and their patterns"
    )
    parser.add_argument(
        "target_path",
        nargs="?",
        default=os.getcwd(),
        help="Repository path to analyze (default: current directory)",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "console"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()
    start_time = time.time()

    # Get repository path
    repo_path = Path(args.target_path)

    # Configuration from environment variables
    days_back = int(os.environ.get("DAYS_BACK", "30"))
    max_commits = int(os.environ.get("MAX_COMMITS", "50"))

    # Initialize analyzer
    analyzer = ChangeAnalyzer(days_back=days_back, max_commits=max_commits)
    result = AnalysisResult(
        AnalysisType.ARCHITECTURE, "recent_changes.py", str(repo_path)
    )

    # Check if we're in a git repository
    if not (repo_path / ".git").exists():
        finding_obj = Finding(
            finding_id="no_git_repo",
            title="No Git Repository",
            description="Not in a git repository - cannot analyze recent changes",
            severity=Severity.INFO,
        )
        result.add_finding(finding_obj)
        result.set_execution_time(start_time)

        # Output based on format choice
        if args.output_format == "console":
            print(ResultFormatter.format_console_output(result))
        else:  # json (default)
            print(result.to_json())
        return

    # Analyze recent commits
    commits = analyzer.get_recent_commits(repo_path)

    if not commits:
        finding_obj = Finding(
            finding_id="no_recent_commits",
            title="No Recent Commits",
            description=f"No commits found in the last {analyzer.days_back} days",
            severity=Severity.INFO,
        )
        result.add_finding(finding_obj)
    else:
        # Analyze commit risks
        risky_commits = analyzer.analyze_change_risk(commits)

        # Analyze timing patterns
        timing_issues = analyzer.analyze_commit_timing_patterns(commits)

        for i, risk_commit in enumerate(risky_commits):
            commit = risk_commit["commit"]
            risks = risk_commit["risks"]
            risk_level = risk_commit["risk_level"]

            severity_map = {
                "critical": Severity.CRITICAL,
                "high": Severity.HIGH,
                "medium": Severity.MEDIUM,
                "low": Severity.LOW,
            }

            finding_obj = Finding(
                finding_id=f"risky_commit_{i}",
                title="Risky Commit Detected",
                description=f"Commit {commit['hash'][:8]} contains risk factors: {', '.join(risks)}",
                severity=severity_map.get(risk_level, Severity.LOW),
                evidence={
                    "commit_hash": commit["hash"],
                    "author": commit["author"],
                    "date": commit["date"],
                    "message": commit["message"],
                    "risk_factors": risks,
                    "risk_level": risk_level,
                },
            )
            result.add_finding(finding_obj)

        # Add timing pattern findings
        for i, timing_issue in enumerate(timing_issues):
            commit = timing_issue["commit"]
            concern = timing_issue["timing_concern"]
            risk_level = timing_issue["risk_level"]

            severity = Severity.HIGH if risk_level == "high" else Severity.MEDIUM

            description = (
                f"Commit {commit['hash'][:8]} made during {concern.replace('_', ' ')}"
            )
            if "time_diff_minutes" in timing_issue:
                description += f" ({timing_issue['time_diff_minutes']:.1f} minutes after previous commit)"

            finding_obj = Finding(
                finding_id=f"timing_issue_{i}",
                title="Suspicious Commit Timing",
                description=description,
                severity=severity,
                evidence={
                    "commit_hash": commit["hash"],
                    "author": commit["author"],
                    "date": commit["date"],
                    "message": commit["message"],
                    "timing_concern": concern,
                    "risk_level": risk_level,
                    **{
                        k: v
                        for k, v in timing_issue.items()
                        if k not in ["commit", "timing_concern", "risk_level"]
                    },
                },
            )
            result.add_finding(finding_obj)

    # Analyze changed files
    changed_files = analyzer.get_changed_files(repo_path)
    hotspots = analyzer.analyze_file_change_frequency(changed_files)

    for i, hotspot in enumerate(hotspots):
        finding_obj = Finding(
            finding_id=f"change_hotspot_{i}",
            title="File Change Hotspot",
            description=f"File {hotspot['file_path']} changed {hotspot['change_count']} times recently",
            severity=Severity.HIGH
            if hotspot["risk_level"] == "high"
            else Severity.MEDIUM,
            file_path=hotspot["file_path"],
            evidence={
                "change_count": hotspot["change_count"],
                "change_types": hotspot["change_types"],
                "recent_commits": hotspot["recent_commits"],
            },
        )
        result.add_finding(finding_obj)

    # Set execution time and add metadata
    result.set_execution_time(start_time)
    metadata = {
        "commits_analyzed": len(commits),
        "risky_commits": len(
            [r for r in risky_commits if r["risk_level"] in ["critical", "high"]]
        )
        if "risky_commits" in locals()
        else 0,
        "files_changed": len(changed_files) if "changed_files" in locals() else 0,
        "change_hotspots": len(hotspots) if "hotspots" in locals() else 0,
        "timing_issues": len(timing_issues) if "timing_issues" in locals() else 0,
        "analysis_period_days": analyzer.days_back,
        "max_commits_limit": analyzer.max_commits,
    }
    result.metadata.update(metadata)

    # Output based on format choice
    if args.output_format == "console":
        print(ResultFormatter.format_console_output(result))
    else:  # json (default)
        print(result.to_json())


if __name__ == "__main__":
    main()
