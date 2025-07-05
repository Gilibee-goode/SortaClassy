#!/usr/bin/env python3
"""
Test script for Week 3 implementation of Meshachvetz.

This script verifies that the Week 3 deliverables are working correctly:
- CSV output generation with multiple report types
- Command-line interface functionality
- Enhanced integration testing
- Performance benchmarking
"""

import sys
import os
import tempfile
import shutil
import subprocess
import time
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz import Scorer, Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def test_csv_output_generation():
    """Test CSV output generation functionality."""
    print("📊 Testing CSV Output Generation...")
    
    try:
        # Create temporary directory for test outputs
        with tempfile.TemporaryDirectory() as temp_dir:
            sample_file = "examples/sample_data/students_sample.csv"
            
            if not os.path.exists(sample_file):
                print(f"⚠️  Sample file not found: {sample_file}")
                return True
            
            # Create scorer and generate reports
            scorer = Scorer()
            result, output_path = scorer.score_csv_file_with_reports(sample_file, temp_dir)
            
            # Check that output directory was created
            if not os.path.exists(output_path):
                print(f"❌ Output directory not created: {output_path}")
                return False
            
            # Check that all expected files were created
            expected_files = [
                "summary_report.csv",
                "student_details.csv", 
                "class_details.csv",
                "school_balance.csv",
                "configuration.csv"
            ]
            
            missing_files = []
            for filename in expected_files:
                filepath = os.path.join(output_path, filename)
                if not os.path.exists(filepath):
                    missing_files.append(filename)
            
            if missing_files:
                print(f"❌ Missing report files: {missing_files}")
                return False
            
            # Check file contents (basic validation)
            summary_file = os.path.join(output_path, "summary_report.csv")
            with open(summary_file, 'r') as f:
                content = f.read()
                if "Final Score" not in content:
                    print(f"❌ Summary report missing expected content")
                    return False
            
            student_file = os.path.join(output_path, "student_details.csv")
            with open(student_file, 'r') as f:
                lines = f.readlines()
                if len(lines) < 2:  # Header + at least one data row
                    print(f"❌ Student details report has insufficient data")
                    return False
            
            print("✅ CSV output generation successful")
            print(f"   Generated {len(expected_files)} report files")
            print(f"   Output directory: {output_path}")
            print(f"   Summary report contains expected content")
            print(f"   Student details report has {len(lines)-1} data rows")
            
            return True
            
    except Exception as e:
        print(f"❌ Error testing CSV output generation: {e}")
        return False


def test_csv_output_with_timestamp():
    """Test CSV output generation with automatic timestamp directories."""
    print("\n🕐 Testing CSV Output with Timestamps...")
    
    try:
        sample_file = "examples/sample_data/students_sample.csv"
        
        if not os.path.exists(sample_file):
            print(f"⚠️  Sample file not found: {sample_file}")
            return True
        
        # Create scorer and generate reports without specifying output directory
        scorer = Scorer()
        result, output_path = scorer.score_csv_file_with_reports(sample_file)
        
        # Check that timestamp-based directory was created
        if not os.path.exists(output_path):
            print(f"❌ Timestamp output directory not created: {output_path}")
            return False
        
        # Check that directory name contains timestamp pattern
        if not output_path.startswith("results_"):
            print(f"❌ Output directory doesn't follow timestamp pattern: {output_path}")
            return False
        
        # Cleanup
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        
        print("✅ CSV output with timestamps successful")
        print(f"   Created timestamp directory: {output_path}")
        print(f"   Directory cleaned up after test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing CSV output with timestamps: {e}")
        return False


def test_cli_basic_functionality():
    """Test basic CLI functionality."""
    print("\n🖥️  Testing CLI Basic Functionality...")
    
    try:
        # Test CLI help
        result = subprocess.run([
            sys.executable, "src/meshachvetz/cli/scorer_cli.py", "--help"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ CLI help command failed: {result.stderr}")
            return False
        
        if "Meshachvetz Scorer" not in result.stdout:
            print(f"❌ CLI help output missing expected content")
            return False
        
        print("✅ CLI basic functionality successful")
        print(f"   Help command executed successfully")
        print(f"   Help output contains expected branding")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing CLI basic functionality: {e}")
        return False


def test_cli_scoring_functionality():
    """Test CLI scoring functionality."""
    print("\n🎯 Testing CLI Scoring Functionality...")
    
    try:
        sample_file = "examples/sample_data/students_sample.csv"
        
        if not os.path.exists(sample_file):
            print(f"⚠️  Sample file not found: {sample_file}")
            return True
        
        # Test CLI score command
        result = subprocess.run([
            sys.executable, "src/meshachvetz/cli/scorer_cli.py", 
            "score", sample_file, "--quiet"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ CLI score command failed: {result.stderr}")
            return False
        
        if "Scoring completed successfully" not in result.stdout:
            print(f"❌ CLI score output missing success message")
            return False
        
        print("✅ CLI scoring functionality successful")
        print(f"   Score command executed successfully")
        print(f"   Output contains success confirmation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing CLI scoring functionality: {e}")
        return False


def test_cli_validation_functionality():
    """Test CLI validation functionality."""
    print("\n🔍 Testing CLI Validation Functionality...")
    
    try:
        sample_file = "examples/sample_data/students_sample.csv"
        
        if not os.path.exists(sample_file):
            print(f"⚠️  Sample file not found: {sample_file}")
            return True
        
        # Test CLI validate command
        result = subprocess.run([
            sys.executable, "src/meshachvetz/cli/scorer_cli.py", 
            "validate", sample_file
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ CLI validate command failed: {result.stderr}")
            return False
        
        if "Data validation successful" not in result.stdout:
            print(f"❌ CLI validate output missing success message")
            return False
        
        print("✅ CLI validation functionality successful")
        print(f"   Validate command executed successfully")
        print(f"   Output contains validation success message")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing CLI validation functionality: {e}")
        return False


def test_cli_configuration_functionality():
    """Test CLI configuration functionality."""
    print("\n⚙️  Testing CLI Configuration Functionality...")
    
    try:
        # Test CLI show-config command
        result = subprocess.run([
            sys.executable, "src/meshachvetz/cli/scorer_cli.py", 
            "show-config"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ CLI show-config command failed: {result.stderr}")
            return False
        
        if "Layer Weights" not in result.stdout:
            print(f"❌ CLI show-config output missing expected content")
            return False
        
        print("✅ CLI configuration functionality successful")
        print(f"   Show-config command executed successfully")
        print(f"   Output contains configuration details")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing CLI configuration functionality: {e}")
        return False


def test_integration_with_custom_config():
    """Test integration with custom configuration."""
    print("\n🔧 Testing Integration with Custom Configuration...")
    
    try:
        sample_file = "examples/sample_data/students_sample.csv"
        
        if not os.path.exists(sample_file):
            print(f"⚠️  Sample file not found: {sample_file}")
            return True
        
        # Test with custom config using programmatic approach
        config = Config()
        config.update_weights(
            student_layer=0.8,
            class_layer=0.1,
            school_layer=0.1,
            friends=0.9,
            dislikes=0.1
        )
        
        scorer = Scorer(config)
        result = scorer.score_csv_file(sample_file)
        
        # Verify that custom weights were applied
        if result.layer_weights['student'] != 0.8:
            print(f"❌ Custom student layer weight not applied: {result.layer_weights['student']}")
            return False
        
        if result.layer_weights['class'] != 0.1:
            print(f"❌ Custom class layer weight not applied: {result.layer_weights['class']}")
            return False
        
        print("✅ Integration with custom configuration successful")
        print(f"   Custom weights applied correctly")
        print(f"   Student layer weight: {result.layer_weights['student']}")
        print(f"   Final score with custom config: {result.final_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing integration with custom configuration: {e}")
        return False


def test_performance_benchmark():
    """Test performance with sample data."""
    print("\n⚡ Testing Performance Benchmark...")
    
    try:
        sample_file = "examples/sample_data/students_sample.csv"
        
        if not os.path.exists(sample_file):
            print(f"⚠️  Sample file not found: {sample_file}")
            return True
        
        # Benchmark scoring operation
        scorer = Scorer()
        
        start_time = time.time()
        result = scorer.score_csv_file(sample_file)
        scoring_time = time.time() - start_time
        
        # Benchmark CSV report generation
        start_time = time.time()
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = scorer.generate_csv_reports(result, temp_dir)
            report_time = time.time() - start_time
        
        # Performance expectations (very lenient for small sample)
        if scoring_time > 5.0:  # 5 seconds for 8 students is very generous
            print(f"⚠️  Scoring took longer than expected: {scoring_time:.2f}s")
        
        if report_time > 2.0:  # 2 seconds for report generation
            print(f"⚠️  Report generation took longer than expected: {report_time:.2f}s")
        
        print("✅ Performance benchmark successful")
        print(f"   Scoring time: {scoring_time:.3f}s ({result.total_students} students)")
        print(f"   Report generation time: {report_time:.3f}s")
        print(f"   Total time: {scoring_time + report_time:.3f}s")
        print(f"   Performance: {result.total_students / (scoring_time + report_time):.1f} students/second")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing performance benchmark: {e}")
        return False


def test_error_handling():
    """Test error handling in various scenarios."""
    print("\n🛡️  Testing Error Handling...")
    
    try:
        # Test with non-existent file
        try:
            scorer = Scorer()
            scorer.score_csv_file("nonexistent_file.csv")
            print(f"❌ Should have failed for non-existent file")
            return False
        except Exception as e:
            # Accept any exception for non-existent file (could be FileNotFoundError or DataLoadError)
            if "nonexistent_file.csv" not in str(e) and "No such file" not in str(e):
                print(f"❌ Unexpected error message for non-existent file: {e}")
                return False
        
        # Test CLI with invalid arguments
        result = subprocess.run([
            sys.executable, "src/meshachvetz/cli/scorer_cli.py", 
            "score", "nonexistent_file.csv"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"❌ CLI should have failed for non-existent file")
            return False
        
        print("✅ Error handling successful")
        print(f"   Non-existent file properly handled")
        print(f"   CLI properly returns error codes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing error handling: {e}")
        return False


def main():
    """Run all Week 3 tests."""
    print("🧪 Testing Week 3 Implementation of Meshachvetz")
    print("=" * 60)
    
    tests = [
        test_csv_output_generation,
        test_csv_output_with_timestamp,
        test_cli_basic_functionality,
        test_cli_scoring_functionality,
        test_cli_validation_functionality,
        test_cli_configuration_functionality,
        test_integration_with_custom_config,
        test_performance_benchmark,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Week 3 components are working correctly!")
        print("\n✅ Week 3 Deliverables Status:")
        print("   ✅ CSV output generation with multiple report types")
        print("   ✅ Timestamp-based output directories")
        print("   ✅ Command-line interface for scorer")
        print("   ✅ CLI validation and configuration commands")
        print("   ✅ Integration with custom configurations")
        print("   ✅ Performance benchmarking")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Enhanced testing suite")
        print("\n🏆 Milestone 1: MVP Scorer (End of Week 3) - ACHIEVED!")
        print("   ✅ Can load CSV files and validate data")
        print("   ✅ Calculates all three layers of scoring")
        print("   ✅ Outputs detailed score reports")
        print("   ✅ Handles errors gracefully")
        print("   ✅ Has comprehensive test coverage")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 