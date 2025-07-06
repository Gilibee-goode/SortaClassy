#!/usr/bin/env python3
"""
CLI Demo Script for Meshachvetz
===============================

This script demonstrates how to use the Meshachvetz CLI for scoring student assignments.
It shows various command examples and their expected outputs.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and display the output."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success!")
            print(result.stdout)
        else:
            print("❌ Error!")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Failed to run command: {e}")

def main():
    """Main demonstration function."""
    print("🎓 MESHACHVETZ CLI DEMONSTRATION")
    print("=" * 60)
    print("This demo shows how to use the Meshachvetz CLI for scoring student assignments.")
    print("Follow along to see various command examples and their outputs.")
    
    # Change to the correct directory
    os.chdir('.')
    
    # Demo 1: Help command
    run_command(
        "./run_meshachvetz.sh --help",
        "Show CLI help and available commands"
    )
    
    # Demo 2: Score command help
    run_command(
        "./run_meshachvetz.sh score --help",
        "Show scoring command options"
    )
    
    # Demo 3: Validate data
    run_command(
        "./run_meshachvetz.sh validate examples/test_data/perfect_score_test.csv",
        "Validate CSV data format"
    )
    
    # Demo 4: Basic scoring
    run_command(
        "./run_meshachvetz.sh score examples/test_data/perfect_score_test.csv",
        "Score student assignments (basic output)"
    )
    
    # Demo 5: Scoring with reports
    run_command(
        "./run_meshachvetz.sh score examples/test_data/perfect_score_test.csv --reports --quiet",
        "Score with CSV reports generation"
    )
    
    # Demo 6: Show configuration
    run_command(
        "./run_meshachvetz.sh config show",
        "Display current configuration settings"
    )
    
    # Demo 7: Custom weights
    run_command(
        "./run_meshachvetz.sh score examples/test_data/perfect_score_test.csv --student-weight 0.8 --class-weight 0.1 --school-weight 0.1 --quiet",
        "Score with custom weight settings"
    )
    
    print("\n" + "="*60)
    print("🎉 CLI DEMONSTRATION COMPLETE")
    print("="*60)
    print("Next steps:")
    print("1. Review the generated reports in the results folder")
    print("2. Try the CLI with your own student data")
    print("3. Experiment with different weight configurations")
    print("4. Read the CLI User Guide for more advanced usage")
    
    print("\nFor detailed documentation, see:")
    print("📖 docs/CLI_USER_GUIDE.md")

if __name__ == "__main__":
    main() 