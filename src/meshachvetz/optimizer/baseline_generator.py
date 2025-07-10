#!/usr/bin/env python3
"""
Baseline Generator for Meshachvetz - establishes performance baselines by running
Random Swap algorithm multiple times and calculating statistical metrics.
"""

import logging
import statistics
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import csv
from datetime import datetime

from .random_swap import RandomSwapOptimizer
from .base_optimizer import OptimizationResult
from ..data.models import SchoolData
from ..utils.logging import LogLevel
from ..utils.output_manager import OutputManager
from ..utils.csv_utils import ExcelCsvWriter
from .optimization_manager import OptimizationManager


class BaselineRun:
    """
    Represents a single baseline run with all collected metrics.
    """
    
    def __init__(self, run_number: int, result: OptimizationResult, 
                 duration: float, iterations_used: int):
        """
        Initialize a baseline run.
        
        Args:
            run_number: Sequential number of this run
            result: Optimization result from the run
            duration: Time taken for the run in seconds
            iterations_used: Number of iterations actually used
        """
        self.run_number = run_number
        self.result = result
        self.duration = duration
        self.iterations_used = iterations_used
        
        # Extract key metrics for easy access
        self.initial_score = result.initial_score
        self.final_score = result.final_score
        self.improvement = result.improvement
        self.improvement_percentage = result.improvement_percentage
        
        # Calculate derived metrics
        self.iterations_per_second = iterations_used / duration if duration > 0 else 0
        self.score_per_second = self.improvement / duration if duration > 0 else 0


class BaselineStatistics:
    """
    Statistical analysis of multiple baseline runs.
    """
    
    def __init__(self, runs: List[BaselineRun]):
        """
        Initialize baseline statistics.
        
        Args:
            runs: List of baseline runs to analyze
        """
        self.runs = runs
        self.run_count = len(runs)
        
        if self.run_count == 0:
            raise ValueError("Cannot create statistics from empty runs list")
        
        # Extract metrics lists
        self.final_scores = [run.final_score for run in runs]
        self.improvements = [run.improvement for run in runs]
        self.improvement_percentages = [run.improvement_percentage for run in runs]
        self.durations = [run.duration for run in runs]
        self.iterations_used = [run.iterations_used for run in runs]
        
        # Calculate statistics
        self._calculate_statistics()
    
    def _calculate_statistics(self) -> None:
        """Calculate statistical measures for all metrics."""
        # Final scores
        self.final_score_mean = statistics.mean(self.final_scores)
        self.final_score_median = statistics.median(self.final_scores)
        self.final_score_stdev = statistics.stdev(self.final_scores) if len(self.final_scores) > 1 else 0.0
        self.final_score_min = min(self.final_scores)
        self.final_score_max = max(self.final_scores)
        
        # Improvements
        self.improvement_mean = statistics.mean(self.improvements)
        self.improvement_median = statistics.median(self.improvements)
        self.improvement_stdev = statistics.stdev(self.improvements) if len(self.improvements) > 1 else 0.0
        self.improvement_min = min(self.improvements)
        self.improvement_max = max(self.improvements)
        
        # Improvement percentages
        self.improvement_pct_mean = statistics.mean(self.improvement_percentages)
        self.improvement_pct_median = statistics.median(self.improvement_percentages)
        self.improvement_pct_stdev = statistics.stdev(self.improvement_percentages) if len(self.improvement_percentages) > 1 else 0.0
        self.improvement_pct_min = min(self.improvement_percentages)
        self.improvement_pct_max = max(self.improvement_percentages)
        
        # Durations
        self.duration_mean = statistics.mean(self.durations)
        self.duration_median = statistics.median(self.durations)
        self.duration_stdev = statistics.stdev(self.durations) if len(self.durations) > 1 else 0.0
        self.duration_min = min(self.durations)
        self.duration_max = max(self.durations)
        
        # Iterations
        self.iterations_mean = statistics.mean(self.iterations_used)
        self.iterations_median = statistics.median(self.iterations_used)
        self.iterations_stdev = statistics.stdev(self.iterations_used) if len(self.iterations_used) > 1 else 0.0
        self.iterations_min = min(self.iterations_used)
        self.iterations_max = max(self.iterations_used)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of baseline statistics.
        
        Returns:
            Dictionary with all statistical measures
        """
        return {
            'run_count': self.run_count,
            'final_score': {
                'mean': self.final_score_mean,
                'median': self.final_score_median,
                'stdev': self.final_score_stdev,
                'min': self.final_score_min,
                'max': self.final_score_max
            },
            'improvement': {
                'mean': self.improvement_mean,
                'median': self.improvement_median,
                'stdev': self.improvement_stdev,
                'min': self.improvement_min,
                'max': self.improvement_max
            },
            'improvement_percentage': {
                'mean': self.improvement_pct_mean,
                'median': self.improvement_pct_median,
                'stdev': self.improvement_pct_stdev,
                'min': self.improvement_pct_min,
                'max': self.improvement_pct_max
            },
            'duration': {
                'mean': self.duration_mean,
                'median': self.duration_median,
                'stdev': self.duration_stdev,
                'min': self.duration_min,
                'max': self.duration_max
            },
            'iterations': {
                'mean': self.iterations_mean,
                'median': self.iterations_median,
                'stdev': self.iterations_stdev,
                'min': self.iterations_min,
                'max': self.iterations_max
            }
        }


class BaselineGenerator:
    """
    Generates performance baselines by running Random Swap algorithm multiple times.
    
    This class establishes performance baselines that other algorithms can be compared against.
    It runs the Random Swap algorithm (simple, unbiased baseline) multiple times and collects
    comprehensive statistics about performance, convergence, and solution quality.
    """
    
    def __init__(self, scorer, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the baseline generator.
        
        Args:
            scorer: Scorer instance for evaluating solutions
            config: Configuration dictionary with baseline parameters
        """
        self.scorer = scorer
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize output manager
        self.output_manager = OutputManager()
        
        # Baseline parameters
        self.num_runs = self.config.get('num_runs', 10)
        self.max_iterations_per_run = self.config.get('max_iterations_per_run', 1000)
        self.random_seed = self.config.get('random_seed', None)
        
        # Convert log level string to enum
        log_level_str = self.config.get('log_level', 'normal')
        try:
            self.log_level = LogLevel(log_level_str.lower())
        except ValueError:
            self.log_level = LogLevel.NORMAL
        
        # Other optimizer parameters
        self.min_friends_required = self.config.get('min_friends_required', 0)
        self.respect_force_constraints = self.config.get('respect_force_constraints', True)
        self.early_stop_threshold = self.config.get('early_stop_threshold', 100)
        self.accept_neutral_moves = self.config.get('accept_neutral_moves', False)
        
        # Storage for results
        self.runs: List[BaselineRun] = []
        self.statistics: Optional[BaselineStatistics] = None
    
    def generate_baseline(self, school_data: SchoolData) -> BaselineStatistics:
        """
        Generate baseline performance by running Random Swap algorithm multiple times.
        
        Args:
            school_data: School data to optimize
            
        Returns:
            BaselineStatistics with comprehensive analysis
        """
        self.logger.info(f"🎯 Generating baseline with {self.num_runs} runs of Random Swap algorithm")
        self.logger.info(f"   Parameters: {self.max_iterations_per_run} iterations, log_level={self.log_level.value}")
        
        self.runs = []
        
        for run_number in range(1, self.num_runs + 1):
            if self.log_level != LogLevel.MINIMAL:
                self.logger.info(f"\n📊 Run {run_number}/{self.num_runs}")
            
            # Create optimizer for this run
            optimizer_config = {
                'min_friends_required': self.min_friends_required,
                'respect_force_constraints': self.respect_force_constraints,
                'early_stop_threshold': self.early_stop_threshold,
                'accept_neutral_moves': self.accept_neutral_moves,
                'log_level': self.log_level.value
            }
            
            optimizer = RandomSwapOptimizer(
                scorer=self.scorer,
                config=optimizer_config
            )
            
            # Run optimization
            start_time = time.time()
            result = optimizer.optimize(school_data, self.max_iterations_per_run)
            duration = time.time() - start_time
            
            # Store run results
            run = BaselineRun(
                run_number=run_number,
                result=result,
                duration=duration,
                iterations_used=len(result.score_history)
            )
            self.runs.append(run)
            
            # Log run completion
            if self.log_level != LogLevel.MINIMAL:
                self.logger.info(f"   ✅ Completed: {result.final_score:.2f} (+{result.improvement:.2f}, {duration:.1f}s)")
        
        # Calculate statistics
        self.statistics = BaselineStatistics(self.runs)
        
        self.logger.info(f"\n🏁 Baseline generation complete!")
        self.logger.info(f"   Mean final score: {self.statistics.final_score_mean:.2f} ± {self.statistics.final_score_stdev:.2f}")
        self.logger.info(f"   Mean improvement: {self.statistics.improvement_mean:.2f} ± {self.statistics.improvement_stdev:.2f}")
        self.logger.info(f"   Mean duration: {self.statistics.duration_mean:.1f}s ± {self.statistics.duration_stdev:.1f}s")
        
        return self.statistics
    
    def save_baseline_report(self, output_dir: str = None, input_file: str = None, prefix: str = "baseline") -> Tuple[str, str]:
        """
        Save comprehensive baseline reports to files using OutputManager.
        
        Args:
            output_dir: Directory to save reports (optional, uses OutputManager if None)
            input_file: Path to input CSV file (used for descriptive directory naming)
            prefix: Prefix for output files (ignored when using OutputManager)
            
        Returns:
            Tuple of (csv_file_path, summary_file_path)
        """
        if not self.statistics:
            raise ValueError("No baseline statistics available. Run generate_baseline() first.")
        
        # Use OutputManager to create descriptive directory if not specified
        if output_dir is None:
            if input_file:
                output_path = self.output_manager.create_baseline_directory(input_file, self.num_runs)
            else:
                output_path = self.output_manager.create_operation_directory("baseline", algorithm="random-swap")
            output_dir = str(output_path)
        else:
            # Use provided directory but ensure it exists
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Create filenames (simplified when using OutputManager)
        csv_file = Path(output_dir) / "baseline_data.csv"
        summary_file = Path(output_dir) / "baseline_summary.txt"
        
        # Save operation information if using OutputManager
        if input_file:
            operation_info = {
                "Operation": "Generate Baseline",
                "Input File": input_file,
                "Algorithm": "Random Swap",
                "Number of Runs": self.num_runs,
                "Iterations per Run": self.max_iterations_per_run,
                "Mean Final Score": f"{self.statistics.final_score_mean:.2f}/100",
                "Mean Improvement": f"{self.statistics.improvement_mean:.2f} ({self.statistics.improvement_pct_mean:.1f}%)",
                "Mean Duration per Run": f"{self.statistics.duration_mean:.2f} seconds",
                "Best Run Score": f"{self.statistics.final_score_max:.2f}/100",
                "Worst Run Score": f"{self.statistics.final_score_min:.2f}/100"
            }
            self.output_manager.save_operation_info(output_path, operation_info)
        
        # Save CSV report
        self._save_csv_report(csv_file)
        
        # Save summary report
        self._save_summary_report(summary_file)
        
        self.logger.info(f"📄 Baseline reports saved:")
        self.logger.info(f"   CSV data: {csv_file}")
        self.logger.info(f"   Summary: {summary_file}")
        
        return str(csv_file), str(summary_file)
    
    def _save_csv_report(self, csv_file: Path) -> None:
        """Save detailed CSV report of all runs."""
        with ExcelCsvWriter(str(csv_file)) as writer:
            
            # Header
            writer.writerow([
                'Run', 'Initial Score', 'Final Score', 'Improvement', 
                'Improvement %', 'Duration (s)', 'Iterations Used',
                'Iterations/s', 'Score/s'
            ])
            
            # Data rows
            for run in self.runs:
                writer.writerow([
                    run.run_number,
                    f"{run.initial_score:.2f}",
                    f"{run.final_score:.2f}",
                    f"{run.improvement:.2f}",
                    f"{run.improvement_percentage:.2f}",
                    f"{run.duration:.2f}",
                    run.iterations_used,
                    f"{run.iterations_per_second:.2f}",
                    f"{run.score_per_second:.3f}"
                ])
    
    def _save_summary_report(self, summary_file: Path) -> None:
        """Save comprehensive summary report."""
        with open(summary_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("MESHACHVETZ BASELINE PERFORMANCE REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Algorithm: Random Swap\n")
            f.write(f"Runs: {self.statistics.run_count}\n")
            f.write(f"Max Iterations per Run: {self.max_iterations_per_run}\n")
            f.write("\n")
            
            # Final Scores
            f.write("FINAL SCORES\n")
            f.write("-" * 20 + "\n")
            f.write(f"Mean:      {self.statistics.final_score_mean:.2f}\n")
            f.write(f"Median:    {self.statistics.final_score_median:.2f}\n")
            f.write(f"Std Dev:   {self.statistics.final_score_stdev:.2f}\n")
            f.write(f"Min:       {self.statistics.final_score_min:.2f}\n")
            f.write(f"Max:       {self.statistics.final_score_max:.2f}\n")
            f.write(f"Range:     {self.statistics.final_score_max - self.statistics.final_score_min:.2f}\n")
            f.write("\n")
            
            # Improvements
            f.write("IMPROVEMENTS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Mean:      {self.statistics.improvement_mean:.2f} ({self.statistics.improvement_pct_mean:.1f}%)\n")
            f.write(f"Median:    {self.statistics.improvement_median:.2f} ({self.statistics.improvement_pct_median:.1f}%)\n")
            f.write(f"Std Dev:   {self.statistics.improvement_stdev:.2f} ({self.statistics.improvement_pct_stdev:.1f}%)\n")
            f.write(f"Min:       {self.statistics.improvement_min:.2f} ({self.statistics.improvement_pct_min:.1f}%)\n")
            f.write(f"Max:       {self.statistics.improvement_max:.2f} ({self.statistics.improvement_pct_max:.1f}%)\n")
            f.write("\n")
            
            # Performance
            f.write("PERFORMANCE\n")
            f.write("-" * 20 + "\n")
            f.write(f"Mean Duration:     {self.statistics.duration_mean:.2f}s ± {self.statistics.duration_stdev:.2f}s\n")
            f.write(f"Mean Iterations:   {self.statistics.iterations_mean:.0f} ± {self.statistics.iterations_stdev:.0f}\n")
            f.write(f"Total Time:        {sum(self.statistics.durations):.1f}s\n")
            f.write(f"Total Iterations:  {sum(self.statistics.iterations_used):,}\n")
            f.write("\n")
            
            # Individual Runs
            f.write("INDIVIDUAL RUNS\n")
            f.write("-" * 40 + "\n")
            f.write("Run | Initial | Final  | Improve | Time  | Iter\n")
            f.write("-" * 40 + "\n")
            for run in self.runs:
                f.write(f"{run.run_number:3d} | {run.initial_score:7.2f} | {run.final_score:6.2f} | "
                       f"{run.improvement:7.2f} | {run.duration:5.1f} | {run.iterations_used:4d}\n")
    
    def compare_to_baseline(self, other_result: OptimizationResult, 
                           algorithm_name: str) -> Dict[str, Any]:
        """
        Compare another algorithm's result to the baseline.
        
        Args:
            other_result: Optimization result from another algorithm
            algorithm_name: Name of the algorithm being compared
            
        Returns:
            Dictionary with comparison results
        """
        if not self.statistics:
            raise ValueError("No baseline statistics available. Run generate_baseline() first.")
        
        comparison = {
            'algorithm_name': algorithm_name,
            'baseline_algorithm': 'Random Swap',
            'baseline_runs': self.statistics.run_count,
            'other_final_score': other_result.final_score,
            'other_improvement': other_result.improvement,
            'other_improvement_percentage': other_result.improvement_percentage,
            'baseline_mean_score': self.statistics.final_score_mean,
            'baseline_median_score': self.statistics.final_score_median,
            'baseline_best_score': self.statistics.final_score_max,
            'baseline_worst_score': self.statistics.final_score_min,
            'score_difference': other_result.final_score - self.statistics.final_score_mean,
            'score_difference_from_median': other_result.final_score - self.statistics.final_score_median,
            'score_difference_from_best': other_result.final_score - self.statistics.final_score_max,
            'is_better_than_baseline': other_result.final_score > self.statistics.final_score_mean,
            'is_better_than_median': other_result.final_score > self.statistics.final_score_median,
            'is_better_than_best': other_result.final_score > self.statistics.final_score_max,
            'percentile_rank': self._calculate_percentile_rank(other_result.final_score)
        }
        
        return comparison
    
    def _calculate_percentile_rank(self, score: float) -> float:
        """Calculate what percentile this score would be in the baseline."""
        scores_below = sum(1 for s in self.statistics.final_scores if s < score)
        return (scores_below / len(self.statistics.final_scores)) * 100
    
    def get_baseline_config(self) -> Dict[str, Any]:
        """
        Get the current baseline configuration.
        
        Returns:
            Dictionary with all baseline parameters
        """
        return {
            'num_runs': self.num_runs,
            'max_iterations_per_run': self.max_iterations_per_run,
            'log_level': self.log_level.value,
            'min_friends_required': self.min_friends_required,
            'respect_force_constraints': self.respect_force_constraints,
            'early_stop_threshold': self.early_stop_threshold,
            'accept_neutral_moves': self.accept_neutral_moves,
            'random_seed': self.random_seed
        } 