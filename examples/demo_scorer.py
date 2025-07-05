#!/usr/bin/env python3
"""
Meshachvetz Scorer Demonstration

This script demonstrates the capabilities of the three-layer scoring system
implemented in Week 2 of the Meshachvetz project.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from meshachvetz import Scorer, Config
import logging

# Configure logging to show the scoring process
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    """Demonstrate the Meshachvetz scoring system."""
    print("🎯 MESHACHVETZ SCORER DEMONSTRATION")
    print("=" * 50)
    
    # Check if sample data exists
    sample_file = "examples/sample_data/students_sample.csv"
    if not os.path.exists(sample_file):
        print(f"❌ Sample data file not found: {sample_file}")
        print("Please ensure the sample data is available.")
        return 1
    
    print(f"📁 Loading student data from: {sample_file}")
    
    # Create scorer with default configuration
    config = Config()
    scorer = Scorer(config)
    
    print("\n⚙️  Configuration Summary:")
    print(f"   Student Layer Weight: {config.weights.student_layer}")
    print(f"   Class Layer Weight: {config.weights.class_layer}")
    print(f"   School Layer Weight: {config.weights.school_layer}")
    print(f"   Friend Satisfaction Weight: {config.weights.friends}")
    print(f"   Conflict Avoidance Weight: {config.weights.dislikes}")
    
    # Score the assignment
    print("\n🧮 Calculating scores...")
    result = scorer.score_csv_file(sample_file)
    
    # Display results
    print(f"\n🏆 SCORING RESULTS")
    print(f"Final Score: {result.final_score:.2f}/100")
    print(f"Total Students: {result.total_students}")
    print(f"Total Classes: {result.total_classes}")
    
    print(f"\n📊 Layer Breakdown:")
    print(f"   Student Layer: {result.student_layer_score:.2f}/100 (weight: {result.layer_weights['student']})")
    print(f"   Class Layer:   {result.class_layer_score:.2f}/100 (weight: {result.layer_weights['class']})")
    print(f"   School Layer:  {result.school_layer_score:.2f}/100 (weight: {result.layer_weights['school']})")
    
    # Student satisfaction analysis
    satisfaction_summary = scorer.get_student_satisfaction_summary(result)
    print(f"\n👥 Student Satisfaction Analysis:")
    print(f"   Average Satisfaction: {satisfaction_summary['average_satisfaction']:.2f}/100")
    print(f"   Highly Satisfied (≥75): {satisfaction_summary['highly_satisfied_count']}/{satisfaction_summary['total_students']}")
    print(f"   Moderately Satisfied (50-74): {satisfaction_summary['moderately_satisfied_count']}/{satisfaction_summary['total_students']}")
    print(f"   Low Satisfaction (<50): {satisfaction_summary['low_satisfaction_count']}/{satisfaction_summary['total_students']}")
    print(f"   Students with Friends Placed: {satisfaction_summary['students_with_friends_placed']}/{satisfaction_summary['total_students']}")
    print(f"   Students with Conflicts: {satisfaction_summary['students_with_conflicts']}/{satisfaction_summary['total_students']}")
    
    # Class analysis
    print(f"\n🏫 Class Analysis:")
    for class_id, class_result in result.class_scores.items():
        gender_balance = class_result['gender_balance']
        print(f"   Class {class_id}: Score {class_result['score']:.1f}/100, "
              f"Students: {gender_balance['male_count']}M + {gender_balance['female_count']}F = {gender_balance['male_count'] + gender_balance['female_count']}, "
              f"Gender Balance: {gender_balance['score']:.1f}/100")
    
    # School balance analysis
    print(f"\n🏛️  School Balance Analysis:")
    school_scores = result.school_scores
    print(f"   Academic Balance: {school_scores['academic_balance']['score']:.1f}/100 (σ={school_scores['academic_balance']['std_dev']:.2f})")
    print(f"   Behavior Balance: {school_scores['behavior_balance']['score']:.1f}/100 (σ={school_scores['behavior_balance']['std_dev']:.2f})")
    print(f"   Size Balance: {school_scores['size_balance']['score']:.1f}/100 (σ={school_scores['size_balance']['std_dev']:.2f})")
    print(f"   Assistance Balance: {school_scores['assistance_balance']['score']:.1f}/100 (σ={school_scores['assistance_balance']['std_dev']:.2f})")
    
    # Detailed individual student results
    print(f"\n👤 Individual Student Results:")
    print("   StudentID    | Score  | Friends | Conflicts | Class")
    print("   -------------|--------|---------|-----------|------")
    
    for student_id, student_result in result.student_scores.items():
        friend_sat = student_result['friend_satisfaction']
        conflict_av = student_result['conflict_avoidance']
        student = scorer.data_loader.load_csv(sample_file).get_student_by_id(student_id)
        
        friends_status = f"{friend_sat['friends_placed']}/{friend_sat['friends_requested']}"
        conflicts_status = f"{len(conflict_av['conflicts_present'])}/{conflict_av['dislikes_total']}"
        
        print(f"   {student_id} | {student_result['score']:6.1f} | {friends_status:>7} | {conflicts_status:>9} | {student.class_id:>5}")
    
    # Show how configuration changes affect scores
    print(f"\n🔧 Configuration Impact Demo:")
    
    # Test with student-focused configuration
    student_focused_config = Config()
    student_focused_config.update_weights(student_layer=0.8, class_layer=0.1, school_layer=0.1)
    student_focused_scorer = Scorer(student_focused_config)
    student_focused_result = student_focused_scorer.score_csv_file(sample_file)
    
    print(f"   Student-Focused Config (80/10/10): {student_focused_result.final_score:.2f}/100")
    
    # Test with balance-focused configuration
    balance_focused_config = Config()
    balance_focused_config.update_weights(student_layer=0.2, class_layer=0.3, school_layer=0.5)
    balance_focused_scorer = Scorer(balance_focused_config)
    balance_focused_result = balance_focused_scorer.score_csv_file(sample_file)
    
    print(f"   Balance-Focused Config (20/30/50): {balance_focused_result.final_score:.2f}/100")
    print(f"   Default Config (50/20/30): {result.final_score:.2f}/100")
    
    # Generate detailed report
    print(f"\n📋 Generating detailed report...")
    detailed_report = scorer.get_detailed_report(result)
    
    # Save report to file
    report_file = "examples/scoring_report.txt"
    with open(report_file, 'w') as f:
        f.write(detailed_report)
    
    print(f"   Detailed report saved to: {report_file}")
    
    print(f"\n✅ Demonstration completed successfully!")
    print(f"🎯 The Meshachvetz three-layer scoring system is fully operational.")
    print(f"\n📝 Key Features Demonstrated:")
    print(f"   ✅ Student Layer: Friend satisfaction and conflict avoidance")
    print(f"   ✅ Class Layer: Gender balance scoring")
    print(f"   ✅ School Layer: Academic, behavior, size, and assistance balance")
    print(f"   ✅ Configurable weights and parameters")
    print(f"   ✅ Comprehensive reporting and analysis")
    print(f"   ✅ Individual student and class-level insights")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 