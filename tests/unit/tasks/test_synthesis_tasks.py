"""
Unit tests for synthesis task management.

This module contains comprehensive tests for the SynthesisTaskManager class,
ensuring proper task creation, content formatting, and integration with
the AnalysisAgent.
"""

from unittest.mock import Mock, patch

import pytest
from crewai import Task

from src.models.evaluation_models import JudgmentScore, PlanEvaluation
from src.tasks.synthesis_tasks import SynthesisTaskManager


class TestSynthesisTaskManager:
    """Test suite for SynthesisTaskManager functionality."""

    @pytest.fixture
    def mock_synthesis_agent(self):
        """Create mock synthesis agent for testing."""
        mock_agent = Mock()
        mock_agent.agent = Mock()
        return mock_agent

    @pytest.fixture
    def task_manager(self, mock_synthesis_agent):
        """Create SynthesisTaskManager instance for testing."""
        return SynthesisTaskManager(mock_synthesis_agent)

    @pytest.fixture
    def sample_plan_evaluations(self):
        """Create sample plan evaluations for testing."""
        return [
            PlanEvaluation(
                plan_name="PlanA",
                judge_id="primary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=9.0,
                        rationale="Excellent prioritization",
                        confidence=0.9,
                    ),
                    JudgmentScore(
                        criterion="technical",
                        score=8.0,
                        rationale="Clear technical guidance",
                        confidence=0.8,
                    ),
                    JudgmentScore(
                        criterion="comprehensive",
                        score=8.5,
                        rationale="Good coverage",
                        confidence=0.85,
                    ),
                    JudgmentScore(
                        criterion="long_term",
                        score=7.0,
                        rationale="Limited vision",
                        confidence=0.7,
                    ),
                ],
                overall_score=8.5,
                detailed_analysis="Strong technical approach with good prioritization",
                pros=["Excellent prioritization", "Clear technical guidance"],
                cons=["Missing automation", "Limited long-term vision"],
            ),
            PlanEvaluation(
                plan_name="PlanA",
                judge_id="secondary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=8.5,
                        rationale="Good implementation details",
                        confidence=0.85,
                    ),
                    JudgmentScore(
                        criterion="technical",
                        score=8.5,
                        rationale="Realistic timeline",
                        confidence=0.8,
                    ),
                    JudgmentScore(
                        criterion="comprehensive",
                        score=8.0,
                        rationale="Adequate coverage",
                        confidence=0.8,
                    ),
                    JudgmentScore(
                        criterion="long_term",
                        score=7.5,
                        rationale="Some long-term thinking",
                        confidence=0.75,
                    ),
                ],
                overall_score=8.2,
                detailed_analysis="Well-structured plan with minor complexity concerns",
                pros=["Good implementation details", "Realistic timeline"],
                cons=["Complex dependencies", "Resource intensive"],
            ),
            PlanEvaluation(
                plan_name="PlanB",
                judge_id="primary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=7.5,
                        rationale="Comprehensive coverage",
                        confidence=0.8,
                    ),
                    JudgmentScore(
                        criterion="technical",
                        score=7.0,
                        rationale="Strong monitoring",
                        confidence=0.7,
                    ),
                    JudgmentScore(
                        criterion="comprehensive",
                        score=9.0,
                        rationale="Very thorough",
                        confidence=0.9,
                    ),
                    JudgmentScore(
                        criterion="long_term",
                        score=8.0,
                        rationale="Good sustainability",
                        confidence=0.8,
                    ),
                ],
                overall_score=7.8,
                detailed_analysis="Thorough but potentially slow approach",
                pros=["Comprehensive coverage", "Strong monitoring"],
                cons=["Slow implementation", "High complexity"],
            ),
        ]

    def test_task_manager_initialization(self, mock_synthesis_agent):
        """Test that SynthesisTaskManager initializes correctly."""
        task_manager = SynthesisTaskManager(mock_synthesis_agent)

        assert task_manager.synthesis_agent == mock_synthesis_agent

    @patch("src.tasks.synthesis_tasks.Task")
    def test_create_optimal_plan_synthesis_task_structure(
        self, mock_task_class, task_manager, sample_plan_evaluations
    ):
        """Test that synthesis tasks are created with correct structure."""
        comparison_analysis = "Test comparison analysis results"
        audit_context = "Test audit context"

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_optimal_plan_synthesis_task(
            sample_plan_evaluations, comparison_analysis, audit_context
        )

        # Verify Task was called with correct parameters
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args[1]

        assert "description" in call_args
        assert "agent" in call_args
        assert "expected_output" in call_args
        assert call_args["agent"] == task_manager.synthesis_agent.agent

    @patch("src.tasks.synthesis_tasks.Task")
    def test_synthesis_task_includes_evaluation_context(
        self, mock_task_class, task_manager, sample_plan_evaluations
    ):
        """Test that synthesis task includes proper evaluation context."""
        comparison_analysis = "Comprehensive analysis of plans"
        audit_context = "Original audit findings"

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_optimal_plan_synthesis_task(
            sample_plan_evaluations, comparison_analysis, audit_context
        )

        call_args = mock_task_class.call_args[1]
        description = call_args["description"]

        # Should include plan count and context
        assert (
            f"{len(sample_plan_evaluations)} individual plan evaluations" in description
        )
        assert "PlanA" in description  # Should include plan names in context
        assert "PlanB" in description
        assert audit_context[:500] in description  # Should include audit context

    @patch("src.tasks.synthesis_tasks.Task")
    def test_synthesis_task_includes_plan_summaries(
        self, mock_task_class, task_manager, sample_plan_evaluations
    ):
        """Test that synthesis task includes formatted plan summaries."""
        comparison_analysis = "Analysis results"
        audit_context = "Audit context"

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_optimal_plan_synthesis_task(
            sample_plan_evaluations, comparison_analysis, audit_context
        )

        call_args = mock_task_class.call_args[1]
        description = call_args["description"]

        # Should include judge evaluations and scores
        assert "PRIMARY Judge" in description
        assert "SECONDARY Judge" in description
        assert "8.5" in description  # PlanA primary score
        assert "8.2" in description  # PlanA secondary score
        assert "7.8" in description  # PlanB primary score

        # Should include strengths and weaknesses
        assert "Excellent prioritization" in description
        assert "Missing automation" in description

    @patch("src.tasks.synthesis_tasks.Task")
    def test_synthesis_task_expected_output_format(
        self, mock_task_class, task_manager, sample_plan_evaluations
    ):
        """Test that synthesis tasks have properly formatted expected output."""
        comparison_analysis = "Test analysis"
        audit_context = "Test audit"

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_optimal_plan_synthesis_task(
            sample_plan_evaluations, comparison_analysis, audit_context
        )

        call_args = mock_task_class.call_args[1]
        expected_output = call_args["expected_output"]

        expected_sections = [
            "# Synthesized Optimal Accessibility Remediation Plan",
            "## Executive Summary",
            "## Strategic Foundation",
            "### Prioritization Framework",
            "## Technical Implementation Guide",
            "### Phase 1: Critical User Path Fixes",
            "### Phase 2: Structural Improvements",
            "### Phase 3: Enhancement and Optimization",
            "## POUR Principle Alignment",
            "## Implementation Strategy",
            "## Long-term Sustainability",
            "## Innovation and Best Practices",
            "## Implementation Timeline",
            "## Conclusion",
        ]

        for section in expected_sections:
            assert section in expected_output

    def test_create_synthesis_context_formatting(
        self, task_manager, sample_plan_evaluations
    ):
        """Test that synthesis context is properly formatted."""
        comparison_analysis = "Detailed comparison analysis with recommendations"

        context = task_manager._create_synthesis_context(
            sample_plan_evaluations, comparison_analysis
        )

        # Should include plan evaluation summary
        assert "PLAN EVALUATION SUMMARY" in context
        assert "**PlanA:**" in context
        assert "**PlanB:**" in context

        # Should include judge scores and details
        assert "PRIMARY Judge: 8.5/10" in context
        assert "SECONDARY Judge: 8.2/10" in context
        assert "PRIMARY Judge: 7.8/10" in context  # PlanB

        # Should include strengths and weaknesses
        assert "Strengths: Excellent prioritization" in context
        assert "Weaknesses: Missing automation" in context

        # Should include comparison analysis
        assert "COMPARISON ANALYSIS" in context
        assert comparison_analysis[:300] in context

    def test_create_synthesis_context_handles_empty_pros_cons(self, task_manager):
        """Test synthesis context handles evaluations with empty pros/cons."""
        evaluations = [
            PlanEvaluation(
                plan_name="TestPlan",
                judge_id="primary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=7.0,
                        rationale="Basic approach",
                        confidence=0.7,
                    )
                ],
                overall_score=7.0,
                detailed_analysis="Basic evaluation",
                pros=[],  # Empty pros
                cons=[],  # Empty cons
            )
        ]

        context = task_manager._create_synthesis_context(evaluations, "Analysis")

        # Should handle empty lists gracefully
        assert "TestPlan" in context
        assert "PRIMARY Judge: 7.0/10" in context
        # Should not crash or include empty strength/weakness lines
        assert "Strengths: " not in context
        assert "Weaknesses: " not in context

    def test_synthesis_task_objectives_comprehensive(
        self, task_manager, sample_plan_evaluations
    ):
        """Test that synthesis task includes comprehensive objectives."""
        with patch("src.tasks.synthesis_tasks.Task") as mock_task_class:
            mock_task_instance = Mock(spec=Task)
            mock_task_class.return_value = mock_task_instance

            task_manager.create_optimal_plan_synthesis_task(
                sample_plan_evaluations, "Analysis", "Audit"
            )

            call_args = mock_task_class.call_args[1]
            description = call_args["description"]

            # Should include all five synthesis objectives
            synthesis_objectives = [
                "Strategic Excellence",
                "Technical Superiority",
                "Complete Coverage",
                "Long-term Success",
                "Innovation Integration",
            ]

            for objective in synthesis_objectives:
                assert objective in description

            # Should include quality requirements
            assert "QUALITY REQUIREMENTS" in description
            assert "Build on proven strengths" in description
            assert "Address all identified weaknesses" in description


class TestSynthesisTaskIntegration:
    """Integration tests for synthesis task functionality."""

    def test_integration_with_mock_agent(self):
        """Test full integration with mocked AnalysisAgent."""
        # Create mock agent with proper structure
        mock_agent = Mock()
        mock_agent.agent = Mock()

        # Create task manager
        task_manager = SynthesisTaskManager(mock_agent)

        # Create sample evaluations
        evaluations = [
            PlanEvaluation(
                plan_name="TestPlan",
                judge_id="primary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=8.0,
                        rationale="Good approach",
                        confidence=0.8,
                    )
                ],
                overall_score=8.0,
                detailed_analysis="Solid plan",
                pros=["Good approach"],
                cons=["Minor issues"],
            )
        ]

        # Should be able to create task without errors
        with patch("src.tasks.synthesis_tasks.Task") as mock_task_class:
            mock_task_instance = Mock(spec=Task)
            mock_task_class.return_value = mock_task_instance

            result = task_manager.create_optimal_plan_synthesis_task(
                evaluations, "Analysis", "Audit context"
            )

            # Task should be created successfully
            mock_task_class.assert_called_once()
            assert result == mock_task_instance
