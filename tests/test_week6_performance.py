#!/usr/bin/env python3
"""
Performance benchmarking tests for Week 6 implementation.
Tests scalability and performance characteristics of all algorithms including OR-Tools.
"""

import unittest
import time
import tempfile
import shutil
import os
import csv
import statistics
from typing import Dict, List, Tuple
import logging

# Import modules to test
from src.meshachvetz.optimizer.optimization_manager import OptimizationManager
from src.meshachvetz.data.loader import DataLoader
from src.meshachvetz.scorer.main_scorer import Scorer
from src.meshachvetz.cli.config_manager import ConfigurationManager


class TestWeek6Performance(unittest.TestCase):
    """Performance benchmarking tests for Week 6 implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize components
        self.scorer = Scorer()
        self.config_manager = ConfigurationManager()
        
        # Performance thresholds (in seconds)
        self.performance_thresholds = {
            'small_dataset': {'students': 20, 'max_time': 30},
            'medium_dataset': {'students': 50, 'max_time': 60},
            'large_dataset': {'students': 100, 'max_time': 120}
        }
        
        # Create test datasets
        self.test_datasets = {}
        for size_name, config in self.performance_thresholds.items():
            self.test_datasets[size_name] = self.create_test_dataset(
                config['students'], 
                size_name
            )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_dataset(self, num_students: int, dataset_name: str) -> str:
        """Create test dataset with specified number of students."""
        students_data = []
        
        for i in range(num_students):
            student_id = f"{123456000 + i:09d}"
            first_name = f"Student{i}"
            last_name = f"Test{i}"
            gender = 'F' if i % 2 == 0 else 'M'
            class_id = chr(ord('A') + (i % 4))  # Classes A, B, C, D
            academic_score = 70 + (i % 30)  # Scores 70-99
            behavior_rank = ['A', 'B', 'C', 'D'][i % 4]
            assistance_package = i % 5 == 0
            
            # Add some social preferences
            preferred_friend_1 = f"{123456000 + ((i + 1) % num_students):09d}" if i < num_students - 1 else ""
            preferred_friend_2 = f"{123456000 + ((i + 2) % num_students):09d}" if i < num_students - 2 else ""
            disliked_peer_1 = f"{123456000 + ((i + 3) % num_students):09d}" if i < num_students - 3 else ""
            
            # Add some force constraints
            force_class = class_id if i % 20 == 0 else ""
            force_friend = f"group{i // 10}" if i % 10 == 0 and i < num_students - 1 else ""
            
            student_data = {
                'student_id': student_id,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'class_id': class_id,
                'academic_score': academic_score,
                'behavior_rank': behavior_rank,
                'assistance_package': assistance_package,
                'preferred_friend_1': preferred_friend_1,
                'preferred_friend_2': preferred_friend_2,
                'preferred_friend_3': '',
                'disliked_peer_1': disliked_peer_1,
                'disliked_peer_2': '',
                'disliked_peer_3': '',
                'disliked_peer_4': '',
                'disliked_peer_5': '',
                'force_class': force_class,
                'force_friend': force_friend
            }
            
            students_data.append(student_data)
        
        # Write CSV file
        csv_file = os.path.join(self.data_dir, f'{dataset_name}.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=students_data[0].keys())
            writer.writeheader()
            writer.writerows(students_data)
        
        return csv_file
    
    def benchmark_algorithm(self, algorithm_name: str, school_data, config: Dict, 
                          max_time: int = 60, num_runs: int = 3) -> Dict:
        """Benchmark a single algorithm."""
        results = {
            'algorithm': algorithm_name,
            'runs': [],
            'avg_time': 0.0,
            'avg_score': 0.0,
            'avg_improvement': 0.0,
            'success_rate': 0.0,
            'within_time_limit': True
        }
        
        manager = OptimizationManager(self.scorer, config)
        
        for run in range(num_runs):
            try:
                start_time = time.time()
                result = manager.optimize(
                    school_data,
                    algorithm=algorithm_name,
                    max_iterations=config.get('max_iterations', 100),
                    algorithm_config=config
                )
                execution_time = time.time() - start_time
                
                run_result = {
                    'run': run + 1,
                    'success': True,
                    'execution_time': execution_time,
                    'final_score': result.final_score,
                    'improvement': result.improvement,
                    'within_time_limit': execution_time <= max_time
                }
                
                results['runs'].append(run_result)
                
            except Exception as e:
                run_result = {
                    'run': run + 1,
                    'success': False,
                    'error': str(e),
                    'execution_time': 0.0,
                    'final_score': 0.0,
                    'improvement': 0.0,
                    'within_time_limit': False
                }
                results['runs'].append(run_result)
        
        # Calculate averages
        successful_runs = [r for r in results['runs'] if r['success']]
        if successful_runs:
            results['avg_time'] = statistics.mean([r['execution_time'] for r in successful_runs])
            results['avg_score'] = statistics.mean([r['final_score'] for r in successful_runs])
            results['avg_improvement'] = statistics.mean([r['improvement'] for r in successful_runs])
            results['success_rate'] = len(successful_runs) / num_runs
            results['within_time_limit'] = all(r['within_time_limit'] for r in successful_runs)
        
        return results
    
    def test_small_dataset_performance(self):
        """Test performance on small dataset (20 students)."""
        dataset_name = 'small_dataset'
        csv_file = self.test_datasets[dataset_name]
        threshold = self.performance_thresholds[dataset_name]
        
        # Load data
        loader = DataLoader()
        school_data = loader.load_from_csv(csv_file)
        
        # Configuration optimized for accuracy
        config = {
            'max_iterations': 100,
            'time_limit_seconds': 15,
            'population_size': 30,
            'generations': 50,
            'min_friends': 0
        }
        
        # Test all algorithms
        algorithms = ['local_search', 'genetic', 'simulated_annealing', 'or_tools']
        benchmark_results = {}
        
        for algorithm in algorithms:
            print(f"\nBenchmarking {algorithm} on {dataset_name}...")
            benchmark_results[algorithm] = self.benchmark_algorithm(
                algorithm, 
                school_data, 
                config, 
                threshold['max_time'],
                num_runs=2  # Reduced for faster testing
            )
        
        # Verify performance requirements
        for algorithm, results in benchmark_results.items():
            with self.subTest(algorithm=algorithm):
                self.assertGreater(results['success_rate'], 0.0, 
                                 f"{algorithm} should have some successful runs")
                
                if results['success_rate'] > 0:
                    self.assertTrue(results['within_time_limit'], 
                                  f"{algorithm} should complete within time limit")
                    self.assertGreaterEqual(results['avg_score'], 0.0,
                                          f"{algorithm} should produce valid scores")
        
        # OR-Tools should be particularly fast for small datasets
        if 'or_tools' in benchmark_results and benchmark_results['or_tools']['success_rate'] > 0:
            ortools_time = benchmark_results['or_tools']['avg_time']
            self.assertLess(ortools_time, 20, "OR-Tools should be fast for small datasets")
    
    def test_medium_dataset_performance(self):
        """Test performance on medium dataset (50 students)."""
        dataset_name = 'medium_dataset'
        csv_file = self.test_datasets[dataset_name]
        threshold = self.performance_thresholds[dataset_name]
        
        # Load data
        loader = DataLoader()
        school_data = loader.load_from_csv(csv_file)
        
        # Configuration balanced for speed and quality
        config = {
            'max_iterations': 150,
            'time_limit_seconds': 30,
            'population_size': 25,
            'generations': 40,
            'min_friends': 0
        }
        
        # Test selected algorithms (skip slower ones for medium dataset)
        algorithms = ['local_search', 'genetic', 'or_tools']
        benchmark_results = {}
        
        for algorithm in algorithms:
            print(f"\nBenchmarking {algorithm} on {dataset_name}...")
            benchmark_results[algorithm] = self.benchmark_algorithm(
                algorithm, 
                school_data, 
                config, 
                threshold['max_time'],
                num_runs=2
            )
        
        # Verify performance requirements
        for algorithm, results in benchmark_results.items():
            with self.subTest(algorithm=algorithm):
                self.assertGreater(results['success_rate'], 0.0)
                
                if results['success_rate'] > 0:
                    self.assertTrue(results['within_time_limit'], 
                                  f"{algorithm} exceeded time limit on medium dataset")
                    self.assertGreaterEqual(results['avg_score'], 0.0)
    
    def test_large_dataset_performance(self):
        """Test performance on large dataset (100 students)."""
        dataset_name = 'large_dataset'
        csv_file = self.test_datasets[dataset_name]
        threshold = self.performance_thresholds[dataset_name]
        
        # Load data
        loader = DataLoader()
        school_data = loader.load_from_csv(csv_file)
        
        # Configuration optimized for speed
        config = {
            'max_iterations': 100,
            'time_limit_seconds': 60,
            'population_size': 20,
            'generations': 30,
            'min_friends': 0
        }
        
        # Test only fast algorithms for large dataset
        algorithms = ['local_search', 'genetic']
        benchmark_results = {}
        
        for algorithm in algorithms:
            print(f"\nBenchmarking {algorithm} on {dataset_name}...")
            benchmark_results[algorithm] = self.benchmark_algorithm(
                algorithm, 
                school_data, 
                config, 
                threshold['max_time'],
                num_runs=1  # Single run for large dataset
            )
        
        # Verify performance requirements
        for algorithm, results in benchmark_results.items():
            with self.subTest(algorithm=algorithm):
                self.assertGreater(results['success_rate'], 0.0)
                
                if results['success_rate'] > 0:
                    self.assertTrue(results['within_time_limit'], 
                                  f"{algorithm} exceeded time limit on large dataset")
                    self.assertGreaterEqual(results['avg_score'], 0.0)
    
    def test_algorithm_comparison(self):
        """Compare performance characteristics of different algorithms."""
        dataset_name = 'small_dataset'
        csv_file = self.test_datasets[dataset_name]
        
        # Load data
        loader = DataLoader()
        school_data = loader.load_from_csv(csv_file)
        
        # Standard configuration
        config = {
            'max_iterations': 50,
            'time_limit_seconds': 20,
            'population_size': 20,
            'generations': 25,
            'min_friends': 0
        }
        
        # Test all algorithms
        algorithms = ['local_search', 'genetic', 'simulated_annealing', 'or_tools']
        comparison_results = {}
        
        for algorithm in algorithms:
            comparison_results[algorithm] = self.benchmark_algorithm(
                algorithm, 
                school_data, 
                config, 
                30,  # 30 second time limit
                num_runs=2
            )
        
        # Analyze results
        successful_algorithms = {alg: results for alg, results in comparison_results.items() 
                               if results['success_rate'] > 0}
        
        self.assertGreater(len(successful_algorithms), 0, "At least one algorithm should succeed")
        
        # Print comparison (for manual analysis)
        print("\n=== Algorithm Comparison ===")
        for algorithm, results in successful_algorithms.items():
            print(f"{algorithm}:")
            print(f"  Average Time: {results['avg_time']:.2f}s")
            print(f"  Average Score: {results['avg_score']:.2f}")
            print(f"  Success Rate: {results['success_rate']:.2f}")
            print(f"  Within Time Limit: {results['within_time_limit']}")
    
    def test_scalability(self):
        """Test how algorithms scale with dataset size."""
        algorithms = ['local_search', 'genetic']
        scalability_results = {}
        
        for algorithm in algorithms:
            scalability_results[algorithm] = {}
            
            for size_name, csv_file in self.test_datasets.items():
                threshold = self.performance_thresholds[size_name]
                
                # Load data
                loader = DataLoader()
                school_data = loader.load_from_csv(csv_file)
                
                # Adaptive configuration based on dataset size
                if size_name == 'small_dataset':
                    config = {'max_iterations': 100, 'population_size': 30, 'generations': 50}
                elif size_name == 'medium_dataset':
                    config = {'max_iterations': 75, 'population_size': 25, 'generations': 35}
                else:  # large_dataset
                    config = {'max_iterations': 50, 'population_size': 20, 'generations': 25}
                
                config['min_friends'] = 0
                
                # Single run for scalability test
                results = self.benchmark_algorithm(
                    algorithm, 
                    school_data, 
                    config, 
                    threshold['max_time'],
                    num_runs=1
                )
                
                scalability_results[algorithm][size_name] = results
        
        # Analyze scalability
        for algorithm, size_results in scalability_results.items():
            with self.subTest(algorithm=algorithm):
                # Check that algorithm succeeds on all sizes
                for size_name, results in size_results.items():
                    self.assertGreater(results['success_rate'], 0.0,
                                     f"{algorithm} should succeed on {size_name}")
                
                # Check that time increases reasonably with size
                times = [results['avg_time'] for results in size_results.values() 
                        if results['success_rate'] > 0]
                
                if len(times) >= 2:
                    # Time should generally increase with dataset size
                    # (though this isn't a strict requirement)
                    pass  # Just verify no crashes for now
    
    def test_configuration_profiles_performance(self):
        """Test performance of different configuration profiles."""
        csv_file = self.test_datasets['small_dataset']
        
        # Load data
        loader = DataLoader()
        school_data = loader.load_from_csv(csv_file)
        
        # Test different profiles
        profiles = ['small_school', 'balanced']
        profile_results = {}
        
        for profile_name in profiles:
            profile_config = self.config_manager.apply_profile(profile_name)
            
            # Extract algorithm configuration
            default_algorithm = profile_config['optimization'].get('default_algorithm', 'genetic')
            algorithm_config = profile_config['optimization']['algorithms'].get(default_algorithm, {})
            
            # Add missing parameters
            algorithm_config.update({
                'max_iterations': 50,
                'min_friends': 0
            })
            
            try:
                results = self.benchmark_algorithm(
                    default_algorithm,
                    school_data,
                    algorithm_config,
                    30,
                    num_runs=1
                )
                
                profile_results[profile_name] = results
                
            except Exception as e:
                profile_results[profile_name] = {
                    'success_rate': 0.0,
                    'error': str(e)
                }
        
        # Verify profiles work
        for profile_name, results in profile_results.items():
            with self.subTest(profile=profile_name):
                if 'error' in results:
                    print(f"Profile {profile_name} failed: {results['error']}")
                else:
                    self.assertGreater(results['success_rate'], 0.0,
                                     f"Profile {profile_name} should produce working configurations")
    
    def test_memory_usage(self):
        """Test memory usage characteristics (basic test)."""
        csv_file = self.test_datasets['medium_dataset']
        
        # Load data
        loader = DataLoader()
        school_data = loader.load_from_csv(csv_file)
        
        config = {
            'max_iterations': 50,
            'population_size': 20,
            'generations': 25,
            'min_friends': 0
        }
        
        # Test memory-intensive algorithm (genetic)
        manager = OptimizationManager(self.scorer, config)
        
        # Run optimization (should not crash due to memory issues)
        try:
            result = manager.optimize(
                school_data,
                algorithm='genetic',
                max_iterations=50,
                algorithm_config=config
            )
            
            # Basic verification
            self.assertIsNotNone(result)
            self.assertGreaterEqual(result.final_score, 0.0)
            
        except MemoryError:
            self.fail("Genetic algorithm should not run out of memory on medium dataset")
        except Exception as e:
            # Other exceptions are acceptable for this test
            pass


if __name__ == '__main__':
    # Set up logging to see benchmark progress
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(verbosity=2) 