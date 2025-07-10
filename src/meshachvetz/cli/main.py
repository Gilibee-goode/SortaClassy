#!/usr/bin/env python3
"""
Main CLI entry point for Meshachvetz - Student Class Assignment Optimizer
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from meshachvetz import __version__
from .scorer_cli import main as scorer_main
from .optimizer_cli import main as optimizer_main
from .baseline_cli import main as baseline_main
from .config_manager import handle_config_set_command, handle_config_reset_command, handle_config_status_command
from .interactive_cli import main as interactive_main


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Meshachvetz - Student Class Assignment Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Commands:
  interactive   Start interactive menu mode (recommended for beginners)
  score         Score a student assignment CSV file
  optimize      Optimize student class assignments
  baseline      Generate performance baselines using Random Swap algorithm
  generate-assignment   Generate initial class assignments
  validate      Validate a student data CSV file  
  config        Show or manage configuration
    show        Show current configuration
    set         Set a configuration file as the new default
    reset       Reset configuration to original defaults
    status      Show configuration status and paths

Interactive Mode:
  # Launch user-friendly menu interface
  meshachvetz interactive
  
  # OR simply run without arguments to enter interactive mode
  meshachvetz

Examples:
  # Get the best optimization result automatically (uses 3 best algorithms)
  meshachvetz optimize students.csv

  # Score an existing assignment
  meshachvetz score assigned_students.csv

  # Score with detailed reports
  meshachvetz score students.csv --reports --output results/

  # Generate performance baseline
  meshachvetz baseline students.csv --output-dir results/

  # Use a specific single algorithm
  meshachvetz optimize students.csv --algorithm genetic

  # Compare specific algorithms with parallel strategy
  meshachvetz optimize students.csv --algorithms local_search genetic --strategy parallel

  # Optimize with custom parameters
  meshachvetz optimize students.csv --max-iterations 2000 --target-classes 5

For more help on a specific command:
  meshachvetz <command> --help
        """
    )
    
    parser.add_argument('--version', action='version', version=f'Meshachvetz {__version__}')
    
    # Add main commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive menu mode')
    
    # Score command
    score_parser = subparsers.add_parser('score', help='Score a student assignment CSV file')
    score_parser.add_argument('csv_file', help='Path to CSV file containing student data')
    score_parser.add_argument('--config', '-c', type=str, help='Path to YAML configuration file')
    score_parser.add_argument('--reports', '-r', action='store_true', help='Generate CSV reports')
    score_parser.add_argument('--output', '-o', type=str, help='Output directory for reports')
    score_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed statistics')
    score_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging (legacy - use --log-level debug instead)')
    score_parser.add_argument('--log-level', choices=['minimal', 'normal', 'detailed', 'debug'], 
                             default='normal', help='Set logging level for scoring progress')
    score_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress non-essential output')
    score_parser.add_argument('--skip-validation', action='store_true', help='Skip data validation (use with caution)')
    
    # Optimize command (now handles both single and multiple algorithms)
    optimize_parser = subparsers.add_parser('optimize', help='Optimize student class assignments')
    optimize_parser.add_argument('csv_file', help='Path to CSV file containing student data')
    optimize_parser.add_argument('--output', '-o', type=str, help='Output file for optimized assignment')
    optimize_parser.add_argument('--output-dir', type=str, help='Output directory for all generated files')
    optimize_parser.add_argument('--skip-validation', action='store_true', help='Skip data validation (use with caution)')
    
    # Multiple algorithms option
    optimize_parser.add_argument('--algorithms', nargs='+', 
                               choices=['random_swap', 'local_search', 'simulated_annealing', 'genetic', 'or_tools'],
                               default=['local_search', 'simulated_annealing', 'genetic'],
                               help='Multiple algorithms to compare (default: local_search, simulated_annealing, genetic)')
    
    # Multi-algorithm strategy (only used when --algorithms is specified)
    optimize_parser.add_argument('--strategy', type=str,
                               choices=['parallel', 'sequential', 'best_of'],
                               default='best_of',
                               help='Strategy when using multiple algorithms (default: best_of)')
                               
    # Single algorithm option (only used when explicitly specified)
    optimize_parser.add_argument('--algorithm', '-a', type=str, 
                                choices=['random_swap', 'local_search', 'simulated_annealing', 'genetic', 'or_tools'], 
                                help='Single optimization algorithm to use (overrides default multi-algorithm approach)')
    
    optimize_parser.add_argument('--max-iterations', type=int, default=1000,
                                help='Maximum number of optimization iterations (default: 1000)')
    optimize_parser.add_argument('--config', '-c', type=str, help='Path to YAML configuration file')
    optimize_parser.add_argument('--reports', '-r', action='store_true', help='Generate detailed reports')
    optimize_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed optimization progress')
    optimize_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging (legacy - use --log-level debug instead)')
    optimize_parser.add_argument('--log-level', choices=['minimal', 'normal', 'detailed', 'debug'], 
                                default='normal', help='Set logging level for optimization progress')
    optimize_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress non-essential output')
    optimize_parser.add_argument('--min-friends', type=int, default=1,
                                help='Minimum friends required per student (default: 1, use 0 to disable)')
    optimize_parser.add_argument('--early-stop', type=int, default=100,
                                help='Early stopping threshold (iterations without improvement)')
    optimize_parser.add_argument('--accept-neutral', action='store_true',
                                help='Accept neutral moves (no score change)')
    optimize_parser.add_argument('--force-constraints', action='store_true', default=True,
                                help='Respect force_class and force_friend constraints')
    # Initialization options
    optimize_parser.add_argument('--init-strategy', type=str, 
                                choices=['random', 'balanced', 'constraint_aware', 'academic_balanced'],
                                default='constraint_aware',
                                help='Initialization strategy for unassigned students (default: constraint_aware)')
    optimize_parser.add_argument('--no-auto-init', action='store_true',
                                help='Disable automatic initialization of unassigned students')
    optimize_parser.add_argument('--target-classes', type=int,
                                help='Number of target classes (auto-calculated if not specified)')
    
    # Baseline command
    baseline_parser = subparsers.add_parser('baseline', help='Generate performance baselines using Random Swap algorithm')
    baseline_parser.add_argument('csv_file', help='Path to CSV file containing student data')
    baseline_parser.add_argument('--num-runs', type=int, default=10,
                                help='Number of optimization runs to perform (default: 10)')
    baseline_parser.add_argument('--max-iterations', type=int, default=1000,
                                help='Maximum iterations per run (default: 1000)')
    baseline_parser.add_argument('--output-dir', '-o', type=str,
                                help='Output directory for baseline reports')
    baseline_parser.add_argument('--output-prefix', type=str, default='baseline',
                                help='Prefix for output files (default: baseline)')
    baseline_parser.add_argument('--config', '-c', type=str, help='Path to YAML configuration file')
    baseline_parser.add_argument('--log-level', choices=['minimal', 'normal', 'detailed', 'debug'],
                                default='normal', help='Logging level (default: normal)')
    baseline_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress summary output')
    baseline_parser.add_argument('--skip-validation', action='store_true', help='Skip data validation (use with caution)')
    baseline_parser.add_argument('--min-friends', type=int, default=0,
                                help='Minimum friends required per student (default: 0)')
    baseline_parser.add_argument('--early-stop', type=int, default=100,
                                help='Early stopping threshold (default: 100)')
    baseline_parser.add_argument('--accept-neutral', action='store_true',
                                help='Accept neutral moves (no score change)')
    baseline_parser.add_argument('--force-constraints', action='store_true', default=True,
                                help='Respect force_class and force_friend constraints')
    baseline_parser.add_argument('--random-seed', type=int, help='Random seed for reproducibility')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a student data CSV file')
    validate_parser.add_argument('csv_file', help='Path to CSV file to validate')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    validate_parser.add_argument('--skip-validation', action='store_true', help='Skip validation and just check file structure (contradictory but allows testing)')
    
    # Config command group
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Configuration commands')
    
    # Config show subcommand
    config_show_parser = config_subparsers.add_parser('show', help='Show current configuration')
    config_show_parser.add_argument('--config', '-c', type=str, help='Path to YAML configuration file')
    
    # Config set subcommand
    config_set_parser = config_subparsers.add_parser('set', help='Set a configuration file as the new default')
    config_set_parser.add_argument('config_file', help='Path to YAML configuration file to set as default')
    
    # Config reset subcommand
    config_reset_parser = config_subparsers.add_parser('reset', help='Reset configuration to original defaults')
    
    # Config status subcommand
    config_status_parser = config_subparsers.add_parser('status', help='Show configuration status and paths')
    
    # Generate assignment command
    generate_parser = subparsers.add_parser('generate-assignment', help='Generate initial class assignments')
    generate_parser.add_argument('csv_file', help='Path to CSV file containing student data')
    generate_parser.add_argument('--output', '-o', type=str, help='Output file for generated assignment')
    generate_parser.add_argument('--output-dir', type=str, help='Output directory for generated files')
    generate_parser.add_argument('--strategy', '-s', type=str,
                                choices=['random', 'balanced', 'constraint_aware', 'academic_balanced'],
                                default='constraint_aware',
                                help='Assignment generation strategy (default: constraint_aware)')
    generate_parser.add_argument('--target-classes', type=int,
                                help='Number of target classes (auto-calculated if not specified)')
    generate_parser.add_argument('--config', '-c', type=str, help='Path to YAML configuration file')
    generate_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    generate_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress non-essential output')
    generate_parser.add_argument('--skip-validation', action='store_true', help='Skip data validation (use with caution)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command provided, default to interactive mode
    if not args.command:
        print("🎯 Welcome to Meshachvetz! Starting interactive mode...")
        interactive_main()
        return
    
    # Handle commands
    try:
        if args.command == 'interactive':
            # Start interactive mode
            interactive_main()
        elif args.command in ['score', 'validate']:
            # Delegate to scorer CLI
            sys.argv = ['scorer_cli.py', args.command] + sys.argv[2:]
            scorer_main()
        elif args.command == 'baseline':
            # Handle baseline generation
            sys.argv = ['baseline_cli.py', 'generate'] + sys.argv[2:]
            baseline_main()
        elif args.command == 'optimize':
            # Handle both single and multiple algorithm optimization
            if hasattr(args, 'algorithm') and args.algorithm:
                # Single algorithm explicitly specified - use single algorithm mode
                sys.argv = ['optimizer_cli.py', 'optimize'] + sys.argv[2:]
                optimizer_main()
            else:
                # Multiple algorithms - use multi-algorithm mode
                sys.argv = ['optimizer_cli.py', 'optimize'] + sys.argv[2:]
                optimizer_main()
        elif args.command == 'generate-assignment':
            # Handle assignment generation
            sys.argv = ['optimizer_cli.py', 'generate-assignment'] + sys.argv[2:]
            optimizer_main()
        elif args.command == 'config':
            # Handle configuration commands
            if args.config_command == 'show':
                # Show current configuration
                sys.argv = ['scorer_cli.py', 'config', 'show'] + sys.argv[3:]
                scorer_main()
            elif args.config_command == 'set':
                handle_config_set_command(args.config_file)
            elif args.config_command == 'reset':
                handle_config_reset_command()
            elif args.config_command == 'status':
                handle_config_status_command()
            else:
                # Default to show if no subcommand
                sys.argv = ['scorer_cli.py', 'config', 'show'] + sys.argv[2:]
                scorer_main()
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 