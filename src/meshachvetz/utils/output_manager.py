#!/usr/bin/env python3
"""
Output Manager for Meshachvetz - centralized output handling with descriptive directory naming.

This module provides a unified interface for all output generation in Meshachvetz,
ensuring consistent directory structures, descriptive naming, and organized file management.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import shutil


@dataclass
class OutputConfig:
    """Configuration for output generation."""
    base_dir: str = "outputs"
    include_timestamp: bool = True
    include_input_filename: bool = True
    preserve_old_runs: bool = True
    max_old_runs: int = 10  # Keep last 10 runs per operation type


class OutputManager:
    """
    Centralized output manager for all Meshachvetz operations.
    
    Provides consistent directory naming, file organization, and output management
    across all components (scoring, optimization, baseline generation).
    """
    
    def __init__(self, config: Optional[OutputConfig] = None):
        """
        Initialize the output manager.
        
        Args:
            config: Output configuration settings
        """
        self.config = config or OutputConfig()
        self.logger = logging.getLogger(__name__)
        
        # Ensure base output directory exists
        self.base_path = Path(self.config.base_dir)
        self.base_path.mkdir(exist_ok=True)
        
        # Track created directories for cleanup
        self.created_directories: List[Path] = []
    
    def create_operation_directory(self, 
                                 operation_type: str,
                                 input_file: Optional[str] = None,
                                 algorithm: Optional[str] = None,
                                 suffix: Optional[str] = None) -> Path:
        """
        Create a descriptive directory for an operation run.
        
        Args:
            operation_type: Type of operation (score, optimize, baseline, generate)
            input_file: Path to input CSV file
            algorithm: Algorithm name for optimization/baseline operations
            suffix: Additional suffix for the directory name
            
        Returns:
            Path object for the created directory
            
        Example directory names:
            - outputs/score_students_sample_2025-01-08_14-30-45/
            - outputs/optimize_large_dataset_local_search_2025-01-08_14-30-45/
            - outputs/baseline_test_data_random_swap_2025-01-08_14-30-45/
            - outputs/generate_unassigned_students_constraint_aware_2025-01-08_14-30-45/
        """
        # Build directory name components
        name_parts = [operation_type]
        
        # Add input filename (without extension and path)
        if input_file and self.config.include_input_filename:
            input_name = Path(input_file).stem
            # Clean filename for directory name (remove special chars)
            clean_input_name = "".join(c for c in input_name if c.isalnum() or c in '-_')
            name_parts.append(clean_input_name)
        
        # Add algorithm name for relevant operations
        if algorithm:
            clean_algorithm = algorithm.replace('_', '-')
            name_parts.append(clean_algorithm)
        
        # Add suffix if provided
        if suffix:
            name_parts.append(suffix)
        
        # Add timestamp
        if self.config.include_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            name_parts.append(timestamp)
        
        # Create directory name
        directory_name = "_".join(name_parts)
        output_dir = self.base_path / directory_name
        
        # Create directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track created directory
        self.created_directories.append(output_dir)
        
        self.logger.info(f"📁 Created output directory: {output_dir}")
        
        # Cleanup old runs if enabled
        if self.config.preserve_old_runs:
            self._cleanup_old_runs(operation_type, input_file, algorithm)
        
        return output_dir
    
    def create_scoring_directory(self, input_file: str, suffix: Optional[str] = None) -> Path:
        """
        Create directory for scoring operation.
        
        Args:
            input_file: Path to input CSV file
            suffix: Optional suffix for directory name
            
        Returns:
            Path to created directory
        """
        return self.create_operation_directory(
            operation_type="score",
            input_file=input_file,
            suffix=suffix
        )
    
    def create_optimization_directory(self, 
                                    input_file: str, 
                                    algorithm: str,
                                    suffix: Optional[str] = None) -> Path:
        """
        Create directory for optimization operation.
        
        Args:
            input_file: Path to input CSV file
            algorithm: Optimization algorithm name
            suffix: Optional suffix for directory name
            
        Returns:
            Path to created directory
        """
        return self.create_operation_directory(
            operation_type="optimize",
            input_file=input_file,
            algorithm=algorithm,
            suffix=suffix
        )
    
    def create_baseline_directory(self, 
                                input_file: str,
                                num_runs: Optional[int] = None,
                                suffix: Optional[str] = None) -> Path:
        """
        Create directory for baseline generation operation.
        
        Args:
            input_file: Path to input CSV file
            num_runs: Number of baseline runs (included in suffix)
            suffix: Optional suffix for directory name
            
        Returns:
            Path to created directory
        """
        # Include number of runs in suffix
        run_suffix = suffix or ""
        if num_runs:
            if run_suffix:
                run_suffix = f"{num_runs}runs-{run_suffix}"
            else:
                run_suffix = f"{num_runs}runs"
        
        return self.create_operation_directory(
            operation_type="baseline",
            input_file=input_file,
            algorithm="random-swap",  # Baseline always uses random swap
            suffix=run_suffix
        )
    
    def create_generation_directory(self, 
                                   input_file: str,
                                   strategy: str,
                                   suffix: Optional[str] = None) -> Path:
        """
        Create directory for assignment generation operation.
        
        Args:
            input_file: Path to input CSV file
            strategy: Assignment generation strategy
            suffix: Optional suffix for directory name
            
        Returns:
            Path to created directory
        """
        return self.create_operation_directory(
            operation_type="generate",
            input_file=input_file,
            algorithm=strategy,
            suffix=suffix
        )
    
    def save_operation_info(self, output_dir: Path, operation_info: Dict[str, Any]) -> None:
        """
        Save operation information to the output directory.
        
        Args:
            output_dir: Output directory path
            operation_info: Dictionary containing operation details
        """
        info_file = output_dir / "operation_info.txt"
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("Meshachvetz Operation Information\n")
            f.write("=" * 40 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for key, value in operation_info.items():
                f.write(f"{key}: {value}\n")
        
        self.logger.debug(f"Operation info saved to: {info_file}")
    
    def get_output_summary(self, output_dir: Path) -> Dict[str, Any]:
        """
        Get summary of files created in output directory.
        
        Args:
            output_dir: Output directory path
            
        Returns:
            Dictionary containing file summary information
        """
        if not output_dir.exists():
            return {"error": "Directory does not exist"}
        
        files = list(output_dir.rglob("*"))
        file_info = []
        total_size = 0
        
        for file_path in files:
            if file_path.is_file():
                size = file_path.stat().st_size
                total_size += size
                file_info.append({
                    "name": file_path.name,
                    "relative_path": str(file_path.relative_to(output_dir)),
                    "size_bytes": size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                })
        
        return {
            "directory": str(output_dir),
            "total_files": len(file_info),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "files": file_info
        }
    
    def _cleanup_old_runs(self, 
                         operation_type: str, 
                         input_file: Optional[str] = None,
                         algorithm: Optional[str] = None) -> None:
        """
        Clean up old run directories, keeping only the most recent ones.
        
        Args:
            operation_type: Type of operation
            input_file: Input file name (for filtering)
            algorithm: Algorithm name (for filtering)
        """
        if not self.config.preserve_old_runs or self.config.max_old_runs <= 0:
            return
        
        try:
            # Build pattern to match similar directories
            pattern_parts = [operation_type]
            
            if input_file and self.config.include_input_filename:
                input_name = Path(input_file).stem
                clean_input_name = "".join(c for c in input_name if c.isalnum() or c in '-_')
                pattern_parts.append(clean_input_name)
            
            if algorithm:
                clean_algorithm = algorithm.replace('_', '-')
                pattern_parts.append(clean_algorithm)
            
            pattern_prefix = "_".join(pattern_parts)
            
            # Find matching directories
            matching_dirs = []
            for item in self.base_path.iterdir():
                if item.is_dir() and item.name.startswith(pattern_prefix):
                    try:
                        # Extract timestamp from directory name
                        timestamp_part = item.name.split('_')[-2:]  # Last two parts: date_time
                        if len(timestamp_part) == 2:
                            timestamp_str = f"{timestamp_part[0]}_{timestamp_part[1]}"
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                            matching_dirs.append((item, timestamp))
                    except (ValueError, IndexError):
                        # Skip directories that don't match expected format
                        continue
            
            # Sort by timestamp (newest first) and remove excess
            if len(matching_dirs) > self.config.max_old_runs:
                matching_dirs.sort(key=lambda x: x[1], reverse=True)
                dirs_to_remove = matching_dirs[self.config.max_old_runs:]
                
                for dir_path, _ in dirs_to_remove:
                    self.logger.info(f"🗑️  Removing old run directory: {dir_path.name}")
                    shutil.rmtree(dir_path)
        
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old runs: {e}")
    
    def list_recent_runs(self, operation_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent run directories.
        
        Args:
            operation_type: Filter by operation type (score, optimize, baseline, generate)
            limit: Maximum number of runs to return
            
        Returns:
            List of dictionaries containing run information
        """
        runs = []
        
        for item in self.base_path.iterdir():
            if not item.is_dir():
                continue
            
            # Filter by operation type if specified
            if operation_type and not item.name.startswith(operation_type):
                continue
            
            try:
                # Extract timestamp from directory name
                timestamp_part = item.name.split('_')[-2:]  # Last two parts: date_time
                if len(timestamp_part) == 2:
                    timestamp_str = f"{timestamp_part[0]}_{timestamp_part[1]}"
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
                    
                    # Get basic info about the run
                    summary = self.get_output_summary(item)
                    
                    runs.append({
                        "directory": item.name,
                        "path": str(item),
                        "timestamp": timestamp,
                        "operation_type": item.name.split('_')[0],
                        "total_files": summary.get("total_files", 0),
                        "total_size_mb": summary.get("total_size_mb", 0.0)
                    })
            except (ValueError, IndexError):
                # Skip directories that don't match expected format
                continue
        
        # Sort by timestamp (newest first) and limit
        runs.sort(key=lambda x: x["timestamp"], reverse=True)
        return runs[:limit]
    
    def get_latest_run(self, operation_type: str, input_file: Optional[str] = None) -> Optional[Path]:
        """
        Get the path to the latest run directory for a specific operation.
        
        Args:
            operation_type: Type of operation
            input_file: Input file to match (optional)
            
        Returns:
            Path to latest run directory or None if not found
        """
        recent_runs = self.list_recent_runs(operation_type, limit=50)
        
        if input_file:
            input_name = Path(input_file).stem
            clean_input_name = "".join(c for c in input_name if c.isalnum() or c in '-_')
            
            # Filter runs that match the input file
            matching_runs = [
                run for run in recent_runs 
                if clean_input_name in run["directory"]
            ]
            
            if matching_runs:
                return Path(matching_runs[0]["path"])
        else:
            if recent_runs:
                return Path(recent_runs[0]["path"])
        
        return None 