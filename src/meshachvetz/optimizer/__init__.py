#!/usr/bin/env python3
"""
Optimizer package for Meshachvetz - contains optimization algorithms and management.
"""

from .base_optimizer import BaseOptimizer, OptimizationResult
from .random_swap import RandomSwapOptimizer
from .local_search import LocalSearchOptimizer
from .simulated_annealing import SimulatedAnnealingOptimizer
from .genetic import GeneticOptimizer
from .optimization_manager import OptimizationManager, AssignmentStatus, InitializationStrategy

__all__ = [
    'BaseOptimizer',
    'OptimizationResult',
    'RandomSwapOptimizer',
    'LocalSearchOptimizer',
    'SimulatedAnnealingOptimizer',
    'GeneticOptimizer',
    'OptimizationManager',
    'AssignmentStatus',
    'InitializationStrategy'
]

__version__ = "1.0.0" 