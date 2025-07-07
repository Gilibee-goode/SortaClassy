#!/usr/bin/env python3
"""
Integration tests for Week 6 implementation - Complete system testing.
Tests OR-Tools integration, configuration management, and end-to-end workflows.
"""

import pytest
import unittest
import tempfile
import shutil
import os
from pathlib import Path
import yaml
import csv
from typing import Dict, Any, List
import copy

# Import modules to test
from src.meshachvetz.optimizer.optimization_manager import OptimizationManager
from src.meshachvetz.optimizer.or_tools_optimizer import ORToolsOptimizer
from src.meshachvetz.cli.config_manager import ConfigurationManager, ConfigurationType
from src.meshachvetz.data.loader import DataLoader
from src.meshachvetz.data.models import SchoolData, Student, ClassData
from src.meshachvetz.scorer.main_scorer import Scorer


class TestWeek6Integration(unittest.TestCase):
    """Integration tests for Week 6 complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        self.data_dir = os.path.join(self.temp_dir, 'data')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create test student data
        self.create_test_data()
        
        # Initialize components
        self.config_manager = ConfigurationManager(self.config_dir)
        self.scorer = Scorer()
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_data(self):
        """Create test student data CSV file."""
        # Create sample student data that tests various scenarios
        students_data = [
            {
                'student_id': '123456789',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'gender': 'F',
                'class': 'A',
                'academic_score': 85.0,
                'behavior_rank': 'A',
                'assistance_package': False,
                'preferred_friend_1': '987654321',
                'preferred_friend_2': '111111111',
                'preferred_friend_3': '',
                'disliked_peer_1': '222222222',
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': '',
                'force_friend': ''
            },
            {
                'student_id': '987654321',
                'first_name': 'Bob',
                'last_name': 'Jones',
                'gender': 'M',
                'class': 'A',
                'academic_score': 75.0,
                'behavior_rank': 'B',
                'assistance_package': True,
                'preferred_friend_1': '123456789',
                'preferred_friend_2': '',
                'preferred_friend_3': '',
                'disliked_peer_1': '',
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': '',
                'force_friend': '111111111'
            },
            {
                'student_id': '111111111',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'gender': 'M',
                'class': 'B',
                'academic_score': 90.0,
                'behavior_rank': 'A',
                'assistance_package': False,
                'preferred_friend_1': '123456789',
                'preferred_friend_2': '',
                'preferred_friend_3': '',
                'disliked_peer_1': '',
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': 'A',
                'force_friend': '111111111'
            },
            {
                'student_id': '222222222',
                'first_name': 'Diana',
                'last_name': 'Wilson',
                'gender': 'F',
                'class': 'B',
                'academic_score': 80.0,
                'behavior_rank': 'B',
                'assistance_package': False,
                'preferred_friend_1': '333333333',
                'preferred_friend_2': '',
                'preferred_friend_3': '',
                'disliked_peer_1': '123456789',
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': '',
                'force_friend': ''
            },
            {
                'student_id': '333333333',
                'first_name': 'Eve',
                'last_name': 'Davis',
                'gender': 'F',
                'class': 'B',
                'academic_score': 78.0,
                'behavior_rank': 'A',
                'assistance_package': True,
                'preferred_friend_1': '222222222',
                'preferred_friend_2': '',
                'preferred_friend_3': '',
                'disliked_peer_1': '',
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': '',
                'force_friend': ''
            },
            {
                'student_id': '444444444',
                'first_name': 'Frank',
                'last_name': 'Miller',
                'gender': 'M',
                'class': 'A',
                'academic_score': 88.0,
                'behavior_rank': 'A',
                'assistance_package': False,
                'preferred_friend_1': '555555555',
                'preferred_friend_2': '',
                'preferred_friend_3': '',
                'disliked_peer_1': '',
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': '',
                'force_friend': ''
            },
            {
                'student_id': '555555555',
                'first_name': 'Grace',
                'last_name': 'Taylor',
                'gender': 'F',
                'class': 'A',
                'academic_score': 92.0,
                'behavior_rank': 'A',
                'assistance_package': False,
                'preferred_friend_1': '444444444',
                'preferred_friend_2': '',
                'preferred_friend_3': '',
                'disliked_peer_1': '',
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': '',
                'force_friend': ''
            },
            {
                'student_id': '666666666',
                'first_name': 'Henry',
                'last_name': 'Clark',
                'gender': 'M',
                'class': 'B',
                'academic_score': 72.0,
                'behavior_rank': 'C',
                'assistance_package': True,
                'preferred_friend_1': '',
                'preferred_friend_2': '',
                'preferred_friend_3': '',
                'disliked_peer_1': '',
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': '',
                'force_friend': ''
            }
        ]
        
        # Write CSV file
        self.test_csv_file = os.path.join(self.data_dir, 'test_students.csv')
        with open(self.test_csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=students_data[0].keys())
            writer.writeheader()
            writer.writerows(students_data)
    
    def test_or_tools_optimizer_integration(self):
        """Test OR-Tools optimizer integration with the complete system."""
        # Load data
        loader = DataLoader(validate_data=False)
        school_data = loader.load_csv(self.test_csv_file)
        
        # Create configuration for OR-Tools
        or_tools_config = {
            'time_limit_seconds': 10,  # Short time for testing
            'target_class_size': 4,    # Small classes for test data
            'class_size_tolerance': 1,
            'friend_weight': 10,
            'conflict_penalty': 20,
            'min_friends': 0  # Relaxed for small dataset
        }
        
        # Initialize optimizer
        optimizer = ORToolsOptimizer(self.scorer, or_tools_config)
        
        # Test optimization
        initial_score = optimizer.evaluate_solution(school_data)
        result = optimizer.optimize(school_data)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result.algorithm_name, "OR-Tools CP-SAT")
        self.assertGreaterEqual(result.final_score, 0)
        self.assertGreaterEqual(result.execution_time, 0)
        
        # Verify solution validity
        is_valid, violations = optimizer.is_valid_solution(result.optimized_school_data)
        if not is_valid:
            print(f"Constraint violations: {violations}")
        
        # OR-Tools should respect hard constraints
        self.assertTrue(is_valid or len(violations) == 0, f"OR-Tools should produce valid solutions, violations: {violations}")
    
    def test_optimization_manager_or_tools_integration(self):
        """Test OptimizationManager with OR-Tools algorithm."""
        # Load data
        loader = DataLoader(validate_data=False)
        school_data = loader.load_csv(self.test_csv_file)
        
        # Create optimization manager
        optimization_config = {
            'time_limit_seconds': 10,
            'target_class_size': 4,
            'min_friends': 0
        }
        
        manager = OptimizationManager(self.scorer, optimization_config)
        
        # Test that OR-Tools is available
        available_algorithms = manager.get_available_algorithms()
        self.assertIn('or_tools', available_algorithms)
        
        # Test optimization with OR-Tools
        result = manager.optimize(
            school_data,
            algorithm='or_tools',
            max_iterations=100,  # Not used by OR-Tools
            algorithm_config=optimization_config
        )
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result.algorithm_name, "OR-Tools CP-SAT")
        self.assertIsInstance(result.optimized_school_data, SchoolData)
    
    def test_configuration_manager_integration(self):
        """Test enhanced configuration manager integration."""
        # Test creating and validating OR-Tools configuration
        template = self.config_manager.create_configuration_template(
            ConfigurationType.OPTIMIZER,
            'or_tools'
        )
        
        # Should include OR-Tools configuration
        self.assertIn('or_tools', template['optimization']['algorithms'])
        ortools_config = template['optimization']['algorithms']['or_tools']
        self.assertTrue(ortools_config['enabled'])
        self.assertIn('time_limit_seconds', ortools_config)
        
        # Test validation
        errors = self.config_manager.validate_configuration(template, ConfigurationType.OPTIMIZER)
        self.assertEqual(len(errors), 0, f"Template should be valid, errors: {errors}")
        
        # Test saving configuration
        config_file = os.path.join(self.config_dir, 'test_or_tools_config.yaml')
        self.config_manager.save_configuration(template, 'test_or_tools_config.yaml')
        
        # Verify file was created and is valid
        self.assertTrue(os.path.exists(config_file))
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        self.assertEqual(loaded_config, template)
    
    def test_small_school_profile_integration(self):
        """Test small school profile with OR-Tools optimization."""
        # Apply small school profile
        small_school_config = self.config_manager.apply_profile('small_school')
        
        # Extract OR-Tools configuration
        ortools_params = small_school_config['optimization']['algorithms']['or_tools']
        
        # Load data
        loader = DataLoader(validate_data=False)
        school_data = loader.load_csv(self.test_csv_file)
        
        # Create optimization manager with profile
        manager = OptimizationManager(self.scorer, ortools_params)
        
        # Test optimization using profile settings
        result = manager.optimize(
            school_data,
            algorithm='or_tools',
            algorithm_config=ortools_params
        )
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.final_score, 0)
    
    def test_multi_algorithm_comparison_with_or_tools(self):
        """Test multi-algorithm comparison including OR-Tools."""
        # Load data
        loader = DataLoader(validate_data=False)
        school_data = loader.load_csv(self.test_csv_file)
        
        # Configuration for fast testing
        fast_config = {
            'max_iterations': 50,
            'time_limit_seconds': 5,
            'population_size': 20,
            'generations': 10,
            'min_friends': 0
        }
        
        # Create optimization manager
        manager = OptimizationManager(self.scorer, fast_config)
        
        # Test comparison with multiple algorithms including OR-Tools
        algorithms = ['local_search', 'genetic', 'or_tools']
        
        results = manager.optimize_with_multiple_algorithms(
            school_data,
            algorithms=algorithms,
            max_iterations=50,
            strategy='parallel'
        )
        
        # Verify all algorithms ran
        self.assertEqual(len(results), len(algorithms))
        for algorithm in algorithms:
            self.assertIn(algorithm, results)
            self.assertIsNotNone(results[algorithm])
            self.assertGreaterEqual(results[algorithm].final_score, 0)
        
        # Verify OR-Tools result
        or_tools_result = results['or_tools']
        self.assertEqual(or_tools_result.algorithm_name, "OR-Tools CP-SAT")
    
    def test_force_constraints_with_or_tools(self):
        """Test that OR-Tools respects force constraints."""
        # Load data
        loader = DataLoader(validate_data=False)
        school_data = loader.load_csv(self.test_csv_file)
        
        # Configuration for OR-Tools
        config = {
            'time_limit_seconds': 15,
            'target_class_size': 4,
            'class_size_tolerance': 2,
            'min_friends': 0,
            'respect_force_constraints': True
        }
        
        # Create optimizer
        optimizer = ORToolsOptimizer(self.scorer, config)
        
        # Run optimization
        result = optimizer.optimize(school_data)
        
        # Verify force constraints are respected
        optimized_data = result.optimized_school_data
        
        # Check force_class constraints
        for student in optimized_data.students.values():
            if student.force_class:
                self.assertEqual(student.class_id, student.force_class,
                               f"Student {student.student_id} should be in force_class {student.force_class}")
        
        # Check force_friend constraints
        force_groups = optimized_data.get_force_friend_groups()
        for group_id, student_ids in force_groups.items():
            if len(student_ids) > 1:
                # All students in group should be in same class
                classes = set()
                for student_id in student_ids:
                    if student_id in optimized_data.students:
                        classes.add(optimized_data.students[student_id].class_id)
                
                self.assertEqual(len(classes), 1,
                               f"Force friend group {group_id} should be in same class, found classes: {classes}")
    
    def test_end_to_end_optimization_workflow(self):
        """Test complete end-to-end optimization workflow."""
        # 1. Load configuration profile
        profile_config = self.config_manager.apply_profile('balanced')
        
        # 2. Load student data
        loader = DataLoader(validate_data=False)
        school_data = loader.load_csv(self.test_csv_file)
        
        # 3. Calculate initial score
        initial_result = self.scorer.calculate_scores(school_data)
        initial_score = initial_result.final_score
        
        # 4. Create optimization manager with profile configuration
        optimization_params = profile_config.get('optimization', {})
        algorithm_configs = optimization_params.get('algorithms', {})
        
        # Adapt for small test dataset
        test_config = {
            'max_iterations': 50,
            'time_limit_seconds': 10,
            'min_friends': 0
        }
        
        manager = OptimizationManager(self.scorer, test_config)
        
        # 5. Run optimization with multiple algorithms
        algorithms = ['genetic', 'local_search']  # Skip OR-Tools for speed
        results = manager.optimize_with_multiple_algorithms(
            school_data,
            algorithms=algorithms,
            strategy='best_of'
        )
        
        # 6. Get best result
        best_result = manager.get_best_result(results)
        
        # 7. Verify improvement or at least maintained quality
        self.assertIsNotNone(best_result)
        self.assertGreaterEqual(best_result.final_score, 0)
        
        # 8. Save results
        output_file = os.path.join(self.output_dir, 'optimized_students.csv')
        final_result, score_result = manager.optimize_and_save(
            school_data,
            output_file,
            algorithm='genetic',
            max_iterations=30,
            generate_reports=True
        )
        
        # 9. Verify output files
        self.assertTrue(os.path.exists(output_file))
        
        # 10. Verify optimized data can be loaded back
        optimized_school_data = loader.load_csv(output_file)
        final_score_result = self.scorer.calculate_scores(optimized_school_data)
        self.assertGreaterEqual(final_score_result.final_score, 0)
    
    def test_configuration_validation_workflow(self):
        """Test configuration validation workflow."""
        # 1. Create invalid configuration
        invalid_config = {
            'optimization': {
                'algorithms': {
                    'genetic': {
                        'enabled': True,
                        'population_size': -10,  # Invalid
                        'mutation_rate': 2.0     # Invalid
                    },
                    'or_tools': {
                        'enabled': True,
                        'time_limit_seconds': -5,  # Invalid
                        'target_class_size': 0     # Invalid
                    }
                }
            }
        }
        
        # 2. Validate configuration
        errors = self.config_manager.validate_configuration(invalid_config, ConfigurationType.OPTIMIZER)
        
        # 3. Should have multiple errors
        self.assertGreater(len(errors), 0)
        
        # 4. Check specific error content
        error_text = ' '.join(errors)
        self.assertIn('population_size', error_text)
        self.assertIn('mutation_rate', error_text)
        
        # 5. Try to save invalid configuration (should fail)
        with self.assertRaises(Exception):  # ConfigurationError
            self.config_manager.save_configuration(
                invalid_config, 
                'invalid_config.yaml', 
                validate=True
            )
        
        # 6. Create valid configuration and save successfully
        valid_config = self.config_manager.create_configuration_template(ConfigurationType.OPTIMIZER, 'or_tools')
        self.config_manager.save_configuration(valid_config, 'valid_config.yaml', validate=True)
        
        # Verify file was created
        saved_file = os.path.join(self.config_dir, 'valid_config.yaml')
        self.assertTrue(os.path.exists(saved_file))
    
    def test_performance_benchmarking(self):
        """Test performance characteristics of different algorithms."""
        # Load data
        loader = DataLoader(validate_data=False)
        school_data = loader.load_csv(self.test_csv_file)
        
        # Test configuration optimized for speed
        fast_config = {
            'max_iterations': 20,
            'time_limit_seconds': 5,
            'population_size': 15,
            'generations': 5,
            'min_friends': 0
        }
        
        manager = OptimizationManager(self.scorer, fast_config)
        
        # Benchmark different algorithms
        algorithms = ['local_search', 'genetic', 'or_tools']
        performance_results = {}
        
        for algorithm in algorithms:
            try:
                result = manager.optimize(
                    school_data,
                    algorithm=algorithm,
                    max_iterations=20,
                    algorithm_config=fast_config
                )
                
                performance_results[algorithm] = {
                    'execution_time': result.execution_time,
                    'final_score': result.final_score,
                    'improvement': result.improvement,
                    'success': True
                }
                
            except Exception as e:
                performance_results[algorithm] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Verify all algorithms completed successfully
        for algorithm, results in performance_results.items():
            self.assertTrue(results['success'], f"{algorithm} failed: {results.get('error', 'Unknown error')}")
            self.assertGreaterEqual(results['execution_time'], 0)
            self.assertGreaterEqual(results['final_score'], 0)
        
        # OR-Tools should typically be fast for small problems
        if 'or_tools' in performance_results and performance_results['or_tools']['success']:
            ortools_time = performance_results['or_tools']['execution_time']
            self.assertLess(ortools_time, 30, "OR-Tools should be fast for small datasets")


if __name__ == '__main__':
    unittest.main() 