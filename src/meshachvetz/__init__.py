"""
Meshachvetz - Student Class Assignment Optimizer

A comprehensive suite of tools for optimal student class assignment
based on social preferences, academic balance, and demographic distribution.

Phase 1: Complete scoring system with three-layer architecture
Phase 2: Optimization algorithms for creating improved assignments
"""

__version__ = "0.2.0"
__author__ = "Meshachvetz Team"

from .data.models import Student, ClassData, SchoolData
from .data.loader import DataLoader
from .data.validator import DataValidator
from .scorer.main_scorer import Scorer, ScoringResult
from .scorer.student_scorer import StudentScorer
from .scorer.class_scorer import ClassScorer
from .scorer.school_scorer import SchoolScorer
from .utils.config import Config

# Phase 2: Optimizer components
from .optimizer.base_optimizer import BaseOptimizer, OptimizationResult
from .optimizer.random_swap import RandomSwapOptimizer
from .optimizer.optimization_manager import OptimizationManager

__all__ = [
    # Data components
    "Student",
    "ClassData", 
    "SchoolData",
    "DataLoader",
    "DataValidator",
    # Scorer components
    "Scorer",
    "ScoringResult",
    "StudentScorer",
    "ClassScorer",
    "SchoolScorer",
    # Configuration
    "Config",
    # Optimizer components
    "BaseOptimizer",
    "OptimizationResult",
    "RandomSwapOptimizer",
    "OptimizationManager"
] 