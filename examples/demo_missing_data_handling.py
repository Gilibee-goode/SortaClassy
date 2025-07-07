#!/usr/bin/env python3
"""
Demonstration of Enhanced Missing Data Handling
===============================================

This script demonstrates the improved data loading capabilities that handle
missing values in ranged fields by using column averages (for numeric fields)
or mode (for categorical fields) instead of hardcoded defaults.

Key Improvements:
- Academic scores: Missing values filled with column average
- Behavior ranks: Missing values filled with most common rank (mode)
- Studentiality ranks: Missing values filled with most common rank (mode)
- Preserves data distribution instead of biasing with defaults
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz.data.loader import DataLoader
from meshachvetz.data.validator import DataValidator
import pandas as pd

def demonstrate_missing_data_handling():
    """Demonstrate the enhanced missing data handling capabilities."""
    
    print("🔧 Enhanced Missing Data Handling Demonstration")
    print("=" * 50)
    print()
    
    # Use the test file with missing values
    test_file = "test_data/missing_data_test.csv"
    
    print("📊 Analyzing raw data with missing values...")
    print("-" * 40)
    
    # Load raw CSV to show missing values
    df_raw = pd.read_csv(test_file, dtype=str, keep_default_na=False, na_values=[])
    
    # Count missing values
    missing_academic = sum(1 for val in df_raw['academic_score'] if val.strip() == '')
    missing_behavior = sum(1 for val in df_raw['behavior_rank'] if val.strip() == '')
    missing_studentiality = sum(1 for val in df_raw['studentiality_rank'] if val.strip() == '')
    
    print(f"📈 Dataset: {len(df_raw)} students")
    print(f"❌ Missing academic scores: {missing_academic}")
    print(f"❌ Missing behavior ranks: {missing_behavior}")
    print(f"❌ Missing studentiality ranks: {missing_studentiality}")
    print()
    
    # Calculate what the imputation values will be
    valid_scores = [float(val) for val in df_raw['academic_score'] if val.strip() != '']
    expected_avg = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
    
    valid_behavior = [val for val in df_raw['behavior_rank'] if val.strip() != '']
    behavior_counts = {rank: valid_behavior.count(rank) for rank in ['A', 'B', 'C', 'D']}
    behavior_mode = max(behavior_counts, key=behavior_counts.get)
    
    valid_studentiality = [val for val in df_raw['studentiality_rank'] if val.strip() != '']
    studentiality_counts = {rank: valid_studentiality.count(rank) for rank in ['A', 'B', 'C', 'D']}
    studentiality_mode = max(studentiality_counts, key=studentiality_counts.get)
    
    print("🧮 Calculated imputation values:")
    print(f"   Academic score average: {expected_avg:.2f}")
    print(f"   Behavior rank mode: {behavior_mode}")
    print(f"   Studentiality rank mode: {studentiality_mode}")
    print()
    
    print("🔄 Loading data with enhanced missing data handling...")
    print("-" * 40)
    
    # Create enhanced DataLoader
    loader = DataLoader(validate_data=True)
    
    # Load data - this will automatically apply missing value imputation
    school_data = loader.load_csv(test_file)
    
    # Get imputation statistics
    imputation_stats = loader.get_imputation_summary()
    
    print("✅ Imputation completed successfully!")
    print()
    print("📋 Imputation Summary:")
    for field, stats in imputation_stats.items():
        if stats['count'] > 0:
            print(f"   {field}: {stats['count']} values → {stats['average']}")
        else:
            print(f"   {field}: No missing values")
    print()
    
    # Analyze the results
    print("📊 Results Analysis:")
    print("-" * 40)
    
    all_scores = [s.academic_score for s in school_data.students.values()]
    all_behavior = [s.behavior_rank for s in school_data.students.values()]
    all_studentiality = [s.studentiality_rank for s in school_data.students.values()]
    
    print(f"✅ All students loaded: {school_data.total_students}")
    print(f"✅ Academic scores: {min(all_scores):.1f} - {max(all_scores):.1f}")
    print(f"✅ Behavior ranks: {sorted(set(all_behavior))}")
    print(f"✅ Studentiality ranks: {sorted(set(all_studentiality))}")
    print()
    
    # Verify no missing values remain
    missing_after = sum(1 for s in school_data.students.values() 
                      if s.academic_score is None or s.behavior_rank == '' or s.studentiality_rank == '')
    
    if missing_after == 0:
        print("🎉 SUCCESS: All missing values successfully imputed!")
    else:
        print(f"⚠️  WARNING: {missing_after} missing values remain")
    
    print()
    print("🔍 Key Benefits:")
    print("-" * 40)
    print("✅ Preserves data distribution (no bias from hardcoded defaults)")
    print("✅ Uses statistically appropriate imputation methods")
    print("✅ Maintains data integrity for optimization algorithms")
    print("✅ Provides transparency through imputation statistics")
    print("✅ Handles edge cases gracefully")
    print()
    
    # Show comparison with old approach
    print("📈 Comparison with Previous Approach:")
    print("-" * 40)
    print("Old approach (hardcoded defaults):")
    print(f"   Academic score: 0.0 (biases distribution downward)")
    print(f"   Behavior rank: A (biases distribution upward)")
    print(f"   Studentiality rank: A (biases distribution upward)")
    print()
    print("New approach (data-driven imputation):")
    print(f"   Academic score: {expected_avg:.2f} (maintains distribution)")
    print(f"   Behavior rank: {behavior_mode} (reflects actual pattern)")
    print(f"   Studentiality rank: {studentiality_mode} (reflects actual pattern)")
    print()
    
    print("✅ Enhanced missing data handling implementation complete!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    demonstrate_missing_data_handling() 