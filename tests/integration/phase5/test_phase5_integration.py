"""
Integration Tests for Phase 5: Advanced Features & Optimization
Tests integration between consensus, batch processing, and monitoring systems

These tests verify that all Phase 5 components work together correctly
"""

import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.batch.batch_processor import BatchProcessor
from src.consensus.advanced_consensus import (
    AdvancedConsensusEngine,
    ConflictAnalysis,
    ConflictSeverity,
)
from src.models.evaluation_models import JudgmentScore, PlanEvaluation
from src.monitoring.performance_monitor import PerformanceMonitor


class TestPhase5Integration:
    """Integration tests for Phase 5 components"""

    def setup_method(self):
        """Set up test components"""
        self.consensus_engine = AdvancedConsensusEngine()
        self.batch_processor = BatchProcessor(Mock(), max_concurrent_jobs=2)
        self.performance_monitor = PerformanceMonitor()

    def test_consensus_with_monitoring(self):
        """Test consensus engine with performance monitoring"""
        # Start monitoring session
        self.performance_monitor.start_monitoring_session("consensus_test")

        # Create mock evaluations with conflicts
        evaluations = [
            Mock(
                plan_name="Plan A",
                judge_id="gemini",
                judgment_scores=[
                    Mock(
                        criterion="Strategic Prioritization",
                        score=8.0,
                        rationale="Excellent strategic approach with WCAG references",
                    ),
                    Mock(
                        criterion="Technical Specificity",
                        score=6.0,
                        rationale="Basic technical implementation",
                    ),
                ],
            ),
            Mock(
                plan_name="Plan A",
                judge_id="gpt4",
                judgment_scores=[
                    Mock(
                        criterion="Strategic Prioritization",
                        score=5.0,
                        rationale="Lacks strategic depth",
                    ),
                    Mock(
                        criterion="Technical Specificity",
                        score=9.0,
                        rationale="Comprehensive technical details with code examples",
                    ),
                ],
            ),
        ]

        # Record initial metrics
        initial_metrics = self.performance_monitor.record_metrics(
            {"active_agents": 2, "tokens_processed": 500}
        )

        # Analyze conflicts
        conflicts = self.consensus_engine.analyze_conflicts(evaluations)

        # Record metrics after conflict analysis
        analysis_metrics = self.performance_monitor.record_metrics(
            {"active_agents": 2, "tokens_processed": 750, "response_time_ms": 2500}
        )

        # Resolve conflicts
        resolutions = self.consensus_engine.resolve_conflicts(conflicts)

        # Record final metrics
        final_metrics = self.performance_monitor.record_metrics(
            {
                "active_agents": 0,
                "tokens_processed": 1000,
                "response_time_ms": 1500,
                "cache_hit_rate": 0.85,
            }
        )

        # Verify integration
        assert len(conflicts) >= 1  # Should detect conflicts
        assert len(resolutions) >= 1  # Should resolve some conflicts
        assert len(self.performance_monitor.metrics_history) == 3

        # Generate performance report
        report = self.performance_monitor.generate_performance_report()
        assert "optimization_recommendations" in report

    @pytest.mark.asyncio
    async def test_batch_processing_with_consensus(self):
        """Test batch processing integration with consensus mechanisms"""
        # Mock crew manager to return evaluations
        mock_crew_manager = Mock()
        batch_processor = BatchProcessor(mock_crew_manager, max_concurrent_jobs=1)

        # Submit batch job
        audit_reports = [Path("audit1.pdf"), Path("audit2.pdf")]
        plan_directories = [Path("plans1/"), Path("plans2/")]

        job_id = batch_processor.submit_batch_job(
            name="Integration Test Batch",
            audit_reports=audit_reports,
            plan_directories=plan_directories,
        )

        # Mock the processing to include consensus resolution
        def mock_process_audit_plan(audit_path, plan_dir, session_id):
            # Simulate evaluations that would trigger consensus
            mock_evaluations = [
                Mock(
                    plan_name="Plan A",
                    judge_id="gemini",
                    judgment_scores=[
                        Mock(
                            criterion="Strategic Prioritization",
                            score=7.0,
                            rationale="Good",
                        )
                    ],
                ),
                Mock(
                    plan_name="Plan A",
                    judge_id="gpt4",
                    judgment_scores=[
                        Mock(
                            criterion="Strategic Prioritization",
                            score=5.0,
                            rationale="Average",
                        )
                    ],
                ),
            ]

            # Use consensus engine to resolve conflicts
            conflicts = self.consensus_engine.analyze_conflicts(mock_evaluations)
            resolutions = self.consensus_engine.resolve_conflicts(conflicts)

            return {
                "plan_scores": {"Plan A": 6.0, "Plan B": 7.5},
                "conflicts_detected": len(conflicts),
                "conflicts_resolved": len(resolutions),
                "consensus_applied": True,
            }

        # Get the job and process it
        job = batch_processor.job_queue[0]

        with patch.object(
            batch_processor,
            "_process_audit_plan_combination",
            side_effect=mock_process_audit_plan,
        ):
            results = await batch_processor.process_batch_job(job)

        # Verify integration
        assert job.status == "completed"
        assert "individual_results" in results
        assert "batch_summary" in results

        # Verify consensus was applied
        individual_results = results["individual_results"]
        for audit_result in individual_results.values():
            assert "consensus_applied" in audit_result
            assert audit_result["consensus_applied"] is True

    def test_performance_monitoring_with_batch_processing(self):
        """Test performance monitoring integration with batch processing"""
        # Start monitoring for batch processing
        session_id = "batch_monitoring_test"
        self.performance_monitor.start_monitoring_session(session_id)

        # Simulate batch processing load
        batch_metrics = [
            {"active_agents": 1, "tokens_processed": 200, "response_time_ms": 1500},
            {"active_agents": 2, "tokens_processed": 400, "response_time_ms": 2500},
            {"active_agents": 3, "tokens_processed": 600, "response_time_ms": 3500},
            {"active_agents": 2, "tokens_processed": 800, "response_time_ms": 2000},
            {"active_agents": 0, "tokens_processed": 1000, "response_time_ms": 500},
        ]

        recorded_metrics = []
        for metrics in batch_metrics:
            recorded = self.performance_monitor.record_metrics(metrics)
            recorded_metrics.append(recorded)

        # Generate performance report
        report = self.performance_monitor.generate_performance_report()

        # Verify monitoring captured batch processing patterns
        assert len(recorded_metrics) == 5
        assert report["throughput_analysis"]["tokens_per_minute"] > 0
        assert "optimization_recommendations" in report

        # Check for batch-specific recommendations
        recommendations = report["optimization_recommendations"]
        if any(m["response_time_ms"] > 3000 for m in batch_metrics):
            assert any("caching" in rec for rec in recommendations)

    def test_full_phase5_workflow(self):
        """Test complete Phase 5 workflow with all components"""
        # 1. Start performance monitoring
        self.performance_monitor.start_monitoring_session("full_workflow_test")

        # 2. Record initial system state
        initial_metrics = self.performance_monitor.record_metrics(
            {"active_agents": 0, "queue_length": 0, "tokens_processed": 0}
        )

        # 3. Create conflicting evaluations
        conflicting_evaluations = [
            Mock(
                plan_name="Plan Alpha",
                judge_id="gemini",
                judgment_scores=[
                    Mock(
                        criterion="Strategic Prioritization",
                        score=9.0,
                        rationale="Excellent strategic framework with specific WCAG examples",
                    ),
                    Mock(
                        criterion="Technical Specificity",
                        score=4.0,
                        rationale="Lacks technical detail",
                    ),
                ],
            ),
            Mock(
                plan_name="Plan Alpha",
                judge_id="gpt4",
                judgment_scores=[
                    Mock(
                        criterion="Strategic Prioritization",
                        score=3.0,
                        rationale="Poor strategic approach",
                    ),
                    Mock(
                        criterion="Technical Specificity",
                        score=8.5,
                        rationale="Comprehensive technical implementation with code samples",
                    ),
                ],
            ),
        ]

        # 4. Record metrics during evaluation
        evaluation_metrics = self.performance_monitor.record_metrics(
            {
                "active_agents": 2,
                "queue_length": 1,
                "tokens_processed": 1500,
                "response_time_ms": 4500,
            }
        )

        # 5. Apply consensus mechanisms
        conflicts = self.consensus_engine.analyze_conflicts(conflicting_evaluations)
        resolutions = self.consensus_engine.resolve_conflicts(conflicts)
        consensus_report = self.consensus_engine.generate_consensus_report(
            conflicts, resolutions
        )

        # 6. Record metrics after consensus
        consensus_metrics = self.performance_monitor.record_metrics(
            {
                "active_agents": 1,
                "queue_length": 0,
                "tokens_processed": 2000,
                "response_time_ms": 2000,
                "cache_hit_rate": 0.75,
            }
        )

        # 7. Generate performance analysis
        performance_report = self.performance_monitor.generate_performance_report()

        # 8. Verify complete workflow
        assert len(conflicts) >= 2  # Should detect conflicts in both criteria
        assert len(resolutions) >= 1  # Should resolve non-critical conflicts
        assert "Executive Summary" in consensus_report
        assert len(self.performance_monitor.metrics_history) == 3

        # Verify performance insights
        assert "memory_analysis" in performance_report
        assert "optimization_recommendations" in performance_report

        # Check that high response time triggered recommendations
        recommendations = performance_report["optimization_recommendations"]
        assert len(recommendations) > 0

        # Verify conflict severity handling
        critical_conflicts = [
            c for c in conflicts if c.severity == ConflictSeverity.CRITICAL
        ]
        high_conflicts = [c for c in conflicts if c.severity == ConflictSeverity.HIGH]

        # Should have detected critical conflicts due to large score differences
        assert len(critical_conflicts) + len(high_conflicts) >= 1

    def test_consensus_evidence_quality_integration(self):
        """Test evidence quality assessment in consensus system"""
        # Create evaluations with varying evidence quality
        evaluations = [
            Mock(
                plan_name="Plan Beta",
                judge_id="gemini",
                judgment_scores=[
                    Mock(
                        criterion="Technical Specificity",
                        score=8.0,
                        rationale="This plan provides specific examples of WCAG implementation with detailed code snippets, CSS modifications, and ARIA attributes for improved accessibility",
                    )
                ],
            ),
            Mock(
                plan_name="Plan Beta",
                judge_id="gpt4",
                judgment_scores=[
                    Mock(
                        criterion="Technical Specificity",
                        score=6.0,
                        rationale="Adequate approach",
                    )
                ],
            ),
        ]

        # Analyze conflicts
        conflicts = self.consensus_engine.analyze_conflicts(evaluations)

        # Should prefer the evaluation with higher evidence quality
        if conflicts:
            conflict = conflicts[0]
            primary_quality = self.consensus_engine._score_evidence_quality(
                conflict.primary_rationale
            )
            secondary_quality = self.consensus_engine._score_evidence_quality(
                conflict.secondary_rationale
            )

            # Primary rationale should score higher (has WCAG references, technical details, examples)
            assert primary_quality > secondary_quality
            assert (
                primary_quality > 0.5
            )  # Should score well due to multiple quality indicators

            # Resolution should favor higher quality evidence
            resolutions = self.consensus_engine.resolve_conflicts(conflicts)
            if (
                conflict.plan_name in resolutions
                and conflict.criterion in resolutions[conflict.plan_name]
            ):
                resolved_score = resolutions[conflict.plan_name][conflict.criterion]
                # Should be closer to the high-evidence score (8.0) than the low-evidence score (6.0)
                assert abs(resolved_score - 8.0) < abs(resolved_score - 6.0)
