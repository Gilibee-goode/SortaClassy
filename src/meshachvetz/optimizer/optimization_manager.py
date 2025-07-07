#!/usr/bin/env python3
"""
Optimization Manager for Meshachvetz - Coordinates different optimization algorithms
and provides a unified interface for student assignment optimization.
"""

import logging
import os
import copy
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import csv
from enum import Enum

from .base_optimizer import BaseOptimizer, OptimizationResult
from .random_swap import RandomSwapOptimizer
from .local_search import LocalSearchOptimizer
from .simulated_annealing import SimulatedAnnealingOptimizer
from .genetic import GeneticOptimizer
from ..data.models import SchoolData, Student, ClassData
from ..scorer.main_scorer import Scorer


class AssignmentStatus(Enum):
    """Enum for different assignment status types."""
    FULLY_ASSIGNED = "fully_assigned"
    PARTIALLY_ASSIGNED = "partially_assigned"
    UNASSIGNED = "unassigned"
    MIXED_ASSIGNMENT = "mixed_assignment"


class InitializationStrategy(Enum):
    """Enum for different initialization strategies."""
    RANDOM = "random"
    BALANCED = "balanced"
    CONSTRAINT_AWARE = "constraint_aware"
    ACADEMIC_BALANCED = "academic_balanced"


class OptimizationManager:
    """
    Manages optimization algorithms and provides a unified interface
    for optimizing student class assignments.
    """
    
    def __init__(self, scorer: Scorer, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the optimization manager.
        
        Args:
            scorer: Scorer instance for evaluating solutions
            config: Configuration dictionary for optimization parameters
        """
        self.scorer = scorer
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Available algorithms
        self.algorithms = {}
        self._register_algorithms()
        
        # Default optimization parameters
        self.default_max_iterations = self.config.get('max_iterations', 1000)
        self.default_algorithm = self.config.get('default_algorithm', 'local_search')
        
    def _register_algorithms(self) -> None:
        """Register available optimization algorithms."""
        self.algorithms = {
            'random_swap': RandomSwapOptimizer,
            'local_search': LocalSearchOptimizer,
            'simulated_annealing': SimulatedAnnealingOptimizer,
            'genetic': GeneticOptimizer,
            # Future algorithms:
            # 'or_tools': ORToolsOptimizer
        }
    
    def get_available_algorithms(self) -> List[str]:
        """
        Get list of available optimization algorithms.
        
        Returns:
            List of algorithm names
        """
        return list(self.algorithms.keys())
    
    def optimize(self, school_data: SchoolData, 
                algorithm: str = None,
                max_iterations: int = None,
                algorithm_config: Optional[Dict[str, Any]] = None,
                initialization_strategy: str = "constraint_aware",
                auto_initialize: bool = True,
                target_classes: Optional[int] = None) -> OptimizationResult:
        """
        Optimize student assignments using the specified algorithm.
        
        Args:
            school_data: Initial school data to optimize
            algorithm: Name of optimization algorithm to use
            max_iterations: Maximum number of optimization iterations
            algorithm_config: Algorithm-specific configuration
            initialization_strategy: Strategy for initializing unassigned students
            auto_initialize: Whether to automatically initialize unassigned students
            target_classes: Number of target classes for initialization (auto-calculated if None)
            
        Returns:
            OptimizationResult with optimized assignment and metrics
        """
        # Use defaults if not specified
        algorithm = algorithm or self.default_algorithm
        max_iterations = max_iterations or self.default_max_iterations
        algorithm_config = algorithm_config or {}
        
        # Merge configurations
        merged_config = self.config.copy()
        merged_config.update(algorithm_config)
        
        # Validate algorithm
        if algorithm not in self.algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}. Available: {list(self.algorithms.keys())}")
        
        # Detect assignment status and initialize if needed
        assignment_status, unassigned_count = self.detect_assignment_status(school_data)
        
        self.logger.info(f"Assignment status: {assignment_status.value}")
        if unassigned_count > 0:
            self.logger.info(f"Found {unassigned_count} unassigned students")
            
        # Initialize if needed
        if auto_initialize and assignment_status != AssignmentStatus.FULLY_ASSIGNED:
            self.logger.info(f"Initializing assignments using {initialization_strategy} strategy")
            school_data = self.initialize_assignments(
                school_data, 
                InitializationStrategy(initialization_strategy),
                target_classes
            )
        
        self.logger.info(f"Starting optimization with {algorithm} algorithm")
        self.logger.info(f"Max iterations: {max_iterations}")
        self.logger.info(f"Configuration: {merged_config}")
        
        # Create optimizer instance
        optimizer_class = self.algorithms[algorithm]
        optimizer = optimizer_class(self.scorer, merged_config)
        
        # Run optimization
        try:
            result = optimizer.optimize(school_data, max_iterations)
            
            self.logger.info(f"Optimization completed successfully")
            self.logger.info(f"Score improvement: {result.initial_score:.2f} -> {result.final_score:.2f} "
                           f"(+{result.improvement:.2f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Optimization failed: {e}")
            raise
    
    def detect_assignment_status(self, school_data: SchoolData) -> Tuple[AssignmentStatus, int]:
        """
        Detect the current assignment status of students.
        
        Args:
            school_data: School data to analyze
            
        Returns:
            Tuple of (assignment_status, unassigned_count)
        """
        assigned_students = 0
        unassigned_students = 0
        
        for student in school_data.students.values():
            if student.class_id and student.class_id.strip():
                assigned_students += 1
            else:
                unassigned_students += 1
        
        total_students = assigned_students + unassigned_students
        
        if unassigned_students == 0:
            return AssignmentStatus.FULLY_ASSIGNED, 0
        elif assigned_students == 0:
            return AssignmentStatus.UNASSIGNED, unassigned_students
        else:
            return AssignmentStatus.PARTIALLY_ASSIGNED, unassigned_students
    
    def initialize_assignments(self, school_data: SchoolData, 
                             strategy: InitializationStrategy = InitializationStrategy.CONSTRAINT_AWARE,
                             target_classes: Optional[int] = None) -> SchoolData:
        """
        Initialize student assignments using the specified strategy.
        
        Args:
            school_data: School data with unassigned students
            strategy: Initialization strategy to use
            target_classes: Number of target classes (auto-calculated if None)
            
        Returns:
            SchoolData with initialized assignments
        """
        
        # Create a working copy
        initialized_data = copy.deepcopy(school_data)
        
        # Determine target classes
        if target_classes is None:
            target_classes = self._calculate_target_classes(initialized_data)
        
        self.logger.info(f"Initializing assignments with {target_classes} target classes")
        
        # Apply initialization strategy
        if strategy == InitializationStrategy.RANDOM:
            initialized_data = self._random_initialization(initialized_data, target_classes)
        elif strategy == InitializationStrategy.BALANCED:
            initialized_data = self._balanced_initialization(initialized_data, target_classes)
        elif strategy == InitializationStrategy.CONSTRAINT_AWARE:
            initialized_data = self._constraint_aware_initialization(initialized_data, target_classes)
        elif strategy == InitializationStrategy.ACADEMIC_BALANCED:
            initialized_data = self._academic_balanced_initialization(initialized_data, target_classes)
        else:
            raise ValueError(f"Unknown initialization strategy: {strategy}")
        
        # Validate the initialized assignment
        self._validate_initialization(initialized_data)
        
        return initialized_data
    
    def _calculate_target_classes(self, school_data: SchoolData) -> int:
        """Calculate optimal number of target classes based on student count."""
        total_students = school_data.total_students
        
        # If there are already classes with students, use that count
        existing_classes = len([cls for cls in school_data.classes.values() if cls.size > 0])
        if existing_classes > 0:
            return existing_classes
        
        # Otherwise, calculate based on student count (aim for 20-30 students per class)
        if total_students <= 25:
            return 1
        elif total_students <= 50:
            return 2
        elif total_students <= 75:
            return 3
        elif total_students <= 100:
            return 4
        else:
            return max(4, min(8, (total_students + 24) // 25))  # 25 students per class average
    
    def _random_initialization(self, school_data: SchoolData, target_classes: int) -> SchoolData:
        """Initialize assignments randomly."""
        import random
        
        # Create class IDs
        class_ids = [f"Class_{i+1}" for i in range(target_classes)]
        
        # Initialize empty classes
        school_data.classes = {class_id: ClassData(class_id, []) for class_id in class_ids}
        
        # Get unassigned students
        unassigned_students = [s for s in school_data.students.values() 
                             if not s.class_id or not s.class_id.strip()]
        
        # Handle force_class constraints first
        for student in unassigned_students:
            if student.force_class and student.force_class.strip():
                force_class = student.force_class.strip()
                if force_class in school_data.classes:
                    student.class_id = force_class
                    school_data.classes[force_class].students.append(student)
                else:
                    self.logger.warning(f"Force class {force_class} not found for student {student.student_id}")
        
        # Assign remaining unassigned students randomly
        still_unassigned = [s for s in unassigned_students 
                          if not s.class_id or not s.class_id.strip()]
        
        for student in still_unassigned:
            student.class_id = random.choice(class_ids)
            school_data.classes[student.class_id].students.append(student)
        
        return school_data
    
    def _balanced_initialization(self, school_data: SchoolData, target_classes: int) -> SchoolData:
        """Initialize assignments with balanced class sizes."""
        import random
        
        # Create class IDs
        class_ids = [f"Class_{i+1}" for i in range(target_classes)]
        
        # Initialize empty classes
        school_data.classes = {class_id: ClassData(class_id, []) for class_id in class_ids}
        
        # Get unassigned students
        unassigned_students = [s for s in school_data.students.values() 
                             if not s.class_id or not s.class_id.strip()]
        
        # Handle force_class constraints first
        for student in unassigned_students:
            if student.force_class and student.force_class.strip():
                force_class = student.force_class.strip()
                if force_class in school_data.classes:
                    student.class_id = force_class
                    school_data.classes[force_class].students.append(student)
        
        # Get remaining unassigned students
        still_unassigned = [s for s in unassigned_students 
                          if not s.class_id or not s.class_id.strip()]
        
        # Shuffle for random distribution within balanced approach
        random.shuffle(still_unassigned)
        
        # Assign students in round-robin fashion for balanced classes
        for i, student in enumerate(still_unassigned):
            class_id = class_ids[i % target_classes]
            student.class_id = class_id
            school_data.classes[class_id].students.append(student)
        
        return school_data
    
    def _constraint_aware_initialization(self, school_data: SchoolData, target_classes: int) -> SchoolData:
        """Initialize assignments with awareness of constraints and preferences."""
        import random
        
        # Create class IDs
        class_ids = [f"Class_{i+1}" for i in range(target_classes)]
        
        # Initialize empty classes
        school_data.classes = {class_id: ClassData(class_id, []) for class_id in class_ids}
        
        # Get unassigned students
        unassigned_students = [s for s in school_data.students.values() 
                             if not s.class_id or not s.class_id.strip()]
        
        # Phase 1: Handle force_class constraints
        for student in unassigned_students:
            if student.force_class and student.force_class.strip():
                force_class = student.force_class.strip()
                if force_class in school_data.classes:
                    student.class_id = force_class
                    school_data.classes[force_class].students.append(student)
        
        # Phase 2: Handle force_friend groups
        processed_groups = set()
        for student in unassigned_students:
            if (student.force_friend and student.force_friend.strip() and 
                student.force_friend not in processed_groups):
                
                force_group = student.force_friend.strip()
                group_members = [s for s in unassigned_students 
                               if s.force_friend == force_group and 
                               (not s.class_id or not s.class_id.strip())]
                
                if group_members:
                    # Assign entire group to same class
                    target_class = random.choice(class_ids)
                    for member in group_members:
                        member.class_id = target_class
                        school_data.classes[target_class].students.append(member)
                    
                    processed_groups.add(force_group)
        
        # Phase 3: Assign remaining students with balanced distribution
        still_unassigned = [s for s in unassigned_students 
                          if not s.class_id or not s.class_id.strip()]
        
        random.shuffle(still_unassigned)
        
        # Assign remaining students in round-robin fashion
        for i, student in enumerate(still_unassigned):
            class_id = class_ids[i % target_classes]
            student.class_id = class_id
            school_data.classes[class_id].students.append(student)
        
        return school_data
    
    def _academic_balanced_initialization(self, school_data: SchoolData, target_classes: int) -> SchoolData:
        """Initialize assignments with academic balance across classes."""
        import random
        
        # Create class IDs
        class_ids = [f"Class_{i+1}" for i in range(target_classes)]
        
        # Initialize empty classes
        school_data.classes = {class_id: ClassData(class_id, []) for class_id in class_ids}
        
        # Get unassigned students
        unassigned_students = [s for s in school_data.students.values() 
                             if not s.class_id or not s.class_id.strip()]
        
        # Handle force constraints first (same as constraint_aware)
        for student in unassigned_students:
            if student.force_class and student.force_class.strip():
                force_class = student.force_class.strip()
                if force_class in school_data.classes:
                    student.class_id = force_class
                    school_data.classes[force_class].students.append(student)
        
        # Get remaining unassigned students
        still_unassigned = [s for s in unassigned_students 
                          if not s.class_id or not s.class_id.strip()]
        
        # Sort by academic score for balanced distribution
        still_unassigned.sort(key=lambda s: s.academic_score, reverse=True)
        
        # Assign students in round-robin fashion to balance academic scores
        for i, student in enumerate(still_unassigned):
            class_id = class_ids[i % target_classes]
            student.class_id = class_id
            school_data.classes[class_id].students.append(student)
        
        return school_data
    
    def _validate_initialization(self, school_data: SchoolData) -> None:
        """Validate that initialization was successful."""
        unassigned_students = [s for s in school_data.students.values() 
                             if not s.class_id or not s.class_id.strip()]
        
        if unassigned_students:
            raise ValueError(f"Initialization failed: {len(unassigned_students)} students remain unassigned")
        
        # Check that all students are in their assigned classes
        for student in school_data.students.values():
            if student.class_id not in school_data.classes:
                raise ValueError(f"Student {student.student_id} assigned to non-existent class {student.class_id}")
            
            if student not in school_data.classes[student.class_id].students:
                raise ValueError(f"Student {student.student_id} not found in their assigned class {student.class_id}")
        
        self.logger.info("Initialization validation successful")
    
    def get_assignment_summary(self, school_data: SchoolData) -> Dict[str, Any]:
        """
        Get a summary of current assignment status.
        
        Args:
            school_data: School data to analyze
            
        Returns:
            Dictionary with assignment summary
        """
        status, unassigned_count = self.detect_assignment_status(school_data)
        
        summary = {
            'assignment_status': status.value,
            'total_students': school_data.total_students,
            'assigned_students': school_data.total_students - unassigned_count,
            'unassigned_students': unassigned_count,
            'total_classes': school_data.total_classes,
            'classes_with_students': len([cls for cls in school_data.classes.values() if cls.size > 0]),
            'class_sizes': school_data.class_sizes,
            'force_class_constraints': len([s for s in school_data.students.values() 
                                          if s.force_class and s.force_class.strip()]),
            'force_friend_groups': len(set([s.force_friend for s in school_data.students.values() 
                                          if s.force_friend and s.force_friend.strip()]))
        }
        
        return summary
    
    def optimize_with_multiple_algorithms(self, school_data: SchoolData,
                                        algorithms: List[str] = None,
                                        max_iterations: int = None,
                                        strategy: str = "best_of") -> Dict[str, OptimizationResult]:
        """
        Run optimization with multiple algorithms and compare results.
        
        Args:
            school_data: Initial school data to optimize
            algorithms: List of algorithm names to try
            max_iterations: Maximum iterations per algorithm
            strategy: Multi-algorithm strategy ('parallel', 'sequential', 'best_of')
            
        Returns:
            Dictionary mapping algorithm names to their results
        """
        algorithms = algorithms or ['local_search', 'simulated_annealing', 'genetic']
        
        # Filter to only available algorithms
        available_algorithms = [alg for alg in algorithms if alg in self.algorithms]
        
        if not available_algorithms:
            raise ValueError(f"No valid algorithms provided. Available: {list(self.algorithms.keys())}")
        
        self.logger.info(f"Running {strategy} strategy with algorithms: {available_algorithms}")
        
        if strategy == "sequential":
            return self._sequential_optimization(school_data, available_algorithms, max_iterations)
        elif strategy == "parallel":
            return self._parallel_optimization(school_data, available_algorithms, max_iterations)
        elif strategy == "best_of":
            return self._best_of_optimization(school_data, available_algorithms, max_iterations)
        else:
            raise ValueError(f"Unknown multi-algorithm strategy: {strategy}")
    
    def _sequential_optimization(self, school_data: SchoolData, algorithms: List[str], 
                               max_iterations: int = None) -> Dict[str, OptimizationResult]:
        """
        Run algorithms sequentially, using output of one as input to the next.
        
        Args:
            school_data: Initial school data
            algorithms: List of algorithms to run in sequence
            max_iterations: Maximum iterations per algorithm
            
        Returns:
            Dictionary of results from each algorithm
        """
        results = {}
        current_solution = copy.deepcopy(school_data)
        
        # Distribute iterations among algorithms
        iterations_per_algorithm = (max_iterations or 1000) // len(algorithms)
        
        for i, algorithm in enumerate(algorithms):
            self.logger.info(f"Running sequential step {i+1}/{len(algorithms)}: {algorithm}")
            
            result = self.optimize(
                school_data=current_solution,
                algorithm=algorithm,
                max_iterations=iterations_per_algorithm,
                auto_initialize=False  # Don't re-initialize between algorithms
            )
            
            results[f"{algorithm}_step_{i+1}"] = result
            current_solution = result.optimized_school_data
            
            self.logger.info(f"{algorithm} completed: score {result.final_score:.2f}")
        
        # Add a final combined result
        final_result = copy.deepcopy(results[f"{algorithms[-1]}_step_{len(algorithms)}"])
        final_result.algorithm_name = f"Sequential: {' → '.join(algorithms)}"
        results['sequential_combined'] = final_result
        
        return results
    
    def _parallel_optimization(self, school_data: SchoolData, algorithms: List[str], 
                             max_iterations: int = None) -> Dict[str, OptimizationResult]:
        """
        Run multiple algorithms in parallel on identical copies of the data.
        
        Args:
            school_data: Initial school data
            algorithms: List of algorithms to run in parallel
            max_iterations: Maximum iterations per algorithm
            
        Returns:
            Dictionary of results from each algorithm
        """
        results = {}
        
        # Get initial score for fair comparison validation
        initial_score = self.scorer.calculate_scores(school_data).final_score
        self.logger.info(f"🏁 Fair comparison: All {len(algorithms)} algorithms starting from score {initial_score:.2f}")
        
        for algorithm in algorithms:
            self.logger.info(f"Running parallel algorithm: {algorithm}")
            
            try:
                # Create identical copy for fair comparison
                algorithm_data = copy.deepcopy(school_data)
                
                # Verify the copy has the same score
                copy_score = self.scorer.calculate_scores(algorithm_data).final_score
                if abs(copy_score - initial_score) > 0.001:
                    self.logger.warning(f"⚠️  Score mismatch: {algorithm} starting with {copy_score:.2f} instead of {initial_score:.2f}")
                else:
                    self.logger.debug(f"✅ {algorithm} starting with correct score: {copy_score:.2f}")
                
                result = self.optimize(
                    school_data=algorithm_data,
                    algorithm=algorithm,
                    max_iterations=max_iterations,
                    auto_initialize=False  # Assume data is already initialized
                )
                
                results[algorithm] = result
                
                self.logger.info(f"{algorithm} completed: "
                               f"score {result.final_score:.2f} "
                               f"(+{result.improvement:.2f}) "
                               f"in {result.execution_time:.2f}s")
                
            except Exception as e:
                self.logger.error(f"Algorithm {algorithm} failed: {e}")
                # Continue with other algorithms
        
        return results
    
    def _best_of_optimization(self, school_data: SchoolData, algorithms: List[str], 
                            max_iterations: int = None) -> Dict[str, OptimizationResult]:
        """
        Run algorithms in parallel and return the best result.
        
        Args:
            school_data: Initial school data
            algorithms: List of algorithms to run
            max_iterations: Maximum iterations per algorithm
            
        Returns:
            Dictionary with the best result and comparison data
        """
        # Run all algorithms in parallel
        all_results = self._parallel_optimization(school_data, algorithms, max_iterations)
        
        if not all_results:
            raise ValueError("No algorithms succeeded")
            
        # Log fair comparison summary
        initial_score = self.scorer.calculate_scores(school_data).final_score
        self.logger.info(f"🏁 Fair comparison summary:")
        self.logger.info(f"   All {len(algorithms)} algorithms started from score {initial_score:.2f}")
        
        # Show final results
        for alg, result in all_results.items():
            self.logger.info(f"   {alg}: {initial_score:.2f} → {result.final_score:.2f} ({result.improvement:+.2f})")
        
        # Find the best result
        best_algorithm = max(all_results.keys(), key=lambda alg: all_results[alg].final_score)
        best_result = all_results[best_algorithm]
        
        # Create summary result
        results = {
            'best_result': best_result,
            'best_algorithm': best_algorithm,
            'all_results': all_results
        }
        
        # Add comparison statistics
        scores = [result.final_score for result in all_results.values()]
        results['comparison_stats'] = {
            'best_score': max(scores),
            'worst_score': min(scores),
            'average_score': sum(scores) / len(scores),
            'score_range': max(scores) - min(scores)
        }
        
        self.logger.info(f"Best algorithm: {best_algorithm} with score {best_result.final_score:.2f}")
        
        return results
    
    def run_algorithm_comparison(self, school_data: SchoolData, 
                               algorithms: List[str] = None,
                               max_iterations: int = None,
                               output_file: str = None) -> Dict[str, Any]:
        """
        Run a comprehensive comparison of multiple algorithms.
        
        Args:
            school_data: Initial school data to optimize
            algorithms: List of algorithms to compare
            max_iterations: Maximum iterations per algorithm
            output_file: Optional file to save comparison results
            
        Returns:
            Comprehensive comparison results
        """
        algorithms = algorithms or list(self.algorithms.keys())
        
        self.logger.info(f"Starting algorithm comparison with {len(algorithms)} algorithms")
        
        # Run parallel optimization
        results = self._parallel_optimization(school_data, algorithms, max_iterations)
        
        # Log comprehensive fair comparison summary
        initial_score = self.scorer.calculate_scores(school_data).final_score
        self.logger.info(f"🏁 Algorithm comparison completed with fair starting conditions:")
        self.logger.info(f"   All {len(algorithms)} algorithms started from score {initial_score:.2f}")
        
        # Calculate comparison metrics
        comparison = {
            'algorithms_tested': algorithms,
            'results': results,
            'rankings': {},
            'performance_metrics': {}
        }
        
        if results:
            # Rank by final score
            sorted_by_score = sorted(results.items(), key=lambda x: x[1].final_score, reverse=True)
            comparison['rankings']['by_score'] = [(alg, result.final_score) for alg, result in sorted_by_score]
            
            # Rank by improvement
            sorted_by_improvement = sorted(results.items(), key=lambda x: x[1].improvement, reverse=True)
            comparison['rankings']['by_improvement'] = [(alg, result.improvement) for alg, result in sorted_by_improvement]
            
            # Rank by execution time
            sorted_by_time = sorted(results.items(), key=lambda x: x[1].execution_time)
            comparison['rankings']['by_speed'] = [(alg, result.execution_time) for alg, result in sorted_by_time]
            
            # Log ranking summaries
            self.logger.info(f"🏆 Rankings:")
            self.logger.info(f"   By Score: {sorted_by_score[0][0]} ({sorted_by_score[0][1]:.2f})")
            self.logger.info(f"   By Improvement: {sorted_by_improvement[0][0]} ({sorted_by_improvement[0][1]:+.2f})")
            self.logger.info(f"   By Speed: {sorted_by_time[0][0]} ({sorted_by_time[0][1]:.2f}s)")
            
            # Calculate aggregate metrics
            scores = [result.final_score for result in results.values()]
            improvements = [result.improvement for result in results.values()]
            times = [result.execution_time for result in results.values()]
            
            comparison['performance_metrics'] = {
                'score_stats': {
                    'best': max(scores),
                    'worst': min(scores),
                    'average': sum(scores) / len(scores),
                    'std_dev': (sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores))**0.5
                },
                'improvement_stats': {
                    'best': max(improvements),
                    'worst': min(improvements),
                    'average': sum(improvements) / len(improvements)
                },
                'time_stats': {
                    'fastest': min(times),
                    'slowest': max(times),
                    'average': sum(times) / len(times)
                }
            }
        
        # Save results if requested
        if output_file:
            self._save_comparison_report(comparison, output_file)
        
        return comparison
    
    def _save_comparison_report(self, comparison: Dict[str, Any], output_file: str) -> None:
        """Save algorithm comparison report to CSV file."""
        import csv
        import os
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Algorithm Comparison Report'])
            writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            # Write rankings
            writer.writerow(['Rankings by Final Score:'])
            writer.writerow(['Rank', 'Algorithm', 'Score'])
            for i, (alg, score) in enumerate(comparison['rankings']['by_score'], 1):
                writer.writerow([i, alg, f"{score:.2f}"])
            writer.writerow([])
            
            writer.writerow(['Rankings by Improvement:'])
            writer.writerow(['Rank', 'Algorithm', 'Improvement'])
            for i, (alg, improvement) in enumerate(comparison['rankings']['by_improvement'], 1):
                writer.writerow([i, alg, f"{improvement:.2f}"])
            writer.writerow([])
            
            writer.writerow(['Rankings by Speed:'])
            writer.writerow(['Rank', 'Algorithm', 'Time (seconds)'])
            for i, (alg, time) in enumerate(comparison['rankings']['by_speed'], 1):
                writer.writerow([i, alg, f"{time:.2f}"])
            writer.writerow([])
            
            # Write detailed results
            writer.writerow(['Detailed Results:'])
            writer.writerow(['Algorithm', 'Initial Score', 'Final Score', 'Improvement', 'Time', 'Iterations'])
            for alg, result in comparison['results'].items():
                writer.writerow([
                    alg,
                    f"{result.initial_score:.2f}",
                    f"{result.final_score:.2f}",
                    f"{result.improvement:.2f}",
                    f"{result.execution_time:.2f}",
                    result.iterations_completed
                ])
        
        self.logger.info(f"Algorithm comparison report saved to: {output_file}")
    
    def get_best_result(self, results: Dict[str, OptimizationResult]) -> OptimizationResult:
        """
        Find the best result from multiple optimization runs.
        
        Args:
            results: Dictionary of optimization results
            
        Returns:
            Best optimization result
        """
        if not results:
            raise ValueError("No results provided")
        
        best_algorithm = max(results.keys(), key=lambda alg: results[alg].final_score)
        best_result = results[best_algorithm]
        
        self.logger.info(f"Best algorithm: {best_algorithm} with score {best_result.final_score:.2f}")
        
        return best_result
    
    def optimize_and_save(self, school_data: SchoolData,
                         output_file: str,
                         algorithm: str = None,
                         max_iterations: int = None,
                         initialization_strategy: str = "constraint_aware",
                         auto_initialize: bool = True,
                         generate_reports: bool = True,
                         target_classes: Optional[int] = None) -> Tuple[OptimizationResult, Any]:
        """
        Optimize assignments and save results to CSV file.
        
        Args:
            school_data: Initial school data to optimize
            output_file: Path to save optimized assignment CSV
            algorithm: Optimization algorithm to use
            max_iterations: Maximum optimization iterations
            initialization_strategy: Strategy for initializing unassigned students
            auto_initialize: Whether to automatically initialize unassigned students
            generate_reports: Whether to generate detailed reports
            target_classes: Number of target classes for initialization (auto-calculated if None)
            
        Returns:
            Tuple of (OptimizationResult, detailed_scoring_result)
        """
        # Run optimization
        result = self.optimize(school_data, algorithm, max_iterations, None, 
                             initialization_strategy, auto_initialize, target_classes)
        
        # Save optimized assignment to CSV
        self._save_assignment_csv(result.optimized_school_data, output_file)
        
        # Always run detailed scorer on final result
        self.logger.info("Running detailed scorer on optimized assignment...")
        scoring_result = self.scorer.calculate_scores(result.optimized_school_data)
        
        # Generate reports if requested
        if generate_reports:
            output_dir = os.path.dirname(output_file) or "."
            base_name = os.path.splitext(os.path.basename(output_file))[0]
            
            # Generate optimization report
            report_file = os.path.join(output_dir, f"{base_name}_optimization_report.csv")
            self._save_optimization_report(result, report_file)
            
            # Generate scoring reports using the scorer
            reports_dir = os.path.join(output_dir, f"{base_name}_reports")
            self.scorer.generate_csv_reports(scoring_result, reports_dir)
            
            self.logger.info(f"Reports generated in: {reports_dir}")
        
        self.logger.info(f"Optimized assignment saved to: {output_file}")
        
        return result, scoring_result
    
    def generate_initial_assignment(self, school_data: SchoolData,
                                   output_file: str,
                                   strategy: str = "constraint_aware",
                                   target_classes: Optional[int] = None) -> SchoolData:
        """
        Generate an initial assignment without optimization.
        
        Args:
            school_data: School data with unassigned students
            output_file: Path to save initial assignment CSV
            strategy: Initialization strategy to use
            target_classes: Number of target classes (auto-calculated if None)
            
        Returns:
            SchoolData with initial assignments
        """
        # Initialize assignments
        initialized_data = self.initialize_assignments(
            school_data, 
            InitializationStrategy(strategy), 
            target_classes
        )
        
        # Save assignment to CSV
        self._save_assignment_csv(initialized_data, output_file)
        
        # Log summary
        summary = self.get_assignment_summary(initialized_data)
        self.logger.info(f"Generated initial assignment:")
        self.logger.info(f"  Strategy: {strategy}")
        self.logger.info(f"  Total students: {summary['total_students']}")
        self.logger.info(f"  Total classes: {summary['total_classes']}")
        self.logger.info(f"  Class sizes: {summary['class_sizes']}")
        self.logger.info(f"  Force constraints: {summary['force_class_constraints']}")
        self.logger.info(f"  Force friend groups: {summary['force_friend_groups']}")
        
        self.logger.info(f"Initial assignment saved to: {output_file}")
        
        return initialized_data
    
    def _save_assignment_csv(self, school_data: SchoolData, output_file: str) -> None:
        """
        Save optimized student assignments to CSV file.
        
        Args:
            school_data: Optimized school data
            output_file: Path to save CSV file
        """
        # Handle empty output file or directory
        if not output_file:
            raise ValueError("Output file path cannot be empty")
        
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header (same format as input CSV)
            writer.writerow([
                'student_id', 'first_name', 'last_name', 'gender', 'class',
                'academic_score', 'behavior_rank', 'assistance_package',
                'preferred_friend_1', 'preferred_friend_2', 'preferred_friend_3',
                'disliked_peer_1', 'disliked_peer_2', 'disliked_peer_3', 
                'disliked_peer_4', 'disliked_peer_5',
                'force_class', 'force_friend'
            ])
            
            # Write student data sorted by class and then by student ID
            for class_id in sorted(school_data.classes.keys()):
                class_data = school_data.classes[class_id]
                sorted_students = sorted(class_data.students, key=lambda s: s.student_id)
                
                for student in sorted_students:
                    writer.writerow([
                        student.student_id,
                        student.first_name,
                        student.last_name,
                        student.gender,
                        student.class_id,
                        student.academic_score,
                        student.behavior_rank,
                        'true' if student.assistance_package else 'false',
                        student.preferred_friend_1 or '',
                        student.preferred_friend_2 or '',
                        student.preferred_friend_3 or '',
                        student.disliked_peer_1 or '',
                        student.disliked_peer_2 or '',
                        student.disliked_peer_3 or '',
                        student.disliked_peer_4 or '',
                        student.disliked_peer_5 or '',
                        student.force_class or '',
                        student.force_friend or ''
                    ])
    
    def _save_optimization_report(self, result: OptimizationResult, output_file: str) -> None:
        """
        Save optimization report to CSV file.
        
        Args:
            result: Optimization result
            output_file: Path to save report CSV
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write optimization summary
            writer.writerow(['Optimization Report'])
            writer.writerow(['Generated:', result.timestamp.strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            writer.writerow(['Algorithm:', result.algorithm_name])
            writer.writerow(['Initial Score:', f"{result.initial_score:.2f}"])
            writer.writerow(['Final Score:', f"{result.final_score:.2f}"])
            writer.writerow(['Improvement:', f"{result.improvement:.2f}"])
            writer.writerow(['Improvement %:', f"{result.improvement_percentage:.1f}%"])
            writer.writerow(['Execution Time (seconds):', f"{result.execution_time:.2f}"])
            writer.writerow(['Iterations Completed:', result.iterations_completed])
            writer.writerow(['Total Iterations:', result.total_iterations])
            writer.writerow(['Constraints Satisfied:', 'Yes' if result.constraints_satisfied else 'No'])
            writer.writerow([])
            
            # Write algorithm parameters
            writer.writerow(['Algorithm Parameters:'])
            for key, value in result.algorithm_parameters.items():
                writer.writerow([key, value])
            writer.writerow([])
            
            # Write constraint violations if any
            if result.constraint_violations:
                writer.writerow(['Constraint Violations:'])
                for violation in result.constraint_violations:
                    writer.writerow([violation])
                writer.writerow([])
            
            # Write score history
            writer.writerow(['Optimization History:'])
            writer.writerow(['Iteration', 'Score', 'Improvement'])
            for i, (score, improvement) in enumerate(zip(result.score_history, result.improvement_history)):
                writer.writerow([i, f"{score:.2f}", f"{improvement:.2f}"]) 