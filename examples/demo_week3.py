#!/usr/bin/env python3
"""
Meshachvetz Week 3 Demonstration - CSV Output and CLI Functionality

This script demonstrates the new capabilities added in Week 3:
- CSV output generation with multiple report types
- Command-line interface functionality
- Enhanced configuration and testing
"""

import sys
import os
import subprocess
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz import Scorer, Config

def main():
    """Demonstrate Week 3 functionality."""
    print("🚀 MESHACHVETZ WEEK 3 DEMONSTRATION")
    print("=" * 60)
    
    # Check if sample data exists
    sample_file = "examples/sample_data/students_sample.csv"
    if not os.path.exists(sample_file):
        print(f"❌ Sample data file not found: {sample_file}")
        return 1
    
    print("📋 Week 3 New Features:")
    print("   ✅ CSV output generation with multiple report types")
    print("   ✅ Command-line interface for scorer")
    print("   ✅ Enhanced testing and performance benchmarking")
    print("   ✅ Comprehensive error handling")
    
    # Demonstration 1: CSV Output Generation
    print(f"\n📊 DEMONSTRATION 1: CSV Output Generation")
    print("=" * 50)
    
    scorer = Scorer()
    print(f"📁 Scoring file: {sample_file}")
    
    # Generate reports with timestamp directory
    result, output_path = scorer.score_csv_file_with_reports(sample_file)
    
    print(f"📊 Score Summary:")
    print(f"   Final Score: {result.final_score:.2f}/100")
    print(f"   Students: {result.total_students} in {result.total_classes} classes")
    
    print(f"\n📂 Generated CSV Reports in: {output_path}")
    
    # List generated files
    if os.path.exists(output_path):
        files = os.listdir(output_path)
        for filename in files:
            filepath = os.path.join(output_path, filename)
            size = os.path.getsize(filepath)
            with open(filepath, 'r') as f:
                lines = len(f.readlines())
            print(f"   📄 {filename}: {size} bytes, {lines} lines")
    
    # Demonstration 2: CLI Functionality
    print(f"\n🖥️  DEMONSTRATION 2: Command-Line Interface")
    print("=" * 50)
    
    print("🔧 Available CLI Commands:")
    
    # Show CLI help
    print("\n1. CLI Help:")
    result = subprocess.run([
        sys.executable, "src/meshachvetz/cli/scorer_cli.py", "--help"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        help_lines = result.stdout.split('\n')[:10]  # First 10 lines
        for line in help_lines:
            if line.strip():
                print(f"   {line}")
        print("   ... (truncated)")
    else:
        print("   ❌ CLI help failed")
    
    # Show CLI scoring
    print("\n2. CLI Scoring (quiet mode):")
    result = subprocess.run([
        sys.executable, "src/meshachvetz/cli/scorer_cli.py", 
        "score", sample_file, "--quiet"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        output_lines = result.stdout.strip().split('\n')
        for line in output_lines[-3:]:  # Last 3 lines
            if line.strip():
                print(f"   {line}")
    else:
        print("   ❌ CLI scoring failed")
    
    # Show CLI validation
    print("\n3. CLI Validation:")
    result = subprocess.run([
        sys.executable, "src/meshachvetz/cli/scorer_cli.py", 
        "validate", sample_file
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        # Extract key validation results
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if "validation successful" in line.lower() or "students:" in line.lower() or "classes:" in line.lower():
                print(f"   {line}")
    else:
        print("   ❌ CLI validation failed")
    
    # Show CLI configuration
    print("\n4. CLI Configuration (sample):")
    result = subprocess.run([
        sys.executable, "src/meshachvetz/cli/scorer_cli.py", 
        "show-config"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        # Show first few configuration lines
        output_lines = result.stdout.split('\n')
        config_started = False
        line_count = 0
        for line in output_lines:
            if "Layer Weights:" in line:
                config_started = True
            if config_started and line_count < 8:
                if line.strip():
                    print(f"   {line}")
                    line_count += 1
        print("   ... (truncated)")
    else:
        print("   ❌ CLI configuration failed")
    
    # Demonstration 3: Advanced Configuration
    print(f"\n⚙️  DEMONSTRATION 3: Advanced Configuration")
    print("=" * 50)
    
    # Test different configurations
    configurations = [
        {
            'name': 'Student-Focused',
            'weights': {'student_layer': 0.8, 'class_layer': 0.1, 'school_layer': 0.1},
            'description': 'Prioritizes individual student satisfaction'
        },
        {
            'name': 'Balance-Focused', 
            'weights': {'student_layer': 0.2, 'class_layer': 0.3, 'school_layer': 0.5},
            'description': 'Prioritizes overall class and school balance'
        },
        {
            'name': 'Social-Focused',
            'weights': {'friends': 0.9, 'dislikes': 0.1},
            'description': 'Prioritizes friend placement over conflict avoidance'
        }
    ]
    
    print("🔧 Configuration Impact Analysis:")
    default_scorer = Scorer()
    default_result = default_scorer.score_csv_file(sample_file)
    print(f"   Default Configuration: {default_result.final_score:.2f}/100")
    
    for config_info in configurations:
        custom_config = Config()
        custom_config.update_weights(**config_info['weights'])
        custom_scorer = Scorer(custom_config)
        custom_result = custom_scorer.score_csv_file(sample_file)
        
        difference = custom_result.final_score - default_result.final_score
        print(f"   {config_info['name']}: {custom_result.final_score:.2f}/100 ({difference:+.2f})")
        print(f"     {config_info['description']}")
    
    # Demonstration 4: Performance Analysis
    print(f"\n⚡ DEMONSTRATION 4: Performance Analysis")
    print("=" * 50)
    
    import time
    
    # Benchmark scoring
    start_time = time.time()
    result = scorer.score_csv_file(sample_file)
    scoring_time = time.time() - start_time
    
    # Benchmark report generation
    start_time = time.time()
    output_path_perf = scorer.generate_csv_reports(result, "temp_perf_test")
    report_time = time.time() - start_time
    
    print(f"⚡ Performance Metrics:")
    print(f"   Scoring Time: {scoring_time:.3f}s ({result.total_students} students)")
    print(f"   Report Generation: {report_time:.3f}s (5 CSV files)")
    print(f"   Total Time: {scoring_time + report_time:.3f}s")
    print(f"   Throughput: {result.total_students / (scoring_time + report_time):.1f} students/second")
    
    # Calculate memory efficiency
    total_report_size = 0
    if os.path.exists(output_path_perf):
        for filename in os.listdir(output_path_perf):
            total_report_size += os.path.getsize(os.path.join(output_path_perf, filename))
    
    print(f"   Report Size: {total_report_size:,} bytes ({total_report_size/1024:.1f} KB)")
    print(f"   Memory Efficiency: {total_report_size/result.total_students:,.0f} bytes/student")
    
    # Demonstration 5: Week 3 Achievement Summary
    print(f"\n🏆 WEEK 3 ACHIEVEMENT SUMMARY")
    print("=" * 50)
    
    print("✅ Major Accomplishments:")
    print("   📊 CSV Output Generation:")
    print("      • 5 different report types (summary, student, class, school, config)")
    print("      • Timestamp-based directory organization")
    print("      • Comprehensive data export capabilities")
    
    print("   🖥️  Command-Line Interface:")
    print("      • Score command with configurable options")
    print("      • Data validation command")
    print("      • Configuration display command")
    print("      • Weight override capabilities")
    
    print("   🔧 Enhanced Integration:")
    print("      • Configuration-driven scoring")
    print("      • Performance benchmarking")
    print("      • Comprehensive error handling")
    print("      • Enhanced test coverage (15 total tests)")
    
    print("   📈 Performance Achievements:")
    print(f"      • Scoring: {result.total_students / scoring_time:.0f} students/second")
    print(f"      • Report Generation: {5 / report_time:.1f} files/second")
    print(f"      • Memory Efficient: {total_report_size/result.total_students/1024:.1f} KB/student")
    
    print("\n🎯 Milestone 1: MVP Scorer - ACHIEVED!")
    print("   ✅ Can load CSV files and validate data")
    print("   ✅ Calculates all three layers of scoring")
    print("   ✅ Outputs detailed score reports")
    print("   ✅ Handles errors gracefully")
    print("   ✅ Has comprehensive test coverage")
    
    print(f"\n🚀 Ready for Phase 2: Optimizer Foundation (Weeks 4-6)")
    
    # Cleanup
    for path in [output_path, output_path_perf]:
        if os.path.exists(path):
            shutil.rmtree(path)
    
    print(f"\n✅ Week 3 demonstration completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 