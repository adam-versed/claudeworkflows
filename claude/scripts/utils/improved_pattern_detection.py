#!/usr/bin/env python3
"""
Improved Pattern Detection Utility
Distinguishes between language syntax and actual architectural patterns.
"""

import re
import ast
from typing import Dict, List, Any, Set
from dataclasses import dataclass


@dataclass
class PatternMatch:
    """Represents a detected pattern with context."""

    pattern_type: str
    pattern_name: str
    severity: str
    description: str
    line_number: int
    context: str
    confidence: float
    is_language_feature: bool


class ImprovedPatternDetector:
    """Enhanced pattern detection that filters out language syntax."""

    def __init__(self):
        # Architectural patterns (actual design patterns)
        self.architectural_patterns = {
            "singleton": {
                "indicators": [
                    # Real singleton implementation
                    r"class\s+\w+.*:\s*\n(?:\s*\n)*\s*_instance\s*=\s*None",
                    r"def\s+__new__\s*\(.*\):\s*\n.*if.*_instance.*is.*None",
                    r"def\s+getInstance\s*\(",
                ],
                "severity": "medium",
                "description": "Singleton pattern implementation detected",
                "exclude_patterns": [
                    r"@\w+",  # Exclude decorators
                    r"\/\*\*.*\*\/",  # Exclude JSDoc
                    r"#.*",  # Exclude comments
                ],
            },
            "factory": {
                "indicators": [
                    r"class\s+\w*Factory\w*.*:\s*\n(?:\s|\n)*def\s+create",
                    r"def\s+create\w*\(.*\):\s*\n.*return\s+\w+\(",
                    r"def\s+make\w*\(.*\):\s*\n.*return\s+\w+\(",
                ],
                "severity": "low",
                "description": "Factory pattern implementation detected",
                "exclude_patterns": [
                    r"@\w+",
                    r"\/\*\*.*\*\/",
                    r"#.*",
                ],
            },
            "observer": {
                "indicators": [
                    r"class\s+\w*Observer\w*.*:\s*\n(?:\s|\n)*def\s+update",
                    r"def\s+notify\s*\(.*\):\s*\n.*for.*in.*observers",
                    r"def\s+subscribe\s*\(.*\):\s*\n.*observers.*append",
                ],
                "severity": "low",
                "description": "Observer pattern implementation detected",
                "exclude_patterns": [
                    r"addEventListener\s*\(",  # DOM events, not observer pattern
                    r"on\w+\s*=",  # Event handlers
                ],
            },
            "strategy": {
                "indicators": [
                    r"class\s+\w*Strategy\w*.*:\s*\n(?:\s|\n)*def\s+execute",
                    r"def\s+set_strategy\s*\(",
                    r"strategy\s*=\s*\w+Strategy\(",
                ],
                "severity": "low",
                "description": "Strategy pattern implementation detected",
                "exclude_patterns": [],
            },
            "repository": {
                "indicators": [
                    r"class\s+\w*Repository\w*.*:\s*\n(?:(?:\s|\n)*def\s+(?:find|save|delete|get).*){2,}",
                    r"def\s+findBy\w*\(.*\):\s*\n.*(?:SELECT|query|filter)",
                ],
                "severity": "low",
                "description": "Repository pattern implementation detected",
                "exclude_patterns": [],
            },
        }

        # Anti-patterns (actual code smells)
        self.antipatterns = {
            "god_class": {
                "indicators": [
                    # Classes with many methods AND responsibilities
                    r"class\s+\w+.*:\s*(?:\n(?:\s*(?:def|class|@).*\n?){15,})",
                ],
                "severity": "high",
                "description": "God class detected - too many responsibilities",
                "exclude_patterns": [
                    r"test.*\.py",  # Test classes can be large
                    r".*test\.py",
                ],
            },
            "long_parameter_list": {
                "indicators": [
                    r"def\s+\w+\s*\([^)]*,\s*[^)]*,\s*[^)]*,\s*[^)]*,\s*[^)]*,\s*[^)]*,\s*[^)]*[^)]*\):",
                ],
                "severity": "medium",
                "description": "Long parameter list detected",
                "exclude_patterns": [],
            },
            "feature_envy": {
                "indicators": [
                    # Multiple chained method calls on external objects
                    r"\w+\.\w+\.\w+\.\w+\.\w+",
                ],
                "severity": "medium",
                "description": "Feature envy - excessive method chaining",
                "exclude_patterns": [
                    r"self\.",  # Method chaining on self is OK
                    r"this\.",  # Method chaining on this is OK
                ],
            },
        }

        # Language features that are NOT architectural patterns
        self.language_features = {
            "decorators": {
                "patterns": [r"@\w+", r"@\w+\(.*\)"],
                "languages": ["python"],
                "description": "Python decorator syntax",
            },
            "jsdoc": {
                "patterns": [r"\/\*\*.*?\*\/", r"\/\*\*.*@type.*\*\/"],
                "languages": ["javascript", "typescript"],
                "description": "JSDoc documentation",
            },
            "comments": {
                "patterns": [r"#.*", r"\/\/.*", r"\/\*.*?\*\/"],
                "languages": ["python", "javascript", "typescript", "java", "csharp"],
                "description": "Code comments",
            },
            "annotations": {
                "patterns": [r"@\w+", r"@\w+\(.*\)"],
                "languages": ["java", "csharp"],
                "description": "Language annotations",
            },
            "type_hints": {
                "patterns": [r":\s*\w+", r"->\s*\w+"],
                "languages": ["python", "typescript"],
                "description": "Type annotations",
            },
        }

    def detect_patterns(
        self, content: str, file_path: str, language: str
    ) -> List[PatternMatch]:
        """
        Detect architectural patterns while filtering out language features.

        Args:
            content: File content to analyze
            file_path: Path to the file being analyzed
            language: Programming language of the file

        Returns:
            List of detected pattern matches
        """
        matches = []
        lines = content.split("\n")

        # First, identify language features to exclude
        language_feature_locations = self._identify_language_features(content, language)

        # Then detect architectural patterns
        for pattern_category in [self.architectural_patterns, self.antipatterns]:
            for pattern_name, pattern_info in pattern_category.items():
                pattern_matches = self._find_pattern_matches(
                    content,
                    lines,
                    pattern_name,
                    pattern_info,
                    language_feature_locations,
                    file_path,
                )
                matches.extend(pattern_matches)

        return matches

    def _identify_language_features(self, content: str, language: str) -> Set[int]:
        """Identify line numbers that contain language features, not patterns."""
        feature_lines = set()

        for feature_name, feature_info in self.language_features.items():
            if language in feature_info["languages"]:
                for pattern in feature_info["patterns"]:
                    for match in re.finditer(
                        pattern, content, re.MULTILINE | re.DOTALL
                    ):
                        line_num = content[: match.start()].count("\n") + 1
                        feature_lines.add(line_num)

        return feature_lines

    def _find_pattern_matches(
        self,
        content: str,
        lines: List[str],
        pattern_name: str,
        pattern_info: Dict,
        feature_lines: Set[int],
        file_path: str,
    ) -> List[PatternMatch]:
        """Find matches for a specific pattern."""
        matches = []

        for indicator in pattern_info["indicators"]:
            for match in re.finditer(indicator, content, re.MULTILINE | re.DOTALL):
                line_num = content[: match.start()].count("\n") + 1

                # Skip if this line contains language features
                if line_num in feature_lines:
                    continue

                # Check exclude patterns
                if self._should_exclude_match(
                    match.group(0), pattern_info.get("exclude_patterns", [])
                ):
                    continue

                # Calculate confidence based on context
                confidence = self._calculate_confidence(match, content, pattern_name)

                # Only include high-confidence matches
                if confidence >= 0.7:
                    matches.append(
                        PatternMatch(
                            pattern_type="architectural"
                            if pattern_name in self.architectural_patterns
                            else "anti",
                            pattern_name=pattern_name,
                            severity=pattern_info["severity"],
                            description=pattern_info["description"],
                            line_number=line_num,
                            context=lines[line_num - 1].strip()
                            if line_num <= len(lines)
                            else "",
                            confidence=confidence,
                            is_language_feature=False,
                        )
                    )

        return matches

    def _should_exclude_match(
        self, match_text: str, exclude_patterns: List[str]
    ) -> bool:
        """Check if match should be excluded based on exclude patterns."""
        for exclude_pattern in exclude_patterns:
            if re.search(exclude_pattern, match_text, re.IGNORECASE):
                return True
        return False

    def _calculate_confidence(
        self, match: re.Match, content: str, pattern_name: str
    ) -> float:
        """Calculate confidence score for a pattern match."""
        confidence = 0.5  # Base confidence

        match_text = match.group(0)

        # Increase confidence based on pattern-specific criteria
        if pattern_name == "singleton":
            if "_instance" in match_text and "None" in match_text:
                confidence += 0.3
            if "__new__" in match_text:
                confidence += 0.2

        elif pattern_name == "factory":
            if "create" in match_text.lower() and "return" in match_text:
                confidence += 0.3
            if "Factory" in match_text:
                confidence += 0.2

        elif pattern_name == "observer":
            if "observer" in match_text.lower() and (
                "notify" in match_text or "update" in match_text
            ):
                confidence += 0.4

        elif pattern_name == "repository":
            if "repository" in match_text.lower() and any(
                op in match_text.lower() for op in ["find", "save", "delete"]
            ):
                confidence += 0.4

        elif pattern_name == "god_class":
            # Count methods in the class
            method_count = len(re.findall(r"def\s+\w+", match_text))
            if method_count > 10:
                confidence += min(0.4, method_count * 0.02)

        # Decrease confidence for common false positives
        if re.search(r"@\w+", match_text):  # Contains decorators
            confidence -= 0.2

        if re.search(r"\/\*\*.*\*\/", match_text):  # Contains JSDoc
            confidence -= 0.3

        if re.search(r"#.*", match_text):  # Contains comments
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    def analyze_python_ast(self, content: str, file_path: str) -> List[PatternMatch]:
        """Use AST analysis for more accurate Python pattern detection."""
        matches = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Detect god classes
                if isinstance(node, ast.ClassDef):
                    method_count = len(
                        [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    )
                    if method_count > 15:
                        matches.append(
                            PatternMatch(
                                pattern_type="anti",
                                pattern_name="god_class",
                                severity="high",
                                description=f"God class with {method_count} methods",
                                line_number=node.lineno,
                                context=f"class {node.name}:",
                                confidence=0.9,
                                is_language_feature=False,
                            )
                        )

                # Detect long parameter lists
                if isinstance(node, ast.FunctionDef):
                    param_count = len(node.args.args)
                    if param_count > 6:
                        matches.append(
                            PatternMatch(
                                pattern_type="anti",
                                pattern_name="long_parameter_list",
                                severity="medium",
                                description=f"Function with {param_count} parameters",
                                line_number=node.lineno,
                                context=f"def {node.name}(...)",
                                confidence=0.9,
                                is_language_feature=False,
                            )
                        )

        except SyntaxError:
            # Skip files with syntax errors
            pass

        return matches

    def get_pattern_summary(self, matches: List[PatternMatch]) -> Dict[str, Any]:
        """Generate summary statistics for detected patterns."""
        total_matches = len(matches)

        by_type = {}
        by_severity = {}
        by_confidence = {"high": 0, "medium": 0, "low": 0}

        for match in matches:
            # Count by pattern type
            by_type[match.pattern_name] = by_type.get(match.pattern_name, 0) + 1

            # Count by severity
            by_severity[match.severity] = by_severity.get(match.severity, 0) + 1

            # Count by confidence level
            if match.confidence >= 0.8:
                by_confidence["high"] += 1
            elif match.confidence >= 0.6:
                by_confidence["medium"] += 1
            else:
                by_confidence["low"] += 1

        return {
            "total_patterns": total_matches,
            "patterns_by_type": by_type,
            "patterns_by_severity": by_severity,
            "patterns_by_confidence": by_confidence,
            "high_confidence_patterns": [m for m in matches if m.confidence >= 0.8],
            "recommendations": self._generate_recommendations(matches),
        }

    def _generate_recommendations(self, matches: List[PatternMatch]) -> List[str]:
        """Generate actionable recommendations based on detected patterns."""
        recommendations = []

        pattern_counts = {}
        for match in matches:
            pattern_counts[match.pattern_name] = (
                pattern_counts.get(match.pattern_name, 0) + 1
            )

        # Generate specific recommendations
        if pattern_counts.get("god_class", 0) > 0:
            recommendations.append(
                "Break down large classes into smaller, focused components"
            )

        if pattern_counts.get("long_parameter_list", 0) > 0:
            recommendations.append(
                "Use parameter objects or builder pattern for methods with many parameters"
            )

        if pattern_counts.get("feature_envy", 0) > 0:
            recommendations.append("Move methods closer to the data they operate on")

        if pattern_counts.get("singleton", 0) > 3:
            recommendations.append(
                "Consider dependency injection instead of multiple singletons"
            )

        # General recommendations
        total_anti_patterns = sum(1 for m in matches if m.pattern_type == "anti")
        if total_anti_patterns > 5:
            recommendations.append(
                "Consider architectural refactoring to address code smells"
            )

        return recommendations[:5]  # Limit to top 5 recommendations


def main():
    """Command-line interface for pattern detection testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Test improved pattern detection")
    parser.add_argument("file_path", help="Path to file to analyze")
    parser.add_argument("--language", default="python", help="Programming language")

    args = parser.parse_args()

    detector = ImprovedPatternDetector()

    try:
        with open(args.file_path, "r", encoding="utf-8") as f:
            content = f.read()

        matches = detector.detect_patterns(content, args.file_path, args.language)

        if args.language == "python":
            ast_matches = detector.analyze_python_ast(content, args.file_path)
            matches.extend(ast_matches)

        summary = detector.get_pattern_summary(matches)

        print(f"Pattern Analysis Results: {args.file_path}")
        print("=" * 50)
        print(f"Total patterns detected: {summary['total_patterns']}")
        print(f"High confidence patterns: {len(summary['high_confidence_patterns'])}")

        print("\nDetected Patterns:")
        for match in matches:
            print(
                f"  {match.pattern_name} (line {match.line_number}, confidence: {match.confidence:.2f})"
            )
            print(f"    {match.description}")
            print(f"    Context: {match.context}")
            print()

        if summary["recommendations"]:
            print("Recommendations:")
            for rec in summary["recommendations"]:
                print(f"  • {rec}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
