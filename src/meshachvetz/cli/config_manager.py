#!/usr/bin/env python3
"""
Configuration management for Meshachvetz CLI - handles setting and resetting default configurations.
"""

import os
import shutil
from pathlib import Path
import yaml
from typing import Optional

# Get the project root directory
def get_project_root() -> Path:
    """Get the project root directory."""
    current_file = Path(__file__)
    # Go up: config_manager.py -> cli -> meshachvetz -> src -> project_root
    return current_file.parent.parent.parent.parent

class ConfigManager:
    """Manages configuration file operations for the Meshachvetz system."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.project_root = get_project_root()
        self.config_dir = self.project_root / "config"
        self.default_config_path = self.config_dir / "default_scoring.yaml"
        self.original_config_path = self.config_dir / "default_scoring_original.yaml"
        
    def validate_config_file(self, config_path: str) -> bool:
        """
        Validate that a configuration file exists and is valid YAML.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            config_file = Path(config_path)
            
            # Check if file exists
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            # Try to parse as YAML
            with open(config_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
                
            return True
            
        except Exception as e:
            print(f"❌ Error validating configuration file: {e}")
            return False
    
    def set_default_config(self, new_config_path: str) -> bool:
        """
        Set a new configuration file as the default.
        
        Args:
            new_config_path: Path to the new configuration file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            new_config_file = Path(new_config_path)
            
            # Validate the new config file
            if not self.validate_config_file(new_config_path):
                return False
            
            # Ensure original backup exists
            if not self.original_config_path.exists():
                print("⚠️  Original configuration backup not found. Creating backup first...")
                if self.default_config_path.exists():
                    shutil.copy2(self.default_config_path, self.original_config_path)
                    print(f"✅ Created backup: {self.original_config_path}")
                else:
                    print("❌ No existing default configuration found.")
                    return False
            
            # Copy the new config to replace the default
            shutil.copy2(new_config_file, self.default_config_path)
            
            print(f"✅ Successfully set new default configuration from: {new_config_path}")
            print(f"📁 Default configuration updated: {self.default_config_path}")
            
            # Show a brief summary of the new config
            self._show_config_summary()
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting default configuration: {e}")
            return False
    
    def reset_to_original(self) -> bool:
        """
        Reset the default configuration to the original.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if original backup exists
            if not self.original_config_path.exists():
                print(f"❌ Original configuration backup not found: {self.original_config_path}")
                print("💡 Cannot reset without the original configuration backup.")
                return False
            
            # Copy the original back to default
            shutil.copy2(self.original_config_path, self.default_config_path)
            
            print(f"✅ Successfully reset configuration to original defaults")
            print(f"📁 Default configuration restored: {self.default_config_path}")
            
            # Show a brief summary of the restored config
            self._show_config_summary()
            
            return True
            
        except Exception as e:
            print(f"❌ Error resetting configuration: {e}")
            return False
    
    def _show_config_summary(self) -> None:
        """Show a brief summary of the current default configuration."""
        try:
            with open(self.default_config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            print(f"\n📊 Configuration Summary:")
            
            # Show layer weights
            if 'weights' in config_data and 'layers' in config_data['weights']:
                layers = config_data['weights']['layers']
                print(f"   Layer Weights: Student={layers.get('student', 'N/A')}, " +
                      f"Class={layers.get('class', 'N/A')}, " +
                      f"School={layers.get('school', 'N/A')}")
            
            # Show normalization factors
            if 'normalization' in config_data:
                norm = config_data['normalization']
                print(f"   Normalization: Academic={norm.get('academic_score_factor', 'N/A')}, " +
                      f"Behavior={norm.get('behavior_rank_factor', 'N/A')}")
            
        except Exception as e:
            print(f"⚠️  Could not load configuration summary: {e}")
    
    def get_config_status(self) -> dict:
        """
        Get the current configuration status.
        
        Returns:
            Dictionary with configuration status information
        """
        status = {
            'default_exists': self.default_config_path.exists(),
            'original_backup_exists': self.original_config_path.exists(),
            'default_path': str(self.default_config_path),
            'original_path': str(self.original_config_path)
        }
        
        # Check if current default is different from original
        if status['default_exists'] and status['original_backup_exists']:
            try:
                with open(self.default_config_path, 'r') as f:
                    default_content = f.read()
                with open(self.original_config_path, 'r') as f:
                    original_content = f.read()
                status['is_modified'] = default_content != original_content
            except:
                status['is_modified'] = None
        else:
            status['is_modified'] = None
            
        return status


def handle_config_set_command(config_file: str) -> None:
    """Handle the config set command."""
    print("⚙️  Meshachvetz Configuration Manager")
    print("=" * 40)
    print(f"🔧 Setting new default configuration from: {config_file}")
    
    manager = ConfigManager()
    
    if manager.set_default_config(config_file):
        print(f"\n💡 The new configuration will be used by default for all future commands.")
        print(f"💡 Use 'meshachvetz config reset' to restore original defaults.")
    else:
        print(f"\n❌ Failed to set new default configuration.")
        exit(1)


def handle_config_reset_command() -> None:
    """Handle the config reset command."""
    print("⚙️  Meshachvetz Configuration Manager")
    print("=" * 40)
    print(f"🔄 Resetting configuration to original defaults...")
    
    manager = ConfigManager()
    
    if manager.reset_to_original():
        print(f"\n💡 Original default configuration has been restored.")
        print(f"💡 All future commands will use the original settings.")
    else:
        print(f"\n❌ Failed to reset configuration to defaults.")
        exit(1)


def handle_config_status_command() -> None:
    """Handle showing configuration status."""
    print("⚙️  Meshachvetz Configuration Status")
    print("=" * 40)
    
    manager = ConfigManager()
    status = manager.get_config_status()
    
    print(f"📁 Default config: {status['default_path']}")
    print(f"   Status: {'✅ Exists' if status['default_exists'] else '❌ Missing'}")
    
    print(f"📁 Original backup: {status['original_path']}")
    print(f"   Status: {'✅ Exists' if status['original_backup_exists'] else '❌ Missing'}")
    
    if status['is_modified'] is not None:
        if status['is_modified']:
            print(f"🔧 Configuration: Modified from original")
        else:
            print(f"📊 Configuration: Using original defaults")
    else:
        print(f"❓ Configuration: Status unknown") 