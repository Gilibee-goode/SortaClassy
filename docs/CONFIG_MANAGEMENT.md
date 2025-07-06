# Configuration Management

The Meshachvetz system now supports advanced configuration management that allows you to easily switch between different configuration profiles.

## Overview

The configuration management system provides the following capabilities:
- **Set custom defaults**: Replace the default configuration with your own custom settings
- **Reset to originals**: Restore the original default configuration
- **Status tracking**: Monitor which configuration is currently active
- **Backup protection**: Automatically maintain backups of original settings

## Commands

### `meshachvetz config set <config-file>`

Sets a custom YAML configuration file as the new default configuration.

```bash
# Set a custom configuration as the default
meshachvetz config set my_custom_config.yaml

# All future commands will use this configuration
meshachvetz score students.csv  # Uses my_custom_config.yaml settings
```

**What happens:**
- The system validates the provided configuration file
- Creates a backup of the original default configuration (if not already exists)
- Copies your custom configuration to become the new default
- Shows a summary of the new configuration weights

### `meshachvetz config reset`

Resets the default configuration back to the original system defaults.

```bash
# Reset to original configuration
meshachvetz config reset

# All future commands will use original settings
meshachvetz score students.csv  # Uses original default settings
```

**What happens:**
- Restores the original default configuration from backup
- Shows a summary of the restored configuration weights
- All future commands will use the original settings

### `meshachvetz config status`

Shows the current configuration status and file paths.

```bash
# Check configuration status
meshachvetz config status
```

**Output shows:**
- Path to current default configuration file
- Path to original backup file
- Whether the configuration has been modified from original

### `meshachvetz config show`

Shows the current configuration values (existing command).

```bash
# Show current configuration weights and values
meshachvetz config show
```

## Configuration Files

The system manages the following configuration files:

- **`config/default_scoring.yaml`**: Current default configuration (actively used)
- **`config/default_scoring_original.yaml`**: Backup of original defaults (for reset)

## Example Workflow

Here's a typical workflow for managing configurations:

```bash
# 1. Check current status
meshachvetz config status

# 2. Test with original configuration
meshachvetz score students.csv

# 3. Set custom configuration
meshachvetz config set examples/custom_config.yaml

# 4. Verify the change
meshachvetz config status

# 5. Test with new configuration
meshachvetz score students.csv

# 6. Reset to original when done
meshachvetz config reset

# 7. Verify reset
meshachvetz config status
```

## Benefits

### Easy Configuration Testing
- Test different configurations without manually editing files
- Quickly switch between different tuning approaches
- Compare results using different weight profiles

### Safe Experimentation
- Original configuration is always preserved
- Easy rollback to known good settings
- No risk of losing working configurations

### Workflow Integration
- Set project-specific configurations as defaults
- Share configurations across team members
- Maintain consistent settings across scoring runs

## Error Handling

The system provides clear error messages for common issues:

- **Invalid YAML**: Shows parsing errors with line numbers
- **Missing files**: Reports file not found errors
- **Missing backup**: Automatically creates backup if needed
- **Permission issues**: Reports file system errors

## Best Practices

### Configuration Management
1. **Test first**: Always test new configurations with `--config` before setting as default
2. **Document changes**: Keep notes on what each custom configuration optimizes for
3. **Use version control**: Track your custom configuration files in git
4. **Reset when done**: Reset to original defaults when finished with experiments

### File Organization
```
project/
├── config/
│   ├── default_scoring.yaml          # Current default (managed by system)
│   └── default_scoring_original.yaml # Original backup (managed by system)
├── custom_configs/
│   ├── high_student_focus.yaml       # Your custom configurations
│   ├── balanced_approach.yaml
│   └── size_priority.yaml
└── examples/
    └── custom_config.yaml             # Example custom configuration
```

This system makes it easy to manage different scoring approaches while maintaining the safety and reliability of the original configuration.

## Logging and Verbosity

The system provides different levels of output detail:

### Default Mode
```bash
meshachvetz score students.csv
```
Shows essential information only - no detailed log messages, clean output.

### Verbose Mode  
```bash
meshachvetz score students.csv --verbose
```
Shows detailed logging including data loading progress, scoring calculations, and technical details.

### Quiet Mode
```bash
meshachvetz score students.csv --quiet
```
Shows minimal output - only final results and errors.

This applies to all commands:
- `meshachvetz score` - Scoring with different verbosity levels
- `meshachvetz validate` - Data validation with optional detailed logging
- `meshachvetz config` - Configuration management (always shows appropriate detail) 