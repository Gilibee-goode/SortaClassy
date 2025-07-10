#!/usr/bin/env python3
"""
Tests for Output Consolidation System - comprehensive testing of OutputManager
and integrated output handling across all Meshachvetz components.
"""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz.utils.output_manager import OutputManager, OutputConfig
from meshachvetz.scorer.main_scorer import Scorer
from meshachvetz.optimizer.optimization_manager import OptimizationManager
from meshachvetz.optimizer.baseline_generator import BaselineGenerator
from meshachvetz.data.loader import DataLoader
from meshachvetz.utils.config import Config


class TestOutputManager:
    """Test the OutputManager class functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = OutputConfig(base_dir=self.temp_dir)
        self.output_manager = OutputManager(self.config)
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_scoring_directory_creation(self):
        """Test creation of scoring operation directories."""
        input_file = "students_sample.csv"
        
        # Create scoring directory
        output_dir = self.output_manager.create_scoring_directory(input_file)
        
        # Verify directory exists and follows naming convention
        assert output_dir.exists()
        assert output_dir.is_dir()
        assert "score_students_sample" in output_dir.name
        assert datetime.now().strftime("%Y-%m-%d") in output_dir.name
    
    def test_optimization_directory_creation(self):
        """Test creation of optimization operation directories."""
        input_file = "large_dataset.csv"
        algorithm = "local_search"
        
        # Create optimization directory
        output_dir = self.output_manager.create_optimization_directory(input_file, algorithm)
        
        # Verify directory structure
        assert output_dir.exists()
        assert "optimize_large_dataset_local-search" in output_dir.name
        assert datetime.now().strftime("%Y-%m-%d") in output_dir.name
    
    def test_baseline_directory_creation(self):
        """Test creation of baseline operation directories."""
        input_file = "test_data.csv"
        num_runs = 20
        
        # Create baseline directory
        output_dir = self.output_manager.create_baseline_directory(input_file, num_runs)
        
        # Verify directory structure
        assert output_dir.exists()
        assert "baseline_test_data_random-swap_20runs" in output_dir.name
        assert datetime.now().strftime("%Y-%m-%d") in output_dir.name
    
    def test_generation_directory_creation(self):
        """Test creation of assignment generation directories."""
        input_file = "unassigned_students.csv"
        strategy = "constraint_aware"
        
        # Create generation directory
        output_dir = self.output_manager.create_generation_directory(input_file, strategy)
        
        # Verify directory structure
        assert output_dir.exists()
        assert "generate_unassigned_students_constraint-aware" in output_dir.name
        assert datetime.now().strftime("%Y-%m-%d") in output_dir.name
    
    def test_operation_info_saving(self):
        """Test saving operation information."""
        output_dir = self.output_manager.create_operation_directory("test")
        
        operation_info = {
            "Operation": "Test Operation",
            "Input File": "test.csv",
            "Score": "85.5/100"
        }
        
        # Save operation info
        self.output_manager.save_operation_info(output_dir, operation_info)
        
        # Verify file was created and contains expected content
        info_file = output_dir / "operation_info.txt"
        assert info_file.exists()
        
        content = info_file.read_text()
        assert "Test Operation" in content
        assert "test.csv" in content
        assert "85.5/100" in content
    
    def test_output_summary_generation(self):
        """Test output summary functionality."""
        output_dir = self.output_manager.create_operation_directory("test")
        
        # Create some test files
        (output_dir / "test1.csv").write_text("test content 1")
        (output_dir / "test2.txt").write_text("test content 2")
        (output_dir / "subdir").mkdir()
        (output_dir / "subdir" / "test3.csv").write_text("test content 3")
        
        # Get summary
        summary = self.output_manager.get_output_summary(output_dir)
        
        # Verify summary content
        assert summary["total_files"] == 3
        assert summary["directory"] == str(output_dir)
        assert summary["total_size_bytes"] > 0
        assert len(summary["files"]) == 3
    
    def test_cleanup_old_runs(self):
        """Test cleanup of old run directories."""
        # Set max_old_runs to 2 for testing
        self.config.max_old_runs = 2
        
        input_file = "test.csv"
        
        # Create 5 directories with different timestamps
        dirs_created = []
        with patch('meshachvetz.utils.output_manager.datetime') as mock_datetime:
            for i in range(5):
                # Mock different timestamps
                mock_time = datetime(2025, 1, 8, 10, i, 0)
                mock_datetime.now.return_value = mock_time
                mock_datetime.strftime = datetime.strftime
                
                output_dir = self.output_manager.create_scoring_directory(input_file)
                dirs_created.append(output_dir)
        
        # Verify that only the most recent ones exist
        existing_dirs = [d for d in dirs_created if d.exists()]
        assert len(existing_dirs) <= self.config.max_old_runs + 1  # +1 for the current one
    
    def test_list_recent_runs(self):
        """Test listing recent run directories."""
        # Create some test directories
        self.output_manager.create_scoring_directory("test1.csv")
        self.output_manager.create_optimization_directory("test2.csv", "genetic")
        self.output_manager.create_baseline_directory("test3.csv", 10)
        
        # List all runs
        all_runs = self.output_manager.list_recent_runs()
        assert len(all_runs) >= 3
        
        # List only optimization runs
        opt_runs = self.output_manager.list_recent_runs("optimize")
        assert len(opt_runs) >= 1
        assert all(run["operation_type"] == "optimize" for run in opt_runs)
        
        # List with limit
        limited_runs = self.output_manager.list_recent_runs(limit=2)
        assert len(limited_runs) <= 2
    
    def test_get_latest_run(self):
        """Test getting the latest run directory."""
        input_file = "test.csv"
        
        # Create multiple runs
        dir1 = self.output_manager.create_scoring_directory(input_file)
        dir2 = self.output_manager.create_optimization_directory(input_file, "genetic")
        
        # Get latest scoring run
        latest_score = self.output_manager.get_latest_run("score", input_file)
        assert latest_score == dir1
        
        # Get latest optimization run
        latest_opt = self.output_manager.get_latest_run("optimize", input_file)
        assert latest_opt == dir2


class TestIntegratedOutputSystem:
    """Test integrated output system across all components."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_csv = self._create_test_csv()
        
        # Configure components to use temporary directory
        output_config = OutputConfig(base_dir=self.temp_dir)
        
        self.config = Config()
        self.scorer = Scorer(self.config)
        self.scorer.output_manager = OutputManager(output_config)
        
        self.optimization_manager = OptimizationManager(self.scorer)
        self.optimization_manager.output_manager = OutputManager(output_config)
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
    
    def _create_test_csv(self):
        """Create a minimal test CSV file."""
        test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        test_file.write("""student_id,first_name,last_name,gender,class,academic_score,behavior_rank,assistance_package,preferred_friend_1,preferred_friend_2,preferred_friend_3,disliked_peer_1,disliked_peer_2,disliked_peer_3,disliked_peer_4,disliked_peer_5,force_class,force_friend
123456789,Alice,Smith,F,,85.5,A,false,987654321,,,,,,,,,
987654321,Bob,Johnson,M,,78.2,B,false,123456789,,,,,,,,,
111222333,Carol,Davis,F,,92.1,A,true,,,,,,,,,,
444555666,David,Wilson,M,,76.8,C,false,,,,,,,,,,
""")
        test_file.close()
        return test_file.name
    
    def test_scorer_output_consolidation(self):
        """Test that scorer uses OutputManager for report generation."""
        # Skip validation for simplified test data
        self.scorer.data_loader.validate_data = False
        
        # Score with reports
        result, output_path = self.scorer.score_csv_file_with_reports(self.test_csv)
        
        # Verify output directory structure
        output_dir = Path(output_path)
        assert output_dir.exists()
        assert output_dir.is_dir()
        
        # Check for descriptive directory naming
        assert "score_" in output_dir.name
        assert datetime.now().strftime("%Y-%m-%d") in output_dir.name
        
        # Verify expected files exist
        expected_files = [
            "operation_info.txt",
            "summary_report.csv",
            "student_details.csv",
            "class_details.csv",
            "school_balance.csv",
            "configuration.csv"
        ]
        
        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Missing file: {filename}"
        
        # Verify operation info content
        operation_info = (output_dir / "operation_info.txt").read_text()
        assert "Score Assignment" in operation_info
        assert Path(self.test_csv).name in operation_info
    
    def test_optimization_output_consolidation(self):
        """Test that optimization uses OutputManager for output generation."""
        # Load test data with validation disabled
        self.scorer.data_loader.validate_data = False
        school_data = self.scorer.load_data(self.test_csv)
        
        # Run optimization with OutputManager (no output file specified)
        result, scoring_result = self.optimization_manager.optimize_and_save(
            school_data=school_data,
            input_file=self.test_csv,
            algorithm="random_swap",
            max_iterations=50,  # Small number for testing
            generate_reports=True
        )
        
        # Find the created output directory
        base_path = Path(self.temp_dir)
        opt_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("optimize_")]
        assert len(opt_dirs) >= 1
        
        output_dir = opt_dirs[0]
        
        # Verify directory structure
        assert "optimize_" in output_dir.name
        assert "random-swap" in output_dir.name
        assert datetime.now().strftime("%Y-%m-%d") in output_dir.name
        
        # Verify files exist
        expected_files = [
            "operation_info.txt",
            "optimization_report.csv"
        ]
        
        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Missing file: {filename}"
        
        # Verify optimized CSV exists
        csv_files = list(output_dir.glob("optimized_*.csv"))
        assert len(csv_files) >= 1
        
        # Verify scoring reports directory exists
        scoring_reports = output_dir / "scoring_reports"
        assert scoring_reports.exists()
        assert scoring_reports.is_dir()
    
    def test_baseline_output_consolidation(self):
        """Test that baseline generator uses OutputManager for output."""
        # Setup baseline generator
        baseline_config = {
            'num_runs': 3,  # Small number for testing
            'max_iterations_per_run': 50,
            'log_level': 'minimal'
        }
        
        baseline_generator = BaselineGenerator(self.scorer, baseline_config)
        baseline_generator.output_manager = OutputManager(OutputConfig(base_dir=self.temp_dir))
        
        # Load test data
        self.scorer.data_loader.validate_data = False
        school_data = self.scorer.load_data(self.test_csv)
        
        # Generate baseline
        statistics = baseline_generator.generate_baseline(school_data)
        
        # Save reports using OutputManager
        csv_file, summary_file = baseline_generator.save_baseline_report(
            input_file=self.test_csv
        )
        
        # Verify files were created
        assert os.path.exists(csv_file)
        assert os.path.exists(summary_file)
        
        # Verify directory structure
        output_dir = Path(csv_file).parent
        assert "baseline_" in output_dir.name
        assert "random-swap" in output_dir.name
        assert "3runs" in output_dir.name
        assert datetime.now().strftime("%Y-%m-%d") in output_dir.name
        
        # Verify operation info exists
        operation_info_file = output_dir / "operation_info.txt"
        assert operation_info_file.exists()
        
        operation_info = operation_info_file.read_text()
        assert "Generate Baseline" in operation_info
        assert "3" in operation_info  # Number of runs
    
    def test_generation_output_consolidation(self):
        """Test that assignment generation uses OutputManager."""
        # Load test data
        self.scorer.data_loader.validate_data = False
        school_data = self.scorer.load_data(self.test_csv)
        
        # Generate initial assignment with OutputManager
        initialized_data = self.optimization_manager.generate_initial_assignment(
            school_data=school_data,
            input_file=self.test_csv,
            strategy="constraint_aware"
        )
        
        # Find the created output directory
        base_path = Path(self.temp_dir)
        gen_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("generate_")]
        assert len(gen_dirs) >= 1
        
        output_dir = gen_dirs[0]
        
        # Verify directory structure
        assert "generate_" in output_dir.name
        assert "constraint-aware" in output_dir.name
        assert datetime.now().strftime("%Y-%m-%d") in output_dir.name
        
        # Verify files exist
        expected_files = [
            "operation_info.txt"
        ]
        
        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Missing file: {filename}"
        
        # Verify assignment CSV exists
        csv_files = list(output_dir.glob("assignment_*.csv"))
        assert len(csv_files) >= 1
    
    def test_multiple_runs_organization(self):
        """Test that multiple runs are properly organized and don't interfere."""
        # Skip validation for test data
        self.scorer.data_loader.validate_data = False
        
        # Run multiple operations
        
        # 1. Score assignment
        result1, output_path1 = self.scorer.score_csv_file_with_reports(self.test_csv)
        
        # 2. Run optimization
        school_data = self.scorer.load_data(self.test_csv)
        result2, scoring_result2 = self.optimization_manager.optimize_and_save(
            school_data=school_data,
            input_file=self.test_csv,
            algorithm="local_search",
            max_iterations=30,
            generate_reports=True
        )
        
        # Test the specific case that was causing the NoneType error
        # This should not raise any exceptions
        result3, scoring_result3 = self.optimization_manager.optimize_and_save(
            school_data=school_data,
            output_file=None,  # Explicitly test None case
            input_file=self.test_csv,
            algorithm="random_swap",
            max_iterations=10,
            generate_reports=True
        )
        
        # Test that CLI handling works correctly with None output_file
        # (This simulates the CLI behavior when no --output is specified)
        import subprocess
        import sys
        from pathlib import Path
        
        # Run a minimal CLI test to ensure no NoneType error occurs
        result = subprocess.run([
            sys.executable, "-m", "meshachvetz.cli.main", "optimize", 
            self.test_csv, "--algorithm", "random_swap", "--max-iterations", "5", 
            "--skip-validation", "--reports"
        ], cwd=Path.cwd(), capture_output=True, text=True)
        
        # Should complete successfully (exit code 0)
        if result.returncode != 0:
            raise AssertionError(f"CLI command failed with exit code {result.returncode}: {result.stderr}")
        if "✅ Optimization completed successfully!" not in result.stdout:
            raise AssertionError("Expected success message not found in CLI output")
        if "Optimized assignment and reports saved to:" not in result.stdout:
            raise AssertionError("Expected output path message not found in CLI output")
        
        # 3. Generate baseline
        baseline_config = {
            'num_runs': 2,
            'max_iterations_per_run': 20,
            'log_level': 'minimal'
        }
        baseline_generator = BaselineGenerator(self.scorer, baseline_config)
        baseline_generator.output_manager = OutputManager(OutputConfig(base_dir=self.temp_dir))
        
        statistics = baseline_generator.generate_baseline(school_data)
        csv_file, summary_file = baseline_generator.save_baseline_report(input_file=self.test_csv)
        
        # Verify all operations created separate directories
        base_path = Path(self.temp_dir)
        all_dirs = [d for d in base_path.iterdir() if d.is_dir()]
        
        score_dirs = [d for d in all_dirs if d.name.startswith("score_")]
        opt_dirs = [d for d in all_dirs if d.name.startswith("optimize_")]
        baseline_dirs = [d for d in all_dirs if d.name.startswith("baseline_")]
        
        assert len(score_dirs) >= 1
        assert len(opt_dirs) >= 1
        assert len(baseline_dirs) >= 1
        
        # Verify each directory has distinct content
        for directory in [score_dirs[0], opt_dirs[0], baseline_dirs[0]]:
            operation_info = directory / "operation_info.txt"
            assert operation_info.exists()
            content = operation_info.read_text()
            
            if directory in score_dirs:
                assert "Score Assignment" in content
            elif directory in opt_dirs:
                assert "Optimize Assignment" in content
            elif directory in baseline_dirs:
                assert "Generate Baseline" in content


def run_tests():
    """Run all output consolidation tests."""
    print("🧪 Running Output Consolidation Tests")
    print("=" * 50)
    
    # Run OutputManager tests
    test_output_manager = TestOutputManager()
    
    tests = [
        ("OutputManager - Directory Creation", [
            test_output_manager.test_scoring_directory_creation,
            test_output_manager.test_optimization_directory_creation,
            test_output_manager.test_baseline_directory_creation,
            test_output_manager.test_generation_directory_creation
        ]),
        ("OutputManager - File Operations", [
            test_output_manager.test_operation_info_saving,
            test_output_manager.test_output_summary_generation
        ]),
        ("OutputManager - Run Management", [
            test_output_manager.test_list_recent_runs,
            test_output_manager.test_get_latest_run
        ])
    ]
    
    # Run integrated system tests
    test_integrated = TestIntegratedOutputSystem()
    
    integrated_tests = [
        ("Integrated - Component Output", [
            test_integrated.test_scorer_output_consolidation,
            test_integrated.test_optimization_output_consolidation,
            test_integrated.test_baseline_output_consolidation,
            test_integrated.test_generation_output_consolidation
        ]),
        ("Integrated - Multiple Runs", [
            test_integrated.test_multiple_runs_organization
        ])
    ]
    
    tests.extend(integrated_tests)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_group, test_functions in tests:
        print(f"\n📋 {test_group}")
        print("-" * 30)
        
        for test_func in test_functions:
            total_tests += 1
            try:
                # Setup
                if hasattr(test_func, '__self__'):
                    test_func.__self__.setup_method()
                
                # Run test
                test_func()
                
                # Teardown
                if hasattr(test_func, '__self__'):
                    test_func.__self__.teardown_method()
                
                print(f"✅ {test_func.__name__}")
                passed_tests += 1
                
            except Exception as e:
                import traceback
                error_details = f"{e}\n{traceback.format_exc()}"
                print(f"❌ {test_func.__name__}: {e}")
                failed_tests.append((test_func.__name__, error_details))
    
    # Summary
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 30)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test_name, error in failed_tests:
            print(f"   {test_name}: {error}")
        return False
    else:
        print("\n✅ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 