#!/usr/bin/env python3
"""
Frontend Performance Analysis Script
Analyzes frontend code for performance issues, bundle size, and optimization opportunities.
"""

import os
import sys
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Add utils to path for cross-platform and output_formatter imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "utils"))

try:
    from cross_platform import PlatformDetector
    from output_formatter import ResultFormatter
    from tech_stack_detector import TechStackDetector
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class FrontendPerformanceAnalyzer:
    """Analyzes frontend performance issues and optimization opportunities."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.formatter = ResultFormatter()
        # Initialize tech stack detector for smart filtering
        self.tech_detector = TechStackDetector()

        # Bundle size and import patterns
        self.bundle_patterns = {
            "large_imports": {
                "indicators": [
                    r'import\s+\*\s+from\s+[\'"].*[\'"]',
                    r'require\s*\(\s*[\'"].*entire.*library.*[\'"]',
                    r'import.*from\s+[\'"]lodash[\'"]',
                    r'import.*from\s+[\'"]moment[\'"]',
                    r'import.*\{.*\}\s*from\s+[\'"]react[\'"]',
                ],
                "severity": "medium",
                "description": "Large or entire library imports affecting bundle size",
            },
            "unused_imports": {
                "indicators": [
                    r"import\s+\w+.*(?!.*\w+)",  # Simple heuristic for unused imports
                    r"import\s+\{[^}]*\}.*from.*(?=\n)",
                    r"const\s+\w+\s*=\s*require.*(?!.*\w+)",
                ],
                "severity": "low",
                "description": "Potentially unused imports",
            },
            "dynamic_imports_missing": {
                "indicators": [
                    r'import.*[\'"].*large.*component.*[\'"]',
                    r'import.*[\'"].*page.*[\'"]',
                    r'import.*[\'"].*route.*[\'"]',
                ],
                "severity": "medium",
                "description": "Missing dynamic imports for code splitting",
            },
        }

        # React performance patterns
        self.react_patterns = {
            "missing_memo": {
                "indicators": [
                    r"function\s+\w+Component.*\{.*map\(",
                    r"const\s+\w+\s*=\s*\(.*\)\s*=>\s*\{.*map\(",
                    r"export.*function.*\{.*\.map\(",
                    r"React\.Component.*render.*map\(",
                ],
                "severity": "medium",
                "description": "Component with expensive operations missing memoization",
            },
            "inline_object_creation": {
                "indicators": [
                    r"style=\{\{.*\}\}",
                    r"onClick=\{.*=>\s*\{",
                    r"onChange=\{.*=>\s*\{",
                    r"<.*\{\{.*\}\}.*>",
                ],
                "severity": "low",
                "description": "Inline object/function creation causing re-renders",
            },
            "missing_key_prop": {
                "indicators": [
                    r"\.map\(.*=>\s*<.*(?!.*key=)",
                    r"\.map\(.*function.*<.*(?!.*key=)",
                    r"for.*in.*<.*(?!.*key=)",
                ],
                "severity": "medium",
                "description": "Missing key prop in list rendering",
            },
            "unnecessary_rerenders": {
                "indicators": [
                    r"useState\(.*\{\}.*\)",
                    r"useState\(.*\[\].*\)",
                    r"useEffect\(.*,\s*\[\]\)",
                    r"component.*render.*new.*",
                ],
                "severity": "medium",
                "description": "Patterns causing unnecessary re-renders",
            },
        }

        # CSS and styling performance
        self.css_patterns = {
            "expensive_selectors": {
                "indicators": [
                    r"\*\s*\{",  # Universal selector
                    r"\[.*\*=.*\]",  # Attribute contains selector
                    r"[^a-zA-Z0-9]nth-child\(",
                    r":not\(.*:not\(",  # Nested :not selectors
                    r"[a-zA-Z]+\s+[a-zA-Z]+\s+[a-zA-Z]+\s+[a-zA-Z]+",  # Deep descendant selectors
                ],
                "severity": "medium",
                "description": "Expensive CSS selectors affecting render performance",
            },
            "large_css_files": {
                "indicators": [
                    r"/\*.*large.*css.*file.*\*/",
                    r"@import.*url\(",
                    r"\.css.*\{.*\n.*\n.*\n.*\n.*\n",  # Heuristic for large CSS blocks
                ],
                "severity": "low",
                "description": "Large CSS files affecting load time",
            },
            "unused_css": {
                "indicators": [
                    r"\.unused-class\s*\{",
                    r"#unused-id\s*\{",
                    r"/\*.*unused.*\*/",
                ],
                "severity": "low",
                "description": "Potentially unused CSS rules",
            },
        }

        # JavaScript performance patterns
        self.js_patterns = {
            "inefficient_dom_queries": {
                "indicators": [
                    r"document\.querySelector.*for.*",
                    r"document\.getElementById.*loop",
                    r"getElementsBy.*for\s*\(",
                    r"querySelectorAll.*map\(",
                ],
                "severity": "medium",
                "description": "Inefficient DOM queries in loops",
            },
            "synchronous_operations": {
                "indicators": [
                    r"for\s*\(.*length.*\)\s*\{.*fetch",
                    r"while\s*\(.*\)\s*\{.*await",
                    r"forEach.*fetch\(",
                    r"map\(.*fetch\(",
                ],
                "severity": "high",
                "description": "Synchronous operations blocking UI thread",
            },
            "memory_leaks": {
                "indicators": [
                    r"setInterval\(.*(?!.*clearInterval)",
                    r"setTimeout\(.*(?!.*clearTimeout)",
                    r"addEventListener\(.*(?!.*removeEventListener)",
                    r"new.*Observer\(.*(?!.*disconnect)",
                ],
                "severity": "high",
                "description": "Potential memory leaks from uncleaned resources",
            },
            "large_data_processing": {
                "indicators": [
                    r"JSON\.parse\(.*large",
                    r"JSON\.stringify\(.*big",
                    r"sort\(.*length.*>.*1000",
                    r"filter\(.*length.*>.*1000",
                ],
                "severity": "medium",
                "description": "Large data processing on main thread",
            },
        }

        # Image and asset optimization
        self.asset_patterns = {
            "unoptimized_images": {
                "indicators": [
                    r"<img.*src.*\.(?!webp|avif)",
                    r"background-image.*url.*\.(?!webp|avif)",
                    r"import.*\.(?:jpg|jpeg|png|gif)",
                    r"require.*\.(?:jpg|jpeg|png|gif)",
                ],
                "severity": "low",
                "description": "Unoptimized image formats",
            },
            "missing_lazy_loading": {
                "indicators": [
                    r"<img.*(?!.*loading=)",
                    r"<iframe.*(?!.*loading=)",
                    r"background-image.*(?!.*lazy)",
                ],
                "severity": "medium",
                "description": "Missing lazy loading for images/iframes",
            },
            "large_bundle_assets": {
                "indicators": [
                    r'import.*[\'"].*\.(?:mp4|webm|gif).*[\'"]',
                    r'require.*[\'"].*\.(?:mp4|webm|gif).*[\'"]',
                    r'url.*[\'"].*\.(?:mp4|webm|gif).*[\'"]',
                ],
                "severity": "medium",
                "description": "Large media assets bundled with application",
            },
        }

    def analyze_frontend_performance(
        self, target_path: str, min_severity: str = "low"
    ) -> Dict[str, Any]:
        """Analyze frontend performance in the target path."""

        start_time = time.time()
        result = ResultFormatter.create_performance_result(
            "analyze_frontend.py", target_path
        )

        if not os.path.exists(target_path):
            result.set_error(f"Path does not exist: {target_path}")
            result.set_execution_time(start_time)
            return result.to_dict()

        performance_summary = defaultdict(int)
        file_count = 0

        try:
            # Walk through all files using universal exclusion system
            exclude_dirs = self.tech_detector.get_simple_exclusions(target_path)[
                "directories"
            ]

            for root, dirs, files in os.walk(target_path):
                # Filter directories using universal exclusion system
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                for file in files:
                    file_path = os.path.join(root, file)
                    # Use universal exclusion system
                    if self.tech_detector.should_analyze_file(
                        file_path, target_path
                    ) and self._should_analyze_file(file):
                        relative_path = os.path.relpath(file_path, target_path)

                        try:
                            file_findings = self._analyze_file_frontend_performance(
                                file_path, relative_path
                            )
                            file_count += 1

                            # Convert findings to Finding objects
                            for finding_data in file_findings:
                                finding = ResultFormatter.create_finding(
                                    finding_id=f"FRONTEND_{performance_summary[finding_data['issue_type']] + 1:03d}",
                                    title=finding_data["issue_type"]
                                    .replace("_", " ")
                                    .title(),
                                    description=finding_data["message"],
                                    severity=finding_data["severity"],
                                    file_path=finding_data["file"],
                                    line_number=finding_data["line"],
                                    recommendation=self._get_frontend_recommendation(
                                        finding_data["issue_type"]
                                    ),
                                    evidence={
                                        "context": finding_data.get("context", ""),
                                        "category": finding_data.get(
                                            "category", "frontend_performance"
                                        ),
                                        "performance_impact": finding_data.get(
                                            "performance_impact", "unknown"
                                        ),
                                    },
                                )
                                result.add_finding(finding)
                                performance_summary[finding_data["issue_type"]] += 1

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
            analysis_summary = self._generate_frontend_summary(
                performance_summary, file_count
            )
            result.metadata = analysis_summary

            result.set_execution_time(start_time)
            return result.to_dict(min_severity=min_severity)

        except Exception as e:
            result.set_error(f"Frontend performance analysis failed: {str(e)}")
            result.set_execution_time(start_time)
            return result.to_dict()

    def _analyze_file_frontend_performance(
        self, file_path: str, relative_path: str
    ) -> List[Dict[str, Any]]:
        """Analyze frontend performance issues in a single file."""
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

            file_ext = Path(file_path).suffix.lower()

            # Check bundle size patterns for JS/TS files
            if file_ext in [".js", ".jsx", ".ts", ".tsx"]:
                findings.extend(
                    self._check_performance_patterns(
                        content,
                        lines,
                        relative_path,
                        self.bundle_patterns,
                        "bundle",
                        "bundle_size",
                    )
                )

                # Check React patterns for React files
                if "react" in content.lower() or file_ext in [".jsx", ".tsx"]:
                    findings.extend(
                        self._check_performance_patterns(
                            content,
                            lines,
                            relative_path,
                            self.react_patterns,
                            "react",
                            "render_performance",
                        )
                    )

                # Check JavaScript patterns
                findings.extend(
                    self._check_performance_patterns(
                        content,
                        lines,
                        relative_path,
                        self.js_patterns,
                        "javascript",
                        "runtime_performance",
                    )
                )

            # Check CSS patterns for CSS files
            elif file_ext in [".css", ".scss", ".sass", ".less"]:
                findings.extend(
                    self._check_performance_patterns(
                        content,
                        lines,
                        relative_path,
                        self.css_patterns,
                        "css",
                        "render_performance",
                    )
                )

            # Check asset patterns for HTML files
            elif file_ext in [".html", ".htm"]:
                findings.extend(
                    self._check_performance_patterns(
                        content,
                        lines,
                        relative_path,
                        self.asset_patterns,
                        "assets",
                        "load_performance",
                    )
                )

            # Check for large files
            if len(content) > 100000:  # Files larger than 100KB
                findings.append(
                    {
                        "file": relative_path,
                        "line": 1,
                        "issue_type": "large_file_size",
                        "severity": "medium",
                        "message": f"Large file size ({len(content)} bytes) may impact performance",
                        "context": f"File size: {len(content)} bytes",
                        "category": "file_size",
                        "performance_impact": "load_performance",
                    }
                )

        except Exception as e:
            findings.append(
                {
                    "file": relative_path,
                    "line": 0,
                    "issue_type": "file_error",
                    "severity": "low",
                    "message": f"Could not analyze file: {str(e)}",
                    "category": "analysis",
                    "performance_impact": "unknown",
                }
            )

        return findings

    def _check_performance_patterns(
        self,
        content: str,
        lines: List[str],
        file_path: str,
        pattern_dict: Dict,
        category: str,
        performance_impact: str,
    ) -> List[Dict[str, Any]]:
        """Check for specific frontend performance patterns in file content."""
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
                            "issue_type": f"{category}_{pattern_name}",
                            "severity": pattern_info["severity"],
                            "message": f"{pattern_info['description']} ({pattern_name})",
                            "context": (
                                lines[line_num - 1].strip()
                                if line_num <= len(lines)
                                else ""
                            ),
                            "category": category,
                            "performance_impact": performance_impact,
                        }
                    )

        return findings

    def _get_frontend_recommendation(self, issue_type: str) -> str:
        """Get specific recommendations for frontend performance issues."""
        recommendations = {
            "bundle_large_imports": "Use tree shaking and import only needed functions",
            "bundle_unused_imports": "Remove unused imports to reduce bundle size",
            "bundle_dynamic_imports_missing": "Implement code splitting with dynamic imports",
            "react_missing_memo": "Use React.memo, useMemo, or useCallback for optimization",
            "react_inline_object_creation": "Move object/function creation outside render",
            "react_missing_key_prop": "Add unique key props to list items",
            "react_unnecessary_rerenders": "Optimize state management and effect dependencies",
            "css_expensive_selectors": "Simplify CSS selectors for better performance",
            "css_large_css_files": "Split large CSS files and use critical CSS",
            "css_unused_css": "Remove unused CSS rules to reduce file size",
            "javascript_inefficient_dom_queries": "Cache DOM queries and avoid queries in loops",
            "javascript_synchronous_operations": "Use async/await and batch operations",
            "javascript_memory_leaks": "Clean up timers, listeners, and observers",
            "javascript_large_data_processing": "Use web workers for heavy data processing",
            "assets_unoptimized_images": "Use modern image formats (WebP, AVIF)",
            "assets_missing_lazy_loading": "Implement lazy loading for images and iframes",
            "assets_large_bundle_assets": "Host large media files externally or use CDN",
            "large_file_size": "Split large files into smaller modules",
        }
        return recommendations.get(
            issue_type, "Review for frontend performance optimization opportunities"
        )

    def _generate_frontend_summary(
        self, performance_summary: Dict, file_count: int
    ) -> Dict[str, Any]:
        """Generate summary of frontend performance analysis."""

        # Categorize issues by performance impact
        impact_categories = {
            "bundle_size": [
                k for k in performance_summary.keys() if k.startswith("bundle_")
            ],
            "render_performance": [
                k
                for k in performance_summary.keys()
                if k.startswith(("react_", "css_"))
            ],
            "runtime_performance": [
                k for k in performance_summary.keys() if k.startswith("javascript_")
            ],
            "load_performance": [
                k
                for k in performance_summary.keys()
                if k.startswith("assets_") or "large_file_size" in k
            ],
        }

        total_issues = sum(performance_summary.values())
        severity_counts = self._count_by_severity(performance_summary)

        return {
            "total_files_analyzed": file_count,
            "total_performance_issues": total_issues,
            "issues_by_performance_impact": {
                category: {
                    "count": sum(performance_summary.get(issue, 0) for issue in issues),
                    "issues": {
                        issue.replace(f"{category}_", ""): performance_summary.get(
                            issue, 0
                        )
                        for issue in issues
                        if performance_summary.get(issue, 0) > 0
                    },
                }
                for category, issues in impact_categories.items()
            },
            "severity_breakdown": severity_counts,
            "performance_score": self._calculate_performance_score(
                total_issues, file_count
            ),
            "optimization_opportunities": self._get_optimization_opportunities(
                performance_summary
            ),
            "recommendations": self._generate_priority_recommendations(
                performance_summary
            ),
        }

    def _count_by_severity(self, performance_summary: Dict) -> Dict[str, int]:
        """Count issues by severity level."""
        severity_mapping = {
            "high": ["synchronous_operations", "memory_leaks"],
            "medium": [
                "large_imports",
                "dynamic_imports_missing",
                "missing_memo",
                "missing_key_prop",
                "unnecessary_rerenders",
                "expensive_selectors",
                "inefficient_dom_queries",
                "large_data_processing",
                "missing_lazy_loading",
                "large_bundle_assets",
                "large_file_size",
            ],
            "low": [
                "unused_imports",
                "inline_object_creation",
                "large_css_files",
                "unused_css",
                "unoptimized_images",
                "file_error",
            ],
        }

        counts = {"high": 0, "medium": 0, "low": 0, "critical": 0}
        for issue, count in performance_summary.items():
            issue_name = issue.split("_", 1)[-1]  # Remove category prefix
            for severity, patterns in severity_mapping.items():
                if issue_name in patterns:
                    counts[severity] += count
                    break

        return counts

    def _calculate_performance_score(self, total_issues: int, file_count: int) -> float:
        """Calculate a performance score (0-100, higher is better)."""
        if file_count == 0:
            return 100.0

        issue_density = total_issues / file_count
        # Score decreases with issue density
        score = max(0, 100 - (issue_density * 12))
        return round(score, 1)

    def _get_optimization_opportunities(
        self, performance_summary: Dict
    ) -> List[Dict[str, Any]]:
        """Get the top frontend optimization opportunities."""
        high_impact_patterns = [
            "large_imports",
            "synchronous_operations",
            "memory_leaks",
            "missing_memo",
            "large_bundle_assets",
        ]
        opportunities = []

        for issue, count in performance_summary.items():
            issue_name = issue.split("_", 1)[-1]
            if issue_name in high_impact_patterns and count > 0:
                opportunities.append(
                    {
                        "optimization": issue.replace("_", " ").title(),
                        "count": count,
                        "impact": (
                            "high"
                            if issue_name in ["synchronous_operations", "memory_leaks"]
                            else "medium"
                        ),
                        "category": issue.split("_")[0],
                    }
                )

        return sorted(opportunities, key=lambda x: x["count"], reverse=True)[:5]

    def _generate_priority_recommendations(
        self, performance_summary: Dict
    ) -> List[str]:
        """Generate priority recommendations based on findings."""
        recommendations = []

        # High impact issues first
        if any("synchronous_operations" in k for k in performance_summary.keys()):
            recommendations.append(
                "HIGH: Fix synchronous operations blocking the UI thread"
            )
        if any("memory_leaks" in k for k in performance_summary.keys()):
            recommendations.append(
                "HIGH: Clean up memory leaks from timers and event listeners"
            )

        # Bundle optimization
        if any("large_imports" in k for k in performance_summary.keys()):
            recommendations.append(
                "MEDIUM: Optimize bundle size with tree shaking and selective imports"
            )
        if any("dynamic_imports_missing" in k for k in performance_summary.keys()):
            recommendations.append(
                "MEDIUM: Implement code splitting for better load performance"
            )

        # React optimization
        if any(
            "missing_memo" in k or "unnecessary_rerenders" in k
            for k in performance_summary.keys()
        ):
            recommendations.append("MEDIUM: Optimize React rendering with memoization")

        # General recommendations
        total_issues = sum(performance_summary.values())
        if total_issues > 15:
            recommendations.append(
                "Consider implementing performance monitoring and metrics"
            )

        return recommendations[:5]

    def _should_analyze_file(self, filename: str) -> bool:
        """Check if file should be analyzed."""
        analyze_extensions = {
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".vue",
            ".svelte",
            ".css",
            ".scss",
            ".sass",
            ".less",
            ".html",
            ".htm",
        }
        return any(filename.endswith(ext) for ext in analyze_extensions)


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze frontend performance in codebase"
    )
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

    analyzer = FrontendPerformanceAnalyzer()
    result = analyzer.analyze_frontend_performance(args.target_path, args.min_severity)

    if args.output_format == "console":
        # Simple console output
        if result.get("success", False):
            print(f"Frontend Performance Analysis Results for: {args.target_path}")
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
