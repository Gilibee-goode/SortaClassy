#!/usr/bin/env python3
"""
Comprehensive tests for the enhanced iteration logging system.

Tests all log levels, progress tracking, and CLI integration.
"""

import pytest
import sys
import os
import time
import io
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz.utils.logging import (
    LogLevel, ProgressMetrics, ProgressTracker, IterationLogger,
    create_iteration_logger, get_available_log_levels
)
from meshachvetz.data.loader import DataLoader
from meshachvetz.scorer.main_scorer import Scorer
from meshachvetz.optimizer.genetic import GeneticOptimizer
from meshachvetz.optimizer.local_search import LocalSearchOptimizer


class TestLogLevel:
    """Test log level enumeration."""
    
    def test_log_level_values(self):
        """Test that log levels have correct values."""
        assert LogLevel.MINIMAL.value == "minimal"
        assert LogLevel.NORMAL.value == "normal"
        assert LogLevel.DETAILED.value == "detailed"
        assert LogLevel.DEBUG.value == "debug"
    
    def test_get_available_log_levels(self):
        """Test getting available log levels."""
        levels = get_available_log_levels()
        assert "minimal" in levels
        assert "normal" in levels
        assert "detailed" in levels
        assert "debug" in levels
        assert len(levels) == 4


class TestProgressMetrics:
    """Test progress metrics calculations."""
    
    def test_progress_metrics_initialization(self):
        """Test progress metrics initialization."""
        metrics = ProgressMetrics(
            total_iterations=100,
            initial_score=50.0,
            current_score=60.0,
            best_score=65.0
        )
        
        assert metrics.total_iterations == 100
        assert metrics.initial_score == 50.0
        assert metrics.current_score == 60.0
        assert metrics.best_score == 65.0
    
    def test_progress_percentage_calculation(self):
        """Test progress percentage calculation."""
        metrics = ProgressMetrics(current_iteration=25, total_iterations=100)
        assert metrics.progress_percentage == 25.0
        
        metrics = ProgressMetrics(current_iteration=0, total_iterations=100)
        assert metrics.progress_percentage == 0.0
        
        metrics = ProgressMetrics(current_iteration=100, total_iterations=100)
        assert metrics.progress_percentage == 100.0
    
    def test_time_estimation(self):
        """Test time estimation calculations."""
        start_time = time.time()
        metrics = ProgressMetrics(
            current_iteration=50,
            total_iterations=100,
            start_time=start_time - 10  # 10 seconds ago
        )
        
        assert metrics.elapsed_time >= 10.0
        assert metrics.estimated_total_time >= 20.0
        assert metrics.estimated_remaining_time >= 10.0
    
    def test_stagnation_count(self):
        """Test stagnation count calculation."""
        metrics = ProgressMetrics(
            current_iteration=50,
            last_improvement_iteration=30
        )
        
        assert metrics.stagnation_count == 20
    
    def test_format_time(self):
        """Test time formatting."""
        metrics = ProgressMetrics()
        
        assert metrics.format_time(30) == "30.0s"
        assert metrics.format_time(90) == "1.5m"
        assert metrics.format_time(3660) == "1.0h"


class TestProgressTracker:
    """Test progress tracker functionality."""
    
    def test_progress_tracker_initialization(self):
        """Test progress tracker initialization."""
        tracker = ProgressTracker(LogLevel.NORMAL, "TestAlgorithm")
        
        assert tracker.log_level == LogLevel.NORMAL
        assert tracker.algorithm_name == "TestAlgorithm"
        assert tracker.display_interval == 1.0
        assert tracker.log_percentage_interval == 10
    
    def test_start_optimization(self):
        """Test optimization start tracking."""
        tracker = ProgressTracker(LogLevel.NORMAL)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tracker.start_optimization(50.0, 100)
            output = mock_stdout.getvalue()
            
            assert "Starting Optimizer optimization" in output
            assert "Initial score: 50.00/100" in output
            assert "Target iterations: 100" in output
        
        assert tracker.metrics.initial_score == 50.0
        assert tracker.metrics.total_iterations == 100
    
    def test_update_iteration_with_improvement(self):
        """Test iteration update with score improvement."""
        tracker = ProgressTracker(LogLevel.DETAILED)
        tracker.start_optimization(50.0, 100)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tracker.update_iteration(10, 55.0)
            output = mock_stdout.getvalue()
            
            # Should log improvement
            assert "New best score 55.00" in output
        
        assert tracker.metrics.current_iteration == 10
        assert tracker.metrics.current_score == 55.0
        assert tracker.metrics.best_score == 55.0
    
    def test_finish_optimization(self):
        """Test optimization finish tracking."""
        tracker = ProgressTracker(LogLevel.NORMAL)
        tracker.start_optimization(50.0, 100)
        
        # Simulate some progress
        tracker.update_iteration(50, 60.0)
        tracker.update_iteration(100, 70.0)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tracker.finish_optimization(70.0, 100)
            output = mock_stdout.getvalue()
            
            assert "Optimizer completed!" in output
            assert "Final score: 70.00/100" in output
            assert "Improvement: +20.00" in output
    
    def test_minimal_log_level_output(self):
        """Test minimal log level produces minimal output."""
        tracker = ProgressTracker(LogLevel.MINIMAL)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tracker.start_optimization(50.0, 100)
            tracker.update_iteration(10, 55.0)
            tracker.update_iteration(50, 60.0)
            tracker.finish_optimization(60.0, 100)
            
            output = mock_stdout.getvalue()
            
            # Should only have finish message
            assert "completed!" in output
            assert "Starting" not in output
    
    def test_detailed_log_level_output(self):
        """Test detailed log level produces detailed output."""
        tracker = ProgressTracker(LogLevel.DETAILED)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            tracker.start_optimization(50.0, 100)
            tracker.update_iteration(10, 55.0)  # Should log improvement
            tracker.update_iteration(50, 60.0)  # Should log improvement
            tracker.finish_optimization(60.0, 100)
            
            output = mock_stdout.getvalue()
            
            # Should have detailed output
            assert "Starting" in output
            assert "New best score" in output
            assert "completed!" in output


class TestIterationLogger:
    """Test iteration logger functionality."""
    
    def test_iteration_logger_initialization(self):
        """Test iteration logger initialization."""
        logger = IterationLogger(LogLevel.NORMAL, "TestAlgorithm")
        
        assert logger.log_level == LogLevel.NORMAL
        assert logger.algorithm_name == "TestAlgorithm"
        assert logger.progress_tracker is not None
    
    def test_create_iteration_logger(self):
        """Test iteration logger creation function."""
        logger = create_iteration_logger("detailed", "TestAlgorithm")
        
        assert logger.log_level == LogLevel.DETAILED
        assert logger.algorithm_name == "TestAlgorithm"
    
    def test_create_iteration_logger_invalid_level(self):
        """Test iteration logger creation with invalid level."""
        logger = create_iteration_logger("invalid", "TestAlgorithm")
        
        # Should default to NORMAL
        assert logger.log_level == LogLevel.NORMAL
    
    def test_log_methods(self):
        """Test different log methods."""
        logger = IterationLogger(LogLevel.DEBUG, "TestAlgorithm")
        
        # These should not raise exceptions
        logger.log_debug("Debug message")
        logger.log_info("Info message")
        logger.log_warning("Warning message")
        logger.log_error("Error message")
    
    def test_optimization_workflow(self):
        """Test complete optimization workflow."""
        logger = IterationLogger(LogLevel.NORMAL, "TestAlgorithm")
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            logger.start_optimization(50.0, 100)
            logger.log_iteration(10, 55.0, {"test_metric": 1.5})
            logger.log_iteration(50, 60.0, {"test_metric": 2.0})
            logger.finish_optimization(60.0, 100)
            
            output = mock_stdout.getvalue()
            
            # Should have optimization messages
            assert "Starting" in output
            assert "completed!" in output


class TestEnhancedLoggingIntegration:
    """Test integration with optimizer classes."""
    
    def setup_method(self):
        """Set up test data."""
        self.sample_data_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "examples", 
            "sample_data", 
            "students_sample.csv"
        )
        
        if not os.path.exists(self.sample_data_path):
            pytest.skip(f"Sample data not found at {self.sample_data_path}")
    
    def test_genetic_optimizer_with_enhanced_logging(self):
        """Test genetic optimizer with enhanced logging."""
        # Load test data
        loader = DataLoader()
        school_data = loader.load_csv(self.sample_data_path)
        
        # Create scorer and optimizer
        scorer = Scorer()
        config = {
            'log_level': 'detailed',
            'population_size': 10,
            'max_generations': 5  # Small for testing
        }
        
        optimizer = GeneticOptimizer(scorer, config)
        
        # Test optimization with enhanced logging
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = optimizer.optimize(school_data, max_iterations=5)
            output = mock_stdout.getvalue()
            
            # Should have enhanced logging output
            assert "Starting" in output
            assert "completed!" in output
            assert result is not None
            assert result.algorithm_name == "Genetic Algorithm"
    
    def test_local_search_with_enhanced_logging(self):
        """Test local search optimizer with enhanced logging."""
        # Load test data
        loader = DataLoader()
        school_data = loader.load_csv(self.sample_data_path)
        
        # Create scorer and optimizer
        scorer = Scorer()
        config = {
            'log_level': 'normal',
            'max_passes': 2  # Small for testing
        }
        
        optimizer = LocalSearchOptimizer(scorer, config)
        
        # Test optimization with enhanced logging
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = optimizer.optimize(school_data, max_iterations=10)
            output = mock_stdout.getvalue()
            
            # Should have enhanced logging output
            assert "Starting" in output
            assert "completed!" in output
            assert result is not None
            assert result.algorithm_name == "Local Search"
    
    def test_different_log_levels_produce_different_output(self):
        """Test that different log levels produce different amounts of output."""
        # Load test data
        loader = DataLoader()
        school_data = loader.load_csv(self.sample_data_path)
        scorer = Scorer()
        
        # Test with minimal logging
        config_minimal = {'log_level': 'minimal'}
        optimizer_minimal = LocalSearchOptimizer(scorer, config_minimal)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result_minimal = optimizer_minimal.optimize(school_data, max_iterations=5)
            output_minimal = mock_stdout.getvalue()
        
        # Test with detailed logging
        config_detailed = {'log_level': 'detailed'}
        optimizer_detailed = LocalSearchOptimizer(scorer, config_detailed)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result_detailed = optimizer_detailed.optimize(school_data, max_iterations=5)
            output_detailed = mock_stdout.getvalue()
        
        # Detailed should produce more output than minimal
        assert len(output_detailed) > len(output_minimal)
        assert "Starting" not in output_minimal  # Minimal should not have startup message
        assert "Starting" in output_detailed  # Detailed should have startup message


class TestCLIIntegration:
    """Test CLI integration with enhanced logging."""
    
    def test_log_level_argument_parsing(self):
        """Test that log level arguments are parsed correctly."""
        # This would require mocking the CLI argument parser
        # For now, just test that the log levels are available
        levels = get_available_log_levels()
        assert "minimal" in levels
        assert "normal" in levels
        assert "detailed" in levels
        assert "debug" in levels


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 