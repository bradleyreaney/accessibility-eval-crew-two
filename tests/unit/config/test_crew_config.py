"""
Test suite for AccessibilityEvaluationCrew configuration and resilience features.

Tests for crew initialization, agent availability checking, and resilience
capabilities for Phase 2 of the LLM error handling enhancement plan.
"""

from datetime import datetime
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from src.config.crew_config import AccessibilityEvaluationCrew
from src.config.llm_config import LLMManager
from src.models.evaluation_models import DocumentContent, EvaluationInput
from src.utils.llm_resilience_manager import LLMResilienceManager, ResilienceConfig


class TestAccessibilityEvaluationCrew:
    """Test suite for AccessibilityEvaluationCrew functionality"""

    @pytest.fixture
    def mock_llm_manager(self):
        """Mock LLMManager for testing"""
        mock_manager = Mock(spec=LLMManager)
        mock_manager.gemini = Mock()
        mock_manager.openai = Mock()
        return mock_manager

    @pytest.fixture
    def mock_resilience_manager(self):
        """Mock LLMResilienceManager for testing"""
        mock_manager = Mock(spec=LLMResilienceManager)
        mock_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": True,
        }
        return mock_manager

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

    def test_initialization_with_llm_manager(self, mock_llm_manager):
        """Test crew initialization with LLM manager"""
        # Act
        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Assert
        assert crew.llm_manager == mock_llm_manager
        assert crew.resilience_manager is None
        assert "primary_judge" in crew.agents
        assert "secondary_judge" in crew.agents
        assert "comparison_agent" in crew.agents
        assert "synthesis_agent" in crew.agents
        assert "evaluation" in crew.task_managers
        assert "comparison" in crew.task_managers
        assert "synthesis" in crew.task_managers

    def test_initialization_with_resilience_manager(
        self, mock_llm_manager, mock_resilience_manager
    ):
        """Test crew initialization with resilience manager"""
        # Act
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Assert
        assert crew.llm_manager == mock_llm_manager
        assert crew.resilience_manager == mock_resilience_manager
        assert crew.agent_availability is not None

    def test_agent_availability_check_with_all_llms_available(
        self, mock_llm_manager, mock_resilience_manager
    ):
        """Test agent availability check when all LLMs are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": True,
        }

        # Act
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Assert
        assert crew.agent_availability["primary_judge"] is True
        assert crew.agent_availability["secondary_judge"] is True
        assert crew.agent_availability["comparison_agent"] is True
        assert crew.agent_availability["synthesis_agent"] is True

    def test_agent_availability_check_with_partial_llm_availability(
        self, mock_llm_manager, mock_resilience_manager
    ):
        """Test agent availability check when only some LLMs are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }

        # Act
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Assert
        assert crew.agent_availability["primary_judge"] is True
        assert crew.agent_availability["secondary_judge"] is False
        assert crew.agent_availability["comparison_agent"] is True  # Can use either LLM
        assert crew.agent_availability["synthesis_agent"] is True  # Can use either LLM

    def test_agent_availability_check_with_no_llms_available(
        self, mock_llm_manager, mock_resilience_manager
    ):
        """Test agent availability check when no LLMs are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": False,
            "openai": False,
        }

        # Act
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Assert
        assert crew.agent_availability["primary_judge"] is False
        assert crew.agent_availability["secondary_judge"] is False
        assert crew.agent_availability["comparison_agent"] is False
        assert crew.agent_availability["synthesis_agent"] is False

    def test_agent_availability_check_without_resilience_manager(
        self, mock_llm_manager
    ):
        """Test agent availability check without resilience manager"""
        # Act
        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Assert
        assert crew.agent_availability["primary_judge"] is True
        assert crew.agent_availability["secondary_judge"] is True
        assert crew.agent_availability["comparison_agent"] is True
        assert crew.agent_availability["synthesis_agent"] is True

    def test_validate_configuration_with_all_agents_available(
        self, mock_llm_manager, mock_resilience_manager
    ):
        """Test configuration validation when all agents are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": True,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Act
        result = crew.validate_configuration()

        # Assert
        assert result is True

    def test_validate_configuration_with_partial_agents_available(
        self, mock_llm_manager, mock_resilience_manager
    ):
        """Test configuration validation when only some agents are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Act
        result = crew.validate_configuration()

        # Assert
        assert result is True  # Should still be valid with partial availability

    def test_validate_configuration_with_no_evaluation_agents(
        self, mock_llm_manager, mock_resilience_manager
    ):
        """Test configuration validation when no evaluation agents are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": False,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Act
        result = crew.validate_configuration()

        # Assert
        assert result is False

    def test_get_available_agents(self, mock_llm_manager, mock_resilience_manager):
        """Test getting list of available agents"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Act
        available_agents = crew.get_available_agents()

        # Assert
        assert "primary_judge" in available_agents
        assert "secondary_judge" not in available_agents
        assert "comparison_agent" in available_agents
        assert "synthesis_agent" in available_agents

    def test_get_unavailable_agents(self, mock_llm_manager, mock_resilience_manager):
        """Test getting list of unavailable agents"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Act
        unavailable_agents = crew.get_unavailable_agents()

        # Assert
        assert "primary_judge" not in unavailable_agents
        assert "secondary_judge" in unavailable_agents
        assert "comparison_agent" not in unavailable_agents
        assert "synthesis_agent" not in unavailable_agents

    @patch("src.config.crew_config.Crew")
    def test_execute_individual_evaluations_with_all_judges_available(
        self,
        mock_crew_class,
        mock_llm_manager,
        mock_resilience_manager,
        sample_evaluation_input,
    ):
        """Test individual evaluations when all judges are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": True,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = {"result": "test"}
        mock_crew_class.return_value = mock_crew_instance

        # Mock task manager method
        crew.task_managers["evaluation"].create_batch_evaluation_tasks = Mock(
            return_value=["task1", "task2"]
        )

        # Act
        result = crew._execute_individual_evaluations(sample_evaluation_input)

        # Assert
        # The result should be a list since we have 2 plans
        assert isinstance(result, list)
        assert len(result) == 2
        # Each result should contain the mocked response
        for item in result:
            assert item == {"result": "test"}
        # Should be called twice (once for each plan)
        assert mock_crew_class.call_count == 2
        # Should have both judges in the crew
        called_agents = mock_crew_class.call_args[1]["agents"]
        assert len(called_agents) == 2

    @patch("src.config.crew_config.Crew")
    def test_execute_individual_evaluations_with_partial_judges_available(
        self,
        mock_crew_class,
        mock_llm_manager,
        mock_resilience_manager,
        sample_evaluation_input,
    ):
        """Test individual evaluations when only some judges are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = {"result": "test"}
        mock_crew_class.return_value = mock_crew_instance

        # Mock task manager method
        crew.task_managers["evaluation"].create_batch_evaluation_tasks = Mock(
            return_value=["task1", "task2"]
        )

        # Act
        result = crew._execute_individual_evaluations(sample_evaluation_input)

        # Assert
        # The result should be a list since we have 2 plans
        assert isinstance(result, list)
        assert len(result) == 2
        # Each result should contain the mocked response
        for item in result:
            assert item == {"result": "test"}
        # Should be called twice (once for each plan)
        assert mock_crew_class.call_count == 2
        # Should have only one judge in the crew
        called_agents = mock_crew_class.call_args[1]["agents"]
        assert len(called_agents) == 1

    def test_execute_individual_evaluations_with_no_judges_available(
        self, mock_llm_manager, mock_resilience_manager, sample_evaluation_input
    ):
        """Test individual evaluations when no judges are available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": False,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Act
        result = crew._execute_individual_evaluations(sample_evaluation_input)

        # Assert
        # The result should be a list of strings, not a dictionary
        assert isinstance(result, list)
        assert len(result) == 2  # One for each plan

        # Check that both plans are mentioned in the results
        plan_a_found = any("PlanA" in item for item in result)
        plan_b_found = any("PlanB" in item for item in result)
        assert plan_a_found, "PlanA should be mentioned in results"
        assert plan_b_found, "PlanB should be mentioned in results"

        # Check that the results contain the expected NA status information
        for item in result:
            assert "**Status:** NA" in item
            assert "No evaluation agents available" in item

    @patch("src.config.crew_config.Crew")
    def test_execute_cross_plan_comparison_with_agent_available(
        self,
        mock_crew_class,
        mock_llm_manager,
        mock_resilience_manager,
        sample_evaluation_input,
    ):
        """Test cross-plan comparison when comparison agent is available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": True,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = {"comparison": "result"}
        mock_crew_class.return_value = mock_crew_instance

        # Mock task manager method
        crew.task_managers["comparison"].create_cross_plan_comparison_task = Mock(
            return_value="task1"
        )

        # Act
        result = crew._execute_cross_plan_comparison(
            sample_evaluation_input, {"test": "data"}
        )

        # Assert
        assert result == {"comparison": "result"}
        mock_crew_class.assert_called_once()

    def test_execute_cross_plan_comparison_with_agent_unavailable(
        self, mock_llm_manager, mock_resilience_manager, sample_evaluation_input
    ):
        """Test cross-plan comparison when comparison agent is unavailable"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": False,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Act
        result = crew._execute_cross_plan_comparison(
            sample_evaluation_input, {"test": "data"}
        )

        # Assert
        assert result["status"] == "NA"
        assert result["reason"] == "Comparison agent unavailable"

    @patch("src.config.crew_config.Crew")
    def test_execute_plan_synthesis_with_agent_available(
        self,
        mock_crew_class,
        mock_llm_manager,
        mock_resilience_manager,
        sample_evaluation_input,
    ):
        """Test plan synthesis when synthesis agent is available"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": True,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = {"synthesis": "result"}
        mock_crew_class.return_value = mock_crew_instance

        # Mock task manager method
        crew.task_managers["synthesis"].create_optimal_plan_synthesis_task = Mock(
            return_value="task1"
        )

        # Act
        result = crew._execute_plan_synthesis(
            sample_evaluation_input, {"test": "data"}, {"comparison": "data"}
        )

        # Assert
        assert result == {"synthesis": "result"}
        mock_crew_class.assert_called_once()

    def test_execute_plan_synthesis_with_agent_unavailable(
        self, mock_llm_manager, mock_resilience_manager, sample_evaluation_input
    ):
        """Test plan synthesis when synthesis agent is unavailable"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": False,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Act
        result = crew._execute_plan_synthesis(
            sample_evaluation_input, {"test": "data"}, {"comparison": "data"}
        )

        # Assert
        assert result["status"] == "NA"
        assert result["reason"] == "Synthesis agent unavailable"

    def test_create_na_evaluation_results(
        self, mock_llm_manager, sample_evaluation_input
    ):
        """Test creation of NA evaluation results"""
        # Arrange
        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Act
        result = crew._create_na_evaluation_results(sample_evaluation_input)

        # Assert
        # The result should be a list of strings, not a dictionary
        assert isinstance(result, list)
        assert len(result) == 2  # One for each plan

        # Check that both plans are mentioned in the results
        plan_a_found = any("PlanA" in item for item in result)
        plan_b_found = any("PlanB" in item for item in result)
        assert plan_a_found, "PlanA should be mentioned in results"
        assert plan_b_found, "PlanB should be mentioned in results"

        # Check that the results contain the expected NA status information
        for item in result:
            assert "**Status:** NA" in item
            assert "No evaluation agents available" in item

    @patch("src.config.crew_config.Crew")
    def test_execute_complete_evaluation_with_resilience(
        self,
        mock_crew_class,
        mock_llm_manager,
        mock_resilience_manager,
        sample_evaluation_input,
    ):
        """Test complete evaluation workflow with resilience capabilities"""
        # Arrange
        mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }
        crew = AccessibilityEvaluationCrew(mock_llm_manager, mock_resilience_manager)

        # Mock individual evaluations
        crew._execute_individual_evaluations = Mock(
            return_value={"individual": "result"}
        )
        crew._execute_cross_plan_comparison = Mock(
            return_value={"comparison": "result"}
        )
        crew._execute_plan_synthesis = Mock(return_value={"synthesis": "result"})

        # Act
        result = crew.execute_complete_evaluation(sample_evaluation_input)

        # Assert
        assert "individual_evaluations" in result
        assert "comparison_analysis" in result
        assert "optimal_plan" in result
        assert result["individual_evaluations"] == {"individual": "result"}
        assert result["comparison_analysis"] == {"comparison": "result"}
        assert result["optimal_plan"] == {"synthesis": "result"}

        # Verify resilience methods were called
        crew._execute_individual_evaluations.assert_called_once_with(
            sample_evaluation_input
        )
        crew._execute_cross_plan_comparison.assert_called_once_with(
            sample_evaluation_input, {"individual": "result"}
        )
        crew._execute_plan_synthesis.assert_called_once_with(
            sample_evaluation_input, {"individual": "result"}, {"comparison": "result"}
        )


class TestAccessibilityEvaluationCrewIntegration:
    """Integration tests for AccessibilityEvaluationCrew"""

    @pytest.fixture
    def mock_llm_manager_integration(self):
        """Mock LLMManager for integration testing"""
        mock_manager = Mock(spec=LLMManager)
        mock_manager.gemini = Mock()
        mock_manager.openai = Mock()
        return mock_manager

    @pytest.fixture
    def mock_resilience_manager_integration(self):
        """Mock LLMResilienceManager for integration testing"""
        mock_manager = Mock(spec=LLMResilienceManager)
        mock_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": True,
        }
        return mock_manager

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

    def test_full_workflow_with_resilience_integration(
        self,
        mock_llm_manager_integration,
        mock_resilience_manager_integration,
        sample_evaluation_input,
    ):
        """Test full workflow integration with resilience capabilities"""
        # Arrange
        crew = AccessibilityEvaluationCrew(
            mock_llm_manager_integration, mock_resilience_manager_integration
        )

        # Mock all internal methods
        crew._execute_individual_evaluations = Mock(
            return_value={"individual": "result"}
        )
        crew._execute_cross_plan_comparison = Mock(
            return_value={"comparison": "result"}
        )
        crew._execute_plan_synthesis = Mock(return_value={"synthesis": "result"})

        # Act
        result = crew.execute_complete_evaluation(sample_evaluation_input)

        # Assert
        assert result["individual_evaluations"] == {"individual": "result"}
        assert result["comparison_analysis"] == {"comparison": "result"}
        assert result["optimal_plan"] == {"synthesis": "result"}

        # Verify resilience manager was used
        mock_resilience_manager_integration.check_llm_availability.assert_called()

    def test_agent_availability_integration(
        self, mock_llm_manager_integration, mock_resilience_manager_integration
    ):
        """Test agent availability integration with resilience manager"""
        # Arrange
        mock_resilience_manager_integration.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }

        # Act
        crew = AccessibilityEvaluationCrew(
            mock_llm_manager_integration, mock_resilience_manager_integration
        )

        # Assert
        assert crew.agent_availability["primary_judge"] is True
        assert crew.agent_availability["secondary_judge"] is False
        assert crew.agent_availability["comparison_agent"] is True
        assert crew.agent_availability["synthesis_agent"] is True

        # Test validation
        assert crew.validate_configuration() is True

        # Test available/unavailable lists
        available = crew.get_available_agents()
        unavailable = crew.get_unavailable_agents()

        assert "primary_judge" in available
        assert "secondary_judge" in unavailable
        assert "comparison_agent" in available
        assert "synthesis_agent" in available
