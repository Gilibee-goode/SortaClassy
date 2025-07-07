#!/usr/bin/env python3
"""
Optimizer package for Meshachvetz - contains optimization algorithms and management.
"""

from .base_optimizer import BaseOptimizer, OptimizationResult
from .random_swap import RandomSwapOptimizer
from .local_search import LocalSearchOptimizer
from .simulated_annealing import SimulatedAnnealingOptimizer
from .genetic import GeneticOptimizer
from .or_tools_optimizer import ORToolsOptimizer
from .optimization_manager import OptimizationManager, AssignmentStatus, InitializationStrategy
from .baseline_generator import BaselineGenerator, BaselineStatistics, BaselineRun

__all__ = [
    'BaseOptimizer',
    'OptimizationResult',
    'RandomSwapOptimizer',
    'LocalSearchOptimizer',
    'SimulatedAnnealingOptimizer',
    'GeneticOptimizer',
    'ORToolsOptimizer',
    'OptimizationManager',
    'AssignmentStatus',
    'InitializationStrategy',
    'BaselineGenerator',
    'BaselineStatistics',
    'BaselineRun'
]

__version__ = "1.0.0" 