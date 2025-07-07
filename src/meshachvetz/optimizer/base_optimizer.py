#!/usr/bin/env python3
"""
Base optimizer framework for Meshachvetz - abstract classes and data structures
for optimization algorithms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import time
import logging
from datetime import datetime

from ..data.models import SchoolData, Student
from meshachvetz.utils.logging import IterationLogger, LogLevel, create_iteration_logger


@dataclass
class OptimizationResult:
    """
    Result of an optimization process.
    
    Contains the optimized assignment, performance metrics, and optimization history.
    """
    # Core results
    optimized_school_data: SchoolData
    initial_score: float
    final_score: float
    improvement: float
    
    # Algorithm information
    algorithm_name: str
    algorithm_parameters: Dict[str, Any]
    
    # Performance metrics
    execution_time: float
    iterations_completed: int
    total_iterations: int
    
    # Optimization history
    score_history: List[float] = field(default_factory=list)
    improvement_history: List[float] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Constraint satisfaction
    constraints_satisfied: bool = True
    constraint_violations: List[str] = field(default_factory=list)
    
    # Additional metrics
    convergence_iteration: Optional[int] = None
    best_score_achieved: Optional[float] = None
    
    @property
    def improvement_percentage(self) -> float:
        """Calculate improvement as percentage."""
        if self.initial_score == 0:
            return 0.0
        return (self.improvement / self.initial_score) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage of total iterations."""
        if self.total_iterations == 0:
            return 0.0
        return (self.iterations_completed / self.total_iterations) * 100
    
    def get_summary(self) -> str:
        """Get a formatted summary of the optimization result."""
        summary = []
        summary.append(f"🎯 Optimization Results - {self.algorithm_name}")
        summary.append("=" * 50)
        summary.append(f"Initial Score: {self.initial_score:.2f}/100")
        summary.append(f"Final Score: {self.final_score:.2f}/100")
        summary.append(f"Improvement: +{self.improvement:.2f} ({self.improvement_percentage:.1f}%)")
        summary.append(f"Execution Time: {self.execution_time:.2f} seconds")
        summary.append(f"Iterations: {self.iterations_completed}/{self.total_iterations}")
        summary.append(f"Constraints Satisfied: {'✅' if self.constraints_satisfied else '❌'}")
        
        if not self.constraints_satisfied:
            summary.append(f"Constraint Violations:")
            for violation in self.constraint_violations:
                summary.append(f"  - {violation}")
        
        return "\n".join(summary)


class BaseOptimizer(ABC):
    """
    Abstract base class for all optimization algorithms.
    
    Defines the interface that all optimizers must implement and provides
    common functionality for constraint validation and progress tracking.
    """
    
    def __init__(self, scorer, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base optimizer.
        
        Args:
            scorer: Scorer instance for evaluating solutions
            config: Configuration dictionary for algorithm parameters
        """
        self.scorer = scorer
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Enhanced iteration logging
        log_level = self.config.get('log_level', 'normal')
        self.iteration_logger = create_iteration_logger(log_level, self.__class__.__name__)
        
        # Progress tracking (for backward compatibility)
        self.current_iteration = 0
        self.best_score = -1
        self.score_history = []
        self.start_time = None
        
        # Constraints configuration
        self.min_friends_required = self.config.get('min_friends', 1)
        self.respect_force_constraints = self.config.get('respect_force_constraints', True)
        self.allow_constraint_override = self.config.get('allow_constraint_override', True)
        
    @abstractmethod
    def optimize(self, school_data: SchoolData, max_iterations: int = 1000) -> OptimizationResult:
        """
        Optimize the student assignment.
        
        Args:
            school_data: Initial school data to optimize
            max_iterations: Maximum number of optimization iterations
            
        Returns:
            OptimizationResult with optimized assignment and metrics
        """
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Get the name of this optimization algorithm."""
        pass
    
    def evaluate_solution(self, school_data: SchoolData) -> float:
        """
        Evaluate the quality of a solution using the scorer.
        
        Args:
            school_data: School data to evaluate
            
        Returns:
            Score (0-100) for the solution
        """
        try:
            result = self.scorer.calculate_scores(school_data)
            return result.final_score
        except Exception as e:
            self.logger.error(f"Error evaluating solution: {e}")
            return 0.0
    
    def is_valid_solution(self, school_data: SchoolData) -> tuple[bool, List[str]]:
        """
        Check if a solution satisfies all hard constraints.
        
        Args:
            school_data: School data to validate
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        try:
            # Check basic data integrity
            if not school_data.students or not school_data.classes:
                violations.append("Missing students or classes data")
                return False, violations
            
            # Check that all students are assigned to classes
            assigned_students = set()
            for class_data in school_data.classes.values():
                for student in class_data.students:
                    if student.student_id in assigned_students:
                        violations.append(f"Student {student.student_id} assigned to multiple classes")
                    assigned_students.add(student.student_id)
            
            missing_students = set(school_data.students.keys()) - assigned_students
            if missing_students:
                violations.append(f"Students not assigned to any class: {list(missing_students)[:5]}")
            
            # Check force constraints if enabled
            if self.respect_force_constraints:
                constraint_violations = school_data.validate_force_constraints()
                violations.extend(constraint_violations)
            
            # Check minimum friend constraints
            if self.min_friends_required > 0:
                friend_violations = self._validate_minimum_friends(school_data)
                violations.extend(friend_violations)
            
            return len(violations) == 0, violations
            
        except Exception as e:
            violations.append(f"Validation error: {e}")
            return False, violations
    
    def _validate_minimum_friends(self, school_data: SchoolData) -> List[str]:
        """
        Validate that students have minimum required friends.
        
        Args:
            school_data: School data to validate
            
        Returns:
            List of constraint violations
        """
        violations = []
        
        for student_id, student in school_data.students.items():
            preferred_friends = student.get_preferred_friends()
            
            if len(preferred_friends) == 0:
                # Student has no friend preferences, so constraint is automatically satisfied
                continue
            
            # Count how many preferred friends are in the same class
            student_class = school_data.get_class_by_id(student.class_id)
            if not student_class:
                violations.append(f"Student {student_id} has invalid class assignment")
                continue
            
            classmate_ids = {s.student_id for s in student_class.students}
            friends_in_class = sum(1 for friend_id in preferred_friends if friend_id in classmate_ids)
            
            if friends_in_class < self.min_friends_required:
                violations.append(
                    f"Student {student_id} has only {friends_in_class} friends in class, "
                    f"minimum required: {self.min_friends_required}"
                )
        
        return violations
    
    def start_optimization(self, school_data: SchoolData) -> float:
        """
        Initialize optimization tracking.
        
        Args:
            school_data: Initial school data
            
        Returns:
            Initial score
        """
        self.start_time = time.time()
        self.current_iteration = 0
        self.score_history = []
        
        initial_score = self.evaluate_solution(school_data)
        self.best_score = initial_score
        self.score_history.append(initial_score)
        
        # Use enhanced iteration logging
        max_iterations = self.config.get('max_iterations', 1000)
        self.iteration_logger.start_optimization(initial_score, max_iterations)
        
        # Legacy logging for backward compatibility
        self.logger.info(f"Starting {self.get_algorithm_name()} optimization")
        self.logger.info(f"Initial score: {initial_score:.2f}")
        
        return initial_score
    
    def update_progress(self, school_data: SchoolData, iteration: int, 
                       additional_metrics: Optional[Dict[str, Any]] = None) -> float:
        """
        Update progress tracking with enhanced logging.
        
        Args:
            school_data: Current school data
            iteration: Current iteration number
            additional_metrics: Additional algorithm-specific metrics
            
        Returns:
            Current score
        """
        self.current_iteration = iteration
        current_score = self.evaluate_solution(school_data)
        self.score_history.append(current_score)
        
        # Track best score for legacy compatibility
        if current_score > self.best_score:
            self.best_score = current_score
            self.logger.debug(f"Iteration {iteration}: New best score {current_score:.2f}")
        
        # Use enhanced iteration logging
        self.iteration_logger.log_iteration(iteration, current_score, additional_metrics)
        
        return current_score
    
    def finish_optimization(self, school_data: SchoolData, total_iterations: int) -> OptimizationResult:
        """
        Finalize optimization and create result with enhanced logging.
        
        Args:
            school_data: Final optimized school data
            total_iterations: Total iterations attempted
            
        Returns:
            OptimizationResult with complete metrics
        """
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        final_score = self.evaluate_solution(school_data)
        initial_score = self.score_history[0] if self.score_history else 0
        improvement = final_score - initial_score
        
        # Use enhanced iteration logging
        self.iteration_logger.finish_optimization(final_score, total_iterations)
        
        # Validate final solution
        is_valid, violations = self.is_valid_solution(school_data)
        
        # Create optimization result
        result = OptimizationResult(
            optimized_school_data=school_data,
            initial_score=initial_score,
            final_score=final_score,
            improvement=improvement,
            algorithm_name=self.get_algorithm_name(),
            algorithm_parameters=self.config,
            execution_time=execution_time,
            iterations_completed=total_iterations,
            total_iterations=self.config.get('max_iterations', total_iterations),
            score_history=self.score_history.copy(),
            improvement_history=[],
            constraints_satisfied=is_valid,
            constraint_violations=violations,
            best_score_achieved=self.best_score
        )
        
        # Calculate improvement history
        if len(self.score_history) > 1:
            improvement_history = []
            for i in range(1, len(self.score_history)):
                improvement = self.score_history[i] - self.score_history[i-1]
                improvement_history.append(improvement)
            result.improvement_history = improvement_history
        
        # Find convergence iteration
        if len(self.score_history) > 1:
            for i in range(len(self.score_history) - 1, 0, -1):
                if abs(self.score_history[i] - self.best_score) < 0.01:
                    result.convergence_iteration = i
                    break
        
        return result
    
    def should_continue(self, iteration: int, max_iterations: int, 
                       no_improvement_count: int = 0, max_no_improvement: int = 100) -> bool:
        """
        Determine if optimization should continue.
        
        Args:
            iteration: Current iteration
            max_iterations: Maximum iterations allowed
            no_improvement_count: Consecutive iterations without improvement
            max_no_improvement: Maximum consecutive iterations without improvement
            
        Returns:
            True if optimization should continue
        """
        if iteration >= max_iterations:
            return False
        
        if no_improvement_count >= max_no_improvement:
            self.logger.info(f"Early stopping: no improvement for {no_improvement_count} iterations")
            return False
        
        return True 