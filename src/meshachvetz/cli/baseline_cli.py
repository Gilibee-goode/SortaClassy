#!/usr/bin/env python3
"""
Baseline CLI for Meshachvetz - command-line interface for baseline generation.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from ..data.loader import DataLoader
from ..data.validator import DataValidator
from ..scorer.main_scorer import Scorer
from ..optimizer.baseline_generator import BaselineGenerator
from ..utils.config import Config
from ..utils.logging import LogLevel


def setup_logging(log_level: LogLevel) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level to use
    """
    level_map = {
        LogLevel.MINIMAL: logging.WARNING,
        LogLevel.NORMAL: logging.INFO,
        LogLevel.DETAILED: logging.DEBUG,
        LogLevel.DEBUG: logging.DEBUG
    }
    
    logging.basicConfig(
        level=level_map.get(log_level, logging.INFO),
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def generate_baseline_command(args) -> None:
    """
    Handle the baseline generation command.
    
    Args:
        args: Parsed command line arguments
    """
    try:
        # Set up logging
        try:
            log_level = LogLevel(args.log_level.lower())
        except ValueError:
            log_level = LogLevel.NORMAL
        setup_logging(log_level)
        
        logger = logging.getLogger(__name__)
        logger.info("🎯 Starting Meshachvetz Baseline Generation")
        
        # Load and validate data
        logger.info(f"📁 Loading data from {args.csv_file}")
        
        # Handle skip validation flag
        validate_data = True
        if hasattr(args, 'skip_validation') and args.skip_validation:
            logger.info("⚠️  Data validation is DISABLED - use with caution!")
            validate_data = False
            
        loader = DataLoader(validate_data=validate_data)
        school_data = loader.load_csv(args.csv_file)
        
        logger.info(f"✅ Loaded {len(school_data.students)} students, {len(school_data.classes)} classes")
        
        # Load configuration
        if args.config:
            config = Config(args.config)
        else:
            config = Config()
        
        # Create scorer
        scorer = Scorer(config)
        
        # Configure baseline generator
        baseline_config = {
            'num_runs': args.num_runs,
            'max_iterations_per_run': args.max_iterations,
            'log_level': log_level.value,
            'min_friends_required': args.min_friends,
            'respect_force_constraints': args.force_constraints,
            'early_stop_threshold': args.early_stop,
            'accept_neutral_moves': args.accept_neutral,
            'random_seed': args.random_seed
        }
        
        # Create baseline generator
        baseline_generator = BaselineGenerator(scorer, baseline_config)
        
        # Generate baseline
        logger.info(f"🚀 Generating baseline with {args.num_runs} runs...")
        statistics = baseline_generator.generate_baseline(school_data)
        
        # Save reports - let OutputManager handle if no directory specified
        if args.output_dir:
            # User specified directory
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            csv_file, summary_file = baseline_generator.save_baseline_report(
                output_dir=str(output_dir), 
                input_file=args.csv_file,
                prefix=args.output_prefix
            )
            
            logger.info(f"📊 Reports saved to {output_dir}")
        else:
            # Let OutputManager create descriptive directory
            csv_file, summary_file = baseline_generator.save_baseline_report(
                input_file=args.csv_file
            )
            
            logger.info(f"📊 Reports saved to descriptive directory")
        
        # Display summary
        if not args.quiet:
            display_baseline_summary(statistics, logger)
        
        logger.info("🎉 Baseline generation complete!")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"❌ Error generating baseline: {e}")
        if args.log_level == 'debug':
            import traceback
            traceback.print_exc()
        sys.exit(1)


def display_baseline_summary(statistics, logger) -> None:
    """
    Display a summary of baseline statistics.
    
    Args:
        statistics: BaselineStatistics object
        logger: Logger instance
    """
    logger.info("\n" + "="*50)
    logger.info("📊 BASELINE PERFORMANCE SUMMARY")
    logger.info("="*50)
    
    logger.info(f"📈 Final Scores:")
    logger.info(f"   Mean:    {statistics.final_score_mean:.2f}")
    logger.info(f"   Median:  {statistics.final_score_median:.2f}")
    logger.info(f"   Std Dev: {statistics.final_score_stdev:.2f}")
    logger.info(f"   Range:   {statistics.final_score_min:.2f} - {statistics.final_score_max:.2f}")
    
    logger.info(f"\n📈 Improvements:")
    logger.info(f"   Mean:    {statistics.improvement_mean:.2f} ({statistics.improvement_pct_mean:.1f}%)")
    logger.info(f"   Median:  {statistics.improvement_median:.2f} ({statistics.improvement_pct_median:.1f}%)")
    logger.info(f"   Std Dev: {statistics.improvement_stdev:.2f} ({statistics.improvement_pct_stdev:.1f}%)")
    logger.info(f"   Range:   {statistics.improvement_min:.2f} - {statistics.improvement_max:.2f}")
    
    logger.info(f"\n⚡ Performance:")
    logger.info(f"   Mean Duration:  {statistics.duration_mean:.2f}s")
    logger.info(f"   Mean Iterations: {statistics.iterations_mean:.0f}")
    logger.info(f"   Total Runs:     {statistics.run_count}")


def compare_to_baseline_command(args) -> None:
    """
    Handle the baseline comparison command.
    
    Args:
        args: Parsed command line arguments
    """
    try:
        # Set up logging
        try:
            log_level = LogLevel(args.log_level.lower())
        except ValueError:
            log_level = LogLevel.NORMAL
        setup_logging(log_level)
        
        logger = logging.getLogger(__name__)
        logger.info("🎯 Starting Baseline Comparison")
        
        # This would be implemented to compare results from other algorithms
        # For now, this is a placeholder for future enhancement
        logger.info("🚧 Baseline comparison feature coming soon!")
        logger.info("   Use the optimize command with --baseline to compare results")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"❌ Error in baseline comparison: {e}")
        if args.log_level == 'debug':
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point for baseline CLI."""
    parser = argparse.ArgumentParser(
        description="Meshachvetz Baseline Generator - Establish performance baselines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate baseline with default settings
  meshachvetz baseline students.csv
  
  # Generate baseline with custom parameters
  meshachvetz baseline students.csv --num-runs 20 --max-iterations 2000
  
  # Generate baseline with reports
  meshachvetz baseline students.csv --output-dir results/ --output-prefix my_baseline
  
  # Generate baseline with minimal logging
  meshachvetz baseline students.csv --log-level minimal --quiet
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate baseline command
    generate_parser = subparsers.add_parser(
        'generate', 
        help='Generate performance baseline using Random Swap algorithm'
    )
    generate_parser.add_argument(
        'csv_file', 
        help='Path to CSV file containing student data'
    )
    generate_parser.add_argument(
        '--num-runs', 
        type=int, 
        default=10,
        help='Number of optimization runs to perform (default: 10)'
    )
    generate_parser.add_argument(
        '--max-iterations', 
        type=int, 
        default=1000,
        help='Maximum iterations per run (default: 1000)'
    )
    generate_parser.add_argument(
        '--output-dir', 
        '-o', 
        type=str,
        help='Output directory for baseline reports'
    )
    generate_parser.add_argument(
        '--output-prefix', 
        type=str, 
        default='baseline',
        help='Prefix for output files (default: baseline)'
    )
    generate_parser.add_argument(
        '--config', 
        '-c', 
        type=str,
        help='Path to YAML configuration file'
    )
    generate_parser.add_argument(
        '--log-level', 
        choices=['minimal', 'normal', 'detailed', 'debug'],
        default='normal',
        help='Logging level (default: normal)'
    )
    generate_parser.add_argument(
        '--quiet', 
        '-q', 
        action='store_true',
        help='Suppress summary output'
    )
    generate_parser.add_argument(
        '--min-friends', 
        type=int, 
        default=0,
        help='Minimum friends required per student (default: 0)'
    )
    generate_parser.add_argument(
        '--early-stop', 
        type=int, 
        default=100,
        help='Early stopping threshold (default: 100)'
    )
    generate_parser.add_argument(
        '--accept-neutral', 
        action='store_true',
        help='Accept neutral moves (no score change)'
    )
    generate_parser.add_argument(
        '--force-constraints', 
        action='store_true', 
        default=True,
        help='Respect force_class and force_friend constraints'
    )
    generate_parser.add_argument(
        '--random-seed', 
        type=int,
        help='Random seed for reproducibility'
    )
    
    # Compare to baseline command (placeholder)
    compare_parser = subparsers.add_parser(
        'compare', 
        help='Compare algorithm results to baseline (coming soon)'
    )
    compare_parser.add_argument(
        'results_file', 
        help='Path to optimization results file'
    )
    compare_parser.add_argument(
        '--baseline-file', 
        type=str,
        help='Path to baseline results file'
    )
    compare_parser.add_argument(
        '--log-level', 
        choices=['minimal', 'normal', 'detailed', 'debug'],
        default='normal',
        help='Logging level (default: normal)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Default to generate if no command specified
    if not args.command:
        args.command = 'generate'
    
    # Execute command
    if args.command == 'generate':
        generate_baseline_command(args)
    elif args.command == 'compare':
        compare_to_baseline_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main() 