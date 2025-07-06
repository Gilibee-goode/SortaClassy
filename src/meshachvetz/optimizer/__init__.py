#!/usr/bin/env python3
"""
Meshachvetz Optimizer Package - Student assignment optimization algorithms and management.

This package provides optimization algorithms for improving student class assignments
based on the three-layer scoring system. It includes various optimization strategies
and a unified management interface.
"""

from .base_optimizer import BaseOptimizer, OptimizationResult
from .random_swap import RandomSwapOptimizer
from .optimization_manager import OptimizationManager

__all__ = [
    'BaseOptimizer',
    'OptimizationResult', 
    'RandomSwapOptimizer',
    'OptimizationManager'
]

__version__ = "1.0.0" 