"""
Test suite for workflow controller functionality

Following TDD approach for Phase 4 implementation.
Tests for workflow management, status tracking, and coordination.
"""

from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.config.crew_config import AccessibilityEvaluationCrew
from src.models.evaluation_models import DocumentContent, EvaluationInput
from src.utils.workflow_controller import WorkflowController, WorkflowStatus


class TestWorkflowController:
    """Test suite for WorkflowController functionality"""

    @pytest.fixture
    def mock_crew(self):
        """Mock AccessibilityEvaluationCrew for testing"""
        mock_crew = Mock(spec=AccessibilityEvaluationCrew)
        mock_crew.execute_complete_evaluation = Mock(
            return_value={"status": "completed"}
        )
        mock_crew.execute_parallel_evaluation = Mock(
            return_value={"status": "completed"}
        )
        return mock_crew

    @pytest.fixture
    def sample_evaluation_input(self):
        """Sample evaluation input for testing"""
        audit_report = DocumentContent(
            title="Test Audit Report",
            content="Sample audit content...",
            page_count=3,
            metadata={"author": "Test Author"},
        )

        remediation_plans = {
            "PlanA": DocumentContent(
                title="Plan A",
                content="Plan A content...",
                page_count=2,
                metadata={"version": "1.0"},
            ),
            "PlanB": DocumentContent(
                title="Plan B",
                content="Plan B content...",
                page_count=2,
                metadata={"version": "1.0"},
            ),
        }

        return EvaluationInput(
            audit_report=audit_report, remediation_plans=remediation_plans
        )

    @pytest.fixture
    def workflow_controller(self, mock_crew):
        """WorkflowController instance for testing"""
        return WorkflowController(mock_crew)

    def test_initialization_with_crew(self, mock_crew):
        """Test that WorkflowController initializes correctly with crew"""
        # Act
        controller = WorkflowController(mock_crew)

        # Assert
        assert controller.crew == mock_crew
        assert controller.current_status.status == "idle"
        assert controller.current_status.progress == 0
        assert controller.current_status.phase == "initialization"

    def test_get_status_returns_current_status(self, workflow_controller):
        """Test that get_status returns the current workflow status"""
        # Act
        status = workflow_controller.get_status()

        # Assert
        assert isinstance(status, WorkflowStatus)
        assert status.status == "idle"
        assert status.progress == 0

    @pytest.mark.asyncio
    async def test_start_evaluation_updates_status_to_running(
        self, workflow_controller, sample_evaluation_input
    ):
        """Test that starting evaluation updates status to running"""
        # Act
        task = workflow_controller.start_evaluation(
            sample_evaluation_input, mode="sequential"
        )

        # Assert
        assert workflow_controller.current_status.status == "running"
        assert workflow_controller.current_status.progress == 10
        assert workflow_controller.current_status.phase == "individual_evaluations"

        # Clean up
        task.cancel()

    @pytest.mark.asyncio
    async def test_start_evaluation_calls_crew_execute_complete_evaluation(
        self, workflow_controller, sample_evaluation_input, mock_crew
    ):
        """Test that starting evaluation calls crew.execute_complete_evaluation"""
        # Arrange
        mock_crew.execute_complete_evaluation.return_value = {"status": "completed"}

        # Act
        task = workflow_controller.start_evaluation(
            sample_evaluation_input, mode="sequential"
        )
        await task

        # Assert
        mock_crew.execute_complete_evaluation.assert_called_once_with(
            sample_evaluation_input
        )

    @pytest.mark.asyncio
    async def test_successful_evaluation_updates_status_to_completed(
        self, workflow_controller, sample_evaluation_input, mock_crew
    ):
        """Test that successful evaluation updates status to completed"""
        # Arrange
        mock_results = {"synthesis_plan": {"title": "Optimal Plan"}}
        mock_crew.execute_complete_evaluation.return_value = mock_results

        # Act
        task = workflow_controller.start_evaluation(
            sample_evaluation_input, mode="sequential"
        )
        result = await task

        # Assert
        assert workflow_controller.current_status.status == "completed"
        assert workflow_controller.current_status.progress == 100
        assert result == mock_results

    @pytest.mark.asyncio
    async def test_failed_evaluation_updates_status_to_failed(
        self, workflow_controller, sample_evaluation_input, mock_crew
    ):
        """Test that failed evaluation updates status to failed"""
        # Arrange
        mock_crew.execute_complete_evaluation.side_effect = Exception("Test error")

        # Act
        task = workflow_controller.start_evaluation(
            sample_evaluation_input, mode="sequential"
        )

        with pytest.raises(Exception):
            await task

        # Assert
        assert workflow_controller.current_status.status == "failed"
        assert "Test error" in workflow_controller.current_status.error

    def test_stop_evaluation_cancels_running_task(self, workflow_controller):
        """Test that stop_evaluation cancels running task"""
        # Arrange
        mock_task = Mock()
        workflow_controller.current_task = mock_task
        workflow_controller.current_status.status = "running"

        # Act
        workflow_controller.stop_evaluation()

        # Assert
        mock_task.cancel.assert_called_once()
        assert workflow_controller.current_status.status == "cancelled"

    def test_stop_evaluation_when_not_running_does_nothing(self, workflow_controller):
        """Test that stop_evaluation does nothing when not running"""
        # Arrange
        workflow_controller.current_status.status = "idle"

        # Act
        workflow_controller.stop_evaluation()

        # Assert
        assert workflow_controller.current_status.status == "idle"

    def test_estimate_time_returns_reasonable_estimate(
        self, workflow_controller, sample_evaluation_input
    ):
        """Test that estimate_time returns reasonable time estimate"""
        # Act
        estimated_minutes = workflow_controller.estimate_time(sample_evaluation_input)

        # Assert
        assert isinstance(estimated_minutes, int)
        assert 1 <= estimated_minutes <= 30  # Reasonable range

    def test_estimate_time_scales_with_plan_count(
        self, workflow_controller, sample_evaluation_input
    ):
        """Test that estimated time scales with number of plans"""
        # Arrange
        # Add more plans to test scaling
        sample_evaluation_input.remediation_plans["PlanC"] = DocumentContent(
            title="Plan C",
            content="Plan C content...",
            page_count=3,
            metadata={"version": "1.0"},
        )

        # Act
        base_time = workflow_controller.estimate_time(
            EvaluationInput(
                audit_report=sample_evaluation_input.audit_report,
                remediation_plans={
                    "PlanA": sample_evaluation_input.remediation_plans["PlanA"]
                },
            )
        )
        scaled_time = workflow_controller.estimate_time(sample_evaluation_input)

        # Assert
        assert scaled_time > base_time  # More plans = more time


class TestWorkflowStatus:
    """Test suite for WorkflowStatus model"""

    def test_workflow_status_creation_with_defaults(self):
        """Test WorkflowStatus creation with default values"""
        # Act
        status = WorkflowStatus()

        # Assert
        assert status.status == "idle"
        assert status.progress == 0
        assert status.phase == "initialization"
        assert status.error is None

    def test_workflow_status_creation_with_values(self):
        """Test WorkflowStatus creation with custom values"""
        # Act
        status = WorkflowStatus(
            status="running", progress=50, phase="comparison", error="Test error"
        )

        # Assert
        assert status.status == "running"
        assert status.progress == 50
        assert status.phase == "comparison"
        assert status.error == "Test error"

    def test_workflow_status_progress_validation(self):
        """Test that progress is validated to be within 0-100 range"""
        # Valid cases
        WorkflowStatus(progress=0)
        WorkflowStatus(progress=50)
        WorkflowStatus(progress=100)

        # Invalid cases should raise validation error
        with pytest.raises(ValueError):
            WorkflowStatus(progress=-1)

        with pytest.raises(ValueError):
            WorkflowStatus(progress=101)


class TestWorkflowControllerCoverage:
    """Additional coverage tests for WorkflowController"""

    def test_workflow_controller_initialization_unittest(self):
        """Test workflow controller initialization with unittest style"""
        from unittest.mock import MagicMock

        mock_crew = MagicMock()
        controller = WorkflowController(mock_crew)

        assert controller is not None
        assert hasattr(controller, "get_status")
        assert controller.current_status is not None

    def test_workflow_status_validation_edge_cases(self):
        """Test workflow status validation edge cases"""
        # Test boundary values
        status_0 = WorkflowStatus(progress=0)
        assert status_0.progress == 0

        status_100 = WorkflowStatus(progress=100)
        assert status_100.progress == 100

        # Test that get_status returns correct type
        from unittest.mock import MagicMock

        mock_crew = MagicMock()
        controller = WorkflowController(mock_crew)

        status = controller.get_status()
        assert isinstance(status, WorkflowStatus)
        assert status.status == "idle"
        assert status.progress == 0

    def test_workflow_phases_enum_values(self):
        """Test workflow phases enum values"""
        from src.utils.workflow_controller import WorkflowPhase

        assert WorkflowPhase.INITIALIZATION == "initialization"
        assert WorkflowPhase.INDIVIDUAL_EVALUATIONS == "individual_evaluations"
        assert WorkflowPhase.CONSENSUS_BUILDING == "consensus_building"
        assert WorkflowPhase.PLAN_SYNTHESIS == "plan_synthesis"
        assert WorkflowPhase.FINAL_COMPILATION == "final_compilation"
