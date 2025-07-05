"""
Command-line interface for Meshachvetz - Student Class Assignment Optimizer.

This package provides CLI tools for:
- Scoring student assignments
- Validating student data
- Configuration management
"""

from .main import main as main_cli
from .scorer_cli import main as scorer_cli

__all__ = [
    "main_cli",
    "scorer_cli"
] 