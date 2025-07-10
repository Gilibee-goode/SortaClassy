#!/usr/bin/env python3
"""
Scorer CLI for Meshachvetz - Command-line interface for scoring student assignments.
"""

import argparse
import sys
import os
import logging
from pathlib import Path

# Add src directory to path for imports
current_dir = os.path.dirname(__file__)
src_dir = os.path.join(current_dir, '..', '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from meshachvetz import Scorer, Config


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_file_exists(filepath: str) -> str:
    """Validate that a file exists."""
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError(f"File does not exist: {filepath}")
    return filepath


def main():
    """Main CLI function for scoring."""
    parser = argparse.ArgumentParser(
        description="Meshachvetz Scorer - Calculate assignment quality scores for student class assignments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score a CSV file with default settings
  python scorer_cli.py score students.csv

  # Score with custom configuration
  python scorer_cli.py score students.csv --config custom_config.yaml

  # Score and generate CSV reports
  python scorer_cli.py score students.csv --reports

  # Score with custom output directory
  python scorer_cli.py score students.csv --reports --output results_2024

  # Score with detailed console output
  python scorer_cli.py score students.csv --detailed

  # Score with verbose logging and detailed statistics
  python scorer_cli.py score students.csv --verbose --detailed

  # Score with specific layer weights
  python scorer_cli.py score students.csv --student-weight 0.6 --class-weight 0.2 --school-weight 0.2
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Score command
    score_parser = subparsers.add_parser('score', help='Score a student assignment CSV file')
    score_parser.add_argument('csv_file', type=validate_file_exists, help='Path to CSV file containing student data')
    score_parser.add_argument('--config', '-c', type=str, help='Path to YAML configuration file')
    score_parser.add_argument('--reports', '-r', action='store_true', help='Generate CSV reports')
    score_parser.add_argument('--output', '-o', type=str, help='Output directory for reports')
    score_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed statistics from each scoring layer')
    score_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    score_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress non-essential output')
    score_parser.add_argument('--skip-validation', action='store_true', help='Skip data validation (use with caution)')
    
    # Configuration override options
    score_parser.add_argument('--student-weight', type=float, help='Student layer weight (0.0-1.0)')
    score_parser.add_argument('--class-weight', type=float, help='Class layer weight (0.0-1.0)')
    score_parser.add_argument('--school-weight', type=float, help='School layer weight (0.0-1.0)')
    score_parser.add_argument('--friends-weight', type=float, help='Friend satisfaction weight (0.0-1.0)')
    score_parser.add_argument('--dislikes-weight', type=float, help='Conflict avoidance weight (0.0-1.0)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a student data CSV file')
    validate_parser.add_argument('csv_file', type=validate_file_exists, help='Path to CSV file to validate')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    validate_parser.add_argument('--skip-validation', action='store_true', help='Skip validation and just check file structure (contradictory but allows testing)')
    
    # Show config command
    config_parser = subparsers.add_parser('show-config', help='Show current configuration')
    config_parser.add_argument('--config', '-c', type=str, help='Path to YAML configuration file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Set up logging
    if hasattr(args, 'verbose') and args.verbose:
        setup_logging("DEBUG")
    elif hasattr(args, 'quiet') and args.quiet:
        setup_logging("WARNING")
    else:
        setup_logging("WARNING")  # Default to WARNING, only show INFO with --verbose
    
    try:
        if args.command == 'score':
            handle_score_command(args)
        elif args.command == 'validate':
            handle_validate_command(args)
        elif args.command == 'show-config':
            handle_show_config_command(args)
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def handle_score_command(args):
    """Handle the score command."""
    print("🎯 Meshachvetz Scorer")
    print("=" * 40)
    
    # Load configuration
    config = Config()
    if args.config:
        print(f"📋 Loading configuration from: {args.config}")
        config = Config(args.config)
    else:
        print("📋 Using default configuration")
    
    # Apply command-line weight overrides
    weight_overrides = {}
    if args.student_weight is not None:
        weight_overrides['student_layer'] = args.student_weight
    if args.class_weight is not None:
        weight_overrides['class_layer'] = args.class_weight
    if args.school_weight is not None:
        weight_overrides['school_layer'] = args.school_weight
    if args.friends_weight is not None:
        weight_overrides['friends'] = args.friends_weight
    if args.dislikes_weight is not None:
        weight_overrides['dislikes'] = args.dislikes_weight
    
    if weight_overrides:
        print(f"⚙️  Applying weight overrides: {weight_overrides}")
        config.update_weights(**weight_overrides)
    
    # Create scorer with validation setting
    # Override validation if skip-validation is specified
    if hasattr(args, 'skip_validation') and args.skip_validation:
        print("⚠️  Data validation is DISABLED - use with caution!")
        # We need to modify the scorer's data loader to skip validation
        scorer = Scorer(config)
        scorer.data_loader.validate_data = False
        scorer.data_loader.validator = None
    else:
        scorer = Scorer(config)
    
    # Score the file
    print(f"📁 Loading and scoring: {args.csv_file}")
    
    if args.reports:
        # Score with reports
        result, output_path = scorer.score_csv_file_with_reports(args.csv_file, args.output)
        print(f"📊 CSV reports generated in: {output_path}")
    else:
        # Score without reports
        result = scorer.score_csv_file(args.csv_file)
    
    # Display results
    if not args.quiet:
        print("\n🏆 SCORING RESULTS")
        print(f"Final Score: {result.final_score:.2f}/100")
        print(f"Total Students: {result.total_students}")
        print(f"Total Classes: {result.total_classes}")
        
        print(f"\n📊 Layer Breakdown:")
        print(f"   Student Layer: {result.student_layer_score:.2f}/100 (weight: {result.layer_weights['student']})")
        print(f"   Class Layer:   {result.class_layer_score:.2f}/100 (weight: {result.layer_weights['class']})")
        print(f"   School Layer:  {result.school_layer_score:.2f}/100 (weight: {result.layer_weights['school']})")
        
        # Show detailed report if requested
        if args.detailed:
            print(f"\n{scorer.get_focused_summary(result)}")
    
    print(f"\n✅ Scoring completed successfully!")


def handle_validate_command(args):
    """Handle the validate command."""
    print("🔍 Meshachvetz Data Validator")
    print("=" * 40)
    
    # Handle skip validation flag (somewhat contradictory but useful for testing)
    if hasattr(args, 'skip_validation') and args.skip_validation:
        print("⚠️  Data validation is DISABLED - only checking file structure!")
    
    # Create scorer to use its data loader
    scorer = Scorer()
    
    # Override validation if skip-validation is specified
    if hasattr(args, 'skip_validation') and args.skip_validation:
        scorer.data_loader.validate_data = False
        scorer.data_loader.validator = None
    
    print(f"📁 Validating: {args.csv_file}")
    
    try:
        # Load and validate data
        school_data = scorer.load_data(args.csv_file)
        
        print(f"✅ Data validation successful!")
        print(f"   Total Students: {school_data.total_students}")
        print(f"   Total Classes: {school_data.total_classes}")
        
        # Check for force constraint issues
        constraint_errors = school_data.validate_force_constraints()
        if constraint_errors:
            print(f"\n⚠️  Force constraint warnings ({len(constraint_errors)}):")
            for error in constraint_errors:
                print(f"   - {error}")
        else:
            print(f"✅ No force constraint issues found")
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


def handle_show_config_command(args):
    """Handle the show-config command."""
    print("⚙️  Meshachvetz Configuration")
    print("=" * 40)
    
    # Load configuration
    if args.config:
        print(f"📋 Loading configuration from: {args.config}")
        config = Config(args.config)
    else:
        print("📋 Showing default configuration")
        config = Config()
    
    # Display configuration
    print(f"\n🏗️  Layer Weights:")
    print(f"   Student Layer: {config.weights.student_layer}")
    print(f"   Class Layer:   {config.weights.class_layer}")
    print(f"   School Layer:  {config.weights.school_layer}")
    
    print(f"\n👥 Student Layer Weights:")
    print(f"   Friends:  {config.weights.friends}")
    print(f"   Dislikes: {config.weights.dislikes}")
    
    print(f"\n🏫 Class Layer Weights:")
    print(f"   Gender Balance: {config.weights.gender_balance}")
    
    print(f"\n🏛️  School Layer Weights:")
    print(f"   Academic Balance:     {config.weights.academic_balance}")
    print(f"   Behavior Balance:     {config.weights.behavior_balance}")
    print(f"   Studentiality Balance: {config.weights.studentiality_balance}")
    print(f"   Size Balance:         {config.weights.size_balance}")
    print(f"   Assistance Balance:   {config.weights.assistance_balance}")
    
    print(f"\n📏 Normalization Factors:")
    print(f"   Academic Score Factor:    {config.normalization.academic_score_factor}")
    print(f"   Behavior Rank Factor:     {config.normalization.behavior_rank_factor}")
    print(f"   Studentiality Rank Factor: {config.normalization.studentiality_rank_factor}")
    print(f"   Class Size Factor:        {config.normalization.class_size_factor}")
    print(f"   Assistance Count Factor:  {config.normalization.assistance_count_factor}")


if __name__ == "__main__":
    main() 