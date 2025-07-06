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
from .config_manager import handle_config_set_command, handle_config_reset_command, handle_config_status_command


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Meshachvetz - Student Class Assignment Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Commands:
  score      Score a student assignment CSV file
  validate   Validate a student data CSV file  
  config     Show or manage configuration
    show     Show current configuration
    set      Set a configuration file as the new default
    reset    Reset configuration to original defaults
    status   Show configuration status and paths

Examples:
  # Score a CSV file with default settings
  meshachvetz score students.csv

  # Score with custom configuration and generate reports
  meshachvetz score students.csv --config custom.yaml --reports

  # Validate a CSV file
  meshachvetz validate students.csv

  # Show current configuration
  meshachvetz config show

  # Set a custom configuration as the new default
  meshachvetz config set my_config.yaml

  # Reset to original configuration
  meshachvetz config reset

  # Show configuration status
  meshachvetz config status

For more help on a specific command:
  meshachvetz <command> --help
        """
    )
    
    parser.add_argument('--version', action='version', version=f'Meshachvetz {__version__}')
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Score command - delegate to scorer_cli
    score_parser = subparsers.add_parser('score', help='Score a student assignment CSV file')
    score_parser.add_argument('csv_file', help='Path to CSV file containing student data')
    score_parser.add_argument('--config', '-c', type=str, help='Path to YAML configuration file')
    score_parser.add_argument('--reports', '-r', action='store_true', help='Generate CSV reports')
    score_parser.add_argument('--output', '-o', type=str, help='Output directory for reports')
    score_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed console report')
    score_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    score_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress non-essential output')
    
    # Configuration override options
    score_parser.add_argument('--student-weight', type=float, help='Student layer weight (0.0-1.0)')
    score_parser.add_argument('--class-weight', type=float, help='Class layer weight (0.0-1.0)')
    score_parser.add_argument('--school-weight', type=float, help='School layer weight (0.0-1.0)')
    score_parser.add_argument('--friends-weight', type=float, help='Friend satisfaction weight (0.0-1.0)')
    score_parser.add_argument('--dislikes-weight', type=float, help='Conflict avoidance weight (0.0-1.0)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a student data CSV file')
    validate_parser.add_argument('csv_file', help='Path to CSV file to validate')
    validate_parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
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
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle commands
    try:
        if args.command in ['score', 'validate']:
            # Delegate to scorer CLI
            sys.argv = ['scorer_cli.py', args.command] + sys.argv[2:]
            scorer_main()
        elif args.command == 'config':
            if args.config_command == 'show':
                # Handle config show
                sys.argv = ['scorer_cli.py', 'show-config'] + (['--config', args.config] if args.config else [])
                scorer_main()
            elif args.config_command == 'set':
                # Handle config set
                handle_config_set_command(args.config_file)
            elif args.config_command == 'reset':
                # Handle config reset
                handle_config_reset_command()
            elif args.config_command == 'status':
                # Handle config status
                handle_config_status_command()
            else:
                config_parser.print_help()
                sys.exit(1)
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 