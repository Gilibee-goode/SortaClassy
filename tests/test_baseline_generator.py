#!/usr/bin/env python3
"""
Tests for Baseline Generator functionality.
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
import sys
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz.optimizer.baseline_generator import BaselineGenerator, BaselineStatistics, BaselineRun
from meshachvetz.optimizer.base_optimizer import OptimizationResult
from meshachvetz.data.models import SchoolData, Student, ClassData
from meshachvetz.scorer.main_scorer import Scorer
from meshachvetz.utils.config import Config


class TestBaselineRun(unittest.TestCase):
    """Test BaselineRun class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock optimization result
        self.mock_result = Mock(spec=OptimizationResult)
        self.mock_result.initial_score = 75.0
        self.mock_result.final_score = 80.0
        self.mock_result.improvement = 5.0
        self.mock_result.improvement_percentage = 6.67
        self.mock_result.score_history = [75.0, 77.0, 79.0, 80.0]
        
        self.run = BaselineRun(
            run_number=1,
            result=self.mock_result,
            duration=10.0,
            iterations_used=100
        )
    
    def test_baseline_run_initialization(self):
        """Test BaselineRun initialization."""
        self.assertEqual(self.run.run_number, 1)
        self.assertEqual(self.run.result, self.mock_result)
        self.assertEqual(self.run.duration, 10.0)
        self.assertEqual(self.run.iterations_used, 100)
        
        # Check extracted metrics
        self.assertEqual(self.run.initial_score, 75.0)
        self.assertEqual(self.run.final_score, 80.0)
        self.assertEqual(self.run.improvement, 5.0)
        self.assertEqual(self.run.improvement_percentage, 6.67)
        
        # Check derived metrics
        self.assertEqual(self.run.iterations_per_second, 10.0)  # 100 / 10.0
        self.assertEqual(self.run.score_per_second, 0.5)  # 5.0 / 10.0


class TestBaselineStatistics(unittest.TestCase):
    """Test BaselineStatistics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock baseline runs
        self.runs = []
        for i in range(5):
            mock_result = Mock(spec=OptimizationResult)
            mock_result.initial_score = 75.0
            mock_result.final_score = 80.0 + i  # Varying final scores
            mock_result.improvement = 5.0 + i
            mock_result.improvement_percentage = 6.67 + i
            mock_result.score_history = [75.0] * (10 + i)
            
            run = BaselineRun(
                run_number=i + 1,
                result=mock_result,
                duration=10.0 + i,
                iterations_used=100 + i * 10
            )
            self.runs.append(run)
        
        self.stats = BaselineStatistics(self.runs)
    
    def test_statistics_initialization(self):
        """Test BaselineStatistics initialization."""
        self.assertEqual(self.stats.run_count, 5)
        self.assertEqual(len(self.stats.final_scores), 5)
        self.assertEqual(len(self.stats.improvements), 5)
        self.assertEqual(len(self.stats.improvement_percentages), 5)
        self.assertEqual(len(self.stats.durations), 5)
        self.assertEqual(len(self.stats.iterations_used), 5)
    
    def test_statistics_calculations(self):
        """Test statistical calculations."""
        # Test final scores (80, 81, 82, 83, 84)
        self.assertEqual(self.stats.final_score_mean, 82.0)
        self.assertEqual(self.stats.final_score_median, 82.0)
        self.assertEqual(self.stats.final_score_min, 80.0)
        self.assertEqual(self.stats.final_score_max, 84.0)
        
        # Test improvements (5, 6, 7, 8, 9)
        self.assertEqual(self.stats.improvement_mean, 7.0)
        self.assertEqual(self.stats.improvement_median, 7.0)
        self.assertEqual(self.stats.improvement_min, 5.0)
        self.assertEqual(self.stats.improvement_max, 9.0)
        
        # Test durations (10, 11, 12, 13, 14)
        self.assertEqual(self.stats.duration_mean, 12.0)
        self.assertEqual(self.stats.duration_median, 12.0)
        self.assertEqual(self.stats.duration_min, 10.0)
        self.assertEqual(self.stats.duration_max, 14.0)
    
    def test_get_summary(self):
        """Test get_summary method."""
        summary = self.stats.get_summary()
        
        self.assertIn('run_count', summary)
        self.assertIn('final_score', summary)
        self.assertIn('improvement', summary)
        self.assertIn('improvement_percentage', summary)
        self.assertIn('duration', summary)
        self.assertIn('iterations', summary)
        
        # Check structure
        self.assertIn('mean', summary['final_score'])
        self.assertIn('median', summary['final_score'])
        self.assertIn('stdev', summary['final_score'])
        self.assertIn('min', summary['final_score'])
        self.assertIn('max', summary['final_score'])


class TestBaselineGenerator(unittest.TestCase):
    """Test BaselineGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create school data with proper initialization
        students = {}
        classes = {}
        
        # Add students
        for i in range(20):
            student = Student(
                student_id=f"{i+1:09d}",
                first_name=f"Student{i}",
                last_name="Test",
                gender="M" if i % 2 == 0 else "F",
                academic_score=85.0 + (i % 10),
                behavior_rank="A" if i % 4 == 0 else "B",
                studentiality_rank="A" if i % 3 == 0 else "B",
                assistance_package=i % 5 == 0,
                class_id=f"Class{i % 4}"
            )
            students[student.student_id] = student
        
        # Add classes and assign students
        for i in range(4):
            class_id = f"Class{i}"
            class_students = [s for s in students.values() if s.class_id == class_id]
            class_data = ClassData(class_id=class_id, students=class_students)
            classes[class_id] = class_data
        
        self.school_data = SchoolData(classes=classes, students=students)
        
        # Create mock scorer
        self.mock_scorer = Mock(spec=Scorer)
        
        # Create baseline generator
        self.generator = BaselineGenerator(
            scorer=self.mock_scorer,
            config={
                'num_runs': 3,
                'max_iterations_per_run': 50,
                'log_level': 'minimal'
            }
        )
        
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generator_initialization(self):
        """Test BaselineGenerator initialization."""
        self.assertEqual(self.generator.scorer, self.mock_scorer)
        self.assertEqual(self.generator.num_runs, 3)
        self.assertEqual(self.generator.max_iterations_per_run, 50)
        self.assertEqual(len(self.generator.runs), 0)
        self.assertIsNone(self.generator.statistics)
    
    def test_get_baseline_config(self):
        """Test get_baseline_config method."""
        config = self.generator.get_baseline_config()
        
        self.assertIn('num_runs', config)
        self.assertIn('max_iterations_per_run', config)
        self.assertIn('log_level', config)
        self.assertIn('min_friends_required', config)
        self.assertIn('respect_force_constraints', config)
        self.assertIn('early_stop_threshold', config)
        self.assertIn('accept_neutral_moves', config)
        
        self.assertEqual(config['num_runs'], 3)
        self.assertEqual(config['max_iterations_per_run'], 50)
        self.assertEqual(config['log_level'], 'minimal')
    
    @patch('meshachvetz.optimizer.baseline_generator.RandomSwapOptimizer')
    def test_generate_baseline(self, mock_optimizer_class):
        """Test generate_baseline method."""
        # Mock the optimizer
        mock_optimizer = Mock()
        mock_optimizer_class.return_value = mock_optimizer
        
        # Mock optimization results
        mock_results = []
        for i in range(3):
            mock_result = Mock(spec=OptimizationResult)
            mock_result.initial_score = 75.0
            mock_result.final_score = 80.0 + i
            mock_result.improvement = 5.0 + i
            mock_result.improvement_percentage = 6.67 + i
            mock_result.score_history = [75.0] * (10 + i)
            mock_results.append(mock_result)
        
        mock_optimizer.optimize.side_effect = mock_results
        
        # Run baseline generation
        statistics = self.generator.generate_baseline(self.school_data)
        
        # Verify results
        self.assertIsNotNone(statistics)
        self.assertEqual(len(self.generator.runs), 3)
        self.assertEqual(statistics.run_count, 3)
        
        # Verify optimizer was called correctly
        self.assertEqual(mock_optimizer.optimize.call_count, 3)
        
        # Check first call arguments
        first_call = mock_optimizer.optimize.call_args_list[0]
        self.assertEqual(first_call[0][0], self.school_data)
        self.assertEqual(first_call[0][1], 50)  # max_iterations_per_run
    
    def test_save_baseline_report(self):
        """Test save_baseline_report method."""
        # Generate some baseline data first
        self.generator.runs = []
        for i in range(3):
            mock_result = Mock(spec=OptimizationResult)
            mock_result.initial_score = 75.0
            mock_result.final_score = 80.0 + i
            mock_result.improvement = 5.0 + i
            mock_result.improvement_percentage = 6.67 + i
            mock_result.score_history = [75.0] * (10 + i)
            
            run = BaselineRun(
                run_number=i + 1,
                result=mock_result,
                duration=10.0 + i,
                iterations_used=100 + i * 10
            )
            self.generator.runs.append(run)
        
        self.generator.statistics = BaselineStatistics(self.generator.runs)
        
        # Save report
        csv_file, summary_file = self.generator.save_baseline_report(
            self.temp_dir, 
            "test_baseline"
        )
        
        # Verify files were created
        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(os.path.exists(summary_file))
        
        # Check CSV content
        with open(csv_file, 'r') as f:
            csv_content = f.read()
            self.assertIn('Run,Initial Score,Final Score', csv_content)
            self.assertIn('1,75.00,80.00', csv_content)
            self.assertIn('2,75.00,81.00', csv_content)
            self.assertIn('3,75.00,82.00', csv_content)
        
        # Check summary content
        with open(summary_file, 'r') as f:
            summary_content = f.read()
            self.assertIn('MESHACHVETZ BASELINE PERFORMANCE REPORT', summary_content)
            self.assertIn('Random Swap', summary_content)
            self.assertIn('FINAL SCORES', summary_content)
            self.assertIn('IMPROVEMENTS', summary_content)
            self.assertIn('PERFORMANCE', summary_content)
    
    def test_compare_to_baseline(self):
        """Test compare_to_baseline method."""
        # Set up baseline statistics
        self.generator.runs = []
        for i in range(3):
            mock_result = Mock(spec=OptimizationResult)
            mock_result.initial_score = 75.0
            mock_result.final_score = 80.0 + i
            mock_result.improvement = 5.0 + i
            mock_result.improvement_percentage = 6.67 + i
            mock_result.score_history = [75.0] * (10 + i)
            
            run = BaselineRun(
                run_number=i + 1,
                result=mock_result,
                duration=10.0 + i,
                iterations_used=100 + i * 10
            )
            self.generator.runs.append(run)
        
        self.generator.statistics = BaselineStatistics(self.generator.runs)
        
        # Create a result to compare
        other_result = Mock(spec=OptimizationResult)
        other_result.final_score = 85.0  # Better than baseline
        other_result.improvement = 10.0
        other_result.improvement_percentage = 12.0
        
        # Compare to baseline
        comparison = self.generator.compare_to_baseline(other_result, "Test Algorithm")
        
        # Check comparison results
        self.assertEqual(comparison['algorithm_name'], "Test Algorithm")
        self.assertEqual(comparison['baseline_algorithm'], "Random Swap")
        self.assertEqual(comparison['baseline_runs'], 3)
        self.assertEqual(comparison['other_final_score'], 85.0)
        self.assertEqual(comparison['baseline_mean_score'], 81.0)
        self.assertEqual(comparison['score_difference'], 4.0)  # 85.0 - 81.0
        self.assertTrue(comparison['is_better_than_baseline'])
        self.assertTrue(comparison['is_better_than_median'])
        self.assertTrue(comparison['is_better_than_best'])
    
    def test_compare_to_baseline_no_statistics(self):
        """Test compare_to_baseline raises error when no statistics available."""
        other_result = Mock(spec=OptimizationResult)
        other_result.final_score = 85.0
        other_result.improvement = 10.0
        
        with self.assertRaises(ValueError) as context:
            self.generator.compare_to_baseline(other_result, "Test Algorithm")
        
        self.assertIn("No baseline statistics available", str(context.exception))


class TestBaselineGeneratorIntegration(unittest.TestCase):
    """Integration tests for BaselineGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create real school data with proper initialization
        students = {}
        classes = {}
        
        # Add students with some social preferences
        for i in range(12):
            student = Student(
                student_id=f"{i+1:09d}",
                first_name=f"Student{i+1}",
                last_name="Test",
                gender="M" if i % 2 == 0 else "F",
                academic_score=85.0 + (i % 10),
                behavior_rank="A" if i % 4 == 0 else "B",
                studentiality_rank="A" if i % 3 == 0 else "B",
                assistance_package=i % 5 == 0,
                class_id=f"Class{(i % 3) + 1}"
            )
            
            # Add some social preferences
            if i < 9:  # First 9 students have preferences
                student.preferred_friend_1 = f"{((i+1) % 9) + 1:09d}"
                if i < 6:
                    student.preferred_friend_2 = f"{((i+2) % 9) + 1:09d}"
                if i < 3:
                    student.disliked_peer_1 = f"{((i+6) % 9) + 1:09d}"
            
            students[student.student_id] = student
        
        # Add classes and assign students
        for i in range(3):
            class_id = f"Class{i+1}"
            class_students = [s for s in students.values() if s.class_id == class_id]
            class_data = ClassData(class_id=class_id, students=class_students)
            classes[class_id] = class_data
        
        self.school_data = SchoolData(classes=classes, students=students)
        
        # Create real scorer
        config = Config()
        self.scorer = Scorer(config)
        
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_real_baseline_generation(self):
        """Test baseline generation with real data and scorer."""
        # Create baseline generator with minimal runs for testing
        generator = BaselineGenerator(
            scorer=self.scorer,
            config={
                'num_runs': 2,
                'max_iterations_per_run': 20,
                'log_level': 'minimal'
            }
        )
        
        # Generate baseline
        statistics = generator.generate_baseline(self.school_data)
        
        # Verify results
        self.assertIsNotNone(statistics)
        self.assertEqual(statistics.run_count, 2)
        self.assertEqual(len(generator.runs), 2)
        
        # Check that scores are reasonable
        self.assertGreater(statistics.final_score_mean, 0)
        self.assertGreaterEqual(statistics.improvement_mean, 0)
        self.assertGreater(statistics.duration_mean, 0)
        
        # Save and verify reports
        csv_file, summary_file = generator.save_baseline_report(
            self.temp_dir, 
            "integration_test"
        )
        
        self.assertTrue(os.path.exists(csv_file))
        self.assertTrue(os.path.exists(summary_file))
        
        # Verify CSV structure
        with open(csv_file, 'r') as f:
            lines = f.readlines()
            self.assertGreaterEqual(len(lines), 3)  # Header + 2 runs
            header = lines[0].strip()
            self.assertIn('Run', header)
            self.assertIn('Initial Score', header)
            self.assertIn('Final Score', header)


if __name__ == '__main__':
    unittest.main() 