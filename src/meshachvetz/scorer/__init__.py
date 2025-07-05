"""
Scorer layer for Meshachvetz - implements the three-layer scoring system.

This package contains:
- StudentScorer: Individual student satisfaction (friend placement, conflict avoidance)
- ClassScorer: Intra-class balance (gender balance)
- SchoolScorer: Inter-class balance (academic, behavior, size, assistance)
- Scorer: Main orchestrator that combines all layers
- ScoringResult: Data structure for scoring results
"""

from .student_scorer import StudentScorer
from .class_scorer import ClassScorer
from .school_scorer import SchoolScorer
from .main_scorer import Scorer, ScoringResult

__all__ = [
    "StudentScorer",
    "ClassScorer", 
    "SchoolScorer",
    "Scorer",
    "ScoringResult"
] 