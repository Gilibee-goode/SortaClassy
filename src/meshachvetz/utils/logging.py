"""Enhanced iteration logging system for Meshachvetz optimization processes.

This module provides sophisticated logging capabilities with configurable levels,
real-time progress tracking, and meaningful status updates during optimization.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import sys
import threading


class LogLevel(Enum):
    """Configurable logging levels for different user needs."""
    MINIMAL = "minimal"      # Only start/end messages and final results
    NORMAL = "normal"        # Basic progress updates every 10% with key metrics
    DETAILED = "detailed"    # Iteration-by-iteration improvements with statistics
    DEBUG = "debug"          # All debug information and internal state


@dataclass
class ProgressMetrics:
    """Metrics for tracking optimization progress."""
    current_iteration: int = 0
    total_iterations: int = 0
    current_score: float = 0.0
    best_score: float = 0.0
    initial_score: float = 0.0
    start_time: float = field(default_factory=time.time)
    last_improvement_iteration: int = 0
    last_improvement_time: float = field(default_factory=time.time)
    score_history: List[float] = field(default_factory=list)
    improvement_history: List[float] = field(default_factory=list)
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time since start."""
        return time.time() - self.start_time
    
    @property
    def progress_percentage(self) -> float:
        """Get progress as percentage."""
        if self.total_iterations == 0:
            return 0.0
        return (self.current_iteration / self.total_iterations) * 100
    
    @property
    def estimated_total_time(self) -> float:
        """Estimate total time based on current progress."""
        if self.current_iteration == 0:
            return 0.0
        time_per_iteration = self.elapsed_time / self.current_iteration
        return time_per_iteration * self.total_iterations
    
    @property
    def estimated_remaining_time(self) -> float:
        """Estimate remaining time."""
        return max(0, self.estimated_total_time - self.elapsed_time)
    
    @property
    def improvement_rate(self) -> float:
        """Calculate improvement rate per iteration."""
        if self.current_iteration == 0:
            return 0.0
        total_improvement = self.current_score - self.initial_score
        return total_improvement / self.current_iteration
    
    @property
    def stagnation_count(self) -> int:
        """Count iterations since last improvement."""
        return self.current_iteration - self.last_improvement_iteration
    
    def format_time(self, seconds: float) -> str:
        """Format time duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"


class ProgressTracker:
    """Real-time progress tracker for optimization processes."""
    
    def __init__(self, log_level: LogLevel = LogLevel.NORMAL, 
                 algorithm_name: str = "Optimizer",
                 update_callback: Optional[Callable] = None):
        """
        Initialize progress tracker.
        
        Args:
            log_level: Logging level for output detail
            algorithm_name: Name of the optimization algorithm
            update_callback: Optional callback function for progress updates
        """
        self.log_level = log_level
        self.algorithm_name = algorithm_name
        self.update_callback = update_callback
        self.metrics = ProgressMetrics()
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{algorithm_name}")
        
        # Progress display settings
        self.last_display_time = 0
        self.display_interval = 1.0  # Display updates every 1 second
        self.last_logged_percentage = 0
        self.log_percentage_interval = 10  # Log every 10% progress
        
        # Thread-safe display
        self._display_lock = threading.Lock()
        self._last_line_length = 0
        
    def start_optimization(self, initial_score: float, total_iterations: int) -> None:
        """
        Start optimization tracking.
        
        Args:
            initial_score: Initial solution score
            total_iterations: Total number of iterations planned
        """
        self.metrics = ProgressMetrics(
            initial_score=initial_score,
            current_score=initial_score,
            best_score=initial_score,
            total_iterations=total_iterations,
            start_time=time.time()
        )
        
        # Log startup message based on level
        if self.log_level != LogLevel.MINIMAL:
            self._log_startup()
    
    def update_iteration(self, iteration: int, current_score: float, 
                        additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        Update progress for current iteration.
        
        Args:
            iteration: Current iteration number
            current_score: Current solution score
            additional_metrics: Additional algorithm-specific metrics
        """
        self.metrics.current_iteration = iteration
        self.metrics.current_score = current_score
        self.metrics.score_history.append(current_score)
        
        # Check for improvement
        improvement = current_score - self.metrics.best_score
        if improvement > 0.01:  # Significant improvement threshold
            self.metrics.best_score = current_score
            self.metrics.last_improvement_iteration = iteration
            self.metrics.last_improvement_time = time.time()
            self.metrics.improvement_history.append(improvement)
            
            # Log improvement based on level
            if self.log_level == LogLevel.DETAILED:
                self._log_improvement(improvement, additional_metrics)
        
        # Display progress based on level and timing
        current_time = time.time()
        if self._should_display_progress(current_time):
            self._display_progress(additional_metrics)
        
        # Percentage-based logging
        if self._should_log_percentage():
            self._log_percentage_progress(additional_metrics)
        
        # Call update callback if provided
        if self.update_callback:
            try:
                self.update_callback(self.metrics, additional_metrics)
            except Exception as e:
                self.logger.debug(f"Update callback failed: {e}")
    
    def finish_optimization(self, final_score: float, iterations_completed: int) -> None:
        """
        Finish optimization tracking.
        
        Args:
            final_score: Final solution score
            iterations_completed: Number of iterations actually completed
        """
        self.metrics.current_score = final_score
        self.metrics.current_iteration = iterations_completed
        
        # Clear any progress line
        self._clear_progress_line()
        
        # Log completion message
        self._log_completion()
    
    def _should_display_progress(self, current_time: float) -> bool:
        """Check if progress should be displayed based on timing."""
        if self.log_level == LogLevel.MINIMAL:
            return False
        
        # Always display on final iteration
        if self.metrics.current_iteration == self.metrics.total_iterations:
            return True
        
        # Display based on time interval
        return current_time - self.last_display_time >= self.display_interval
    
    def _should_log_percentage(self) -> bool:
        """Check if percentage-based logging should occur."""
        if self.log_level == LogLevel.MINIMAL:
            return False
        
        current_percentage = int(self.metrics.progress_percentage)
        threshold_crossed = (current_percentage >= self.last_logged_percentage + self.log_percentage_interval)
        
        return threshold_crossed or self.metrics.current_iteration == self.metrics.total_iterations
    
    def _log_startup(self) -> None:
        """Log optimization startup message."""
        print(f"🚀 Starting {self.algorithm_name} optimization...")
        print(f"   Initial score: {self.metrics.initial_score:.2f}/100")
        print(f"   Target iterations: {self.metrics.total_iterations:,}")
        
        if self.log_level == LogLevel.DETAILED:
            print(f"   Optimization started at: {datetime.now().strftime('%H:%M:%S')}")
    
    def _log_improvement(self, improvement: float, additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Log score improvement."""
        elapsed = self.metrics.elapsed_time
        print(f"✨ Iteration {self.metrics.current_iteration:,}: "
              f"New best score {self.metrics.best_score:.2f} "
              f"(+{improvement:.2f}) after {self.metrics.format_time(elapsed)}")
        
        if additional_metrics and self.log_level == LogLevel.DEBUG:
            for key, value in additional_metrics.items():
                print(f"   {key}: {value}")
    
    def _display_progress(self, additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Display current progress."""
        self.last_display_time = time.time()
        
        if self.log_level == LogLevel.DETAILED:
            # Detailed real-time progress
            self._display_detailed_progress(additional_metrics)
        else:
            # Normal progress bar
            self._display_progress_bar()
    
    def _display_detailed_progress(self, additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Display detailed progress information."""
        with self._display_lock:
            # Clear previous line
            self._clear_progress_line()
            
            # Progress information
            progress_info = [
                f"Iteration {self.metrics.current_iteration:,}/{self.metrics.total_iterations:,}",
                f"({self.metrics.progress_percentage:.1f}%)",
                f"Score: {self.metrics.current_score:.2f}",
                f"Best: {self.metrics.best_score:.2f}",
                f"Elapsed: {self.metrics.format_time(self.metrics.elapsed_time)}",
                f"ETA: {self.metrics.format_time(self.metrics.estimated_remaining_time)}",
            ]
            
            # Add stagnation info if relevant
            if self.metrics.stagnation_count > 10:
                progress_info.append(f"Stagnant: {self.metrics.stagnation_count}")
            
            # Add additional metrics
            if additional_metrics:
                for key, value in additional_metrics.items():
                    if isinstance(value, (int, float)):
                        progress_info.append(f"{key}: {value:.2f}")
                    else:
                        progress_info.append(f"{key}: {value}")
            
            progress_line = " | ".join(progress_info)
            print(f"\r⏳ {progress_line}", end="", flush=True)
            self._last_line_length = len(progress_line) + 3
    
    def _display_progress_bar(self) -> None:
        """Display progress bar for normal logging level."""
        with self._display_lock:
            # Clear previous line
            self._clear_progress_line()
            
            # Create progress bar
            bar_width = 30
            filled_width = int(bar_width * self.metrics.progress_percentage / 100)
            bar = "█" * filled_width + "░" * (bar_width - filled_width)
            
            progress_line = (f"⏳ {bar} {self.metrics.progress_percentage:.1f}% "
                           f"({self.metrics.current_iteration:,}/{self.metrics.total_iterations:,}) "
                           f"Score: {self.metrics.current_score:.2f} "
                           f"ETA: {self.metrics.format_time(self.metrics.estimated_remaining_time)}")
            
            print(f"\r{progress_line}", end="", flush=True)
            self._last_line_length = len(progress_line)
    
    def _log_percentage_progress(self, additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Log percentage-based progress milestones."""
        current_percentage = int(self.metrics.progress_percentage)
        
        if current_percentage >= self.last_logged_percentage + self.log_percentage_interval:
            self.last_logged_percentage = current_percentage
            
            # Clear progress line for clean logging
            self._clear_progress_line()
            
            elapsed = self.metrics.elapsed_time
            eta = self.metrics.estimated_remaining_time
            
            print(f"📊 {current_percentage}% complete "
                  f"({self.metrics.current_iteration:,}/{self.metrics.total_iterations:,}) | "
                  f"Current: {self.metrics.current_score:.2f} | "
                  f"Best: {self.metrics.best_score:.2f} | "
                  f"Time: {self.metrics.format_time(elapsed)} | "
                  f"ETA: {self.metrics.format_time(eta)}")
            
            # Show stagnation warning if applicable
            if self.metrics.stagnation_count > self.metrics.total_iterations * 0.2:
                print(f"⚠️  No improvement for {self.metrics.stagnation_count} iterations")
    
    def _log_completion(self) -> None:
        """Log optimization completion."""
        improvement = self.metrics.current_score - self.metrics.initial_score
        improvement_pct = (improvement / self.metrics.initial_score * 100) if self.metrics.initial_score > 0 else 0
        
        print(f"\n🏁 {self.algorithm_name} completed!")
        print(f"   Final score: {self.metrics.current_score:.2f}/100")
        print(f"   Improvement: +{improvement:.2f} ({improvement_pct:.1f}%)")
        print(f"   Total time: {self.metrics.format_time(self.metrics.elapsed_time)}")
        print(f"   Iterations: {self.metrics.current_iteration:,}/{self.metrics.total_iterations:,}")
        
        if self.log_level == LogLevel.DETAILED:
            print(f"   Best score achieved: {self.metrics.best_score:.2f}")
            if self.metrics.improvement_history:
                avg_improvement = sum(self.metrics.improvement_history) / len(self.metrics.improvement_history)
                print(f"   Average improvement per breakthrough: {avg_improvement:.3f}")
                print(f"   Number of improvements: {len(self.metrics.improvement_history)}")
    
    def _clear_progress_line(self) -> None:
        """Clear the current progress line."""
        if self._last_line_length > 0:
            print(f"\r{' ' * self._last_line_length}\r", end="", flush=True)
            self._last_line_length = 0


class IterationLogger:
    """Enhanced iteration logger for optimization algorithms."""
    
    def __init__(self, log_level: LogLevel = LogLevel.NORMAL, 
                 algorithm_name: str = "Optimizer"):
        """
        Initialize iteration logger.
        
        Args:
            log_level: Logging level for output detail
            algorithm_name: Name of the optimization algorithm
        """
        self.log_level = log_level
        self.algorithm_name = algorithm_name
        self.progress_tracker = ProgressTracker(log_level, algorithm_name)
        
        # Configure Python logging
        self.logger = logging.getLogger(f"meshachvetz.{algorithm_name}")
        self._configure_logging()
    
    def _configure_logging(self) -> None:
        """Configure Python logging based on log level."""
        # Set logging level based on our custom levels
        if self.log_level == LogLevel.DEBUG:
            self.logger.setLevel(logging.DEBUG)
        elif self.log_level == LogLevel.DETAILED:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)
    
    def start_optimization(self, initial_score: float, total_iterations: int) -> None:
        """Start optimization logging."""
        self.progress_tracker.start_optimization(initial_score, total_iterations)
    
    def log_iteration(self, iteration: int, current_score: float, 
                     additional_metrics: Optional[Dict[str, Any]] = None) -> None:
        """Log iteration progress."""
        self.progress_tracker.update_iteration(iteration, current_score, additional_metrics)
    
    def finish_optimization(self, final_score: float, iterations_completed: int) -> None:
        """Finish optimization logging."""
        self.progress_tracker.finish_optimization(final_score, iterations_completed)
    
    def log_debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message if debug level is enabled."""
        if self.log_level == LogLevel.DEBUG:
            self.logger.debug(message, *args, **kwargs)
    
    def log_info(self, message: str, *args, **kwargs) -> None:
        """Log info message if detailed level is enabled."""
        if self.log_level in [LogLevel.DETAILED, LogLevel.DEBUG]:
            self.logger.info(message, *args, **kwargs)
    
    def log_warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message (always shown except in minimal mode)."""
        if self.log_level != LogLevel.MINIMAL:
            self.logger.warning(message, *args, **kwargs)
    
    def log_error(self, message: str, *args, **kwargs) -> None:
        """Log error message (always shown)."""
        self.logger.error(message, *args, **kwargs)


def create_iteration_logger(log_level: str = "normal", algorithm_name: str = "Optimizer") -> IterationLogger:
    """
    Create an iteration logger with the specified level.
    
    Args:
        log_level: Logging level ("minimal", "normal", "detailed", "debug")
        algorithm_name: Name of the optimization algorithm
        
    Returns:
        Configured IterationLogger instance
    """
    try:
        level = LogLevel(log_level.lower())
    except ValueError:
        level = LogLevel.NORMAL
    
    return IterationLogger(level, algorithm_name)


def get_available_log_levels() -> List[str]:
    """Get list of available logging levels."""
    return [level.value for level in LogLevel] 