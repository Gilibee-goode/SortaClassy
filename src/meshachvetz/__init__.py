"""
Meshachvetz - Student Class Assignment Optimizer

A comprehensive suite of tools for optimal student class assignment
based on social preferences, academic balance, and demographic distribution.
"""

__version__ = "0.1.0"
__author__ = "Meshachvetz Team"

from .data.models import Student, ClassData, SchoolData
from .data.loader import DataLoader
from .data.validator import DataValidator
from .scorer.main_scorer import Scorer, ScoringResult
from .scorer.student_scorer import StudentScorer
from .scorer.class_scorer import ClassScorer
from .scorer.school_scorer import SchoolScorer
from .utils.config import Config

__all__ = [
    "Student",
    "ClassData", 
    "SchoolData",
    "DataLoader",
    "DataValidator",
    "Scorer",
    "ScoringResult",
    "StudentScorer",
    "ClassScorer",
    "SchoolScorer",
    "Config"
] 