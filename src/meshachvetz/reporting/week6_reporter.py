#!/usr/bin/env python3
"""
Enhanced Reporting System for Week 6 - Provides comprehensive optimization reports,
algorithm comparisons, and performance analysis.
"""

import json
import yaml
import csv
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import statistics
from dataclasses import dataclass, asdict
import copy

from ..optimizer.base_optimizer import OptimizationResult
from ..data.models import SchoolData, Student, ClassData
from ..scorer.main_scorer import Scorer, ScoreResult


@dataclass
class AlgorithmMetrics:
    """Metrics for a single algorithm run."""
    algorithm_name: str
    execution_time: float
    initial_score: float
    final_score: float
    improvement: float
    improvement_percentage: float
    iterations_completed: int
    convergence_iterations: int
    success: bool
    error_message: Optional[str] = None
    constraint_violations: int = 0
    memory_usage_mb: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class ComparisonReport:
    """Comprehensive comparison report for multiple algorithms."""
    timestamp: str
    dataset_info: Dict[str, Any]
    algorithm_metrics: List[AlgorithmMetrics]
    best_algorithm: str
    worst_algorithm: str
    performance_ranking: List[str]
    summary_statistics: Dict[str, Any]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp,
            'dataset_info': self.dataset_info,
            'algorithm_metrics': [metric.to_dict() for metric in self.algorithm_metrics],
            'best_algorithm': self.best_algorithm,
            'worst_algorithm': self.worst_algorithm,
            'performance_ranking': self.performance_ranking,
            'summary_statistics': self.summary_statistics,
            'recommendations': self.recommendations
        }


class Week6Reporter:
    """
    Enhanced reporting system for Week 6 implementation.
    
    Provides comprehensive optimization reports, algorithm comparisons,
    and performance analysis with multiple output formats.
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the reporter.
        
        Args:
            output_dir: Directory for report output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.scorer = Scorer()
        
        # Report configuration
        self.report_config = {
            'include_detailed_metrics': True,
            'include_student_level_analysis': True,
            'include_class_level_analysis': True,
            'include_convergence_analysis': True,
            'include_performance_recommendations': True,
            'generate_visualizations': False,  # Would require additional dependencies
            'export_formats': ['json', 'yaml', 'csv', 'txt']
        }
    
    def generate_single_algorithm_report(self, 
                                       result: OptimizationResult, 
                                       initial_data: SchoolData,
                                       save_to_file: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive report for a single algorithm run.
        
        Args:
            result: Optimization result
            initial_data: Initial school data
            save_to_file: Whether to save report to file
            
        Returns:
            Complete report as dictionary
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Calculate detailed metrics
        metrics = self._calculate_detailed_metrics(result, initial_data)
        
        # Generate report structure
        report = {
            'metadata': {
                'timestamp': timestamp,
                'report_type': 'single_algorithm',
                'algorithm': result.algorithm_name,
                'meshachvetz_version': '1.0.0'
            },
            'dataset_info': self._analyze_dataset(initial_data),
            'execution_summary': {
                'algorithm_name': result.algorithm_name,
                'execution_time': result.execution_time,
                'iterations_completed': result.iterations_completed,
                'convergence_achieved': result.convergence_iterations > 0,
                'success': result.improvement >= 0
            },
            'score_analysis': {
                'initial_score': result.initial_score,
                'final_score': result.final_score,
                'improvement': result.improvement,
                'improvement_percentage': (result.improvement / result.initial_score * 100) if result.initial_score > 0 else 0,
                'score_breakdown': self._get_score_breakdown(result.optimized_school_data)
            },
            'detailed_metrics': metrics,
            'constraint_analysis': self._analyze_constraints(result.optimized_school_data),
            'student_satisfaction': self._analyze_student_satisfaction(result.optimized_school_data),
            'class_balance': self._analyze_class_balance(result.optimized_school_data),
            'recommendations': self._generate_recommendations(result, initial_data)
        }
        
        if save_to_file:
            self._save_report(report, f"single_algorithm_report_{timestamp}")
        
        return report
    
    def generate_algorithm_comparison_report(self, 
                                           results: Dict[str, OptimizationResult],
                                           initial_data: SchoolData,
                                           save_to_file: bool = True) -> ComparisonReport:
        """
        Generate comprehensive comparison report for multiple algorithms.
        
        Args:
            results: Dictionary of algorithm results
            initial_data: Initial school data
            save_to_file: Whether to save report to file
            
        Returns:
            Comparison report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Calculate metrics for each algorithm
        algorithm_metrics = []
        for algorithm_name, result in results.items():
            metrics = AlgorithmMetrics(
                algorithm_name=algorithm_name,
                execution_time=result.execution_time,
                initial_score=result.initial_score,
                final_score=result.final_score,
                improvement=result.improvement,
                improvement_percentage=(result.improvement / result.initial_score * 100) if result.initial_score > 0 else 0,
                iterations_completed=result.iterations_completed,
                convergence_iterations=result.convergence_iterations,
                success=result.improvement >= 0,
                constraint_violations=len(self._analyze_constraints(result.optimized_school_data).get('violations', []))
            )
            algorithm_metrics.append(metrics)
        
        # Determine best and worst algorithms
        successful_metrics = [m for m in algorithm_metrics if m.success]
        if successful_metrics:
            best_algorithm = max(successful_metrics, key=lambda m: m.final_score).algorithm_name
            worst_algorithm = min(successful_metrics, key=lambda m: m.final_score).algorithm_name
        else:
            best_algorithm = algorithm_metrics[0].algorithm_name if algorithm_metrics else "None"
            worst_algorithm = best_algorithm
        
        # Create performance ranking
        performance_ranking = sorted(
            [m.algorithm_name for m in successful_metrics],
            key=lambda alg: next(m.final_score for m in successful_metrics if m.algorithm_name == alg),
            reverse=True
        )
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_statistics(algorithm_metrics)
        
        # Generate recommendations
        recommendations = self._generate_comparison_recommendations(algorithm_metrics, initial_data)
        
        # Create comparison report
        comparison_report = ComparisonReport(
            timestamp=timestamp,
            dataset_info=self._analyze_dataset(initial_data),
            algorithm_metrics=algorithm_metrics,
            best_algorithm=best_algorithm,
            worst_algorithm=worst_algorithm,
            performance_ranking=performance_ranking,
            summary_statistics=summary_stats,
            recommendations=recommendations
        )
        
        if save_to_file:
            self._save_comparison_report(comparison_report, f"algorithm_comparison_{timestamp}")
        
        return comparison_report
    
    def generate_performance_benchmark_report(self, 
                                            benchmark_results: Dict[str, Dict[str, Any]],
                                            save_to_file: bool = True) -> Dict[str, Any]:
        """
        Generate performance benchmark report.
        
        Args:
            benchmark_results: Benchmark results from performance tests
            save_to_file: Whether to save report to file
            
        Returns:
            Benchmark report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        report = {
            'metadata': {
                'timestamp': timestamp,
                'report_type': 'performance_benchmark',
                'meshachvetz_version': '1.0.0'
            },
            'benchmark_summary': {
                'total_algorithms_tested': len(benchmark_results),
                'successful_algorithms': sum(1 for r in benchmark_results.values() if r.get('success_rate', 0) > 0),
                'total_runs': sum(len(r.get('runs', [])) for r in benchmark_results.values()),
                'average_execution_time': statistics.mean([r.get('avg_time', 0) for r in benchmark_results.values() if r.get('success_rate', 0) > 0])
            },
            'algorithm_performance': benchmark_results,
            'performance_analysis': self._analyze_performance_results(benchmark_results),
            'scalability_analysis': self._analyze_scalability(benchmark_results),
            'recommendations': self._generate_performance_recommendations(benchmark_results)
        }
        
        if save_to_file:
            self._save_report(report, f"performance_benchmark_{timestamp}")
        
        return report
    
    def generate_configuration_analysis_report(self, 
                                             config_validation_results: Dict[str, Any],
                                             save_to_file: bool = True) -> Dict[str, Any]:
        """
        Generate configuration analysis report.
        
        Args:
            config_validation_results: Configuration validation results
            save_to_file: Whether to save report to file
            
        Returns:
            Configuration analysis report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        report = {
            'metadata': {
                'timestamp': timestamp,
                'report_type': 'configuration_analysis',
                'meshachvetz_version': '1.0.0'
            },
            'validation_summary': {
                'total_configurations': len(config_validation_results),
                'valid_configurations': sum(1 for r in config_validation_results.values() if len(r.get('errors', [])) == 0),
                'invalid_configurations': sum(1 for r in config_validation_results.values() if len(r.get('errors', [])) > 0),
                'common_errors': self._identify_common_errors(config_validation_results)
            },
            'detailed_results': config_validation_results,
            'best_practices': self._generate_configuration_best_practices(),
            'recommendations': self._generate_configuration_recommendations(config_validation_results)
        }
        
        if save_to_file:
            self._save_report(report, f"configuration_analysis_{timestamp}")
        
        return report
    
    def _calculate_detailed_metrics(self, result: OptimizationResult, initial_data: SchoolData) -> Dict[str, Any]:
        """Calculate detailed metrics for optimization result."""
        metrics = {}
        
        # Performance metrics
        metrics['performance'] = {
            'execution_time_seconds': result.execution_time,
            'iterations_per_second': result.iterations_completed / result.execution_time if result.execution_time > 0 else 0,
            'score_improvement_rate': result.improvement / result.execution_time if result.execution_time > 0 else 0
        }
        
        # Convergence metrics
        metrics['convergence'] = {
            'convergence_achieved': result.convergence_iterations > 0,
            'convergence_iteration': result.convergence_iterations,
            'convergence_rate': result.convergence_iterations / result.iterations_completed if result.iterations_completed > 0 else 0
        }
        
        # Quality metrics
        metrics['quality'] = {
            'relative_improvement': result.improvement / result.initial_score if result.initial_score > 0 else 0,
            'score_efficiency': result.final_score / result.execution_time if result.execution_time > 0 else 0,
            'constraint_satisfaction_rate': self._calculate_constraint_satisfaction_rate(result.optimized_school_data)
        }
        
        return metrics
    
    def _analyze_dataset(self, school_data: SchoolData) -> Dict[str, Any]:
        """Analyze dataset characteristics."""
        analysis = {
            'total_students': len(school_data.students),
            'total_classes': len(school_data.classes),
            'average_class_size': len(school_data.students) / len(school_data.classes) if len(school_data.classes) > 0 else 0,
            'gender_distribution': self._analyze_gender_distribution(school_data),
            'academic_score_distribution': self._analyze_academic_distribution(school_data),
            'behavior_rank_distribution': self._analyze_behavior_distribution(school_data),
            'social_preferences': self._analyze_social_preferences(school_data),
            'force_constraints': self._analyze_force_constraints(school_data)
        }
        
        return analysis
    
    def _get_score_breakdown(self, school_data: SchoolData) -> Dict[str, Any]:
        """Get detailed score breakdown."""
        score_result = self.scorer.calculate_scores(school_data)
        
        return {
            'final_score': score_result.final_score,
            'student_layer_score': score_result.student_layer_score,
            'class_layer_score': score_result.class_layer_score,
            'school_layer_score': score_result.school_layer_score,
            'detailed_breakdown': score_result.detailed_breakdown
        }
    
    def _analyze_constraints(self, school_data: SchoolData) -> Dict[str, Any]:
        """Analyze constraint satisfaction."""
        violations = []
        
        # Check force constraints
        for student in school_data.students.values():
            if student.force_class and student.class_id != student.force_class:
                violations.append({
                    'type': 'force_class',
                    'student_id': student.student_id,
                    'expected': student.force_class,
                    'actual': student.class_id
                })
        
        # Check force friend constraints
        force_groups = school_data.get_force_friend_groups()
        for group_id, student_ids in force_groups.items():
            if len(student_ids) > 1:
                classes = set()
                for student_id in student_ids:
                    if student_id in school_data.students:
                        classes.add(school_data.students[student_id].class_id)
                
                if len(classes) > 1:
                    violations.append({
                        'type': 'force_friend',
                        'group_id': group_id,
                        'students': student_ids,
                        'classes': list(classes)
                    })
        
        return {
            'total_violations': len(violations),
            'violations': violations,
            'constraint_satisfaction_rate': 1.0 - (len(violations) / len(school_data.students)) if len(school_data.students) > 0 else 1.0
        }
    
    def _analyze_student_satisfaction(self, school_data: SchoolData) -> Dict[str, Any]:
        """Analyze student satisfaction metrics."""
        total_students = len(school_data.students)
        satisfied_students = 0
        friend_satisfaction = 0
        conflict_avoidance = 0
        
        for student in school_data.students.values():
            student_class = school_data.classes.get(student.class_id)
            if not student_class:
                continue
            
            classmates = [s.student_id for s in student_class.students if s.student_id != student.student_id]
            
            # Count satisfied friend preferences
            preferred_friends = student.get_preferred_friends()
            friends_in_class = sum(1 for friend_id in preferred_friends if friend_id in classmates)
            
            # Count avoided conflicts
            disliked_peers = student.get_disliked_peers()
            conflicts_in_class = sum(1 for peer_id in disliked_peers if peer_id in classmates)
            
            if friends_in_class > 0:
                friend_satisfaction += friends_in_class / len(preferred_friends) if preferred_friends else 0
            
            if len(disliked_peers) > 0:
                conflict_avoidance += 1 - (conflicts_in_class / len(disliked_peers))
            else:
                conflict_avoidance += 1
            
            # Overall satisfaction
            if friends_in_class > 0 and conflicts_in_class == 0:
                satisfied_students += 1
        
        return {
            'total_students': total_students,
            'satisfied_students': satisfied_students,
            'satisfaction_rate': satisfied_students / total_students if total_students > 0 else 0,
            'average_friend_satisfaction': friend_satisfaction / total_students if total_students > 0 else 0,
            'average_conflict_avoidance': conflict_avoidance / total_students if total_students > 0 else 0
        }
    
    def _analyze_class_balance(self, school_data: SchoolData) -> Dict[str, Any]:
        """Analyze class balance metrics."""
        class_sizes = [len(class_data.students) for class_data in school_data.classes.values()]
        
        if not class_sizes:
            return {'error': 'No classes found'}
        
        balance_analysis = {
            'total_classes': len(school_data.classes),
            'class_sizes': class_sizes,
            'min_class_size': min(class_sizes),
            'max_class_size': max(class_sizes),
            'average_class_size': statistics.mean(class_sizes),
            'class_size_std_dev': statistics.stdev(class_sizes) if len(class_sizes) > 1 else 0,
            'size_balance_coefficient': (max(class_sizes) - min(class_sizes)) / statistics.mean(class_sizes) if statistics.mean(class_sizes) > 0 else 0
        }
        
        # Gender balance analysis
        gender_balance = {}
        for class_id, class_data in school_data.classes.items():
            male_count = sum(1 for student in class_data.students if student.gender == 'M')
            female_count = sum(1 for student in class_data.students if student.gender == 'F')
            gender_balance[class_id] = {
                'male': male_count,
                'female': female_count,
                'balance_ratio': abs(male_count - female_count) / len(class_data.students) if len(class_data.students) > 0 else 0
            }
        
        balance_analysis['gender_balance'] = gender_balance
        
        return balance_analysis
    
    def _generate_recommendations(self, result: OptimizationResult, initial_data: SchoolData) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Performance recommendations
        if result.execution_time > 60:
            recommendations.append("Consider using faster algorithms like Local Search for large datasets")
        
        if result.improvement < 1.0:
            recommendations.append("Low improvement suggests trying different algorithm parameters or multiple algorithms")
        
        # Dataset recommendations
        student_count = len(initial_data.students)
        if student_count < 200:
            recommendations.append("For datasets under 200 students, consider using OR-Tools for optimal solutions")
        elif student_count > 500:
            recommendations.append("For large datasets, use fast heuristic algorithms like Genetic or Local Search")
        
        # Constraint recommendations
        constraint_analysis = self._analyze_constraints(result.optimized_school_data)
        if constraint_analysis['total_violations'] > 0:
            recommendations.append("Consider adjusting constraint weights or using constraint-aware algorithms")
        
        return recommendations
    
    def _calculate_summary_statistics(self, algorithm_metrics: List[AlgorithmMetrics]) -> Dict[str, Any]:
        """Calculate summary statistics for algorithm comparison."""
        successful_metrics = [m for m in algorithm_metrics if m.success]
        
        if not successful_metrics:
            return {'error': 'No successful algorithm runs'}
        
        execution_times = [m.execution_time for m in successful_metrics]
        final_scores = [m.final_score for m in successful_metrics]
        improvements = [m.improvement for m in successful_metrics]
        
        return {
            'total_algorithms': len(algorithm_metrics),
            'successful_algorithms': len(successful_metrics),
            'success_rate': len(successful_metrics) / len(algorithm_metrics),
            'execution_time_stats': {
                'mean': statistics.mean(execution_times),
                'median': statistics.median(execution_times),
                'min': min(execution_times),
                'max': max(execution_times),
                'std_dev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            },
            'score_stats': {
                'mean': statistics.mean(final_scores),
                'median': statistics.median(final_scores),
                'min': min(final_scores),
                'max': max(final_scores),
                'std_dev': statistics.stdev(final_scores) if len(final_scores) > 1 else 0
            },
            'improvement_stats': {
                'mean': statistics.mean(improvements),
                'median': statistics.median(improvements),
                'min': min(improvements),
                'max': max(improvements),
                'std_dev': statistics.stdev(improvements) if len(improvements) > 1 else 0
            }
        }
    
    def _generate_comparison_recommendations(self, algorithm_metrics: List[AlgorithmMetrics], initial_data: SchoolData) -> List[str]:
        """Generate recommendations based on algorithm comparison."""
        recommendations = []
        
        successful_metrics = [m for m in algorithm_metrics if m.success]
        if not successful_metrics:
            return ["No algorithms completed successfully. Check dataset and configuration."]
        
        # Best algorithm recommendation
        best_algorithm = max(successful_metrics, key=lambda m: m.final_score)
        recommendations.append(f"Best performing algorithm: {best_algorithm.algorithm_name} (Score: {best_algorithm.final_score:.2f})")
        
        # Speed recommendation
        fastest_algorithm = min(successful_metrics, key=lambda m: m.execution_time)
        recommendations.append(f"Fastest algorithm: {fastest_algorithm.algorithm_name} ({fastest_algorithm.execution_time:.2f}s)")
        
        # Balanced recommendation
        # Score algorithms by score/time ratio
        if len(successful_metrics) > 1:
            efficiency_scores = [(m.final_score / m.execution_time, m.algorithm_name) for m in successful_metrics]
            most_efficient = max(efficiency_scores, key=lambda x: x[0])
            recommendations.append(f"Most efficient algorithm: {most_efficient[1]} (Score/Time: {most_efficient[0]:.2f})")
        
        # Dataset-specific recommendations
        student_count = len(initial_data.students)
        if student_count < 100:
            recommendations.append("For small datasets, prioritize solution quality over speed")
        elif student_count > 300:
            recommendations.append("For large datasets, prioritize speed and use quality algorithms selectively")
        
        return recommendations
    
    def _analyze_performance_results(self, benchmark_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance benchmark results."""
        analysis = {
            'speed_ranking': [],
            'quality_ranking': [],
            'reliability_ranking': [],
            'overall_ranking': []
        }
        
        successful_results = {k: v for k, v in benchmark_results.items() if v.get('success_rate', 0) > 0}
        
        if successful_results:
            # Speed ranking (lower time is better)
            speed_ranking = sorted(successful_results.items(), key=lambda x: x[1].get('avg_time', float('inf')))
            analysis['speed_ranking'] = [(alg, data['avg_time']) for alg, data in speed_ranking]
            
            # Quality ranking (higher score is better)
            quality_ranking = sorted(successful_results.items(), key=lambda x: x[1].get('avg_score', 0), reverse=True)
            analysis['quality_ranking'] = [(alg, data['avg_score']) for alg, data in quality_ranking]
            
            # Reliability ranking (higher success rate is better)
            reliability_ranking = sorted(successful_results.items(), key=lambda x: x[1].get('success_rate', 0), reverse=True)
            analysis['reliability_ranking'] = [(alg, data['success_rate']) for alg, data in reliability_ranking]
        
        return analysis
    
    def _analyze_scalability(self, benchmark_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze scalability characteristics."""
        # This would be more complex with actual multi-size benchmark data
        return {
            'scalability_notes': "Scalability analysis requires benchmark data across multiple dataset sizes",
            'recommendations': [
                "Use Local Search for datasets > 500 students",
                "Use OR-Tools for datasets < 200 students",
                "Use Genetic Algorithm for balanced approach"
            ]
        }
    
    def _generate_performance_recommendations(self, benchmark_results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate performance-based recommendations."""
        recommendations = []
        
        successful_results = {k: v for k, v in benchmark_results.items() if v.get('success_rate', 0) > 0}
        
        if successful_results:
            # Find best performers
            fastest = min(successful_results.items(), key=lambda x: x[1].get('avg_time', float('inf')))
            highest_quality = max(successful_results.items(), key=lambda x: x[1].get('avg_score', 0))
            
            recommendations.append(f"Use {fastest[0]} for speed-critical applications ({fastest[1]['avg_time']:.2f}s avg)")
            recommendations.append(f"Use {highest_quality[0]} for quality-critical applications (Score: {highest_quality[1]['avg_score']:.2f})")
            
            # Time-based recommendations
            quick_algorithms = [alg for alg, data in successful_results.items() if data.get('avg_time', 0) < 30]
            if quick_algorithms:
                recommendations.append(f"For quick optimization (<30s): {', '.join(quick_algorithms)}")
        
        return recommendations
    
    def _save_report(self, report: Dict[str, Any], filename: str) -> None:
        """Save report in multiple formats."""
        base_path = self.output_dir / filename
        
        # JSON format
        if 'json' in self.report_config['export_formats']:
            json_file = base_path.with_suffix('.json')
            with open(json_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Report saved to {json_file}")
        
        # YAML format
        if 'yaml' in self.report_config['export_formats']:
            yaml_file = base_path.with_suffix('.yaml')
            with open(yaml_file, 'w') as f:
                yaml.dump(report, f, default_flow_style=False, indent=2)
            self.logger.info(f"Report saved to {yaml_file}")
        
        # Text format
        if 'txt' in self.report_config['export_formats']:
            txt_file = base_path.with_suffix('.txt')
            with open(txt_file, 'w') as f:
                self._write_text_report(report, f)
            self.logger.info(f"Report saved to {txt_file}")
    
    def _save_comparison_report(self, report: ComparisonReport, filename: str) -> None:
        """Save comparison report in multiple formats."""
        report_dict = report.to_dict()
        self._save_report(report_dict, filename)
    
    def _write_text_report(self, report: Dict[str, Any], file_handle) -> None:
        """Write human-readable text report."""
        file_handle.write("=" * 80 + "\n")
        file_handle.write("MESHACHVETZ OPTIMIZATION REPORT\n")
        file_handle.write("=" * 80 + "\n\n")
        
        # Metadata
        if 'metadata' in report:
            file_handle.write(f"Generated: {report['metadata'].get('timestamp', 'Unknown')}\n")
            file_handle.write(f"Report Type: {report['metadata'].get('report_type', 'Unknown')}\n")
            file_handle.write(f"Version: {report['metadata'].get('meshachvetz_version', 'Unknown')}\n\n")
        
        # Summary
        if 'execution_summary' in report:
            file_handle.write("EXECUTION SUMMARY\n")
            file_handle.write("-" * 40 + "\n")
            summary = report['execution_summary']
            file_handle.write(f"Algorithm: {summary.get('algorithm_name', 'Unknown')}\n")
            file_handle.write(f"Execution Time: {summary.get('execution_time', 0):.2f} seconds\n")
            file_handle.write(f"Iterations: {summary.get('iterations_completed', 0)}\n")
            file_handle.write(f"Success: {summary.get('success', False)}\n\n")
        
        # Score Analysis
        if 'score_analysis' in report:
            file_handle.write("SCORE ANALYSIS\n")
            file_handle.write("-" * 40 + "\n")
            scores = report['score_analysis']
            file_handle.write(f"Initial Score: {scores.get('initial_score', 0):.2f}\n")
            file_handle.write(f"Final Score: {scores.get('final_score', 0):.2f}\n")
            file_handle.write(f"Improvement: {scores.get('improvement', 0):.2f}\n")
            file_handle.write(f"Improvement %: {scores.get('improvement_percentage', 0):.2f}%\n\n")
        
        # Recommendations
        if 'recommendations' in report:
            file_handle.write("RECOMMENDATIONS\n")
            file_handle.write("-" * 40 + "\n")
            for i, rec in enumerate(report['recommendations'], 1):
                file_handle.write(f"{i}. {rec}\n")
            file_handle.write("\n")
    
    # Additional analysis methods...
    def _analyze_gender_distribution(self, school_data: SchoolData) -> Dict[str, int]:
        """Analyze gender distribution."""
        gender_counts = {'M': 0, 'F': 0, 'Other': 0}
        for student in school_data.students.values():
            gender = student.gender
            if gender in gender_counts:
                gender_counts[gender] += 1
            else:
                gender_counts['Other'] += 1
        return gender_counts
    
    def _analyze_academic_distribution(self, school_data: SchoolData) -> Dict[str, Any]:
        """Analyze academic score distribution."""
        scores = [student.academic_score for student in school_data.students.values()]
        if not scores:
            return {'error': 'No scores found'}
        
        return {
            'mean': statistics.mean(scores),
            'median': statistics.median(scores),
            'min': min(scores),
            'max': max(scores),
            'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0
        }
    
    def _analyze_behavior_distribution(self, school_data: SchoolData) -> Dict[str, int]:
        """Analyze behavior rank distribution."""
        behavior_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        for student in school_data.students.values():
            rank = student.behavior_rank
            if rank in behavior_counts:
                behavior_counts[rank] += 1
        return behavior_counts
    
    def _analyze_social_preferences(self, school_data: SchoolData) -> Dict[str, Any]:
        """Analyze social preferences."""
        total_students = len(school_data.students)
        students_with_preferences = 0
        students_with_dislikes = 0
        
        for student in school_data.students.values():
            if student.get_preferred_friends():
                students_with_preferences += 1
            if student.get_disliked_peers():
                students_with_dislikes += 1
        
        return {
            'students_with_preferences': students_with_preferences,
            'students_with_dislikes': students_with_dislikes,
            'preference_rate': students_with_preferences / total_students if total_students > 0 else 0,
            'dislike_rate': students_with_dislikes / total_students if total_students > 0 else 0
        }
    
    def _analyze_force_constraints(self, school_data: SchoolData) -> Dict[str, Any]:
        """Analyze force constraints."""
        force_class_count = sum(1 for student in school_data.students.values() if student.force_class)
        force_friend_groups = school_data.get_force_friend_groups()
        
        return {
            'force_class_students': force_class_count,
            'force_friend_groups': len(force_friend_groups),
            'force_friend_students': sum(len(group) for group in force_friend_groups.values())
        }
    
    def _calculate_constraint_satisfaction_rate(self, school_data: SchoolData) -> float:
        """Calculate constraint satisfaction rate."""
        constraint_analysis = self._analyze_constraints(school_data)
        return constraint_analysis['constraint_satisfaction_rate']
    
    def _identify_common_errors(self, validation_results: Dict[str, Any]) -> List[str]:
        """Identify common validation errors."""
        error_counts = {}
        
        for result in validation_results.values():
            errors = result.get('errors', [])
            for error in errors:
                error_type = error.split(':')[0] if ':' in error else error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # Return top 5 most common errors
        return sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _generate_configuration_best_practices(self) -> List[str]:
        """Generate configuration best practices."""
        return [
            "Use OR-Tools for small datasets (<200 students) when solution quality is critical",
            "Use Genetic Algorithm for balanced approach on medium datasets",
            "Use Local Search for large datasets when speed is important",
            "Set reasonable time limits: 30s for small, 60s for medium, 120s for large datasets",
            "Start with default parameters and adjust based on performance results",
            "Use constraint-aware initialization for datasets with many force constraints",
            "Monitor memory usage for large datasets with genetic algorithms",
            "Use early stopping to prevent unnecessary computation"
        ]
    
    def _generate_configuration_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate configuration recommendations."""
        recommendations = []
        
        valid_configs = sum(1 for r in validation_results.values() if len(r.get('errors', [])) == 0)
        total_configs = len(validation_results)
        
        if valid_configs == 0:
            recommendations.append("All configurations failed validation. Check parameter ranges and types.")
        elif valid_configs < total_configs * 0.5:
            recommendations.append("More than half of configurations failed validation. Review parameter constraints.")
        else:
            recommendations.append("Most configurations passed validation. System is properly configured.")
        
        # Add specific recommendations based on common errors
        common_errors = self._identify_common_errors(validation_results)
        for error_type, count in common_errors[:3]:
            recommendations.append(f"Common error '{error_type}' found in {count} configurations - review parameter values")
        
        return recommendations


# Global reporter instance
week6_reporter = Week6Reporter() 