#!/usr/bin/env python3
"""
Validation utilities for Claude Code Workflows analysis scripts.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


def validate_target_directory(
    target_path: str,
) -> Tuple[bool, Optional[str], Optional[Path]]:
    """Validate target directory for analysis."""
    try:
        target_dir = Path(target_path).resolve()

        if not target_dir.exists():
            return False, f"Target directory does not exist: {target_path}", None

        if not target_dir.is_dir():
            return False, f"Target path is not a directory: {target_path}", None

        # Check if directory is accessible
        try:
            list(target_dir.iterdir())
        except PermissionError:
            return False, f"Permission denied accessing directory: {target_path}", None

        return True, None, target_dir

    except Exception as e:
        return False, f"Error validating directory: {str(e)}", None


def validate_git_repository(repo_path: Path) -> Tuple[bool, Optional[str]]:
    """Validate that directory is a git repository."""
    try:
        git_dir = repo_path / ".git"

        if not git_dir.exists():
            return False, "Directory is not a git repository (no .git directory found)"

        # Check if it's a valid git repository by testing basic commands
        import subprocess

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return False, "Invalid git repository (git rev-parse failed)"
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return False, "Git command failed or git not installed"

        return True, None

    except Exception as e:
        return False, f"Error validating git repository: {str(e)}"


def validate_file_access(
    file_path: Path, max_size_mb: int = 10
) -> Tuple[bool, Optional[str]]:
    """Validate file can be safely analyzed."""
    try:
        if not file_path.exists():
            return False, f"File does not exist: {file_path}"

        if not file_path.is_file():
            return False, f"Path is not a file: {file_path}"

        # Check file size
        try:
            file_size = file_path.stat().st_size
            max_size_bytes = max_size_mb * 1024 * 1024
            if file_size > max_size_bytes:
                return (
                    False,
                    f"File too large ({file_size / 1024 / 1024:.1f}MB > {max_size_mb}MB): {file_path}",
                )
        except OSError as e:
            return False, f"Cannot access file stats: {str(e)}"

        # Test read permissions
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                f.read(1)  # Try to read first byte
        except (PermissionError, OSError) as e:
            return False, f"Cannot read file: {str(e)}"

        return True, None

    except Exception as e:
        return False, f"Error validating file: {str(e)}"


def validate_environment_config() -> Dict[str, Any]:
    """Validate and return environment configuration."""
    config = {}

    # Parse integer environment variables with defaults and validation
    int_configs = {
        "MAX_FILES": (50, 1, 1000),
        "MAX_FILE_SIZE": (
            1048576,
            1024,
            100 * 1024 * 1024,
        ),  # 1MB default, 1KB min, 100MB max
        "DAYS_BACK": (30, 1, 365),
        "MAX_COMMITS": (50, 1, 500),
        "ANALYSIS_TIMEOUT": (
            300,
            10,
            3600,
        ),  # 5 minutes default, 10 sec min, 1 hour max
    }

    for key, (default, min_val, max_val) in int_configs.items():
        try:
            value = int(os.environ.get(key, default))
            if value < min_val:
                value = min_val
            elif value > max_val:
                value = max_val
            config[key] = value
        except ValueError:
            config[key] = default

    # Parse boolean environment variables
    bool_configs = {
        "ENABLE_DEBUG": False,
        "STRICT_VALIDATION": False,
        "SKIP_LARGE_FILES": True,
    }

    for key, default in bool_configs.items():
        config[key] = os.environ.get(key, "").lower() in ("true", "1", "yes", "on")

    return config


def create_safe_filename(name: str) -> str:
    """Create a safe filename from a string."""
    import re

    # Remove/replace unsafe characters
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    # Limit length
    if len(safe_name) > 100:
        safe_name = safe_name[:100]
    return safe_name


def log_debug(message: str, config: Dict[str, Any]):
    """Log debug message if debug is enabled."""
    if config.get("ENABLE_DEBUG", False):
        print(f"DEBUG: {message}", file=sys.stderr)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def require_valid_path(path_str: str, path_type: str = "path") -> Path:
    """Require a valid path or raise ValidationError."""
    is_valid, error_msg, validated_path = validate_target_directory(path_str)
    if not is_valid:
        raise ValidationError(f"Invalid {path_type}: {error_msg}")
    return validated_path


def require_git_repo(repo_path: Path) -> None:
    """Require a valid git repository or raise ValidationError."""
    is_valid, error_msg = validate_git_repository(repo_path)
    if not is_valid:
        raise ValidationError(f"Git repository validation failed: {error_msg}")
