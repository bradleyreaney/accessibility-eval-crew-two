"""
Test-Driven Development Tests for Advanced Consensus Engine
Tests for Phase 5: Advanced Features & Optimization - Consensus Mechanisms

Following TDD approach:
1. Write failing tests first
2. Implement minimal code to pass tests
3. Refactor and improve
"""

from typing import Dict, List
from unittest.mock import Mock, patch

import numpy as np
import pytest

from src.consensus.advanced_consensus import (
    AdvancedConsensusEngine,
    ConflictAnalysis,
    ConflictSeverity,
    MetaEvaluationSystem,
)
from src.models.evaluation_models import JudgmentScore, PlanEvaluation


class TestConflictSeverity:
    """Test ConflictSeverity enum values"""

    def test_conflict_severity_values(self):
        """Test that ConflictSeverity has expected values"""
        assert ConflictSeverity.LOW.value == "low"
        assert ConflictSeverity.MEDIUM.value == "medium"
        assert ConflictSeverity.HIGH.value == "high"
        assert ConflictSeverity.CRITICAL.value == "critical"


class TestConflictAnalysis:
    """Test ConflictAnalysis dataclass"""

    def test_conflict_analysis_creation(self):
        """Test creating ConflictAnalysis instance"""
        conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Strategic Prioritization",
            primary_score=7.5,
            secondary_score=6.0,
            difference=1.5,
            severity=ConflictSeverity.MEDIUM,
            primary_rationale="Good strategic approach",
            secondary_rationale="Lacks strategic depth",
            confidence_delta=0.2,
        )

        assert conflict.plan_name == "Plan A"
        assert conflict.criterion == "Strategic Prioritization"
        assert conflict.primary_score == 7.5
        assert conflict.secondary_score == 6.0
        assert conflict.difference == 1.5
        assert conflict.severity == ConflictSeverity.MEDIUM
        assert conflict.confidence_delta == 0.2


class TestAdvancedConsensusEngine:
    """Test Advanced Consensus Engine functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = AdvancedConsensusEngine()

        # Create mock evaluations
        self.mock_evaluations = [Mock(spec=PlanEvaluation), Mock(spec=PlanEvaluation)]

        # Configure mock evaluations
        self.mock_evaluations[0].plan_name = "Plan A"
        self.mock_evaluations[0].judge_id = "gemini"
        self.mock_evaluations[0].judgment_scores = [
            Mock(
                criterion="Strategic Prioritization",
                score=7.5,
                rationale="Good strategy",
            ),
            Mock(
                criterion="Technical Specificity",
                score=6.0,
                rationale="Adequate technical detail",
            ),
        ]

        self.mock_evaluations[1].plan_name = "Plan A"
        self.mock_evaluations[1].judge_id = "gpt4"
        self.mock_evaluations[1].judgment_scores = [
            Mock(
                criterion="Strategic Prioritization",
                score=6.0,
                rationale="Lacks strategic depth",
            ),
            Mock(
                criterion="Technical Specificity",
                score=7.0,
                rationale="Strong technical approach",
            ),
        ]

    def test_engine_initialization(self):
        """Test consensus engine initializes correctly"""
        engine = AdvancedConsensusEngine()

        assert engine is not None
        assert hasattr(engine, "resolution_strategies")
        assert hasattr(engine, "judge_reliability_scores")

        # Check resolution strategies are mapped correctly
        assert ConflictSeverity.LOW in engine.resolution_strategies
        assert ConflictSeverity.MEDIUM in engine.resolution_strategies
        assert ConflictSeverity.HIGH in engine.resolution_strategies
        assert ConflictSeverity.CRITICAL in engine.resolution_strategies

    def test_judge_reliability_scores(self):
        """Test judge reliability scores are configured"""
        engine = AdvancedConsensusEngine()

        assert "gemini" in engine.judge_reliability_scores
        assert "gpt4" in engine.judge_reliability_scores

        gemini_scores = engine.judge_reliability_scores["gemini"]
        assert "accuracy" in gemini_scores
        assert "consistency" in gemini_scores
        assert "bias_factor" in gemini_scores

        # Test scores are in valid ranges
        assert 0 <= gemini_scores["accuracy"] <= 1
        assert 0 <= gemini_scores["consistency"] <= 1
        assert 0 <= gemini_scores["bias_factor"] <= 1

    def test_analyze_conflicts_identifies_conflicts(self):
        """Test that analyze_conflicts identifies judge disagreements"""
        conflicts = self.engine.analyze_conflicts(self.mock_evaluations)

        assert isinstance(conflicts, list)
        # Should identify conflicts for both criteria
        assert len(conflicts) >= 1

        # Check conflict structure
        if conflicts:
            conflict = conflicts[0]
            assert hasattr(conflict, "plan_name")
            assert hasattr(conflict, "criterion")
            assert hasattr(conflict, "severity")

    def test_resolve_conflicts_returns_scores(self):
        """Test that resolve_conflicts returns resolved scores"""
        # Create sample conflicts
        conflicts = [
            ConflictAnalysis(
                plan_name="Plan A",
                criterion="Strategic Prioritization",
                primary_score=7.5,
                secondary_score=6.0,
                difference=1.5,
                severity=ConflictSeverity.MEDIUM,
                primary_rationale="Good strategy",
                secondary_rationale="Lacks depth",
                confidence_delta=0.1,
            )
        ]

        resolved_scores = self.engine.resolve_conflicts(conflicts)

        assert isinstance(resolved_scores, dict)
        assert "Plan A" in resolved_scores
        assert "Strategic Prioritization" in resolved_scores["Plan A"]

        resolved_score = resolved_scores["Plan A"]["Strategic Prioritization"]
        assert isinstance(resolved_score, (int, float))
        assert 0 <= resolved_score <= 10

    def test_weighted_average_resolution(self):
        """Test weighted average resolution for low severity conflicts"""
        conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Strategic Prioritization",
            primary_score=7.0,
            secondary_score=6.0,
            difference=1.0,
            severity=ConflictSeverity.LOW,
            primary_rationale="Good",
            secondary_rationale="Average",
            confidence_delta=0.0,
        )

        resolved_score = self.engine._weighted_average_resolution(conflict)

        # Should be between the two scores
        assert 6.0 <= resolved_score <= 7.0
        assert isinstance(resolved_score, float)

    def test_evidence_based_resolution(self):
        """Test evidence-based resolution for medium severity conflicts"""
        conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Strategic Prioritization",
            primary_score=8.0,
            secondary_score=5.0,
            difference=3.0,
            severity=ConflictSeverity.MEDIUM,
            primary_rationale="Detailed analysis with specific examples and WCAG references",
            secondary_rationale="Brief assessment",
            confidence_delta=0.1,
        )

        resolved_score = self.engine._evidence_based_resolution(conflict)

        assert isinstance(resolved_score, float)
        assert 0 <= resolved_score <= 10

    def test_score_evidence_quality(self):
        """Test evidence quality scoring functionality"""
        # High quality rationale
        high_quality = "This plan provides specific examples of WCAG implementation with detailed code and technical considerations for user accessibility"

        # Low quality rationale
        low_quality = "This is okay"

        high_score = self.engine._score_evidence_quality(high_quality)
        low_score = self.engine._score_evidence_quality(low_quality)

        assert high_score > low_score
        assert 0 <= high_score <= 1
        assert 0 <= low_score <= 1

    def test_evidence_quality_indicators(self):
        """Test specific evidence quality indicators"""
        # Test WCAG references
        wcag_rationale = "This follows WCAG level AA guidelines"
        wcag_score = self.engine._score_evidence_quality(wcag_rationale)
        assert wcag_score > 0

        # Test technical details
        technical_rationale = "Implementation requires CSS and ARIA attributes"
        technical_score = self.engine._score_evidence_quality(technical_rationale)
        assert technical_score > 0

        # Test specific examples
        examples_rationale = "For example, the navigation menu specifically addresses keyboard accessibility"
        examples_score = self.engine._score_evidence_quality(examples_rationale)
        assert examples_score > 0

    def test_expert_mediation_resolution(self):
        """Test expert mediation for high severity conflicts"""
        conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Strategic Prioritization",
            primary_score=9.0,
            secondary_score=4.0,
            difference=5.0,
            severity=ConflictSeverity.HIGH,
            primary_rationale="Excellent strategic approach",
            secondary_rationale="Poor strategy",
            confidence_delta=0.3,
        )

        resolved_score = self.engine._expert_mediation_resolution(conflict)

        assert isinstance(resolved_score, float)
        assert 0 <= resolved_score <= 10

    def test_human_escalation_resolution(self):
        """Test human escalation for critical conflicts"""
        conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Strategic Prioritization",
            primary_score=9.0,
            secondary_score=2.0,
            difference=7.0,
            severity=ConflictSeverity.CRITICAL,
            primary_rationale="Excellent",
            secondary_rationale="Poor",
            confidence_delta=0.5,
        )

        result = self.engine._human_escalation_resolution(conflict)

        # Should return None to indicate human review required
        assert result is None

    def test_generate_consensus_report(self):
        """Test generation of consensus building report"""
        conflicts = [
            ConflictAnalysis(
                plan_name="Plan A",
                criterion="Strategic Prioritization",
                primary_score=7.0,
                secondary_score=6.0,
                difference=1.0,
                severity=ConflictSeverity.LOW,
                primary_rationale="Good",
                secondary_rationale="Average",
                confidence_delta=0.0,
            ),
            ConflictAnalysis(
                plan_name="Plan B",
                criterion="Technical Specificity",
                primary_score=8.0,
                secondary_score=3.0,
                difference=5.0,
                severity=ConflictSeverity.CRITICAL,
                primary_rationale="Excellent",
                secondary_rationale="Poor",
                confidence_delta=0.4,
            ),
        ]

        resolutions = {"Plan A": {"Strategic Prioritization": 6.5}}

        report = self.engine.generate_consensus_report(conflicts, resolutions)

        assert isinstance(report, str)
        assert "Executive Summary" in report
        assert "Total Conflicts Identified: 2" in report
        assert "Conflict Severity Breakdown" in report
        assert "Resolution Strategies Applied" in report


class TestMetaEvaluationSystem:
    """Test Meta-Evaluation System functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.meta_system = MetaEvaluationSystem()

    def test_meta_system_initialization(self):
        """Test meta-evaluation system initializes correctly"""
        system = MetaEvaluationSystem()

        assert system is not None
        assert hasattr(system, "evaluation_history")
        assert hasattr(system, "performance_metrics")
        assert isinstance(system.evaluation_history, list)
        assert isinstance(system.performance_metrics, dict)

    def test_track_judge_performance(self):
        """Test tracking judge performance over time"""
        session_data = {
            "session_id": "test_session_1",
            "timestamp": "2025-08-14",
            "judge_evaluations": {
                "gemini": {"accuracy": 0.85, "consistency": 0.80},
                "gpt4": {"accuracy": 0.88, "consistency": 0.82},
            },
        }

        initial_count = len(self.meta_system.evaluation_history)
        self.meta_system.track_judge_performance(session_data)

        assert len(self.meta_system.evaluation_history) == initial_count + 1
        assert self.meta_system.evaluation_history[-1] == session_data

    def test_identify_bias_patterns(self):
        """Test identification of systematic bias patterns"""
        # Add some evaluation history
        self.meta_system.evaluation_history = [
            {"judge_scores": {"gemini": [7, 8, 7, 8], "gpt4": [6, 5, 6, 5]}}
        ]

        bias_patterns = self.meta_system.identify_bias_patterns()

        assert isinstance(bias_patterns, dict)
        assert "gemini" in bias_patterns
        assert "gpt4" in bias_patterns
        assert isinstance(bias_patterns["gemini"], list)
        assert isinstance(bias_patterns["gpt4"], list)

    def test_generate_calibration_recommendations(self):
        """Test generation of calibration recommendations"""
        recommendations = self.meta_system.generate_calibration_recommendations()

        assert isinstance(recommendations, list)
        # Should return recommendations even with empty history
        assert len(recommendations) >= 0


class TestAdvancedConsensusIntegration:
    """Integration tests for consensus mechanisms"""

    def test_end_to_end_consensus_workflow(self):
        """Test complete consensus workflow from evaluation to resolution"""
        engine = AdvancedConsensusEngine()

        # Create realistic evaluation data
        evaluations = [
            Mock(
                plan_name="Plan A",
                judge_id="gemini",
                judgment_scores=[
                    Mock(
                        criterion="Strategic Prioritization",
                        score=7.5,
                        rationale="Strong strategic focus",
                    ),
                    Mock(
                        criterion="Technical Specificity",
                        score=6.0,
                        rationale="Adequate technical detail",
                    ),
                ],
            ),
            Mock(
                plan_name="Plan A",
                judge_id="gpt4",
                judgment_scores=[
                    Mock(
                        criterion="Strategic Prioritization",
                        score=6.0,
                        rationale="Lacks strategic depth",
                    ),
                    Mock(
                        criterion="Technical Specificity",
                        score=8.0,
                        rationale="Excellent technical approach",
                    ),
                ],
            ),
        ]

        # Analyze conflicts
        conflicts = engine.analyze_conflicts(evaluations)

        # Resolve conflicts
        if conflicts:
            resolutions = engine.resolve_conflicts(conflicts)

            # Generate report
            report = engine.generate_consensus_report(conflicts, resolutions)

            assert isinstance(resolutions, dict)
            assert isinstance(report, str)
            assert len(report) > 0

    def test_severity_classification(self):
        """Test that conflicts are properly classified by severity"""
        engine = AdvancedConsensusEngine()

        # Test low severity (< 0.5 difference)
        low_conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Test",
            primary_score=7.0,
            secondary_score=6.6,
            difference=0.4,
            severity=ConflictSeverity.LOW,
            primary_rationale="",
            secondary_rationale="",
            confidence_delta=0.0,
        )

        # Test medium severity (0.5-1.0 difference)
        medium_conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Test",
            primary_score=7.0,
            secondary_score=6.0,
            difference=1.0,
            severity=ConflictSeverity.MEDIUM,
            primary_rationale="",
            secondary_rationale="",
            confidence_delta=0.0,
        )

        # Test high severity (1.0-2.0 difference)
        high_conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Test",
            primary_score=8.0,
            secondary_score=6.0,
            difference=2.0,
            severity=ConflictSeverity.HIGH,
            primary_rationale="",
            secondary_rationale="",
            confidence_delta=0.0,
        )

        # Test critical severity (> 2.0 difference)
        critical_conflict = ConflictAnalysis(
            plan_name="Plan A",
            criterion="Test",
            primary_score=9.0,
            secondary_score=4.0,
            difference=5.0,
            severity=ConflictSeverity.CRITICAL,
            primary_rationale="",
            secondary_rationale="",
            confidence_delta=0.0,
        )

        # Test resolution strategies are applied correctly
        low_resolved = engine.resolve_conflicts([low_conflict])
        medium_resolved = engine.resolve_conflicts([medium_conflict])
        high_resolved = engine.resolve_conflicts([high_conflict])
        critical_resolved = engine.resolve_conflicts([critical_conflict])

        assert isinstance(low_resolved, dict)
        assert isinstance(medium_resolved, dict)
        assert isinstance(high_resolved, dict)
        assert isinstance(critical_resolved, dict)
