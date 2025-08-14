"""
Unit tests for crew configuration and orchestration.

This module contains comprehensive tests for the AccessibilityEvaluationCrew class,
ensuring proper initialization, configuration validation, and workflow execution.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from crewai import Crew

from src.config.crew_config import AccessibilityEvaluationCrew
from src.models.evaluation_models import DocumentContent, EvaluationInput


class TestAccessibilityEvaluationCrew:
    """Test suite for AccessibilityEvaluationCrew functionality."""

    @pytest.fixture
    def mock_llm_manager(self):
        """Create mock LLM manager for testing."""
        mock_manager = Mock()
        mock_manager.gemini = Mock()
        mock_manager.openai = Mock()
        return mock_manager

    @pytest.fixture
    def sample_evaluation_input(self):
        """Create sample evaluation input for testing."""
        return EvaluationInput(
            audit_report=DocumentContent(
                title="Sample Audit",
                content="Sample audit content with accessibility issues",
                page_count=10,
                metadata={"type": "audit"},
            ),
            remediation_plans={
                "PlanA": DocumentContent(
                    title="Plan A",
                    content="Remediation plan A content",
                    page_count=5,
                    metadata={"plan": "A"},
                ),
                "PlanB": DocumentContent(
                    title="Plan B",
                    content="Remediation plan B content",
                    page_count=6,
                    metadata={"plan": "B"},
                ),
            },
        )

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_crew_initialization(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
    ):
        """Test that AccessibilityEvaluationCrew initializes correctly."""
        # Setup mocks
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Verify initialization
        assert crew.llm_manager == mock_llm_manager
        assert "primary_judge" in crew.agents
        assert "secondary_judge" in crew.agents
        assert "comparison_agent" in crew.agents
        assert "synthesis_agent" in crew.agents

        assert "evaluation" in crew.task_managers
        assert "comparison" in crew.task_managers
        assert "synthesis" in crew.task_managers

        # Verify agents were created with LLM manager
        mock_primary_judge.assert_called_once_with(mock_llm_manager)
        mock_secondary_judge.assert_called_once_with(mock_llm_manager)
        assert mock_analysis_agent.call_count == 2  # comparison and synthesis agents

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_agent_initialization(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
    ):
        """Test that all agents are properly initialized."""
        # Setup mocks with agent attributes
        mock_primary_instance = Mock()
        mock_primary_instance.agent = Mock()
        mock_primary_judge.return_value = mock_primary_instance

        mock_secondary_instance = Mock()
        mock_secondary_instance.agent = Mock()
        mock_secondary_judge.return_value = mock_secondary_instance

        mock_analysis_instance = Mock()
        mock_analysis_instance.agent = Mock()
        mock_analysis_agent.return_value = mock_analysis_instance

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Verify agent structure
        assert hasattr(crew.agents["primary_judge"], "agent")
        assert hasattr(crew.agents["secondary_judge"], "agent")
        assert hasattr(crew.agents["comparison_agent"], "agent")
        assert hasattr(crew.agents["synthesis_agent"], "agent")

    @patch("src.config.crew_config.EvaluationTaskManager")
    @patch("src.config.crew_config.ComparisonTaskManager")
    @patch("src.config.crew_config.SynthesisTaskManager")
    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_task_manager_initialization(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_synthesis_manager,
        mock_comparison_manager,
        mock_evaluation_manager,
        mock_llm_manager,
    ):
        """Test that task managers are properly initialized."""
        # Setup agent mocks
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        # Setup task manager mocks
        mock_eval_instance = Mock()
        mock_evaluation_manager.return_value = mock_eval_instance

        mock_comp_instance = Mock()
        mock_comparison_manager.return_value = mock_comp_instance

        mock_synth_instance = Mock()
        mock_synthesis_manager.return_value = mock_synth_instance

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Verify task managers were created correctly
        mock_evaluation_manager.assert_called_once()
        mock_comparison_manager.assert_called_once()
        mock_synthesis_manager.assert_called_once()

        assert crew.task_managers["evaluation"] == mock_eval_instance
        assert crew.task_managers["comparison"] == mock_comp_instance
        assert crew.task_managers["synthesis"] == mock_synth_instance

    @patch("src.config.crew_config.Crew")
    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_execute_complete_evaluation_workflow(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_crew_class,
        mock_llm_manager,
        sample_evaluation_input,
    ):
        """Test complete evaluation workflow execution."""
        # Setup agent mocks
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        # Setup crew mock
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = "Mock evaluation result"
        mock_crew_class.return_value = mock_crew_instance

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Mock task managers
        crew.task_managers["evaluation"].create_batch_evaluation_tasks = Mock(
            return_value=["task1", "task2"]
        )
        crew.task_managers["comparison"].create_cross_plan_comparison_task = Mock(
            return_value="comparison_task"
        )
        crew.task_managers["synthesis"].create_optimal_plan_synthesis_task = Mock(
            return_value="synthesis_task"
        )

        # Execute workflow
        results = crew.execute_complete_evaluation(sample_evaluation_input)

        # Verify workflow phases
        assert "individual_evaluations" in results
        assert "comparison_analysis" in results
        assert "optimal_plan" in results

        # Verify crew was called multiple times for different phases
        assert mock_crew_class.call_count == 3  # evaluation, comparison, synthesis

        # Verify kickoff was called for each phase
        assert mock_crew_instance.kickoff.call_count == 3

    @patch("src.config.crew_config.Crew")
    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_execute_parallel_evaluation(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_crew_class,
        mock_llm_manager,
        sample_evaluation_input,
    ):
        """Test parallel evaluation workflow execution."""
        # Setup agent mocks
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        # Setup crew mock
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = "Parallel results"
        mock_crew_class.return_value = mock_crew_instance

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Mock task manager
        crew.task_managers["evaluation"].create_batch_evaluation_tasks = Mock(
            return_value=["task1", "task2", "task3"]
        )

        # Execute parallel workflow
        results = crew.execute_parallel_evaluation(sample_evaluation_input)

        # Verify results
        assert "parallel_results" in results
        assert results["parallel_results"] == "Parallel results"

        # Verify crew configuration for parallel execution
        mock_crew_class.assert_called_once()
        call_args = mock_crew_class.call_args[1]
        assert len(call_args["agents"]) == 2  # primary and secondary judges
        assert len(call_args["tasks"]) == 3  # all evaluation tasks

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_get_agent_status(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
    ):
        """Test agent status reporting."""
        # Setup mocks
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        crew = AccessibilityEvaluationCrew(mock_llm_manager)
        status = crew.get_agent_status()

        # Verify status information
        assert status["total_agents"] == 4
        assert set(status["agent_types"]) == {
            "primary_judge",
            "secondary_judge",
            "comparison_agent",
            "synthesis_agent",
        }
        assert set(status["task_managers"]) == {"evaluation", "comparison", "synthesis"}

        # Verify LLM model assignments
        assert status["llm_models"]["primary_judge"] == "gemini"
        assert status["llm_models"]["secondary_judge"] == "openai"
        assert status["llm_models"]["comparison_agent"] == "openai"
        assert status["llm_models"]["synthesis_agent"] == "openai"

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_validate_configuration_success(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
    ):
        """Test successful configuration validation."""
        # Setup proper agent mocks
        mock_primary_instance = Mock()
        mock_primary_instance.agent = Mock()
        mock_primary_judge.return_value = mock_primary_instance

        mock_secondary_instance = Mock()
        mock_secondary_instance.agent = Mock()
        mock_secondary_judge.return_value = mock_secondary_instance

        mock_analysis_instance = Mock()
        mock_analysis_instance.agent = Mock()
        mock_analysis_agent.return_value = mock_analysis_instance

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Validate configuration
        assert crew.validate_configuration() is True

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_validate_configuration_missing_agent(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
    ):
        """Test configuration validation with missing agent."""
        # Setup incomplete mocks
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Remove an agent to simulate missing configuration
        del crew.agents["primary_judge"]

        # Validate configuration should fail
        assert crew.validate_configuration() is False

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_validate_configuration_missing_agent_attribute(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
    ):
        """Test configuration validation with agent missing 'agent' attribute."""
        # Setup agent without 'agent' attribute
        mock_primary_instance = Mock()
        mock_primary_judge.return_value = mock_primary_instance

        mock_secondary_instance = Mock()
        mock_secondary_instance.agent = Mock()
        mock_secondary_judge.return_value = mock_secondary_instance

        mock_analysis_instance = Mock()
        mock_analysis_instance.agent = Mock()
        mock_analysis_agent.return_value = mock_analysis_instance

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Remove the agent attribute to force the check to fail
        delattr(crew.agents["primary_judge"], "agent")

        # Validate configuration should fail due to missing agent attribute
        assert crew.validate_configuration() is False

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_validate_configuration_missing_task_manager(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
    ):
        """Test configuration validation with missing task manager."""
        # Setup proper agent mocks
        mock_primary_instance = Mock()
        mock_primary_instance.agent = Mock()
        mock_primary_judge.return_value = mock_primary_instance

        mock_secondary_instance = Mock()
        mock_secondary_instance.agent = Mock()
        mock_secondary_judge.return_value = mock_secondary_instance

        mock_analysis_instance = Mock()
        mock_analysis_instance.agent = Mock()
        mock_analysis_agent.return_value = mock_analysis_instance

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Remove a task manager to simulate missing configuration
        del crew.task_managers["evaluation"]

        # Validate configuration should fail
        assert crew.validate_configuration() is False

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_validate_configuration_missing_llm_config(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
    ):
        """Test configuration validation with missing LLM configuration."""
        # Setup proper agent mocks
        mock_primary_instance = Mock()
        mock_primary_instance.agent = Mock()
        mock_primary_judge.return_value = mock_primary_instance

        mock_secondary_instance = Mock()
        mock_secondary_instance.agent = Mock()
        mock_secondary_judge.return_value = mock_secondary_instance

        mock_analysis_instance = Mock()
        mock_analysis_instance.agent = Mock()
        mock_analysis_agent.return_value = mock_analysis_instance

        # Create LLM manager missing required attributes
        mock_llm_manager_incomplete = Mock(
            spec=[]
        )  # spec=[] ensures it has no attributes

        crew = AccessibilityEvaluationCrew(mock_llm_manager_incomplete)

        # Validate configuration should fail due to missing LLM configs
        assert crew.validate_configuration() is False

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_validate_configuration_exception_handling(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
    ):
        """Test configuration validation exception handling."""
        # Setup agent that will cause exception
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Force an exception by making hasattr fail
        with patch("builtins.hasattr", side_effect=Exception("hasattr failed")):
            # Validate configuration should fail gracefully
            assert crew.validate_configuration() is False

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_create_sample_evaluations(
        self,
        mock_analysis_agent,
        mock_secondary_judge,
        mock_primary_judge,
        mock_llm_manager,
        sample_evaluation_input,
    ):
        """Test sample evaluation creation for testing."""
        # Setup mocks
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Create sample evaluations
        evaluations = crew._create_sample_evaluations(sample_evaluation_input)

        # Verify evaluations were created
        assert len(evaluations) == 4  # 2 plans × 2 judges

        # Verify evaluation structure
        plan_names = {eval.plan_name for eval in evaluations}
        judge_ids = {eval.judge_id for eval in evaluations}

        assert plan_names == {"PlanA", "PlanB"}
        assert judge_ids == {"primary", "secondary"}

        # Verify all evaluations have required fields
        for evaluation in evaluations:
            assert evaluation.overall_score > 0
            assert len(evaluation.scores) > 0
            assert evaluation.detailed_analysis
            assert len(evaluation.pros) > 0
            assert len(evaluation.cons) > 0


class TestCrewConfigurationIntegration:
    """Integration tests for crew configuration functionality."""

    def test_crew_config_module_imports(self):
        """Test that all required imports work correctly."""
        from crewai import Process

        from src.config.crew_config import AccessibilityEvaluationCrew

        # Verify imports are successful
        assert AccessibilityEvaluationCrew is not None
        assert Process is not None

    @patch("src.config.crew_config.PrimaryJudgeAgent")
    @patch("src.config.crew_config.SecondaryJudgeAgent")
    @patch("src.config.crew_config.AnalysisAgent")
    def test_full_crew_integration(
        self, mock_analysis_agent, mock_secondary_judge, mock_primary_judge
    ):
        """Test full crew integration with all components."""
        # Setup mock LLM manager
        mock_llm_manager = Mock()
        mock_llm_manager.gemini = Mock()
        mock_llm_manager.openai = Mock()

        # Setup agent mocks
        mock_primary_judge.return_value = Mock()
        mock_secondary_judge.return_value = Mock()
        mock_analysis_agent.return_value = Mock()

        # Should be able to create crew without errors
        crew = AccessibilityEvaluationCrew(mock_llm_manager)

        # Verify all components are properly initialized
        assert crew.llm_manager is not None
        assert len(crew.agents) == 4
        assert len(crew.task_managers) == 3

        # Verify configuration is valid
        status = crew.get_agent_status()
        assert status["total_agents"] == 4
        assert len(status["agent_types"]) == 4
        assert len(status["task_managers"]) == 3
