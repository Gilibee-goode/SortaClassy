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

__all__ = [
    "Student",
    "ClassData", 
    "SchoolData",
    "DataLoader",
    "DataValidator",
] 