# Behavior Rank System Update

## Overview
Updated the behavior rank system from A-E (1-5) to A-D (1-4) with revised descriptions and expected distribution.

## Changes Made

### 1. Rank Range and Descriptions
**Before:**
- A = Excellent (1)
- B = Good (2)
- C = Medium (3)
- D = Below Average (4)
- E = Poor (5)

**After:**
- A = Excellent (1)
- B = Good (2)
- C = Almost Good (3)
- D = Not Good (4)

### 2. Expected Distribution
The new system reflects realistic school behavior distributions:
- **Most students**: A (Excellent) - the majority
- **Second most**: B (Good) - still substantial
- **Steep drop**: C (Almost Good) - significantly fewer
- **Rare**: D (Not Good) - exceptional cases only

This distribution recognizes that serious behavior issues should be rare in a typical school environment.

### 3. Normalization Factor Adjustment
- **Before**: `behavior_rank_factor: 25.0`
- **After**: `behavior_rank_factor: 35.0`

The increased factor makes the system more sensitive to behavior imbalances, reflecting that with the new expected distribution, any significant presence of C or D students should be flagged as a balance concern.

## Technical Implementation

### Files Updated
1. **Configuration Files:**
   - `config/default_scoring.yaml` - Updated valid ranks and normalization factor
   - `src/meshachvetz/utils/config.py` - Updated default values

2. **Data Models:**
   - `src/meshachvetz/data/models.py` - Updated validation and conversion functions
   - `src/meshachvetz/data/validator.py` - Updated validation constants

3. **Documentation:**
   - `docs/02_data_format_specification.md` - Updated behavior rank descriptions
   - `docs/03_scorer_design.md` - Updated scoring system documentation
   - `docs/06_technical_specifications.md` - Updated technical specs
   - `.cursorrules` - Updated project rules

4. **Test Data:**
   - `examples/test_data/bad_score_test.csv` - Replaced E ranks with D

### Validation Changes
- **Input Validation**: Now rejects E ranks and only accepts A-D
- **Numeric Conversion**: Maps A=1, B=2, C=3, D=4 (was A=1, B=2, C=3, D=4, E=5)
- **Error Messages**: Updated to reflect A-D range

## Impact on Scoring

### Behavior Balance Calculation
The formula remains the same: `100 - (std_dev * normalization_factor)`

However, with the new normalization factor (35.0 vs 25.0), the system is more sensitive to behavior imbalances:

**Example:**
- Classes with behavior rank averages of 2.0, 2.5, 3.0 (B, B+, C)
- Standard deviation: 0.41
- **Old score**: 100 - (0.41 × 25.0) = 89.75/100
- **New score**: 100 - (0.41 × 35.0) = 85.65/100

This reflects that having a class with mostly C students should be more concerning in the new system.

### Expected Impact
- **Better Discrimination**: The system now better distinguishes between acceptable (A/B) and concerning (C/D) behavior distributions
- **Realistic Modeling**: Aligns with actual school behavior patterns
- **Improved Optimization**: Future optimizers will better balance behavior ranks according to realistic expectations

## Testing Results
- ✅ Configuration loads correctly with new values
- ✅ Validation properly rejects E ranks
- ✅ Numeric conversion works correctly (A=1, B=2, C=3, D=4)
- ✅ Scoring system processes A-D ranks without errors
- ✅ Updated test data works correctly

## Backward Compatibility
⚠️ **Breaking Change**: CSV files containing E behavior ranks will now fail validation and must be updated to use A-D ranks only.

## Next Steps
1. Update any existing CSV files that contain E ranks
2. Inform users of the change through documentation
3. Consider creating a migration script for large datasets if needed 