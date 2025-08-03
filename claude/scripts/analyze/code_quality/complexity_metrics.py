#!/usr/bin/env python3
"""
Code quality analysis script: Complexity metrics and code smells.
Part of Claude Code Workflows.
"""

import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Set

# Add utils to path for imports
script_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(script_dir / "utils"))

try:
    from output_formatter import ResultFormatter, AnalysisResult
    from tech_stack_detector import TechStackDetector
except ImportError as e:
    print(f"Error importing utilities: {e}", file=sys.stderr)
    sys.exit(1)


class ComplexityAnalyzer:
    """Analyze code complexity and quality metrics."""

    def __init__(self):
        # Initialize tech stack detector for smart filtering
        self.tech_detector = TechStackDetector()
        # Detected tech stacks will be populated during analysis
        self.detected_tech_stacks = []
        # Complexity patterns - Use proper analysis methods instead of crude regex
        self.complexity_patterns = {
            # Disable broken patterns that fire on every function/control structure
            # "long_function" - handled by analyze_function_length() method
            # "cyclomatic_complexity" - handled by analyze_cyclomatic_complexity() method
            
            "deep_nesting": {
                "pattern": r"(\s{12,}|\t{6,})(?:if|for|while|switch|try)",  # Increased threshold
                "severity": "medium", 
                "description": "Very deep nesting detected (6+ levels) - consider refactoring",
            },
            "many_parameters": {
                "pattern": r"(?:function\s+\w+|def\s+\w+|\w+\s*)\([^)]*,[^)]*,[^)]*,[^)]*,[^)]*,[^)]*,[^)]*,",  # 7+ params
                "severity": "medium",
                "description": "Function has too many parameters (>7)",
            },
        }

        # Code smell patterns - Focus on high-impact issues only
        self.code_smell_patterns = {
            "magic_numbers": {
                "pattern": r"(?<![.\w])\b(?!(?:0|1|10|100|1000|404|200|201|301|302|500|8080|3000|5000)\b)\d{3,}(?![.\w])",
                "severity": "low",
                "description": "Magic number - consider using named constant",
            },
            "long_variable": {
                "pattern": r'(?<![\'""])\b[a-zA-Z][a-zA-Z0-9_]{40,}\b(?![\'""])',  # Increased threshold
                "severity": "low",
                "description": "Extremely long variable/function name (>40 chars)",
            },
            "empty_catch": {
                "pattern": r"catch\s*\([^)]*\)\s*{\s*}",
                "severity": "high",
                "description": "Empty catch block - errors silently ignored",
            },
            # Disabled noisy patterns:
            # "todo_fixme" - too many legitimate TODOs in development
            # "console_log" - too granular, often intentional in dev
            # "duplicate_code" - too many false positives
        }

        # Naming convention patterns - Disabled to reduce noise
        self.naming_patterns = {
            # All naming patterns disabled - too many false positives in real codebases
            # Legitimate single-letter variables: i, j, k in loops, x, y coordinates, etc.
        }

        # File extensions to scan
        self.code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".java",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".rs",
            ".swift",
            ".kt",
            ".scala",
            ".dart",
        }

        # Files to skip
        self.skip_patterns = {
            "node_modules",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "venv",
            "env",
            ".venv",
            "dist",
            "build",
            ".next",
            "coverage",
            ".nyc_output",
            "target",
            "vendor",
            "test",
            "tests",
            "spec",
            "__tests__",
            "docs",
            "documentation",
        }

        # Config files that should have reduced scrutiny
        self.config_files = {
            "config.js",
            "config.ts",
            ".config.js",
            ".config.ts",
            "tailwind.config.ts",
            "vite.config.ts",
            "metro.config.js",
            "docusaurus.config.ts",
            "next.config.js",
            "jest.config.js",
        }

    def should_scan_file(self, file_path: Path, exclusion_patterns: list = None) -> bool:
        """Determine if file should be scanned using smart filtering."""
        if exclusion_patterns is None:
            exclusion_patterns = []
        
        # Use tech stack detector for smart filtering
        file_path_str = str(file_path).lower()
        for pattern in exclusion_patterns:
            if pattern in file_path_str:
                return False
        
        # Additional basic checks for minified files
        filename = file_path.name.lower()
        if (
            ".min." in filename
            or filename.endswith("-min.js")
            or filename.endswith("-min.css")
        ):
            return False

        # Skip generated/compiled files
        if any(
            pattern in filename
            for pattern in [
                "workbox-",
                "sw.js",
                "service-worker.js",
                ".chunk.",
                "vendor.",
                "bundle.",
            ]
        ):
            return False

        # Check file extension
        suffix = file_path.suffix.lower()
        return suffix in self.code_extensions

    def is_config_file(self, file_path: Path) -> bool:
        """Check if file is a configuration file that should have reduced scrutiny."""
        filename = file_path.name.lower()
        return any(pattern in filename for pattern in self.config_files)

    def analyze_function_length(
        self, content: str, file_path: Path
    ) -> List[Dict[str, Any]]:
        """Analyze function/method length."""
        findings = []
        lines = content.split("\n")

        # Only analyze certain file types with better patterns
        suffix = file_path.suffix.lower()

        if suffix in [".js", ".ts", ".jsx", ".tsx"]:
            # JavaScript/TypeScript function patterns
            function_patterns = [
                (r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(", "function"),
                (
                    r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*(?::|=>)",
                    "arrow",
                ),
                (r"^\s*(?:export\s+)?class\s+(\w+)", "class"),
            ]
        elif suffix == ".py":
            # Python function patterns
            function_patterns = [
                (r"^\s*(?:async\s+)?def\s+(\w+)\s*\(", "function"),
                (r"^\s*class\s+(\w+)", "class"),
            ]
        else:
            # Skip other file types for now
            return findings

        for i, line in enumerate(lines):
            for pattern, func_type in function_patterns:
                match = re.search(pattern, line)
                if match:
                    match.group(1)
                    # Count lines until closing brace or next function
                    func_lines = self._count_function_lines(lines, i)

                    if func_lines > 100:  # Only flag genuinely long functions
                        findings.append(
                            {
                                "category": "Complexity",
                                "pattern_type": "long_function",
                                "file_path": str(file_path),
                                "line_number": i + 1,
                                "line_content": line.strip(),
                                "severity": "high" if func_lines > 200 else "medium",
                                "description": f"Function is {func_lines} lines long (recommended: <100)",
                                "function_length": func_lines,
                            }
                        )

        return findings

    def _count_function_lines(self, lines: List[str], start_idx: int) -> int:
        """Count lines in a function/method."""
        brace_count = 0
        indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        for i in range(start_idx, len(lines)):
            line = lines[i]

            # Count braces for languages that use them
            brace_count += line.count("{") - line.count("}")

            # For Python, use indentation
            if not line.strip():
                continue

            current_indent = len(line) - len(line.lstrip())

            # End of function for indentation-based languages
            if i > start_idx and current_indent <= indent_level and line.strip():
                return i - start_idx

            # End of function for brace-based languages
            if brace_count == 0 and i > start_idx and "{" in lines[start_idx]:
                return i - start_idx + 1

        return len(lines) - start_idx

    def analyze_cyclomatic_complexity(
        self, content: str, file_path: Path
    ) -> List[Dict[str, Any]]:
        """Calculate cyclomatic complexity indicators."""
        findings = []
        content.split("\n")

        # Count complexity indicators per function
        complexity_keywords = (
            r"\b(?:if|else|elif|for|while|catch|case|switch|&&|\|\|)\b"
        )

        # Simple approach: count per file (could be enhanced to per-function)
        matches = re.findall(complexity_keywords, content, re.IGNORECASE)
        complexity_score = len(matches)

        if complexity_score > 60:  # Only flag genuinely complex files
            findings.append(
                {
                    "category": "Complexity",
                    "pattern_type": "high_complexity",
                    "file_path": str(file_path),
                    "line_number": 1,
                    "line_content": f"File complexity score: {complexity_score}",
                    "severity": "high" if complexity_score > 120 else "medium",
                    "description": f"File has high cyclomatic complexity ({complexity_score} indicators)",
                    "complexity_score": complexity_score,
                }
            )

        return findings

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Scan a single file for code quality issues.

        Returns:
            List of findings dictionaries
        """
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

                # Analyze function length
                findings.extend(self.analyze_function_length(content, file_path))

                # Analyze cyclomatic complexity
                findings.extend(self.analyze_cyclomatic_complexity(content, file_path))

                # Check complexity patterns
                for pattern_name, pattern_info in self.complexity_patterns.items():
                    findings.extend(
                        self._find_pattern_matches(
                            content,
                            lines,
                            file_path,
                            pattern_name,
                            pattern_info,
                            "Complexity",
                        )
                    )

                # Check code smell patterns
                for pattern_name, pattern_info in self.code_smell_patterns.items():
                    findings.extend(
                        self._find_pattern_matches(
                            content,
                            lines,
                            file_path,
                            pattern_name,
                            pattern_info,
                            "Code Smell",
                        )
                    )

                # Check naming patterns (skip for config files)
                if not self.is_config_file(file_path):
                    for pattern_name, pattern_info in self.naming_patterns.items():
                        findings.extend(
                            self._find_pattern_matches(
                                content,
                                lines,
                                file_path,
                                pattern_name,
                                pattern_info,
                                "Naming",
                            )
                        )

        except Exception:
            # Log error but continue scanning
            pass

        return findings

    def _find_pattern_matches(
        self,
        content: str,
        lines: List[str],
        file_path: Path,
        pattern_name: str,
        pattern_info: Dict[str, str],
        category: str,
    ) -> List[Dict[str, Any]]:
        """Find matches for a specific pattern."""
        findings = []

        try:
            matches = re.finditer(
                pattern_info["pattern"], content, re.MULTILINE | re.IGNORECASE
            )

            for match in matches:
                # Apply framework-specific exclusions for magic_numbers
                if pattern_name == "magic_numbers" and hasattr(self, 'framework_exclusions'):
                    if self._should_exclude_magic_number(match, content, file_path):
                        continue

                # Find line number
                line_start = content[: match.start()].count("\n") + 1

                finding = {
                    "category": category,
                    "pattern_type": pattern_name,
                    "file_path": str(file_path),
                    "line_number": line_start,
                    "line_content": lines[line_start - 1].strip()
                    if line_start <= len(lines)
                    else "",
                    "matched_text": match.group(0)[:50],  # Limit length
                    "severity": pattern_info["severity"],
                    "description": pattern_info["description"],
                }
                findings.append(finding)
        except re.error:
            # Skip invalid regex patterns
            pass

        return findings
    
    def _should_exclude_magic_number(self, match, content: str, file_path: Path) -> bool:
        """Check if a magic number should be excluded based on framework context."""
        matched_text = match.group(0)
        
        # Get surrounding context (50 chars before and after)
        start = max(0, match.start() - 50)
        end = min(len(content), match.end() + 50)
        context = content[start:end]
        
        # Check against all framework exclusion patterns
        for exclusion_category in self.framework_exclusions.values():
            for exclusion_pattern in exclusion_category:
                try:
                    if re.search(exclusion_pattern, context, re.IGNORECASE):
                        return True
                except re.error:
                    continue
        
        # Additional context-based exclusions
        file_ext = file_path.suffix.lower()
        
        # Exclude CSS/styling context
        if file_ext in ['.css', '.scss', '.less']:
            return True
            
        # Enhanced CSS class detection
        # Check if number is part of Tailwind-style class names
        tailwind_pattern = r'(?:bg|text|border|ring|shadow|p|m|w|h|gap|space|inset|top|right|bottom|left|z|opacity|scale|rotate|skew|translate)-[^"\']*?' + re.escape(matched_text) + r'[^"\']*?'
        if re.search(tailwind_pattern, context):
            return True
            
        # Exclude if in string literals that contain CSS-like patterns
        css_string_patterns = [
            r'["\'][^"\']*(?:bg|text|border|ring|shadow|hover|focus|active)-[^"\']*?' + re.escape(matched_text) + r'[^"\']*?["\']',
            r'["\'][^"\']*\b' + re.escape(matched_text) + r'(?:px|em|rem|%|vh|vw)\b[^"\']*?["\']',
            r'["\'][^"\']*#[0-9a-fA-F]*?' + re.escape(matched_text) + r'[0-9a-fA-F]*?["\']'
        ]
        
        for pattern in css_string_patterns:
            if re.search(pattern, context):
                return True
            
        # Exclude if in className or style props (React/JSX)
        jsx_context = re.search(r'(?:className|style)\s*=\s*["\'][^"\']*\b' + re.escape(matched_text) + r'\b', context)
        if jsx_context:
            return True
            
        # Exclude SVG path data (like the d attribute values)
        svg_path_context = re.search(r'd\s*=\s*["\'][^"\']*\b' + re.escape(matched_text) + r'\b[^"\']*["\']', context)
        if svg_path_context:
            return True
            
        # Exclude numbers in SVG/XML attributes
        svg_attr_context = re.search(r'(?:viewBox|x|y|width|height|cx|cy|r|x1|y1|x2|y2|dx|dy)\s*=\s*["\'][^"\']*\b' + re.escape(matched_text) + r'\b', context)
        if svg_attr_context:
            return True
            
        return False

    def get_exclude_dirs(self, exclusion_patterns: set) -> set:
        """Extract directory names from exclusion patterns."""
        exclude_dirs = set()
        for pattern in exclusion_patterns:
            # Extract directory name from patterns like "node_modules/**/*"
            if "/**/*" in pattern:
                dir_name = pattern.replace("/**/*", "")
                exclude_dirs.add(dir_name)
            elif pattern.endswith("/**/*"):
                dir_name = pattern.replace("/**/*", "")
                exclude_dirs.add(dir_name)
            # Handle simple directory patterns
            elif "/" not in pattern and not pattern.startswith("*"):
                exclude_dirs.add(pattern)
        
        # Add common directories that should always be excluded
        exclude_dirs.update({
            "node_modules", ".git", "__pycache__", "venv", ".venv", 
            "coverage", "dist", "build", ".expo", ".next", ".nyc_output",
            "todos", "worktrees", ".worktrees", "tmp", "temp"
        })
        
        return exclude_dirs

    def get_framework_specific_exclusions(self, target_path: str) -> Dict[str, Set[str]]:
        """Get framework-specific pattern exclusions based on detected tech stack."""
        # Detect tech stacks for the target path
        self.detected_tech_stacks = self.tech_detector.detect_tech_stack(target_path)
        
        exclusions = {
            "magic_numbers_context": set(),
            "css_classes": set(),
            "framework_constants": set()
        }
        
        for tech_stack in self.detected_tech_stacks:
            if tech_stack in ["react_native_expo", "next_js", "react"]:
                # CSS/Tailwind exclusions for React-based projects
                exclusions["css_classes"].update({
                    # Tailwind color scales
                    r"(?:bg|text|border|ring|shadow)-(?:gray|red|blue|green|yellow|purple|pink|indigo|cyan|teal|orange|amber|lime|emerald|sky|violet|fuchsia|rose|slate|zinc|neutral|stone)-(?:50|100|200|300|400|500|600|700|800|900)",
                    # Tailwind spacing/sizing
                    r"(?:p|m|w|h|gap|space|inset|top|right|bottom|left)-(?:\d+|px|0\.5|1\.5|2\.5|3\.5)",
                    # Tailwind z-index, opacity, etc.
                    r"(?:z|opacity|scale|rotate|skew|translate)-\d+",
                    # CSS pixel values in JSX
                    r"(?<=[\"\'])\d+px(?=[\"\'])",
                    # React/CSS custom properties
                    r"(?<=[\"\'])--[\w-]+:\s*\d+(?=[\"\'])"
                })
                
                # Framework constants
                exclusions["framework_constants"].update({
                    # React Hook timeouts/delays
                    r"(?:setTimeout|setInterval|delay)\(\w+,\s*\d{3,}\)",
                    # Port numbers in development
                    r"(?:PORT|port).*?(?:3000|8080|5000|9000)",
                    # HTTP status codes
                    r"(?:status|code).*?(?:200|201|400|401|403|404|500)"
                })
                
            elif tech_stack in ["django", "flask"]:
                # Python web framework exclusions
                exclusions["framework_constants"].update({
                    # Django settings
                    r"DEBUG\s*=\s*\d+",
                    r"MAX_LENGTH\s*=\s*\d+",
                    # Common Python constants
                    r"(?:TIMEOUT|DELAY|RETRY_COUNT)\s*=\s*\d+"
                })
                
            elif tech_stack == "java_maven" or tech_stack == "java_gradle":
                # Java framework exclusions
                exclusions["framework_constants"].update({
                    # Spring Boot common ports
                    r"server\.port\s*=\s*\d+",
                    # JPA/Hibernate constants
                    r"@Column\(length\s*=\s*\d+\)",
                    # Test timeouts
                    r"@Timeout\(\d+\)"
                })
                
        return exclusions

    def scan_directory(self, target_path: str) -> List[Dict[str, Any]]:
        """
        Scan directory recursively for code quality issues with smart filtering.

        Args:
            target_path: Path to scan

        Returns:
            List of all findings
        """
        import os
        all_findings = []
        target = Path(target_path)
        
        # Get exclusion patterns for smart filtering
        exclusion_patterns = self.tech_detector.get_exclusion_patterns(target_path)
        exclude_dirs = self.get_exclude_dirs(exclusion_patterns)
        
        # Get framework-specific exclusions for magic numbers and other patterns
        self.framework_exclusions = self.get_framework_specific_exclusions(target_path)

        if target.is_file():
            if self.should_scan_file(target, list(exclusion_patterns)):
                all_findings.extend(self.scan_file(target))
        elif target.is_dir():
            # Use os.walk with proper directory filtering
            for root, dirs, files in os.walk(target_path):
                # Filter directories in-place to prevent traversal into excluded dirs
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    file_path = Path(os.path.join(root, file))
                    if self.should_scan_file(file_path, list(exclusion_patterns)):
                        all_findings.extend(self.scan_file(file_path))

        return all_findings

    def analyze(self, target_path: str) -> AnalysisResult:
        """
        Main analysis function.

        Args:
            target_path: Path to analyze

        Returns:
            AnalysisResult object
        """
        start_time = time.time()
        result = ResultFormatter.create_code_quality_result(
            "complexity_metrics.py", target_path
        )

        try:
            # Scan for code quality issues
            findings = self.scan_directory(target_path)

            # Convert to Finding objects
            finding_id = 1
            for finding_data in findings:
                recommendation = self._get_recommendation(finding_data["pattern_type"])

                finding = ResultFormatter.create_finding(
                    f"QUAL{finding_id:03d}",
                    f"{finding_data['category']}: {finding_data['pattern_type']}",
                    finding_data["description"],
                    finding_data["severity"],
                    finding_data["file_path"],
                    finding_data["line_number"],
                    recommendation,
                    {
                        "category": finding_data["category"],
                        "pattern_type": finding_data["pattern_type"],
                        "line_content": finding_data["line_content"],
                        "matched_text": finding_data.get("matched_text", ""),
                        "complexity_score": finding_data.get("complexity_score"),
                        "function_length": finding_data.get("function_length"),
                    },
                )
                result.add_finding(finding)
                finding_id += 1

            # Add metadata
            unique_files = set(f["file_path"] for f in findings)
            result.metadata = {
                "files_scanned": len(unique_files),
                "patterns_checked": len(self.complexity_patterns)
                + len(self.code_smell_patterns)
                + len(self.naming_patterns),
                "categories": {
                    "complexity": len(
                        [f for f in findings if f["category"] == "Complexity"]
                    ),
                    "code_smells": len(
                        [f for f in findings if f["category"] == "Code Smell"]
                    ),
                    "naming": len([f for f in findings if f["category"] == "Naming"]),
                },
            }

        except Exception as e:
            result.set_error(f"Analysis failed: {str(e)}")

        result.set_execution_time(start_time)
        return result

    def _get_recommendation(self, pattern_type: str) -> str:
        """Get recommendation for specific pattern type."""
        recommendations = {
            "long_function": "Break down into smaller, focused functions",
            "deep_nesting": "Extract nested logic into separate functions or use early returns",
            "many_parameters": "Use parameter objects or configuration classes",
            "high_complexity": "Simplify control flow and extract complex logic",
            "duplicate_code": "Extract common code into reusable functions",
            "magic_numbers": "Replace with named constants or configuration",
            "long_variable": "Use shorter, more concise names while maintaining clarity",
            "todo_fixme": "Address TODO items or convert to proper issue tracking",
            "empty_catch": "Add proper error handling or logging",
            "console_log": "Remove debug statements or use proper logging framework",
            "camelCase_violation": "Use consistent camelCase naming",
            "snake_case_violation": "Use consistent snake_case naming",
            "single_letter": "Use descriptive variable names",
        }
        return recommendations.get(pattern_type, "Review and improve code quality")


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze code complexity metrics and quality issues"
    )
    parser.add_argument("target_path", help="Path to analyze")
    parser.add_argument(
        "--output-format",
        choices=["json", "console", "summary"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Limit output to top 10 critical/high findings for large codebases",
    )
    parser.add_argument(
        "--min-severity",
        choices=["critical", "high", "medium", "low"],
        default="low",
        help="Minimum severity level (default: low)",
    )

    args = parser.parse_args()

    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze(args.target_path)

    # Auto-enable summary mode for large result sets
    if len(result.findings) > 50 and not args.summary:
        print(
            f"⚠️ Large result set detected ({len(result.findings)} findings). Consider using --summary flag.",
            file=sys.stderr,
        )

    # Output based on format choice
    if args.output_format == "console":
        print(ResultFormatter.format_console_output(result))
    elif args.output_format == "summary":
        print(result.to_json(summary_mode=True, min_severity=args.min_severity))
    else:  # json (default)
        print(result.to_json(summary_mode=args.summary, min_severity=args.min_severity))
        # Also print console summary to stderr for human readability
        print(ResultFormatter.format_console_output(result), file=sys.stderr)


if __name__ == "__main__":
    main()
