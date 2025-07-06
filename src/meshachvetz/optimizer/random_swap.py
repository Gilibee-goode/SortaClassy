#!/usr/bin/env python3
"""
Random Swap Optimizer for Meshachvetz - Simple but effective optimization algorithm
that randomly swaps students between classes and accepts improvements.
"""

import random
import copy
import logging
from typing import Set, List, Tuple, Optional

from .base_optimizer import BaseOptimizer, OptimizationResult
from ..data.models import SchoolData, Student


class RandomSwapOptimizer(BaseOptimizer):
    """
    Random Swap Optimization Algorithm.
    
    Randomly selects two students from different classes and swaps them.
    Accepts the swap if it improves the overall score, rejects otherwise.
    Respects force constraints and minimum friend requirements.
    """
    
    def __init__(self, scorer, config: Optional[dict] = None):
        """
        Initialize Random Swap Optimizer.
        
        Args:
            scorer: Scorer instance for evaluating solutions
            config: Configuration dictionary with algorithm parameters
        """
        super().__init__(scorer, config)
        
        # Algorithm-specific parameters
        self.early_stop_threshold = self.config.get('early_stop_threshold', 100)
        self.accept_neutral_moves = self.config.get('accept_neutral_moves', False)
        self.max_swap_attempts = self.config.get('max_swap_attempts', 50)
        
        # Track force-constrained students (cannot be moved)
        self.immovable_students: Set[str] = set()
        self.force_groups: dict = {}  # force_friend groups
        
        self.logger = logging.getLogger(__name__)
    
    def get_algorithm_name(self) -> str:
        """Get the name of this optimization algorithm."""
        return "Random Swap"
    
    def optimize(self, school_data: SchoolData, max_iterations: int = 1000) -> OptimizationResult:
        """
        Optimize student assignments using random swaps.
        
        Args:
            school_data: Initial school data to optimize
            max_iterations: Maximum number of swap attempts
            
        Returns:
            OptimizationResult with optimized assignment and metrics
        """
        # Create a working copy
        current_data = copy.deepcopy(school_data)
        best_data = copy.deepcopy(school_data)
        
        # Initialize tracking
        initial_score = self.start_optimization(current_data)
        best_score = initial_score
        no_improvement_count = 0
        
        # Identify force-constrained students
        self._identify_constrained_students(current_data)
        
        self.logger.info(f"Starting optimization with {len(self.immovable_students)} force-constrained students")
        
        for iteration in range(max_iterations):
            # Try to find a valid swap
            swap_made = False
            for attempt in range(self.max_swap_attempts):
                student1, student2 = self._select_swap_candidates(current_data)
                
                if student1 and student2:
                    # Attempt the swap
                    test_data = self._perform_swap(current_data, student1, student2)
                    
                    if test_data:
                        # Evaluate the swap
                        new_score = self.evaluate_solution(test_data)
                        
                        # Accept if improvement (or neutral if configured)
                        if (new_score > best_score or 
                            (self.accept_neutral_moves and new_score >= best_score)):
                            
                            current_data = test_data
                            best_score = new_score
                            best_data = copy.deepcopy(test_data)
                            no_improvement_count = 0
                            swap_made = True
                            
                            self.logger.debug(f"Iteration {iteration}: Accepted swap "
                                            f"{student1.student_id}<->{student2.student_id}, "
                                            f"new score: {new_score:.2f}")
                            break
                        else:
                            # Track that we tried but didn't improve
                            pass
                    
            if not swap_made:
                no_improvement_count += 1
            
            # Update progress tracking
            self.update_progress(best_data, iteration)
            
            # Check stopping conditions
            if not self.should_continue(iteration, max_iterations, 
                                      no_improvement_count, self.early_stop_threshold):
                break
        
        return self.finish_optimization(best_data, max_iterations)
    
    def _identify_constrained_students(self, school_data: SchoolData) -> None:
        """
        Identify students who cannot be moved due to force constraints.
        
        Args:
            school_data: School data to analyze
        """
        self.immovable_students.clear()
        self.force_groups.clear()
        
        if not self.respect_force_constraints:
            return
        
        for student_id, student in school_data.students.items():
            # Students with force_class cannot be moved
            if student.force_class and student.force_class.strip():
                self.immovable_students.add(student_id)
            
            # Students with force_friend form groups that must move together
            if student.force_friend and student.force_friend.strip():
                force_group = student.force_friend.strip()
                if force_group not in self.force_groups:
                    self.force_groups[force_group] = []
                self.force_groups[force_group].append(student_id)
        
        # Add all force_friend group members to immovable (for now, simplification)
        # In a more advanced implementation, we would move entire groups together
        for group_members in self.force_groups.values():
            if len(group_members) > 1:  # Only if it's actually a group
                self.immovable_students.update(group_members)
        
        self.logger.debug(f"Identified {len(self.immovable_students)} immovable students")
        if self.force_groups:
            self.logger.debug(f"Found {len(self.force_groups)} force friend groups")
    
    def _select_swap_candidates(self, school_data: SchoolData) -> Tuple[Optional[Student], Optional[Student]]:
        """
        Select two students from different classes for potential swapping.
        
        Args:
            school_data: Current school data
            
        Returns:
            Tuple of (student1, student2) or (None, None) if no valid candidates
        """
        # Get all movable students grouped by class
        movable_by_class = {}
        for class_id, class_data in school_data.classes.items():
            movable_students = [s for s in class_data.students 
                             if s.student_id not in self.immovable_students]
            if movable_students:
                movable_by_class[class_id] = movable_students
        
        # Need at least 2 classes with movable students
        if len(movable_by_class) < 2:
            return None, None
        
        # Randomly select two different classes
        class_ids = list(movable_by_class.keys())
        class1_id, class2_id = random.sample(class_ids, 2)
        
        # Randomly select one student from each class
        student1 = random.choice(movable_by_class[class1_id])
        student2 = random.choice(movable_by_class[class2_id])
        
        return student1, student2
    
    def _perform_swap(self, school_data: SchoolData, student1: Student, student2: Student) -> Optional[SchoolData]:
        """
        Perform a swap between two students and validate the result.
        
        Args:
            school_data: Current school data
            student1: First student to swap
            student2: Second student to swap
            
        Returns:
            New SchoolData with swap applied, or None if swap is invalid
        """
        try:
            # Create a copy for the swap
            new_data = copy.deepcopy(school_data)
            
            # Get the new copies of students from the copied data
            new_student1 = new_data.students[student1.student_id]
            new_student2 = new_data.students[student2.student_id]
            
            # Store original classes
            original_class1 = new_student1.class_id
            original_class2 = new_student2.class_id
            
            # Perform the swap
            new_student1.class_id = original_class2
            new_student2.class_id = original_class1
            
            # Rebuild the class assignments
            self._rebuild_class_assignments(new_data)
            
            # Validate the new assignment
            is_valid, violations = self.is_valid_solution(new_data)
            
            if not is_valid:
                self.logger.debug(f"Swap rejected: {violations[:2]}")  # Show first 2 violations
                return None
            
            return new_data
            
        except Exception as e:
            self.logger.error(f"Error performing swap: {e}")
            return None
    
    def _rebuild_class_assignments(self, school_data: SchoolData) -> None:
        """
        Rebuild class assignments based on student class_id values.
        
        Args:
            school_data: School data to rebuild
        """
        # Clear existing class assignments
        for class_data in school_data.classes.values():
            class_data.students.clear()
        
        # Reassign students based on their class_id
        for student in school_data.students.values():
            if student.class_id in school_data.classes:
                school_data.classes[student.class_id].students.append(student)
            else:
                # This should not happen in valid data
                self.logger.warning(f"Student {student.student_id} assigned to non-existent class {student.class_id}")
        
        # Update class averages and other computed properties
        for class_data in school_data.classes.values():
            # The properties are computed dynamically, so just accessing them updates the cache
            _ = class_data.average_academic_score
            _ = class_data.average_behavior_rank
    
    def get_optimization_config(self) -> dict:
        """
        Get the current optimization configuration.
        
        Returns:
            Dictionary with algorithm parameters
        """
        return {
            'algorithm': self.get_algorithm_name(),
            'early_stop_threshold': self.early_stop_threshold,
            'accept_neutral_moves': self.accept_neutral_moves,
            'max_swap_attempts': self.max_swap_attempts,
            'min_friends_required': self.min_friends_required,
            'respect_force_constraints': self.respect_force_constraints,
            'immovable_students_count': len(self.immovable_students),
            'force_groups_count': len(self.force_groups)
        }
    
    def get_swap_statistics(self) -> dict:
        """
        Get statistics about the swap attempts.
        
        Returns:
            Dictionary with swap statistics
        """
        return {
            'total_iterations': self.current_iteration,
            'best_score': self.best_score,
            'score_improvements': len([i for i, score in enumerate(self.score_history[1:], 1) 
                                     if score > self.score_history[i-1]]),
            'immovable_students': len(self.immovable_students),
            'force_groups': len(self.force_groups)
        } 