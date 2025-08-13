"""
Test suite for comparison task management system.
Following TDD approach for Phase 3 workflow implementation.
"""

from unittest.mock import Mock, patch

import pytest
from crewai import Agent, Task

from src.agents.analysis_agent import AnalysisAgent
from src.models.evaluation_models import JudgmentScore, PlanEvaluation
from src.tasks.comparison_tasks import ComparisonTaskManager


class TestComparisonTaskManager:
    """Test cases for ComparisonTaskManager class."""

    @pytest.fixture
    def mock_comparison_agent(self):
        """Mock comparison agent."""
        agent = Mock(spec=AnalysisAgent)
        agent.agent = Mock(spec=Agent)
        return agent

    @pytest.fixture
    def task_manager(self, mock_comparison_agent):
        """Create ComparisonTaskManager instance for testing."""
        return ComparisonTaskManager(mock_comparison_agent)

    @pytest.fixture
    def sample_plan_evaluations(self):
        """Sample plan evaluations for testing."""
        return [
            PlanEvaluation(
                plan_name="PlanA",
                judge_id="primary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=8.0,
                        rationale="Good strategy",
                        confidence=0.9,
                    ),
                    JudgmentScore(
                        criterion="technical",
                        score=9.0,
                        rationale="Strong technical approach",
                        confidence=0.8,
                    ),
                ],
                overall_score=8.5,
                detailed_analysis="Well-structured approach with good prioritization",
                pros=["Strong prioritization", "Clear implementation"],
                cons=["Limited accessibility details", "Missing testing"],
            ),
            PlanEvaluation(
                plan_name="PlanA",
                judge_id="secondary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=7.0,
                        rationale="Decent strategy",
                        confidence=0.8,
                    ),
                    JudgmentScore(
                        criterion="technical",
                        score=8.0,
                        rationale="Good technical details",
                        confidence=0.9,
                    ),
                ],
                overall_score=7.5,
                detailed_analysis="Solid but conservative approach",
                pros=["Good technical details", "Realistic timeline"],
                cons=["Lacks innovation", "Insufficient user testing"],
            ),
            PlanEvaluation(
                plan_name="PlanB",
                judge_id="primary",
                scores=[
                    JudgmentScore(
                        criterion="strategic",
                        score=6.5,
                        rationale="Some strategy issues",
                        confidence=0.7,
                    ),
                    JudgmentScore(
                        criterion="technical",
                        score=7.5,
                        rationale="Innovative but complex",
                        confidence=0.8,
                    ),
                ],
                overall_score=7.0,
                detailed_analysis="Creative but resource-intensive solution",
                pros=["Innovative approach", "User-focused"],
                cons=["Complex implementation", "High resource needs"],
            ),
        ]

    def test_task_manager_initialization(self, mock_comparison_agent):
        """Test that ComparisonTaskManager initializes correctly."""
        manager = ComparisonTaskManager(mock_comparison_agent)
        assert manager.comparison_agent == mock_comparison_agent

    @patch("src.tasks.comparison_tasks.Task")
    def test_create_cross_plan_comparison_task_structure(
        self, mock_task_class, task_manager, sample_plan_evaluations
    ):
        """Test that cross-plan comparison task is created with correct structure."""
        audit_context = "Original audit report content..."

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_cross_plan_comparison_task(
            sample_plan_evaluations, audit_context
        )

        # Verify Task was called with correct parameters
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args[1]

        # Test task properties from the call
        assert "cross-plan comparison" in call_args["description"].lower()
        assert "Quantitative Analysis" in call_args["description"]
        assert "Qualitative Analysis" in call_args["description"]
        assert "Gap Analysis" in call_args["description"]
        assert "Synthesis Preparation" in call_args["description"]
        assert call_args["agent"] == task_manager.comparison_agent.agent
        assert "output/comparisons/cross_plan_analysis.md" in call_args["output_file"]

    @patch("src.tasks.comparison_tasks.Task")
    def test_create_cross_plan_comparison_includes_evaluation_summary(
        self, mock_task_class, task_manager, sample_plan_evaluations
    ):
        """Test that comparison task includes evaluation summary."""
        audit_context = "Test audit context"

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_cross_plan_comparison_task(
            sample_plan_evaluations, audit_context
        )

        call_args = mock_task_class.call_args[1]
        description = call_args["description"]

        # Should include plan names and scores
        assert "PlanA" in description
        assert "PlanB" in description
        assert "8.5" in description  # PlanA primary score
        assert "7.5" in description  # PlanA secondary score

    def test_create_evaluation_summary_format(
        self, task_manager, sample_plan_evaluations
    ):
        """Test the evaluation summary formatting."""
        summary = task_manager._create_evaluation_summary(sample_plan_evaluations)

        # Should include all plans and their evaluations
        assert "PlanA" in summary
        assert "PlanB" in summary
        assert "PRIMARY Judge" in summary
        assert "SECONDARY Judge" in summary
        assert "8.5" in summary  # PlanA primary score
        assert "7.5" in summary  # PlanA secondary score

    @patch("src.tasks.comparison_tasks.Task")
    def test_comparison_task_expected_output_format(
        self, mock_task_class, task_manager, sample_plan_evaluations
    ):
        """Test that comparison tasks have properly formatted expected output."""
        audit_context = "Test audit"

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_cross_plan_comparison_task(
            sample_plan_evaluations, audit_context
        )

        call_args = mock_task_class.call_args[1]
        expected_output = call_args["expected_output"]

        expected_sections = [
            "## Comprehensive Plan Comparison Analysis",
            "### Executive Summary",
            "### Quantitative Comparison Matrix",
            "### Qualitative Analysis by Plan",
            "### Cross-Plan Trade-off Analysis",
            "### Critical Gap Analysis",
            "### Synthesis Recommendations",
            "### Consensus Assessment",
        ]

        for section in expected_sections:
            assert section in expected_output
