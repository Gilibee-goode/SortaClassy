"""
Configuration management for Meshachvetz - handles YAML configuration files
for scoring weights and system parameters.
"""

from typing import Dict, Any, Optional, List
import yaml
from pathlib import Path
from dataclasses import dataclass


class ConfigError(Exception):
    """Exception raised when configuration is invalid."""
    pass


@dataclass
class ScoringWeights:
    """Configuration for scoring weights."""
    # Student layer weights
    friends: float = 0.7
    dislikes: float = 0.3
    
    # Class layer weights
    gender_balance: float = 1.0
    
    # School layer weights
    academic_balance: float = 0.05
    behavior_balance: float = 0.4
    studentiality_balance: float = 0.4
    size_balance: float = 0.0
    assistance_balance: float = 0.15
    school_origin_balance: float = 0.0  # Weight for school origin distribution balance
    
    # Layer weights
    student_layer: float = 0.75
    class_layer: float = 0.05
    school_layer: float = 0.2
    
    def validate(self) -> None:
        """Validate that all weights are positive."""
        weights = [
            self.friends, self.dislikes, self.gender_balance,
            self.academic_balance, self.behavior_balance, self.studentiality_balance,
            self.size_balance, self.assistance_balance, self.school_origin_balance,
            self.student_layer, self.class_layer, self.school_layer
        ]
        
        for weight in weights:
            if weight < 0:
                raise ConfigError(f"Weight cannot be negative: {weight}")


@dataclass 
class NormalizationFactors:
    """Configuration for normalization factors."""
    academic_score_factor: float = 2.0
    behavior_rank_factor: float = 35.0
    studentiality_rank_factor: float = 35.0
    class_size_factor: float = 5.0
    assistance_count_factor: float = 10.0
    school_origin_factor: float = 20.0  # Normalization factor for school origin balance
    
    def validate(self) -> None:
        """Validate that all factors are positive."""
        factors = [
            self.academic_score_factor, self.behavior_rank_factor, self.studentiality_rank_factor,
            self.class_size_factor, self.assistance_count_factor, self.school_origin_factor
        ]
        
        for factor in factors:
            if factor <= 0:
                raise ConfigError(f"Normalization factor must be positive: {factor}")


@dataclass
class ClassConfig:
    """Configuration for class organization parameters."""
    target_classes: int = 5
    min_class_size: int = 15
    max_class_size: int = 30
    preferred_class_size: int = 25
    allow_uneven_classes: bool = True
    
    def validate(self) -> None:
        """Validate class configuration parameters."""
        if self.target_classes <= 0:
            raise ConfigError(f"Target classes must be positive: {self.target_classes}")
        if self.min_class_size <= 0:
            raise ConfigError(f"Min class size must be positive: {self.min_class_size}")
        if self.max_class_size <= 0:
            raise ConfigError(f"Max class size must be positive: {self.max_class_size}")
        if self.preferred_class_size <= 0:
            raise ConfigError(f"Preferred class size must be positive: {self.preferred_class_size}")
        if self.min_class_size > self.max_class_size:
            raise ConfigError(f"Min class size ({self.min_class_size}) cannot be greater than max class size ({self.max_class_size})")
        if self.preferred_class_size < self.min_class_size or self.preferred_class_size > self.max_class_size:
            raise ConfigError(f"Preferred class size ({self.preferred_class_size}) must be between min ({self.min_class_size}) and max ({self.max_class_size})")


@dataclass
class ValidationRules:
    """Configuration for data validation rules."""
    student_id_length: int = 9
    max_name_length: int = 50
    min_academic_score: float = 0.0
    max_academic_score: float = 100.0
    valid_behavior_ranks: List[str] = None
    valid_boolean_values: List[str] = None
    
    def __post_init__(self):
        """Set default values for list fields."""
        if self.valid_behavior_ranks is None:
            self.valid_behavior_ranks = ['A', 'B', 'C', 'D']
        if self.valid_boolean_values is None:
            self.valid_boolean_values = [
                'true', 'false', '1', '0', 'yes', 'no',
                'True', 'False', 'TRUE', 'FALSE', 'YES', 'NO'
            ]
    
    def validate(self) -> None:
        """Validate validation rules."""
        if self.student_id_length <= 0:
            raise ConfigError(f"Student ID length must be positive: {self.student_id_length}")
        if self.max_name_length <= 0:
            raise ConfigError(f"Max name length must be positive: {self.max_name_length}")
        if self.min_academic_score < 0:
            raise ConfigError(f"Min academic score cannot be negative: {self.min_academic_score}")
        if self.max_academic_score <= self.min_academic_score:
            raise ConfigError(f"Max academic score ({self.max_academic_score}) must be greater than min ({self.min_academic_score})")
        if not self.valid_behavior_ranks:
            raise ConfigError("Valid behavior ranks cannot be empty")
        if not self.valid_boolean_values:
            raise ConfigError("Valid boolean values cannot be empty")


class Config:
    """
    Main configuration class for Meshachvetz.
    
    Manages loading and validation of YAML configuration files.
    """
    
    DEFAULT_CONFIG = {
        'weights': {
            'student_layer': {
                'friends': 0.7,
                'dislikes': 0.3
            },
            'class_layer': {
                'gender_balance': 1.0
            },
            'school_layer': {
                'academic_balance': 0.05,
                'behavior_balance': 0.4,
                'studentiality_balance': 0.4,
                'size_balance': 0.0,
                'assistance_balance': 0.15,
                'school_origin_balance': 0.0
            },
            'layers': {
                'student': 0.75,
                'class': 0.05,
                'school': 0.2
            }
        },
        'class_config': {
            'target_classes': 5,
            'min_class_size': 15,
            'max_class_size': 30,
            'preferred_class_size': 25,
            'allow_uneven_classes': True
        },
        'normalization': {
            'academic_score_factor': 2.0,
            'behavior_rank_factor': 35.0,
            'studentiality_rank_factor': 35.0,
            'class_size_factor': 5.0,
            'assistance_count_factor': 10.0,
            'school_origin_factor': 20.0
        },
        'validation': {
            'student_id_length': 9,
            'max_name_length': 50,
            'min_academic_score': 0.0,
            'max_academic_score': 100.0,
            'valid_behavior_ranks': ['A', 'B', 'C', 'D'],
            'valid_boolean_values': [
                'true', 'false', '1', '0', 'yes', 'no',
                'True', 'False', 'TRUE', 'FALSE', 'YES', 'NO'
            ]
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to YAML configuration file. If None, tries to load from 
                        default config file, falling back to defaults if not found.
        """
        self.config_file = config_file
        self.config_data = {}
        
        # Load configuration
        if config_file:
            self.load_from_file(config_file)
        else:
            # Try to load from default config file
            default_config_path = self._get_default_config_path()
            if default_config_path and default_config_path.exists():
                self.load_from_file(str(default_config_path))
            else:
                # Fall back to hardcoded defaults
                self.config_data = self.DEFAULT_CONFIG.copy()
            
        # Create structured configuration objects
        self._create_config_objects()
    
    def _get_default_config_path(self) -> Optional[Path]:
        """Get the path to the default configuration file."""
        try:
            # Get the project root directory
            current_file = Path(__file__)
            # Go up: config.py -> utils -> meshachvetz -> src -> project_root
            project_root = current_file.parent.parent.parent.parent
            default_config_path = project_root / "config" / "default_scoring.yaml"
            return default_config_path
        except Exception:
            return None
            
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            file_path: Path to the YAML configuration file
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise ConfigError(f"Configuration file not found: {file_path}")
                
            with open(path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                
            # Merge with defaults
            self.config_data = self._merge_with_defaults(loaded_config)
            
            # Validate configuration
            self._validate_config()
            
        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing YAML file: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}")
            
    def _merge_with_defaults(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge loaded configuration with defaults.
        
        Args:
            loaded_config: Configuration loaded from file
            
        Returns:
            Merged configuration
        """
        merged = self.DEFAULT_CONFIG.copy()
        
        # Deep merge function
        def deep_merge(base: Dict, update: Dict) -> Dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base
        
        return deep_merge(merged, loaded_config)
        
    def _validate_config(self) -> None:
        """Validate the configuration structure and values."""
        required_sections = ['weights', 'normalization', 'validation']
        
        for section in required_sections:
            if section not in self.config_data:
                raise ConfigError(f"Missing required configuration section: {section}")
                
        # Validate weights section
        weights = self.config_data['weights']
        required_weight_sections = ['student_layer', 'class_layer', 'school_layer', 'layers']
        
        for section in required_weight_sections:
            if section not in weights:
                raise ConfigError(f"Missing required weights section: {section}")
                
    def _create_config_objects(self) -> None:
        """Create configuration objects from loaded data."""
        # Create scoring weights
        weights_data = self.config_data.get('weights', {})
        
        student_weights = weights_data.get('student_layer', {})
        class_weights = weights_data.get('class_layer', {})
        school_weights = weights_data.get('school_layer', {})
        layer_weights = weights_data.get('layers', {})
        
        self.weights = ScoringWeights(
            # Student layer
            friends=student_weights.get('friends', 0.7),
            dislikes=student_weights.get('dislikes', 0.3),
            # Class layer
            gender_balance=class_weights.get('gender_balance', 1.0),
            # School layer
            academic_balance=school_weights.get('academic_balance', 0.05),
            behavior_balance=school_weights.get('behavior_balance', 0.4),
            studentiality_balance=school_weights.get('studentiality_balance', 0.4),
            size_balance=school_weights.get('size_balance', 0.0),
            assistance_balance=school_weights.get('assistance_balance', 0.15),
            school_origin_balance=school_weights.get('school_origin_balance', 0.0),
            # Layer weights
            student_layer=layer_weights.get('student', 0.75),
            class_layer=layer_weights.get('class', 0.05),
            school_layer=layer_weights.get('school', 0.2)
        )
        
        # Create normalization factors
        norm_data = self.config_data.get('normalization', {})
        self.normalization = NormalizationFactors(
            academic_score_factor=norm_data.get('academic_score_factor', 2.0),
            behavior_rank_factor=norm_data.get('behavior_rank_factor', 35.0),
            studentiality_rank_factor=norm_data.get('studentiality_rank_factor', 35.0),
            class_size_factor=norm_data.get('class_size_factor', 5.0),
            assistance_count_factor=norm_data.get('assistance_count_factor', 10.0),
            school_origin_factor=norm_data.get('school_origin_factor', 20.0)
        )
        
        # Create validation rules object
        val_config = self.config_data['validation']
        self.validation = ValidationRules(
            student_id_length=val_config['student_id_length'],
            max_name_length=val_config['max_name_length'],
            min_academic_score=val_config['min_academic_score'],
            max_academic_score=val_config['max_academic_score'],
            valid_behavior_ranks=val_config['valid_behavior_ranks'],
            valid_boolean_values=val_config['valid_boolean_values']
        )
        
        # Create class configuration object
        class_config_data = self.config_data.get('class_config', {})
        self.class_config = ClassConfig(
            target_classes=class_config_data.get('target_classes', 5),
            min_class_size=class_config_data.get('min_class_size', 15),
            max_class_size=class_config_data.get('max_class_size', 30),
            preferred_class_size=class_config_data.get('preferred_class_size', 25),
            allow_uneven_classes=class_config_data.get('allow_uneven_classes', True)
        )
        
        # Validate all objects
        self.weights.validate()
        self.class_config.validate()
        self.normalization.validate()
        self.validation.validate()
        
    def save_to_file(self, file_path: str) -> None:
        """
        Save current configuration to YAML file.
        
        Args:
            file_path: Path where to save the configuration
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigError(f"Error saving configuration: {e}")
            
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config_data.copy()
        
    def update_weights(self, **kwargs) -> None:
        """
        Update scoring weights.
        
        Args:
            **kwargs: Weight values to update
        """
        valid_weights = [
            'friends', 'dislikes', 'gender_balance',
            'academic_balance', 'behavior_balance', 'studentiality_balance',
            'size_balance', 'assistance_balance', 'school_origin_balance',
            'student_layer', 'class_layer', 'school_layer'
        ]
        
        for key, value in kwargs.items():
            if key not in valid_weights:
                raise ConfigError(f"Invalid weight name: {key}")
                
            if value < 0:
                raise ConfigError(f"Weight cannot be negative: {key}={value}")
                
            # Update the appropriate weight
            if key in ['friends', 'dislikes']:
                self.config_data['weights']['student_layer'][key] = value
            elif key in ['gender_balance']:
                self.config_data['weights']['class_layer'][key] = value
            elif key in ['academic_balance', 'behavior_balance', 'studentiality_balance', 'size_balance', 'assistance_balance', 'school_origin_balance']:
                self.config_data['weights']['school_layer'][key] = value
            elif key in ['student_layer', 'class_layer', 'school_layer']:
                layer_key = key.replace('_layer', '')
                self.config_data['weights']['layers'][layer_key] = value
                
        # Recreate config objects
        self._create_config_objects()
        
    @classmethod
    def create_default_config_file(cls, file_path: str) -> None:
        """
        Create a default configuration file.
        
        Args:
            file_path: Path where to create the configuration file
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(cls.DEFAULT_CONFIG, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigError(f"Error creating default configuration: {e}")
            
    def get_summary(self) -> str:
        """
        Get a formatted summary of the configuration.
        
        Returns:
            Formatted configuration summary
        """
        summary = []
        summary.append("📊 Meshachvetz Configuration Summary")
        summary.append("=" * 40)
        
        # Weights section
        summary.append("\n🎯 Scoring Weights:")
        summary.append(f"  Student Layer:")
        summary.append(f"    Friends: {self.weights.friends}")
        summary.append(f"    Dislikes: {self.weights.dislikes}")
        summary.append(f"  Class Layer:")
        summary.append(f"    Gender Balance: {self.weights.gender_balance}")
        summary.append(f"  School Layer:")
        summary.append(f"    Academic Balance: {self.weights.academic_balance}")
        summary.append(f"    Behavior Balance: {self.weights.behavior_balance}")
        summary.append(f"    Studentiality Balance: {self.weights.studentiality_balance}")
        summary.append(f"    Size Balance: {self.weights.size_balance}")
        summary.append(f"    Assistance Balance: {self.weights.assistance_balance}")
        summary.append(f"    School Origin Balance: {self.weights.school_origin_balance}")
        summary.append(f"  Layer Weights:")
        summary.append(f"    Student Layer: {self.weights.student_layer}")
        summary.append(f"    Class Layer: {self.weights.class_layer}")
        summary.append(f"    School Layer: {self.weights.school_layer}")
        
        # Normalization section
        summary.append(f"\n⚖️  Normalization Factors:")
        summary.append(f"  Academic Score Factor: {self.normalization.academic_score_factor}")
        summary.append(f"  Behavior Rank Factor: {self.normalization.behavior_rank_factor}")
        summary.append(f"  Studentiality Rank Factor: {self.normalization.studentiality_rank_factor}")
        summary.append(f"  Class Size Factor: {self.normalization.class_size_factor}")
        summary.append(f"  Assistance Count Factor: {self.normalization.assistance_count_factor}")
        summary.append(f"  School Origin Factor: {self.normalization.school_origin_factor}")
        
        # Validation section
        summary.append(f"\n✅ Validation Rules:")
        summary.append(f"  Student ID Length: {self.validation.student_id_length}")
        summary.append(f"  Max Name Length: {self.validation.max_name_length}")
        summary.append(f"  Academic Score Range: {self.validation.min_academic_score}-{self.validation.max_academic_score}")
        summary.append(f"  Valid Behavior Ranks: {', '.join(self.validation.valid_behavior_ranks)}")
        
        if self.config_file:
            summary.append(f"\n📁 Loaded from: {self.config_file}")
        else:
            summary.append(f"\n📁 Using default configuration")
            
        return "\n".join(summary) 