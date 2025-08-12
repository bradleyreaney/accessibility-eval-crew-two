"""
Test suite for evaluation task management system.
Following TDD approach for Phase 3 workflow implementation.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from crewai import Agent, Task

from src.agents.judge_agent import PrimaryJudgeAgent, SecondaryJudgeAgent
from src.models.evaluation_models import DocumentContent, EvaluationInput
from src.tasks.evaluation_tasks import EvaluationTaskManager


class TestEvaluationTaskManager:
    """Test cases for EvaluationTaskManager class."""

    @pytest.fixture
    def mock_task(self):
        """Mock CrewAI Task for testing."""
        task = Mock(spec=Task)
        task.description = ""
        task.expected_output = ""
        task.output_file = ""
        task.agent = None
        return task

    @pytest.fixture
    def mock_primary_judge(self):
        """Mock primary judge agent."""
        judge = Mock(spec=PrimaryJudgeAgent)
        judge.agent = Mock(spec=Agent)
        return judge

    @pytest.fixture
    def mock_secondary_judge(self):
        """Mock secondary judge agent."""
        judge = Mock(spec=SecondaryJudgeAgent)
        judge.agent = Mock(spec=Agent)
        return judge

    @pytest.fixture
    def task_manager(self, mock_primary_judge, mock_secondary_judge):
        """Create EvaluationTaskManager instance for testing."""
        return EvaluationTaskManager(mock_primary_judge, mock_secondary_judge)

    @pytest.fixture
    def sample_evaluation_input(self):
        """Sample evaluation input for testing."""
        audit_report = DocumentContent(
            title="Test Accessibility Audit",
            content="This is a test audit report with various accessibility issues...",
            page_count=5,
            metadata={"author": "Test Auditor", "date": "2024-01-01"},
        )

        remediation_plans = {
            "PlanA": DocumentContent(
                title="Remediation Plan A",
                content="This is a comprehensive plan for accessibility remediation...",
                page_count=10,
                metadata={"plan_type": "comprehensive"},
            ),
            "PlanB": DocumentContent(
                title="Remediation Plan B",
                content="This is an alternative approach to accessibility fixes...",
                page_count=8,
                metadata={"plan_type": "iterative"},
            ),
        }

        return EvaluationInput(
            audit_report=audit_report, remediation_plans=remediation_plans
        )

    def test_task_manager_initialization(
        self, mock_primary_judge, mock_secondary_judge
    ):
        """Test that EvaluationTaskManager initializes correctly."""
        manager = EvaluationTaskManager(mock_primary_judge, mock_secondary_judge)

        assert manager.primary_judge == mock_primary_judge
        assert manager.secondary_judge == mock_secondary_judge

    @patch("src.tasks.evaluation_tasks.Task")
    def test_create_primary_evaluation_task_structure(
        self, mock_task_class, task_manager
    ):
        """Test that primary evaluation task is created with correct structure."""
        plan_name = "PlanA"
        plan_content = "Test plan content for evaluation..."
        audit_context = "Original audit report content..."

        # Setup mock to return our mock task
        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_primary_evaluation_task(
            plan_name, plan_content, audit_context
        )

        # Verify Task was called with correct parameters
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args[1]  # Get keyword arguments

        # Test task properties from the call
        assert plan_name in call_args["description"]
        assert "Strategic Prioritization (40%)" in call_args["description"]
        assert "Technical Specificity (30%)" in call_args["description"]
        assert "Comprehensiveness (20%)" in call_args["description"]
        assert "Long-term Vision (10%)" in call_args["description"]
        assert call_args["agent"] == task_manager.primary_judge.agent
        assert (
            call_args["output_file"]
            == f"output/evaluations/{plan_name}_primary_evaluation.md"
        )

    @patch("src.tasks.evaluation_tasks.Task")
    def test_create_primary_evaluation_task_content_truncation(
        self, mock_task_class, task_manager
    ):
        """Test that long content is properly truncated in task description."""
        plan_name = "PlanA"
        plan_content = "A" * 1000  # Very long content
        audit_context = "B" * 1000  # Very long content

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_primary_evaluation_task(
            plan_name, plan_content, audit_context
        )

        # Get the description from the call
        call_args = mock_task_class.call_args[1]
        description = call_args["description"]

        # Content should be truncated to ~500 chars plus "..."
        plan_line = next(
            line for line in description.split("\n") if "Plan Content:" in line
        )
        audit_line = next(
            line for line in description.split("\n") if "Original Audit:" in line
        )

        assert len(plan_line) < 600
        assert len(audit_line) < 600
        assert "..." in plan_line
        assert "..." in audit_line

    @patch("src.tasks.evaluation_tasks.Task")
    def test_create_secondary_evaluation_task_structure(
        self, mock_task_class, task_manager
    ):
        """Test that secondary evaluation task is created with correct structure."""
        plan_name = "PlanB"
        plan_content = "Test plan content for secondary evaluation..."
        audit_context = "Original audit report content..."

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_secondary_evaluation_task(
            plan_name, plan_content, audit_context
        )

        # Verify Task was called correctly
        mock_task_class.assert_called_once()
        call_args = mock_task_class.call_args[1]

        # Test task properties
        assert plan_name in call_args["description"]
        assert "independent secondary evaluation" in call_args["description"]
        assert "Cross-Validation Notes" in call_args["expected_output"]
        assert call_args["agent"] == task_manager.secondary_judge.agent
        assert (
            call_args["output_file"]
            == f"output/evaluations/{plan_name}_secondary_evaluation.md"
        )

    @patch("src.tasks.evaluation_tasks.Task")
    def test_create_secondary_evaluation_task_with_primary_result(
        self, mock_task_class, task_manager
    ):
        """Test secondary task with primary result for cross-validation."""
        plan_name = "PlanC"
        plan_content = "Test plan content..."
        audit_context = "Test audit context..."
        primary_result = "Primary judge found strategic score of 8.5..."

        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_secondary_evaluation_task(
            plan_name, plan_content, audit_context, primary_result
        )

        # Get call arguments
        call_args = mock_task_class.call_args[1]

        # Should include cross-validation section
        assert "CROSS-VALIDATION NOTE:" in call_args["description"]
        assert "Primary Judge Result Summary:" in call_args["description"]
        assert primary_result[:300] in call_args["description"]

    @patch("src.tasks.evaluation_tasks.Task")
    def test_create_batch_evaluation_tasks(
        self, mock_task_class, task_manager, sample_evaluation_input
    ):
        """Test batch creation of evaluation tasks for all plans."""
        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        tasks = task_manager.create_batch_evaluation_tasks(sample_evaluation_input)

        # Should create 2 tasks per plan (primary + secondary)
        expected_task_count = len(sample_evaluation_input.remediation_plans) * 2
        assert len(tasks) == expected_task_count

        # Verify correct number of Task calls
        assert mock_task_class.call_count == expected_task_count

    @patch("src.tasks.evaluation_tasks.Task")
    def test_evaluation_task_expected_output_format(
        self, mock_task_class, task_manager
    ):
        """Test that evaluation tasks have properly formatted expected output."""
        plan_name = "TestPlan"
        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        task_manager.create_primary_evaluation_task(plan_name, "content", "audit")

        call_args = mock_task_class.call_args[1]
        expected_output = call_args["expected_output"]

        expected_sections = [
            "## Primary Evaluation:",
            "### Strategic Prioritization (40%)",
            "### Technical Specificity (30%)",
            "### Comprehensiveness (20%)",
            "### Long-term Vision (10%)",
            "### Overall Assessment",
            "**Overall Score:",
            "**Key Strengths:**",
            "**Key Weaknesses:**",
            "**Rationale:**",
        ]

        for section in expected_sections:
            assert section in expected_output

    def test_task_manager_handles_empty_plans(self, task_manager):
        """Test that task manager handles empty remediation plans gracefully."""
        empty_input = EvaluationInput(
            audit_report=DocumentContent(
                title="Test Audit", content="Test content", page_count=1, metadata={}
            ),
            remediation_plans={},
        )

        tasks = task_manager.create_batch_evaluation_tasks(empty_input)
        assert len(tasks) == 0

    @patch("src.tasks.evaluation_tasks.Task")
    def test_task_manager_validates_input_types(
        self, mock_task_class, mock_primary_judge, mock_secondary_judge
    ):
        """Test that task manager validates input parameter types."""
        manager = EvaluationTaskManager(mock_primary_judge, mock_secondary_judge)
        mock_task_instance = Mock(spec=Task)
        mock_task_class.return_value = mock_task_instance

        # Should handle string inputs correctly
        manager.create_primary_evaluation_task("PlanA", "content", "audit")
        assert mock_task_class.called

        # Reset mock for second call
        mock_task_class.reset_mock()

        # Should handle None values gracefully
        manager.create_secondary_evaluation_task("PlanB", "content", "audit", None)
        call_args = mock_task_class.call_args[1]
        assert "CROSS-VALIDATION NOTE:" not in call_args["description"]


class TestEvaluationTaskIntegration:
    """Integration tests for evaluation tasks with real agent objects."""

    @pytest.fixture
    def real_evaluation_input(self):
        """Create realistic evaluation input for integration testing."""
        # This would typically use actual PDF content in real scenario
        return EvaluationInput(
            audit_report=DocumentContent(
                title="ACME Website Accessibility Audit",
                content="""
                This accessibility audit identifies several critical issues:
                1. Missing alt text on product images
                2. Insufficient color contrast in navigation
                3. Keyboard navigation issues in dropdown menus
                4. Missing ARIA labels on form controls
                """,
                page_count=15,
                metadata={"auditor": "AccessibilityPro", "wcag_version": "2.1"},
            ),
            remediation_plans={
                "PlanA": DocumentContent(
                    title="Comprehensive Accessibility Remediation",
                    content="""
                    Phase 1: Critical Issues (Weeks 1-4)
                    - Implement alt text for all product images using descriptive text
                    - Update color scheme to meet WCAG AA contrast requirements

                    Phase 2: Navigation Improvements (Weeks 5-8)
                    - Redesign dropdown menus with proper keyboard support
                    - Add ARIA labels to all form controls
                    """,
                    page_count=12,
                    metadata={"approach": "phased", "timeline": "8 weeks"},
                )
            },
        )

    @patch("src.agents.judge_agent.PrimaryJudgeAgent")
    @patch("src.agents.judge_agent.SecondaryJudgeAgent")
    def test_integration_with_mock_agents(
        self, mock_secondary_class, mock_primary_class, real_evaluation_input
    ):
        """Test task creation with mocked agent classes."""
        # Setup mocks
        mock_primary = mock_primary_class.return_value
        mock_secondary = mock_secondary_class.return_value
        mock_primary.agent = Mock(spec=Agent)
        mock_secondary.agent = Mock(spec=Agent)

        # Create task manager and generate tasks
        with patch("src.tasks.evaluation_tasks.Task") as mock_task_class:
            mock_task_instance = Mock(spec=Task)
            mock_task_class.return_value = mock_task_instance

            manager = EvaluationTaskManager(mock_primary, mock_secondary)
            tasks = manager.create_batch_evaluation_tasks(real_evaluation_input)

            # Verify realistic task creation
            assert len(tasks) == 2  # One plan, two tasks (primary + secondary)

            # Check that task descriptions contain actual content from input
            call_args_list = mock_task_class.call_args_list

            # First call should be primary task
            primary_description = call_args_list[0][1]["description"]
            assert (
                "Missing alt text" in primary_description
            )  # This content appears in the plan
            assert "product images" in primary_description
            assert "PlanA" in primary_description
