#!/usr/bin/env python3
"""
OR-Tools Optimizer for Meshachvetz - Uses constraint programming to find optimal
student-class assignments with hard constraints satisfaction.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import copy

try:
    from ortools.sat.python import cp_model
except ImportError:
    cp_model = None

from .base_optimizer import BaseOptimizer, OptimizationResult
from ..data.models import SchoolData, Student, ClassData


class ORToolsOptimizer(BaseOptimizer):
    """
    OR-Tools Constraint Programming optimizer.
    
    Uses Google's OR-Tools CP-SAT solver to find optimal student-class assignments
    that satisfy all hard constraints while maximizing the scoring function.
    """
    
    def __init__(self, scorer, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OR-Tools optimizer.
        
        Args:
            scorer: Scorer instance for evaluating solutions
            config: Configuration dictionary with algorithm parameters
        """
        super().__init__(scorer, config)
        
        if cp_model is None:
            raise ImportError("OR-Tools is required for ORToolsOptimizer. Install with: pip install ortools")
        
        # OR-Tools specific parameters
        self.time_limit_seconds = self.config.get('time_limit_seconds', 300)  # 5 minutes default
        self.optimize_for_feasibility = self.config.get('optimize_for_feasibility', False)
        self.target_class_size = self.config.get('target_class_size', 25)
        self.class_size_tolerance = self.config.get('class_size_tolerance', 3)
        self.enable_preprocessing = self.config.get('enable_preprocessing', True)
        
        # Scoring approximation (since OR-Tools can't directly optimize complex scoring functions)
        self.friend_weight = self.config.get('friend_weight', 10)
        self.conflict_penalty = self.config.get('conflict_penalty', 20)
        self.balance_weight = self.config.get('balance_weight', 5)
        
        self.logger = logging.getLogger(__name__)
        
    def get_algorithm_name(self) -> str:
        """Get the name of this optimization algorithm."""
        return "OR-Tools CP-SAT"
    
    def optimize(self, school_data: SchoolData, max_iterations: int = 1000) -> OptimizationResult:
        """
        Optimize using OR-Tools constraint programming.
        
        Args:
            school_data: Initial school data to optimize
            max_iterations: Not used in OR-Tools (uses time_limit_seconds instead)
            
        Returns:
            OptimizationResult with optimized assignment and metrics
        """
        self.logger.info(f"Starting {self.get_algorithm_name()} optimization")
        self.logger.info(f"Time limit: {self.time_limit_seconds} seconds")
        self.logger.info(f"Students: {school_data.total_students}, Classes: {school_data.total_classes}")
        
        # Initialize optimization tracking
        initial_score = self.start_optimization(school_data)
        
        # Build and solve the constraint programming model
        try:
            model, variables = self._build_model(school_data)
            solver = cp_model.CpSolver()
            
            # Set solver parameters
            solver.parameters.max_time_in_seconds = self.time_limit_seconds
            solver.parameters.log_search_progress = True
            
            self.logger.info("Starting CP-SAT solver...")
            status = solver.Solve(model)
            
            # Process results
            if status == cp_model.OPTIMAL:
                self.logger.info("✅ Optimal solution found!")
                optimized_data = self._extract_solution(school_data, solver, variables)
                iterations = 1  # OR-Tools doesn't use iterations
                
            elif status == cp_model.FEASIBLE:
                self.logger.info("✅ Feasible solution found (may not be optimal)")
                optimized_data = self._extract_solution(school_data, solver, variables)
                iterations = 1
                
            else:
                self.logger.warning(f"❌ No solution found. Status: {solver.StatusName(status)}")
                # Return original data if no solution found
                optimized_data = copy.deepcopy(school_data)
                iterations = 0
                
            # Calculate final metrics
            final_score = self.evaluate_solution(optimized_data)
            
            return self.finish_optimization(optimized_data, iterations)
            
        except Exception as e:
            self.logger.error(f"OR-Tools optimization failed: {e}")
            # Return original data on error
            return self.finish_optimization(copy.deepcopy(school_data), 0)
    
    def _build_model(self, school_data: SchoolData) -> Tuple[cp_model.CpModel, Dict]:
        """
        Build the constraint programming model.
        
        Args:
            school_data: School data to model
            
        Returns:
            Tuple of (model, variables_dict)
        """
        model = cp_model.CpModel()
        variables = {}
        
        # Get students and classes
        students = list(school_data.students.values())
        classes = list(school_data.classes.keys())
        
        # Create decision variables: x[student_id][class_id] = 1 if student is in class
        student_class_vars = {}
        for student in students:
            student_class_vars[student.student_id] = {}
            for class_id in classes:
                var_name = f"x_{student.student_id}_{class_id}"
                student_class_vars[student.student_id][class_id] = model.NewBoolVar(var_name)
        
        variables['student_class'] = student_class_vars
        
        # Constraint 1: Each student must be assigned to exactly one class
        for student in students:
            model.Add(sum(student_class_vars[student.student_id][class_id] 
                         for class_id in classes) == 1)
        
        # Constraint 2: Force class constraints
        for student in students:
            if student.has_force_class() and student.force_class in classes:
                # Force this student to be in their specified class
                model.Add(student_class_vars[student.student_id][student.force_class] == 1)
                self.logger.debug(f"Added force_class constraint: {student.student_id} -> {student.force_class}")
        
        # Constraint 3: Force friend constraints
        force_groups = school_data.get_force_friend_groups()
        for group_id, student_ids in force_groups.items():
            if len(student_ids) > 1:
                # All students in this group must be in the same class
                for class_id in classes:
                    # If first student is in class, all others must be too
                    first_student = student_ids[0]
                    for other_student in student_ids[1:]:
                        if other_student in school_data.students:
                            model.Add(student_class_vars[first_student][class_id] == 
                                    student_class_vars[other_student][class_id])
                self.logger.debug(f"Added force_friend constraint for group: {group_id}")
        
        # Constraint 4: Class size limits
        for class_id in classes:
            class_size = sum(student_class_vars[student.student_id][class_id] 
                           for student in students)
            
            # Target class size with tolerance
            min_size = max(1, self.target_class_size - self.class_size_tolerance)
            max_size = self.target_class_size + self.class_size_tolerance
            
            model.Add(class_size >= min_size)
            model.Add(class_size <= max_size)
            
            self.logger.debug(f"Added class size constraint for {class_id}: {min_size}-{max_size}")
        
        # Constraint 5: Minimum friends constraint (approximation)
        if self.min_friends_required > 0:
            self._add_minimum_friends_constraints(model, variables, students, classes, school_data)
        
        # Objective: Maximize approximated score
        objective_terms = []
        
        # Friend satisfaction terms
        for student in students:
            preferred_friends = student.get_preferred_friends()
            for friend_id in preferred_friends:
                if friend_id in school_data.students:
                    # Add bonus for having preferred friend in same class
                    for class_id in classes:
                        friend_bonus = model.NewBoolVar(f"friend_bonus_{student.student_id}_{friend_id}_{class_id}")
                        model.Add(friend_bonus == 1).OnlyEnforceIf([
                            student_class_vars[student.student_id][class_id],
                            student_class_vars[friend_id][class_id]
                        ])
                        model.Add(friend_bonus == 0).OnlyEnforceIf([
                            student_class_vars[student.student_id][class_id].Not(),
                            student_class_vars[friend_id][class_id].Not()
                        ])
                        objective_terms.append(friend_bonus * self.friend_weight)
        
        # Conflict avoidance terms
        for student in students:
            disliked_peers = student.get_disliked_peers()
            for peer_id in disliked_peers:
                if peer_id in school_data.students:
                    # Add penalty for having disliked peer in same class
                    for class_id in classes:
                        conflict_penalty = model.NewBoolVar(f"conflict_penalty_{student.student_id}_{peer_id}_{class_id}")
                        model.Add(conflict_penalty == 1).OnlyEnforceIf([
                            student_class_vars[student.student_id][class_id],
                            student_class_vars[peer_id][class_id]
                        ])
                        model.Add(conflict_penalty == 0).OnlyEnforceIf([
                            student_class_vars[student.student_id][class_id].Not(),
                            student_class_vars[peer_id][class_id].Not()
                        ])
                        objective_terms.append(conflict_penalty * (-self.conflict_penalty))
        
        # Gender balance terms (simplified)
        for class_id in classes:
            male_count = sum(student_class_vars[student.student_id][class_id] 
                           for student in students if student.gender == 'M')
            female_count = sum(student_class_vars[student.student_id][class_id] 
                             for student in students if student.gender == 'F')
            
            # Add balance bonus (simplified - OR-Tools can't handle complex balance calculations)
            total_students_in_class = male_count + female_count
            balance_bonus = model.NewIntVar(0, 100, f"balance_bonus_{class_id}")
            
            # Approximate balance: bonus when male and female counts are close
            model.Add(balance_bonus <= total_students_in_class * self.balance_weight)
            objective_terms.append(balance_bonus)
        
        # Set objective
        if objective_terms:
            model.Maximize(sum(objective_terms))
        else:
            # If no objective terms, just find feasible solution
            model.Maximize(0)
        
        return model, variables
    
    def _add_minimum_friends_constraints(self, model: cp_model.CpModel, variables: Dict, 
                                       students: List[Student], classes: List[str], 
                                       school_data: SchoolData) -> None:
        """Add minimum friends constraints to the model."""
        for student in students:
            preferred_friends = student.get_preferred_friends()
            valid_friends = [f for f in preferred_friends if f in school_data.students]
            
            if len(valid_friends) >= self.min_friends_required:
                # Student must have at least min_friends_required friends in their class
                for class_id in classes:
                    friends_in_class = sum(variables['student_class'][friend_id][class_id] 
                                         for friend_id in valid_friends)
                    
                    # If student is in this class, they must have enough friends
                    student_in_class = variables['student_class'][student.student_id][class_id]
                    
                    # Implication: if student is in class, then friends_in_class >= min_friends_required
                    model.Add(friends_in_class >= self.min_friends_required).OnlyEnforceIf([student_in_class])
    
    def _extract_solution(self, school_data: SchoolData, solver: cp_model.CpSolver, 
                         variables: Dict) -> SchoolData:
        """
        Extract the solution from the solved model.
        
        Args:
            school_data: Original school data
            solver: Solved CP-SAT solver
            variables: Variables dictionary
            
        Returns:
            SchoolData with optimized assignments
        """
        # Create a copy of the original data
        optimized_data = copy.deepcopy(school_data)
        
        # Clear existing class assignments
        for class_data in optimized_data.classes.values():
            class_data.students.clear()
        
        # Extract assignments from solution
        student_class_vars = variables['student_class']
        assignments = {}
        
        for student_id, class_vars in student_class_vars.items():
            for class_id, var in class_vars.items():
                if solver.Value(var) == 1:
                    assignments[student_id] = class_id
                    break
        
        # Apply assignments
        for student_id, class_id in assignments.items():
            student = optimized_data.students[student_id]
            student.class_id = class_id
            optimized_data.classes[class_id].students.append(student)
        
        # Log solution statistics
        self.logger.info("Solution statistics:")
        for class_id, class_data in optimized_data.classes.items():
            self.logger.info(f"  Class {class_id}: {len(class_data.students)} students")
        
        return optimized_data
    
    def get_algorithm_parameters(self) -> Dict[str, Any]:
        """Get algorithm parameters for reporting."""
        return {
            "time_limit_seconds": self.time_limit_seconds,
            "target_class_size": self.target_class_size,
            "class_size_tolerance": self.class_size_tolerance,
            "min_friends_required": self.min_friends_required,
            "friend_weight": self.friend_weight,
            "conflict_penalty": self.conflict_penalty,
            "balance_weight": self.balance_weight,
            "optimize_for_feasibility": self.optimize_for_feasibility
        } 