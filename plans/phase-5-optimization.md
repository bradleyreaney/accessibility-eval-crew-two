# Phase 5: Advanced Features & Optimization
*Week 5 Implementation Plan*

**← [Phase 4: Interface](./phase-4-interface.md)** | **[Back to Master Plan](./master-plan.md)**

## Overview

Phase 5 focuses on advanced features, performance optimization, and production readiness. This final phase transforms the system from a functional prototype into a robust, scalable solution ready for enterprise deployment with advanced consensus mechanisms, batch processing, and comprehensive monitoring.

## Prerequisites

- [x] **Phase 4 Complete**: Full Streamlit interface functional
- [x] **End-to-End Testing**: Complete system working with real data
- [x] **User Interface**: All core features accessible and working
- [x] **Export System**: Reports and data export functioning

## Objectives

- [x] **Advanced Consensus**: Sophisticated judge disagreement resolution
- [x] **Batch Processing**: Multiple audit reports and plan sets
- [x] **Performance Optimization**: Speed and reliability improvements
- [x] **Enterprise Features**: API endpoints, authentication, monitoring
- [x] **Production Deployment**: Docker, cloud deployment, scaling
- [x] **Production Documentation**: Deployment guides, monitoring setup, and performance benchmarks

## Deliverables

### 5.1 Advanced Consensus Mechanisms

#### Enhanced Consensus Engine (`src/consensus/advanced_consensus.py`)
```python
"""
Advanced consensus building system for judge disagreements
References: Master Plan - Multi-Judge Consensus, Phase 3 - Quality Assurance
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from ..models.evaluation_models import PlanEvaluation, JudgmentScore

class ConflictSeverity(Enum):
    LOW = "low"           # <0.5 score difference
    MEDIUM = "medium"     # 0.5-1.0 score difference  
    HIGH = "high"         # 1.0-2.0 score difference
    CRITICAL = "critical" # >2.0 score difference

@dataclass
class ConflictAnalysis:
    plan_name: str
    criterion: str
    primary_score: float
    secondary_score: float
    difference: float
    severity: ConflictSeverity
    primary_rationale: str
    secondary_rationale: str
    confidence_delta: float

class AdvancedConsensusEngine:
    """
    Sophisticated consensus building with multiple resolution strategies
    """
    
    def __init__(self):
        self.resolution_strategies = {
            ConflictSeverity.LOW: self._weighted_average_resolution,
            ConflictSeverity.MEDIUM: self._evidence_based_resolution,
            ConflictSeverity.HIGH: self._expert_mediation_resolution,
            ConflictSeverity.CRITICAL: self._human_escalation_resolution
        }
        
        self.judge_reliability_scores = {
            'gemini': {'accuracy': 0.85, 'consistency': 0.80, 'bias_factor': 0.05},
            'gpt4': {'accuracy': 0.88, 'consistency': 0.82, 'bias_factor': 0.03}
        }
    
    def analyze_conflicts(self, evaluations: List[PlanEvaluation]) -> List[ConflictAnalysis]:
        """
        Identify and analyze all conflicts between judge evaluations
        
        Args:
            evaluations: All evaluation results from both judges
            
        Returns:
            List of detailed conflict analyses
        """
        conflicts = []
        
        # Group evaluations by plan
        plan_groups = self._group_evaluations_by_plan(evaluations)
        
        for plan_name, plan_evals in plan_groups.items():
            if len(plan_evals) >= 2:  # Have both judge evaluations
                primary_eval = next((e for e in plan_evals if e.judge_id == 'gemini'), None)
                secondary_eval = next((e for e in plan_evals if e.judge_id == 'gpt4'), None)
                
                if primary_eval and secondary_eval:
                    plan_conflicts = self._analyze_plan_conflicts(primary_eval, secondary_eval)
                    conflicts.extend(plan_conflicts)
        
        return conflicts
    
    def resolve_conflicts(self, conflicts: List[ConflictAnalysis]) -> Dict[str, Dict[str, float]]:
        """
        Resolve conflicts using appropriate strategies based on severity
        
        Args:
            conflicts: List of identified conflicts
            
        Returns:
            Dictionary of resolved scores by plan and criterion
        """
        resolved_scores = {}
        
        for conflict in conflicts:
            # Select resolution strategy based on severity
            resolution_func = self.resolution_strategies[conflict.severity]
            resolved_score = resolution_func(conflict)
            
            # Store resolved score
            if conflict.plan_name not in resolved_scores:
                resolved_scores[conflict.plan_name] = {}
            
            resolved_scores[conflict.plan_name][conflict.criterion] = resolved_score
        
        return resolved_scores
    
    def _weighted_average_resolution(self, conflict: ConflictAnalysis) -> float:
        """
        Resolve low-severity conflicts with weighted averaging
        Weights based on judge reliability scores
        """
        primary_weight = self.judge_reliability_scores['gemini']['accuracy']
        secondary_weight = self.judge_reliability_scores['gpt4']['accuracy']
        
        total_weight = primary_weight + secondary_weight
        
        resolved_score = (
            (conflict.primary_score * primary_weight) + 
            (conflict.secondary_score * secondary_weight)
        ) / total_weight
        
        return round(resolved_score, 2)
    
    def _evidence_based_resolution(self, conflict: ConflictAnalysis) -> float:
        """
        Resolve medium-severity conflicts by analyzing evidence quality
        """
        # Analyze rationale quality and evidence strength
        primary_evidence_score = self._score_evidence_quality(conflict.primary_rationale)
        secondary_evidence_score = self._score_evidence_quality(conflict.secondary_rationale)
        
        # Weight scores based on evidence quality
        if primary_evidence_score > secondary_evidence_score * 1.2:
            # Primary has significantly stronger evidence
            return conflict.primary_score
        elif secondary_evidence_score > primary_evidence_score * 1.2:
            # Secondary has significantly stronger evidence
            return conflict.secondary_score
        else:
            # Evidence quality similar, use confidence-weighted average
            primary_confidence = 1.0 - conflict.confidence_delta if conflict.confidence_delta < 0 else 1.0
            secondary_confidence = 1.0 + conflict.confidence_delta if conflict.confidence_delta > 0 else 1.0
            
            total_confidence = primary_confidence + secondary_confidence
            
            resolved_score = (
                (conflict.primary_score * primary_confidence) +
                (conflict.secondary_score * secondary_confidence)
            ) / total_confidence
            
            return round(resolved_score, 2)
    
    def _expert_mediation_resolution(self, conflict: ConflictAnalysis) -> float:
        """
        Resolve high-severity conflicts with expert mediation logic
        Uses sophisticated heuristics to determine most likely correct score
        """
        # Multi-factor analysis for resolution
        factors = {
            'judge_reliability': self._calculate_judge_reliability_factor(conflict),
            'consistency_check': self._perform_consistency_check(conflict),
            'external_validation': self._validate_against_benchmarks(conflict),
            'bias_detection': self._detect_systematic_bias(conflict)
        }
        
        # Weighted decision based on multiple factors
        if factors['judge_reliability'] > 0.7:
            # High confidence in one judge's reliability for this type of evaluation
            if factors['judge_reliability'] > 0:
                return conflict.primary_score
            else:
                return conflict.secondary_score
        
        # No clear reliability winner, use comprehensive analysis
        composite_score = self._calculate_composite_resolution(conflict, factors)
        return round(composite_score, 2)
    
    def _human_escalation_resolution(self, conflict: ConflictAnalysis) -> Optional[float]:
        """
        Mark critical conflicts for human expert review
        These require domain expert intervention
        """
        # Log for human review
        escalation_data = {
            'conflict': conflict,
            'automated_resolution': 'ESCALATED_TO_HUMAN',
            'urgency': 'HIGH',
            'required_expertise': 'ACCESSIBILITY_EXPERT',
            'review_deadline': '24_HOURS'
        }
        
        # In production, this would integrate with issue tracking system
        self._log_escalation(escalation_data)
        
        # Return None to indicate human review required
        return None
    
    def _score_evidence_quality(self, rationale: str) -> float:
        """
        Score the quality of evidence in judge rationale
        
        Args:
            rationale: Judge's explanation for their score
            
        Returns:
            Evidence quality score (0-1)
        """
        quality_indicators = {
            'specific_examples': 0.3,      # Contains specific examples from plan
            'wcag_references': 0.2,        # References WCAG guidelines  
            'technical_details': 0.2,      # Includes technical implementation details
            'user_impact': 0.15,           # Discusses user impact
            'quantitative_data': 0.15      # Includes measurable criteria
        }
        
        score = 0.0
        rationale_lower = rationale.lower()
        
        # Check for specific examples
        if any(phrase in rationale_lower for phrase in ['for example', 'such as', 'specifically']):
            score += quality_indicators['specific_examples']
        
        # Check for WCAG references  
        if any(phrase in rationale_lower for phrase in ['wcag', 'guideline', 'level aa', 'level a']):
            score += quality_indicators['wcag_references']
        
        # Check for technical details
        if any(phrase in rationale_lower for phrase in ['code', 'css', 'html', 'aria', 'implementation']):
            score += quality_indicators['technical_details']
        
        # Check for user impact discussion
        if any(phrase in rationale_lower for phrase in ['user', 'accessibility', 'usability', 'barrier']):
            score += quality_indicators['user_impact']
        
        # Check for quantitative elements
        if any(char.isdigit() for char in rationale) and any(phrase in rationale_lower for phrase in ['%', 'seconds', 'pixels', 'ratio']):
            score += quality_indicators['quantitative_data']
        
        return min(score, 1.0)  # Cap at 1.0
    
    def generate_consensus_report(self, conflicts: List[ConflictAnalysis], 
                                resolutions: Dict[str, Dict[str, float]]) -> str:
        """
        Generate comprehensive consensus building report
        """
        report = f"""
# Consensus Building Report

## Executive Summary
- Total Conflicts Identified: {len(conflicts)}
- Conflicts Resolved Automatically: {len([c for c in conflicts if c.severity != ConflictSeverity.CRITICAL])}
- Conflicts Requiring Human Review: {len([c for c in conflicts if c.severity == ConflictSeverity.CRITICAL])}

## Conflict Severity Breakdown
"""
        
        severity_counts = {}
        for conflict in conflicts:
            severity_counts[conflict.severity] = severity_counts.get(conflict.severity, 0) + 1
        
        for severity, count in severity_counts.items():
            report += f"- {severity.value.title()}: {count} conflicts\n"
        
        report += "\n## Resolution Strategies Applied\n"
        
        for conflict in conflicts:
            strategy = self.resolution_strategies[conflict.severity].__name__
            report += f"- {conflict.plan_name} ({conflict.criterion}): {strategy}\n"
        
        report += "\n## Judge Performance Analysis\n"
        report += self._generate_judge_performance_analysis(conflicts)
        
        return report

class MetaEvaluationSystem:
    """
    System for evaluating and improving judge performance over time
    """
    
    def __init__(self):
        self.evaluation_history = []
        self.performance_metrics = {}
    
    def track_judge_performance(self, evaluation_session: Dict):
        """Track judge performance metrics across evaluations"""
        self.evaluation_history.append(evaluation_session)
        self._update_performance_metrics()
    
    def identify_bias_patterns(self) -> Dict[str, List[str]]:
        """Identify systematic bias patterns in judge evaluations"""
        bias_patterns = {
            'gemini': [],
            'gpt4': []
        }
        
        # Analyze scoring patterns
        for judge in ['gemini', 'gpt4']:
            judge_scores = self._extract_judge_scores(judge)
            
            # Check for systematic biases
            if self._detect_criterion_bias(judge_scores, 'Strategic Prioritization'):
                bias_patterns[judge].append('Overweights strategic considerations')
            
            if self._detect_score_clustering(judge_scores):
                bias_patterns[judge].append('Tends to cluster scores around specific values')
            
            if self._detect_severity_bias(judge_scores):
                bias_patterns[judge].append('Systematically lenient/harsh scoring')
        
        return bias_patterns
    
    def generate_calibration_recommendations(self) -> List[str]:
        """Generate recommendations for improving judge calibration"""
        recommendations = []
        
        bias_patterns = self.identify_bias_patterns()
        
        for judge, biases in bias_patterns.items():
            if biases:
                recommendations.append(f"Recalibrate {judge} to address: {', '.join(biases)}")
        
        # Additional recommendations based on performance analysis
        if self._detect_inconsistency():
            recommendations.append("Implement consistency checking mechanisms")
        
        if self._detect_confidence_issues():
            recommendations.append("Enhance evidence validation requirements")
        
        return recommendations
```

### 5.2 Batch Processing System

#### Batch Processing Engine (`src/batch/batch_processor.py`)
```python
"""
Batch processing system for multiple audit reports and plan sets
References: Master Plan - Batch Processing, Phase 3 - Workflow Integration
"""
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

@dataclass
class BatchJob:
    job_id: str
    name: str
    audit_reports: List[Path]
    plan_directories: List[Path]
    status: str = "pending"
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Optional[Dict] = None
    error: Optional[str] = None

class BatchProcessor:
    """
    Processes multiple audit reports and plan sets in parallel
    Provides progress tracking and result aggregation
    """
    
    def __init__(self, crew_manager, max_concurrent_jobs: int = 3):
        self.crew_manager = crew_manager
        self.max_concurrent_jobs = max_concurrent_jobs
        self.active_jobs = {}
        self.job_queue = []
        self.completed_jobs = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_jobs)
    
    def submit_batch_job(self, 
                        name: str,
                        audit_reports: List[Path],
                        plan_directories: List[Path]) -> str:
        """
        Submit a new batch processing job
        
        Args:
            name: Human-readable name for the batch
            audit_reports: List of audit report file paths
            plan_directories: List of directories containing remediation plans
            
        Returns:
            Job ID for tracking
        """
        job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_jobs)}"
        
        job = BatchJob(
            job_id=job_id,
            name=name,
            audit_reports=audit_reports,
            plan_directories=plan_directories,
            created_at=datetime.now()
        )
        
        self.job_queue.append(job)
        self._process_queue()
        
        return job_id
    
    async def process_batch_job(self, job: BatchJob) -> Dict[str, Any]:
        """
        Process a single batch job with multiple audit/plan combinations
        
        Args:
            job: Batch job to process
            
        Returns:
            Aggregated results from all evaluations in the batch
        """
        job.status = "running"
        job.started_at = datetime.now()
        
        try:
            batch_results = {}
            
            # Process each audit report with its corresponding plan sets
            for i, audit_path in enumerate(job.audit_reports):
                audit_name = audit_path.stem
                
                # Get corresponding plan directory
                plan_dir = job.plan_directories[i] if i < len(job.plan_directories) else job.plan_directories[0]
                
                # Process this audit/plan combination
                evaluation_result = await self._process_audit_plan_combination(
                    audit_path, plan_dir, f"{audit_name}_{i}"
                )
                
                batch_results[audit_name] = evaluation_result
            
            # Generate batch summary
            batch_summary = self._generate_batch_summary(batch_results)
            
            job.status = "completed"
            job.completed_at = datetime.now()
            job.results = {
                'individual_results': batch_results,
                'batch_summary': batch_summary
            }
            
            return job.results
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.now()
            raise
    
    def get_batch_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a batch job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
        elif job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
        else:
            return None
        
        return {
            'job_id': job.job_id,
            'name': job.name,
            'status': job.status,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'audit_count': len(job.audit_reports),
            'plan_set_count': len(job.plan_directories),
            'error': job.error
        }
    
    def list_all_jobs(self) -> List[Dict[str, Any]]:
        """List all batch jobs (active, queued, and completed)"""
        all_jobs = []
        
        # Queued jobs
        for job in self.job_queue:
            all_jobs.append({
                **self.get_batch_status(job.job_id),
                'queue_position': self.job_queue.index(job)
            })
        
        # Active jobs
        for job_id in self.active_jobs:
            all_jobs.append(self.get_batch_status(job_id))
        
        # Completed jobs
        for job_id in self.completed_jobs:
            all_jobs.append(self.get_batch_status(job_id))
        
        return sorted(all_jobs, key=lambda x: x['created_at'], reverse=True)
    
    def _generate_batch_summary(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics across all evaluations in batch"""
        summary = {
            'total_evaluations': len(batch_results),
            'average_scores': {},
            'best_performing_plans': {},
            'consistency_metrics': {},
            'recommendations': []
        }
        
        # Aggregate scores across all evaluations
        all_plan_scores = {}
        
        for audit_name, result in batch_results.items():
            if hasattr(result, 'plan_scores'):
                for plan_name, score in result.plan_scores.items():
                    if plan_name not in all_plan_scores:
                        all_plan_scores[plan_name] = []
                    all_plan_scores[plan_name].append(score)
        
        # Calculate average scores per plan across all audits
        for plan_name, scores in all_plan_scores.items():
            summary['average_scores'][plan_name] = {
                'mean': sum(scores) / len(scores),
                'min': min(scores),
                'max': max(scores),
                'std_dev': self._calculate_std_dev(scores)
            }
        
        # Identify best performing plans
        best_plan = max(summary['average_scores'].items(), key=lambda x: x[1]['mean'])
        summary['best_performing_plans']['overall'] = {
            'plan': best_plan[0],
            'average_score': best_plan[1]['mean']
        }
        
        # Calculate consistency metrics
        summary['consistency_metrics'] = self._calculate_consistency_metrics(all_plan_scores)
        
        # Generate recommendations
        summary['recommendations'] = self._generate_batch_recommendations(batch_results, summary)
        
        return summary
    
    def export_batch_results(self, job_id: str, format: str = "json") -> str:
        """Export batch results in specified format"""
        job = self.completed_jobs.get(job_id)
        if not job or not job.results:
            raise ValueError(f"No completed results found for job {job_id}")
        
        if format.lower() == "json":
            return json.dumps(job.results, indent=2, default=str)
        elif format.lower() == "csv":
            return self._export_to_csv(job.results)
        elif format.lower() == "markdown":
            return self._export_to_markdown(job.results)
        else:
            raise ValueError(f"Unsupported export format: {format}")

class HistoricalAnalysis:
    """
    Analyzes trends and patterns across multiple batch evaluations
    """
    
    def __init__(self):
        self.evaluation_database = []
    
    def add_batch_results(self, batch_results: Dict[str, Any]):
        """Add batch results to historical database"""
        self.evaluation_database.append({
            'timestamp': datetime.now(),
            'results': batch_results
        })
    
    def analyze_trends(self, time_period: str = "all") -> Dict[str, Any]:
        """
        Analyze trends in plan performance over time
        
        Args:
            time_period: "all", "last_month", "last_week"
            
        Returns:
            Trend analysis results
        """
        relevant_data = self._filter_by_time_period(time_period)
        
        return {
            'plan_performance_trends': self._analyze_plan_trends(relevant_data),
            'judge_consistency_trends': self._analyze_judge_trends(relevant_data),
            'improvement_opportunities': self._identify_improvement_opportunities(relevant_data)
        }
    
    def generate_benchmark_scores(self) -> Dict[str, float]:
        """Generate benchmark scores based on historical data"""
        all_scores = []
        
        for batch in self.evaluation_database:
            for audit_result in batch['results']['individual_results'].values():
                if hasattr(audit_result, 'plan_scores'):
                    all_scores.extend(audit_result.plan_scores.values())
        
        if not all_scores:
            return {}
        
        return {
            'excellent_threshold': self._percentile(all_scores, 90),
            'good_threshold': self._percentile(all_scores, 75),
            'average_threshold': self._percentile(all_scores, 50),
            'below_average_threshold': self._percentile(all_scores, 25)
        }
```

### 5.3 Performance Optimization

#### Performance Monitoring (`src/monitoring/performance_monitor.py`)
```python
"""
Performance monitoring and optimization system
References: Master Plan - Performance Considerations
"""
import time
import psutil
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    memory_usage_mb: float
    cpu_usage_percent: float
    response_time_ms: float
    active_agents: int
    queue_length: int
    tokens_processed: int
    api_calls_made: int
    cache_hit_rate: float

class PerformanceMonitor:
    """
    Monitors system performance and provides optimization recommendations
    """
    
    def __init__(self):
        self.metrics_history = []
        self.performance_thresholds = {
            'max_memory_mb': 4096,
            'max_cpu_percent': 80,
            'max_response_time_ms': 30000,
            'min_cache_hit_rate': 0.7
        }
        self.logger = logging.getLogger(__name__)
    
    def start_monitoring_session(self, session_id: str):
        """Start monitoring a specific evaluation session"""
        self.current_session = {
            'session_id': session_id,
            'start_time': datetime.now(),
            'metrics': []
        }
    
    def record_metrics(self, custom_metrics: Dict[str, Any] = None):
        """Record current system performance metrics"""
        current_metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            memory_usage_mb=psutil.virtual_memory().used / (1024 * 1024),
            cpu_usage_percent=psutil.cpu_percent(interval=1),
            response_time_ms=custom_metrics.get('response_time_ms', 0) if custom_metrics else 0,
            active_agents=custom_metrics.get('active_agents', 0) if custom_metrics else 0,
            queue_length=custom_metrics.get('queue_length', 0) if custom_metrics else 0,
            tokens_processed=custom_metrics.get('tokens_processed', 0) if custom_metrics else 0,
            api_calls_made=custom_metrics.get('api_calls_made', 0) if custom_metrics else 0,
            cache_hit_rate=custom_metrics.get('cache_hit_rate', 0) if custom_metrics else 0
        )
        
        self.metrics_history.append(current_metrics)
        
        # Check for performance issues
        self._check_performance_thresholds(current_metrics)
        
        return current_metrics
    
    def _check_performance_thresholds(self, metrics: PerformanceMetrics):
        """Check if any performance thresholds are exceeded"""
        warnings = []
        
        if metrics.memory_usage_mb > self.performance_thresholds['max_memory_mb']:
            warnings.append(f"High memory usage: {metrics.memory_usage_mb:.1f}MB")
        
        if metrics.cpu_usage_percent > self.performance_thresholds['max_cpu_percent']:
            warnings.append(f"High CPU usage: {metrics.cpu_usage_percent:.1f}%")
        
        if metrics.response_time_ms > self.performance_thresholds['max_response_time_ms']:
            warnings.append(f"Slow response time: {metrics.response_time_ms:.0f}ms")
        
        if metrics.cache_hit_rate < self.performance_thresholds['min_cache_hit_rate']:
            warnings.append(f"Low cache hit rate: {metrics.cache_hit_rate:.2f}")
        
        for warning in warnings:
            self.logger.warning(f"Performance threshold exceeded: {warning}")
    
    def generate_performance_report(self, time_window: timedelta = None) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report"""
        if time_window:
            cutoff_time = datetime.now() - time_window
            relevant_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        else:
            relevant_metrics = self.metrics_history
        
        if not relevant_metrics:
            return {"error": "No metrics available for the specified time window"}
        
        return {
            'time_period': {
                'start': relevant_metrics[0].timestamp,
                'end': relevant_metrics[-1].timestamp,
                'duration_minutes': (relevant_metrics[-1].timestamp - relevant_metrics[0].timestamp).total_seconds() / 60
            },
            'memory_analysis': self._analyze_memory_usage(relevant_metrics),
            'cpu_analysis': self._analyze_cpu_usage(relevant_metrics),
            'response_time_analysis': self._analyze_response_times(relevant_metrics),
            'throughput_analysis': self._analyze_throughput(relevant_metrics),
            'optimization_recommendations': self._generate_optimization_recommendations(relevant_metrics)
        }
    
    def _analyze_memory_usage(self, metrics: List[PerformanceMetrics]) -> Dict[str, float]:
        """Analyze memory usage patterns"""
        memory_values = [m.memory_usage_mb for m in metrics]
        
        return {
            'average_mb': sum(memory_values) / len(memory_values),
            'peak_mb': max(memory_values),
            'min_mb': min(memory_values),
            'growth_rate_mb_per_hour': self._calculate_growth_rate(metrics, 'memory_usage_mb')
        }
    
    def _generate_optimization_recommendations(self, metrics: List[PerformanceMetrics]) -> List[str]:
        """Generate specific optimization recommendations based on performance data"""
        recommendations = []
        
        # Memory optimization
        avg_memory = sum(m.memory_usage_mb for m in metrics) / len(metrics)
        if avg_memory > 2048:
            recommendations.append("Consider implementing memory pooling for agent instances")
            recommendations.append("Enable garbage collection optimization for long-running evaluations")
        
        # CPU optimization
        avg_cpu = sum(m.cpu_usage_percent for m in metrics) / len(metrics)
        if avg_cpu > 60:
            recommendations.append("Implement parallel processing for independent evaluation tasks")
            recommendations.append("Consider CPU-bound task optimization with asyncio")
        
        # Response time optimization
        response_times = [m.response_time_ms for m in metrics if m.response_time_ms > 0]
        if response_times and sum(response_times) / len(response_times) > 15000:
            recommendations.append("Implement request caching for similar evaluation inputs")
            recommendations.append("Consider using streaming responses for long evaluations")
        
        # Cache optimization
        cache_rates = [m.cache_hit_rate for m in metrics if m.cache_hit_rate > 0]
        if cache_rates and sum(cache_rates) / len(cache_rates) < 0.5:
            recommendations.append("Expand cache size and implement smarter cache invalidation")
            recommendations.append("Pre-cache common evaluation patterns and templates")
        
        return recommendations

class CacheManager:
    """
    Intelligent caching system for evaluation results and intermediate data
    """
    
    def __init__(self, max_cache_size_mb: int = 512):
        self.cache = {}
        self.cache_metadata = {}
        self.max_cache_size_mb = max_cache_size_mb
        self.current_cache_size_mb = 0
        self.hit_count = 0
        self.miss_count = 0
    
    def get_cache_key(self, audit_content: str, plan_content: str, evaluation_type: str) -> str:
        """Generate unique cache key for evaluation input"""
        import hashlib
        
        combined_content = f"{audit_content}:{plan_content}:{evaluation_type}"
        return hashlib.md5(combined_content.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Retrieve cached evaluation result"""
        if cache_key in self.cache:
            # Update access time
            self.cache_metadata[cache_key]['last_accessed'] = datetime.now()
            self.cache_metadata[cache_key]['access_count'] += 1
            self.hit_count += 1
            
            return self.cache[cache_key]
        
        self.miss_count += 1
        return None
    
    def cache_result(self, cache_key: str, result: Any, size_estimate_mb: float = 1.0):
        """Cache evaluation result with size management"""
        # Check if we need to free up space
        if self.current_cache_size_mb + size_estimate_mb > self.max_cache_size_mb:
            self._evict_old_entries(size_estimate_mb)
        
        # Store result and metadata
        self.cache[cache_key] = result
        self.cache_metadata[cache_key] = {
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'access_count': 0,
            'size_mb': size_estimate_mb
        }
        
        self.current_cache_size_mb += size_estimate_mb
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'total_entries': len(self.cache),
            'current_size_mb': self.current_cache_size_mb,
            'max_size_mb': self.max_cache_size_mb,
            'utilization_percent': (self.current_cache_size_mb / self.max_cache_size_mb) * 100
        }
    
    def _evict_old_entries(self, space_needed_mb: float):
        """Evict least recently used entries to free up space"""
        # Sort by last accessed time
        sorted_entries = sorted(
            self.cache_metadata.items(),
            key=lambda x: x[1]['last_accessed']
        )
        
        space_freed = 0
        for cache_key, metadata in sorted_entries:
            if space_freed >= space_needed_mb:
                break
            
            # Remove entry
            del self.cache[cache_key]
            space_freed += metadata['size_mb']
            self.current_cache_size_mb -= metadata['size_mb']
            del self.cache_metadata[cache_key]
```

### 5.4 Production Deployment

#### Docker Configuration (`Dockerfile`)
```dockerfile
# Multi-stage build for optimized production deployment
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY src/ ./src/
COPY app/ ./app/
COPY promt/ ./promt/

# Create necessary directories
RUN mkdir -p data output temp logs \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set Python path
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH="/app"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose ports
EXPOSE 8501 8000

# Default command
CMD ["streamlit", "run", "app/main.py", "--server.address", "0.0.0.0"]
```

#### Docker Compose Configuration (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  accessibility-evaluator:
    build: .
    ports:
      - "8501:8501"  # Streamlit
      - "8000:8000"  # FastAPI (if enabled)
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
      - CACHE_SIZE_MB=512
      - MAX_CONCURRENT_JOBS=3
    volumes:
      - ./data:/app/data:ro
      - ./output:/app/output
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

  redis-cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped

  monitoring:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

networks:
  default:
    name: accessibility-evaluator-network
```

#### Kubernetes Deployment (`k8s/deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: accessibility-evaluator
  labels:
    app: accessibility-evaluator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: accessibility-evaluator
  template:
    metadata:
      labels:
        app: accessibility-evaluator
    spec:
      containers:
      - name: accessibility-evaluator
        image: accessibility-evaluator:latest
        ports:
        - containerPort: 8501
        - containerPort: 8000
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: google-api-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-api-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: accessibility-evaluator-service
spec:
  selector:
    app: accessibility-evaluator
  ports:
  - name: streamlit
    port: 8501
    targetPort: 8501
  - name: api
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

## Quality Gates

### Phase 5 Completion Criteria
- [ ] **Performance Optimization**: System performs within acceptable limits
- [ ] **Production Deployment**: Full deployment pipeline operational
- [ ] **Documentation**: Complete technical and user documentation
- [ ] **Quality Standards**: All enhanced quality gates passing
- [ ] **Monitoring Systems**: Production monitoring and alerting active
- [ ] **User Acceptance**: Successfully validated by stakeholders
- [ ] **Business Value**: Demonstrable ROI and business impact
- [ ] **Sustainability**: Long-term maintenance plan established
- [ ] **Knowledge Transfer**: Team properly trained on system

### Enhanced Quality Gates

#### 🚀 Production Readiness
- [ ] **Deployment Pipeline**: Fully automated CI/CD deployment
- [ ] **Infrastructure as Code**: All infrastructure properly versioned
- [ ] **Container Orchestration**: Production-ready container deployment
- [ ] **Auto-scaling**: System automatically scales with demand
- [ ] **Load Balancing**: Traffic properly distributed across instances

#### 📊 Performance & Monitoring
- [ ] **SLA Compliance**: System meets defined service level agreements
- [ ] **Application Performance Monitoring**: Full APM implementation
- [ ] **Custom Metrics**: Business-specific metrics tracked and alerted
- [ ] **Capacity Planning**: Resource usage trends monitored and projected
- [ ] **Performance Benchmarking**: Baseline performance metrics established

#### 🔧 Operational Excellence
- [ ] **Incident Response**: Clear incident management procedures
- [ ] **Disaster Recovery**: Comprehensive backup and recovery plan
- [ ] **Business Continuity**: System designed for high availability
- [ ] **Change Management**: Controlled change deployment process
- [ ] **Runbook Documentation**: Complete operational procedures documented

#### 🎯 Business Impact & ROI
- [ ] **KPI Tracking**: Key performance indicators defined and measured
- [ ] **User Satisfaction**: User satisfaction metrics above target thresholds
- [ ] **Business Value Metrics**: Quantifiable business impact demonstrated
- [ ] **Cost Optimization**: System operates within defined cost parameters
- [ ] **Scalability Planning**: Growth scenarios planned and validated

### Performance Standards
- [ ] **Response Time**: UI responses under 2 seconds
- [ ] **Report Generation**: PDF reports generate under 30 seconds
- [ ] **System Availability**: 99.9% uptime SLA
- [ ] **Concurrent Users**: Support for 50+ simultaneous users
- [ ] **Data Processing**: Handle 100+ remediation plans per hour
- [ ] **Memory Usage**: Efficient memory utilization under load
- [ ] **Storage Optimization**: Intelligent data archiving and cleanup
- [ ] **Network Efficiency**: Optimized API calls and data transfer

### Production Monitoring
- [ ] **Health Checks**: Comprehensive system health monitoring
- [ ] **Error Tracking**: Automatic error detection and alerting
- [ ] **Performance Metrics**: Real-time performance dashboards
- [ ] **User Analytics**: Usage patterns and behavior tracking
- [ ] **Security Monitoring**: Continuous security threat detection
- [ ] **Compliance Tracking**: Regulatory compliance monitoring
- [ ] **Audit Logging**: Complete audit trail for all operations
- [ ] **Incident Alerting**: Proactive alerting for system issues

### Business Continuity & Support
- [ ] **Backup Strategy**: Automated, tested backup procedures
- [ ] **Disaster Recovery**: Tested disaster recovery procedures
- [ ] **Knowledge Transfer**: Team knowledge documented and transferred
- [ ] **Support Documentation**: Comprehensive support procedures
- [ ] **Training Materials**: User and administrator training complete
- [ ] **Maintenance Schedule**: Regular maintenance procedures established
- [ ] **Vendor Management**: Third-party dependencies properly managed
- [ ] **Legal Compliance**: All legal and regulatory requirements met
