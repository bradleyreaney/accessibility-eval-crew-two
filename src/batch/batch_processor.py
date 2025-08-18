"""
Batch processing system for multiple audit reports and plan sets
References: Master Plan - Batch Processing, Phase 3 - Workflow Integration

Phase 5: Advanced Features & Optimization - Batch Processing
"""

import asyncio
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class BatchJob:
    """Data structure for batch processing jobs"""

    job_id: str
    name: str
    audit_reports: List[Path]
    plan_directories: List[Path]
    status: str = "pending"
    created_at: Optional[datetime] = None
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
        """Initialize the batch processor with crew manager and concurrent job limit."""
        self.crew_manager = crew_manager
        self.max_concurrent_jobs = max_concurrent_jobs
        self.active_jobs: Dict[str, BatchJob] = {}
        self.job_queue: List[BatchJob] = []
        self.completed_jobs: Dict[str, BatchJob] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_jobs)

    def submit_batch_job(
        self, name: str, audit_reports: List[Path], plan_directories: List[Path]
    ) -> str:
        """
        Submit a new batch processing job

        Args:
            name: Human-readable name for the batch
            audit_reports: List of audit report file paths
            plan_directories: List of directories containing remediation plans

        Returns:
            Job ID for tracking
        """
        job_id = (
            f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_jobs)}"
        )

        job = BatchJob(
            job_id=job_id,
            name=name,
            audit_reports=audit_reports,
            plan_directories=plan_directories,
            created_at=datetime.now(),
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
                plan_dir = (
                    job.plan_directories[i]
                    if i < len(job.plan_directories)
                    else job.plan_directories[0]
                )

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
                "individual_results": batch_results,
                "batch_summary": batch_summary,
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
            # Check if job is in queue
            queued_job = next((j for j in self.job_queue if j.job_id == job_id), None)
            if queued_job:
                job = queued_job
            else:
                return None

        return {
            "job_id": job.job_id,
            "name": job.name,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "audit_count": len(job.audit_reports),
            "plan_set_count": len(job.plan_directories),
            "error": job.error,
        }

    def list_all_jobs(self) -> List[Dict[str, Any]]:
        """List all batch jobs (active, queued, and completed)"""
        all_jobs = []

        # Queued jobs
        for job in self.job_queue:
            job_status = self.get_batch_status(job.job_id)
            if job_status:
                job_status["queue_position"] = self.job_queue.index(job)
                all_jobs.append(job_status)

        # Active jobs
        for job_id in self.active_jobs:
            job_status = self.get_batch_status(job_id)
            if job_status:
                all_jobs.append(job_status)

        # Completed jobs
        for job_id in self.completed_jobs:
            job_status = self.get_batch_status(job_id)
            if job_status:
                all_jobs.append(job_status)

        return sorted(all_jobs, key=lambda x: x["created_at"] or "", reverse=True)

    def _generate_batch_summary(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics across all evaluations in batch"""
        summary: Dict[str, Any] = {
            "total_evaluations": len(batch_results),
            "average_scores": {},
            "best_performing_plans": {},
            "consistency_metrics": {},
            "recommendations": [],
        }

        # Aggregate scores across all evaluations
        all_plan_scores: Dict[str, List[float]] = {}

        for audit_name, result in batch_results.items():
            if hasattr(result, "plan_scores"):
                for plan_name, score in result.plan_scores.items():
                    if plan_name not in all_plan_scores:
                        all_plan_scores[plan_name] = []
                    all_plan_scores[plan_name].append(score)

        # Calculate average scores per plan across all audits
        for plan_name, scores in all_plan_scores.items():
            summary["average_scores"][plan_name] = {
                "mean": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "std_dev": self._calculate_std_dev(scores),
            }

        # Identify best performing plans
        if summary["average_scores"]:
            best_plan = max(
                summary["average_scores"].items(), key=lambda x: x[1]["mean"]
            )
            summary["best_performing_plans"]["overall"] = {
                "plan": best_plan[0],
                "average_score": best_plan[1]["mean"],
            }

        # Calculate consistency metrics
        summary["consistency_metrics"] = self._calculate_consistency_metrics(
            all_plan_scores
        )

        # Generate recommendations
        summary["recommendations"] = self._generate_batch_recommendations(
            batch_results, summary
        )

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

    def _process_queue(self):
        """Process jobs in the queue if there's capacity"""
        # Simplified implementation for now
        pass

    async def _process_audit_plan_combination(
        self, audit_path: Path, plan_dir: Path, session_id: str
    ):
        """Process a single audit/plan combination"""
        # This would integrate with the existing crew evaluation system
        # For now, return mock result structure
        return {
            "plan_scores": {"Plan A": 7.5, "Plan B": 6.0},
            "session_id": session_id,
            "audit_path": str(audit_path),
            "plan_directory": str(plan_dir),
        }

    def _calculate_std_dev(self, scores: List[float]) -> float:
        """Calculate standard deviation of scores"""
        if len(scores) <= 1:
            return 0.0
        return statistics.stdev(scores)

    def _calculate_consistency_metrics(
        self, all_plan_scores: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """Calculate consistency metrics across evaluations"""
        metrics = {}

        for plan_name, scores in all_plan_scores.items():
            if len(scores) > 1:
                metrics[f"{plan_name}_consistency"] = 1.0 / (
                    1.0 + self._calculate_std_dev(scores)
                )
            else:
                metrics[f"{plan_name}_consistency"] = 1.0

        return metrics

    def _generate_batch_recommendations(
        self, batch_results: Dict[str, Any], summary: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on batch analysis"""
        recommendations = []

        if summary["total_evaluations"] > 1:
            recommendations.append(
                "Consider cross-audit analysis for pattern identification"
            )

        if summary.get("best_performing_plans"):
            best_plan = summary["best_performing_plans"]["overall"]["plan"]
            recommendations.append(
                f"Consider adopting elements from {best_plan} in other plans"
            )

        return recommendations

    def _export_to_csv(self, results: Dict[str, Any]) -> str:
        """Export results to CSV format"""
        # Simplified CSV export implementation
        csv_lines = ["Plan,Score,Audit"]

        individual_results = results.get("individual_results", {})
        for audit_name, audit_result in individual_results.items():
            if hasattr(audit_result, "plan_scores"):
                for plan_name, score in audit_result.plan_scores.items():
                    csv_lines.append(f"{plan_name},{score},{audit_name}")

        return "\n".join(csv_lines)

    def _export_to_markdown(self, results: Dict[str, Any]) -> str:
        """Export results to Markdown format"""
        markdown = "# Batch Evaluation Results\n\n"

        batch_summary = results.get("batch_summary", {})
        total_evals = batch_summary.get("total_evaluations", 0)

        markdown += "## Summary\n\n"
        markdown += f"- Total Evaluations: {total_evals}\n"

        average_scores = batch_summary.get("average_scores", {})
        if average_scores:
            markdown += "\n## Average Scores\n\n"
            for plan_name, scores in average_scores.items():
                markdown += f"- **{plan_name}**: {scores['mean']:.2f} (±{scores['std_dev']:.2f})\n"

        return markdown


class HistoricalAnalysis:
    """
    Analyzes trends and patterns across multiple batch evaluations
    """

    def __init__(self):
        """Initialize the historical analysis system for tracking evaluation trends."""
        self.evaluation_database = []

    def add_batch_results(self, batch_results: Dict[str, Any]):
        """Add batch results to historical database"""
        self.evaluation_database.append(
            {"timestamp": datetime.now(), "results": batch_results}
        )

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
            "plan_performance_trends": self._analyze_plan_trends(relevant_data),
            "judge_consistency_trends": self._analyze_judge_trends(relevant_data),
            "improvement_opportunities": self._identify_improvement_opportunities(
                relevant_data
            ),
        }

    def generate_benchmark_scores(self) -> Dict[str, float]:
        """Generate benchmark scores based on historical data"""
        all_scores = []

        for batch in self.evaluation_database:
            individual_results = batch["results"].get("individual_results", {})
            for audit_result in individual_results.values():
                if hasattr(audit_result, "plan_scores"):
                    all_scores.extend(audit_result.plan_scores.values())

        if not all_scores:
            return {}

        return {
            "excellent_threshold": self._percentile(all_scores, 90),
            "good_threshold": self._percentile(all_scores, 75),
            "average_threshold": self._percentile(all_scores, 50),
            "below_average_threshold": self._percentile(all_scores, 25),
        }

    def _filter_by_time_period(self, time_period: str) -> List[Dict]:
        """Filter evaluation data by time period"""
        if time_period == "all":
            return self.evaluation_database

        now = datetime.now()
        if time_period == "last_week":
            cutoff = now - timedelta(weeks=1)
        elif time_period == "last_month":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = now - timedelta(days=365)  # Default to last year

        return [
            entry for entry in self.evaluation_database if entry["timestamp"] >= cutoff
        ]

    def _analyze_plan_trends(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze plan performance trends over time"""
        # Simplified implementation
        return {"trend": "stable", "growth_rate": 0.02}

    def _analyze_judge_trends(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze judge consistency trends over time"""
        # Simplified implementation
        return {"consistency": "improving", "agreement_rate": 0.85}

    def _identify_improvement_opportunities(self, data: List[Dict]) -> List[str]:
        """Identify improvement opportunities from historical data"""
        # Simplified implementation
        return [
            "Increase technical specificity in plans",
            "Improve strategic prioritization",
        ]

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)

        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index

            if upper_index >= len(sorted_values):
                return sorted_values[lower_index]

            return (
                sorted_values[lower_index] * (1 - weight)
                + sorted_values[upper_index] * weight
            )
