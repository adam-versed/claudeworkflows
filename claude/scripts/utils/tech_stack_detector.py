#!/usr/bin/env python3
"""
Tech Stack Detection and Filtering Utility
Automatically detects project technology stack and provides appropriate filtering rules.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any
from dataclasses import dataclass


@dataclass
class TechStackConfig:
    """Configuration for a specific technology stack."""

    name: str
    primary_languages: Set[str]
    exclude_patterns: Set[str]
    dependency_dirs: Set[str]
    config_files: Set[str]
    source_patterns: Set[str]
    build_artifacts: Set[str]


class TechStackDetector:
    """Detects project technology stack and provides filtering rules."""

    def __init__(self):
        self.tech_stacks = {
            "react_native_expo": TechStackConfig(
                name="React Native with Expo",
                primary_languages={"javascript", "typescript", "jsx", "tsx"},
                exclude_patterns={
                    "node_modules/**/*",
                    "ios/Pods/**/*",
                    "android/build/**/*",
                    ".expo/**/*",
                    "web-build/**/*",
                    "dist/**/*",
                    ".next/**/*",
                    "coverage/**/*",
                    ".nyc_output/**/*",
                    "**/*.log",
                    "**/.DS_Store",
                    "**/Thumbs.db",
                },
                dependency_dirs={"node_modules", "ios/Pods", "android/build"},
                config_files={
                    "package.json",
                    "app.json",
                    "expo.json",
                    "metro.config.js",
                },
                source_patterns={
                    "app/**/*",
                    "src/**/*",
                    "components/**/*",
                    "screens/**/*",
                },
                build_artifacts={"dist", "build", "web-build", ".expo"},
            ),
            "node_js": TechStackConfig(
                name="Node.js",
                primary_languages={"javascript", "typescript"},
                exclude_patterns={
                    "node_modules/**/*",
                    "dist/**/*",
                    "build/**/*",
                    "coverage/**/*",
                    ".nyc_output/**/*",
                    "logs/**/*",
                    "*.log",
                    ".next/**/*",
                    ".nuxt/**/*",
                },
                dependency_dirs={"node_modules"},
                config_files={"package.json", "tsconfig.json", "webpack.config.js"},
                source_patterns={
                    "src/**/*",
                    "lib/**/*",
                    "routes/**/*",
                    "controllers/**/*",
                },
                build_artifacts={"dist", "build", "lib"},
            ),
            "python": TechStackConfig(
                name="Python",
                primary_languages={"python"},
                exclude_patterns={
                    "venv/**/*",
                    "env/**/*",
                    ".venv/**/*",
                    "__pycache__/**/*",
                    "*.pyc",
                    ".pytest_cache/**/*",
                    "dist/**/*",
                    "build/**/*",
                    "*.egg-info/**/*",
                    ".coverage",
                    "htmlcov/**/*",
                    ".tox/**/*",
                },
                dependency_dirs={"venv", "env", ".venv", "__pycache__"},
                config_files={
                    "requirements.txt",
                    "setup.py",
                    "pyproject.toml",
                    "Pipfile",
                },
                source_patterns={"src/**/*", "app/**/*", "lib/**/*", "**/*.py"},
                build_artifacts={"dist", "build", "*.egg-info"},
            ),
            "java_maven": TechStackConfig(
                name="Java with Maven",
                primary_languages={"java"},
                exclude_patterns={
                    "target/**/*",
                    ".m2/**/*",
                    "*.class",
                    "*.jar",
                    "*.war",
                    "logs/**/*",
                    ".idea/**/*",
                    ".vscode/**/*",
                },
                dependency_dirs={"target", ".m2"},
                config_files={"pom.xml", "maven-wrapper.properties"},
                source_patterns={"src/main/**/*", "src/test/**/*"},
                build_artifacts={"target"},
            ),
            "java_gradle": TechStackConfig(
                name="Java with Gradle",
                primary_languages={"java", "kotlin"},
                exclude_patterns={
                    "build/**/*",
                    ".gradle/**/*",
                    "*.class",
                    "*.jar",
                    "*.war",
                    "logs/**/*",
                    ".idea/**/*",
                    ".vscode/**/*",
                },
                dependency_dirs={"build", ".gradle"},
                config_files={"build.gradle", "gradle.properties", "settings.gradle"},
                source_patterns={"src/main/**/*", "src/test/**/*"},
                build_artifacts={"build"},
            ),
            "dotnet": TechStackConfig(
                name=".NET",
                primary_languages={"csharp"},
                exclude_patterns={
                    "bin/**/*",
                    "obj/**/*",
                    "packages/**/*",
                    "*.dll",
                    "*.exe",
                    "*.pdb",
                    ".vs/**/*",
                    "TestResults/**/*",
                },
                dependency_dirs={"bin", "obj", "packages"},
                config_files={"*.csproj", "*.sln", "packages.config", "project.json"},
                source_patterns={
                    "**/*.cs",
                    "Controllers/**/*",
                    "Models/**/*",
                    "Views/**/*",
                },
                build_artifacts={"bin", "obj"},
            ),
            "go": TechStackConfig(
                name="Go",
                primary_languages={"go"},
                exclude_patterns={
                    "vendor/**/*",
                    "bin/**/*",
                    "*.exe",
                    ".idea/**/*",
                    ".vscode/**/*",
                },
                dependency_dirs={"vendor", "bin"},
                config_files={"go.mod", "go.sum"},
                source_patterns={"**/*.go", "cmd/**/*", "pkg/**/*", "internal/**/*"},
                build_artifacts={"bin"},
            ),
            "rust": TechStackConfig(
                name="Rust",
                primary_languages={"rust"},
                exclude_patterns={
                    "target/**/*",
                    "Cargo.lock",
                    ".idea/**/*",
                    ".vscode/**/*",
                },
                dependency_dirs={"target"},
                config_files={"Cargo.toml"},
                source_patterns={"src/**/*", "**/*.rs"},
                build_artifacts={"target"},
            ),
            "php": TechStackConfig(
                name="PHP",
                primary_languages={"php"},
                exclude_patterns={
                    "vendor/**/*",
                    "composer.lock",
                    ".phpunit.cache/**/*",
                    "coverage/**/*",
                },
                dependency_dirs={"vendor"},
                config_files={"composer.json", "composer.lock"},
                source_patterns={"**/*.php", "src/**/*", "app/**/*"},
                build_artifacts={"vendor"},
            ),
            "ruby": TechStackConfig(
                name="Ruby",
                primary_languages={"ruby"},
                exclude_patterns={
                    "vendor/**/*",
                    ".bundle/**/*",
                    "coverage/**/*",
                    "log/**/*",
                    "tmp/**/*",
                },
                dependency_dirs={"vendor", ".bundle"},
                config_files={"Gemfile", "Gemfile.lock"},
                source_patterns={"**/*.rb", "app/**/*", "lib/**/*"},
                build_artifacts={"vendor"},
            ),
            "cpp": TechStackConfig(
                name="C/C++",
                primary_languages={"cpp", "c"},
                exclude_patterns={
                    "build/**/*",
                    "cmake-build-*/**/*",
                    "*.o",
                    "*.exe",
                    "*.out",
                    ".vscode/**/*",
                    ".idea/**/*",
                },
                dependency_dirs={"build", "cmake-build-debug", "cmake-build-release"},
                config_files={"CMakeLists.txt", "Makefile", "*.vcxproj"},
                source_patterns={
                    "**/*.cpp",
                    "**/*.c",
                    "**/*.h",
                    "**/*.hpp",
                    "src/**/*",
                },
                build_artifacts={"build"},
            ),
            "swift": TechStackConfig(
                name="Swift",
                primary_languages={"swift"},
                exclude_patterns={
                    ".build/**/*",
                    "build/**/*",
                    "DerivedData/**/*",
                    "*.xcworkspace/**/*",
                    "*.xcodeproj/**/*",
                },
                dependency_dirs={".build", "build", "DerivedData"},
                config_files={"Package.swift", "*.xcodeproj", "*.xcworkspace"},
                source_patterns={"**/*.swift", "Sources/**/*"},
                build_artifacts={".build", "build"},
            ),
            "kotlin": TechStackConfig(
                name="Kotlin",
                primary_languages={"kotlin"},
                exclude_patterns={
                    "build/**/*",
                    ".gradle/**/*",
                    "*.class",
                    "*.jar",
                    ".idea/**/*",
                },
                dependency_dirs={"build", ".gradle"},
                config_files={"build.gradle.kts", "settings.gradle.kts"},
                source_patterns={"**/*.kt", "src/**/*"},
                build_artifacts={"build"},
            ),
        }

    def detect_tech_stack(self, project_path: str) -> List[str]:
        """
        Detect technology stacks in the project.

        Args:
            project_path: Path to the project root

        Returns:
            List of detected technology stack names
        """
        detected_stacks = []
        project_root = Path(project_path)

        # Check for each tech stack
        for stack_id, config in self.tech_stacks.items():
            if self._matches_tech_stack(project_root, config):
                detected_stacks.append(stack_id)

        return detected_stacks

    def _matches_tech_stack(self, project_root: Path, config: TechStackConfig) -> bool:
        """Check if project matches a specific tech stack."""
        config_file_matches = 0

        # Check for config files
        for config_file in config.config_files:
            if self._file_exists_pattern(project_root, config_file):
                config_file_matches += 1

        # If multiple config files match, it's likely this tech stack
        return config_file_matches > 0

    def _file_exists_pattern(self, project_root: Path, pattern: str) -> bool:
        """Check if files matching pattern exist."""
        if "*" in pattern:
            # Handle glob patterns
            try:
                matches = list(project_root.glob(pattern))
                return len(matches) > 0
            except Exception:
                return False
        else:
            # Direct file check
            return (project_root / pattern).exists()

    def get_exclusion_patterns(self, project_path: str) -> Set[str]:
        """
        Get exclusion patterns for detected tech stacks.

        Args:
            project_path: Path to the project root

        Returns:
            Set of exclusion patterns to apply
        """
        detected_stacks = self.detect_tech_stack(project_path)

        # Universal exclusions (always apply)
        universal_exclusions = {
            ".git/**/*",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*.log",
            "**/logs/**/*",
            "**/.env",
            "**/.env.*",
            "**/coverage/**/*",
            "**/.coverage",
            "**/htmlcov/**/*",
            "**/.idea/**/*",
            "**/.vscode/**/*",
            "**/tmp/**/*",
            "**/temp/**/*",
        }

        # Combine exclusions from detected stacks
        all_exclusions = universal_exclusions.copy()
        for stack_id in detected_stacks:
            if stack_id in self.tech_stacks:
                all_exclusions.update(self.tech_stacks[stack_id].exclude_patterns)

        return all_exclusions

    def get_source_patterns(self, project_path: str) -> Set[str]:
        """
        Get source code patterns for detected tech stacks.

        Args:
            project_path: Path to the project root

        Returns:
            Set of source patterns to analyze
        """
        detected_stacks = self.detect_tech_stack(project_path)

        # Universal source patterns - aligned with documented supported languages
        universal_sources = {
            "**/*.py",  # Python
            "**/*.js",  # JavaScript
            "**/*.jsx",  # JavaScript
            "**/*.ts",  # TypeScript
            "**/*.tsx",  # TypeScript
            "**/*.java",  # Java
            "**/*.cs",  # C#
            "**/*.go",  # Go
            "**/*.rs",  # Rust
            "**/*.php",  # PHP
            "**/*.rb",  # Ruby
            "**/*.swift",  # Swift
            "**/*.kt",  # Kotlin
            "**/*.scala",  # Scala
            "**/*.cpp",  # C++
            "**/*.cc",  # C++
            "**/*.cxx",  # C++
            "**/*.c",  # C
            "**/*.h",  # C/C++
            "**/*.hpp",  # C++
        }

        # Combine sources from detected stacks
        all_sources = universal_sources.copy()
        for stack_id in detected_stacks:
            if stack_id in self.tech_stacks:
                all_sources.update(self.tech_stacks[stack_id].source_patterns)

        return all_sources

    def get_analysis_report(self, project_path: str) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis report.

        Args:
            project_path: Path to the project root

        Returns:
            Analysis report with detected stacks and recommendations
        """
        detected_stacks = self.detect_tech_stack(project_path)
        exclusions = self.get_exclusion_patterns(project_path)
        sources = self.get_source_patterns(project_path)

        # Generate statistics
        project_root = Path(project_path)
        total_files = len(list(project_root.rglob("*"))) if project_root.exists() else 0

        # Estimate filtered files
        filtered_files = 0
        for source_pattern in sources:
            try:
                filtered_files += len(list(project_root.glob(source_pattern)))
            except Exception:
                continue

        return {
            "project_path": project_path,
            "detected_tech_stacks": [
                {
                    "id": stack_id,
                    "name": self.tech_stacks[stack_id].name,
                    "primary_languages": list(
                        self.tech_stacks[stack_id].primary_languages
                    ),
                }
                for stack_id in detected_stacks
            ],
            "filtering_rules": {
                "exclusion_patterns": sorted(list(exclusions)),
                "source_patterns": sorted(list(sources)),
                "total_exclusions": len(exclusions),
                "total_source_patterns": len(sources),
            },
            "file_statistics": {
                "total_files_in_project": total_files,
                "estimated_files_to_analyze": filtered_files,
                "estimated_filtering_ratio": round(
                    (1 - filtered_files / max(total_files, 1)) * 100, 1
                ),
            },
            "supported_languages": [
                "Python",
                "JavaScript",
                "TypeScript",
                "Java",
                "C#",
                "Go",
                "Rust",
                "PHP",
                "Ruby",
                "C/C++",
                "Swift",
                "Kotlin",
            ],
        }


def main():
    """Command-line interface for tech stack detection."""
    import argparse

    parser = argparse.ArgumentParser(description="Detect project technology stack")
    parser.add_argument("project_path", help="Path to project root")
    parser.add_argument(
        "--format", choices=["json", "report"], default="report", help="Output format"
    )

    args = parser.parse_args()

    detector = TechStackDetector()

    if args.format == "json":
        result = detector.get_analysis_report(args.project_path)
        print(json.dumps(result, indent=2))
    else:
        # Human-readable report
        report = detector.get_analysis_report(args.project_path)

        print(f"Tech Stack Analysis: {args.project_path}")
        print("=" * 50)

        print("\nDetected Tech Stacks:")
        for stack in report["detected_tech_stacks"]:
            print(f"  • {stack['name']} ({', '.join(stack['primary_languages'])})")

        print("\nFiltering Rules:")
        print(f"  • {report['filtering_rules']['total_exclusions']} exclusion patterns")
        print(
            f"  • {report['filtering_rules']['total_source_patterns']} source patterns"
        )

        print("\nFile Statistics:")
        print(f"  • Total files: {report['file_statistics']['total_files_in_project']}")
        print(
            f"  • Files to analyze: {report['file_statistics']['estimated_files_to_analyze']}"
        )
        print(
            f"  • Filtering ratio: {report['file_statistics']['estimated_filtering_ratio']}%"
        )

        if not report["detected_tech_stacks"]:
            print("\n⚠️  No specific tech stack detected. Using universal patterns.")


if __name__ == "__main__":
    main()
