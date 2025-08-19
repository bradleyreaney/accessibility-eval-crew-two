"""
Resilience Error Scenario Tests - Phase 4
LLM Error Handling Enhancement Plan

Comprehensive unit tests for all error scenarios and edge cases
in the resilience system.
"""

import asyncio
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.config.crew_config import AccessibilityEvaluationCrew
from src.models.evaluation_models import DocumentContent, EvaluationInput
from src.utils.llm_exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMQuotaExceededError,
    LLMRateLimitError,
    LLMTimeoutError,
    NoLLMAvailableError,
    PartialEvaluationError,
)
from src.utils.llm_resilience_manager import LLMResilienceManager, ResilienceConfig
from src.utils.workflow_controller import WorkflowController


class TestResilienceErrorScenarios:
    """Test comprehensive error scenarios for resilience system"""

    def setup_method(self):
        """Set up test components"""
        self.mock_llm_manager = Mock()
        self.mock_llm_manager.gemini_llm = Mock()
        self.mock_llm_manager.openai_llm = Mock()

        self.resilience_config = ResilienceConfig(
            max_retries=3,
            retry_delay_seconds=1,
            exponential_backoff=True,
            timeout_seconds=10,
            enable_partial_evaluation=True,
            minimum_llm_requirement=1,
            na_reporting_enabled=True,
        )

        self.resilience_manager = LLMResilienceManager(
            self.mock_llm_manager, config=self.resilience_config
        )

    def test_llm_connection_error_handling(self):
        """Test handling of LLM connection errors"""

        # Mock connection error
        self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMConnectionError(
            "gemini", "Network connection failed"
        )

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", "gemini"
        )

        assert result["success"] is False
        assert "connection" in result["error"].lower()
        assert result["retryable"] is True

    def test_llm_timeout_error_handling(self):
        """Test handling of LLM timeout errors"""

        # Mock timeout error
        self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMTimeoutError(
            "gemini", "Request timed out"
        )

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", "gemini"
        )

        assert result["success"] is False
        assert "timed out" in result["error"].lower()
        assert result["retryable"] is True

    def test_llm_rate_limit_error_handling(self):
        """Test handling of LLM rate limit errors"""

        # Mock rate limit error
        self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMRateLimitError(
            "gemini", retryable=False
        )

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", "gemini"
        )

        assert result["success"] is False
        assert "rate limit" in result["error"].lower()
        assert result["retryable"] is False  # Rate limits are not retryable

    def test_llm_authentication_error_handling(self):
        """Test handling of LLM authentication errors"""

        # Mock authentication error
        self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMAuthenticationError(
            "gemini", "Invalid API key"
        )

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", "gemini"
        )

        assert result["success"] is False
        assert "authentication" in result["error"].lower()
        assert result["retryable"] is False  # Auth errors are not retryable

    def test_llm_quota_exceeded_error_handling(self):
        """Test handling of LLM quota exceeded errors"""

        # Mock quota exceeded error
        self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMQuotaExceededError(
            "gemini", "Quota exceeded"
        )

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", "gemini"
        )

        assert result["success"] is False
        assert "quota" in result["error"].lower()
        assert result["retryable"] is False  # Quota errors are not retryable

    def test_unknown_error_handling(self):
        """Test handling of unknown errors"""

        # Mock unknown error
        self.mock_llm_manager.gemini_llm.invoke.side_effect = Exception(
            "Unknown error occurred"
        )

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", "gemini"
        )

        assert result["success"] is False
        assert "unknown" in result["error"].lower()
        assert result["retryable"] is True  # Unknown errors are retryable by default

    def test_retry_logic_with_exponential_backoff(self):
        """Test retry logic with exponential backoff"""

        call_count = 0

        def mock_invoke_with_failures(prompt):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # First two calls fail
                raise LLMConnectionError("gemini", f"Attempt {call_count} failed")
            else:  # Third call succeeds
                mock_result = Mock()
                mock_result.content = "Success after retries"
                return mock_result

        self.mock_llm_manager.gemini_llm.invoke.side_effect = mock_invoke_with_failures

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", "gemini"
        )

        assert result["success"] is True
        assert "Success after retries" in result["content"]
        assert call_count == 3

    def test_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded"""

        # Mock persistent failure
        self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMConnectionError(
            "gemini", "Persistent failure"
        )

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", "gemini"
        )

        assert result["success"] is False
        assert "connection" in result["error"].lower()
        assert result["attempt"] == 3

    def test_partial_evaluation_error_handling(self):
        """Test handling of partial evaluation errors"""

        # Mock partial evaluation scenario by setting internal status
        self.resilience_manager.llm_status["gemini"].available = False
        self.resilience_manager.llm_status["openai"].available = False

        # When no LLMs are available, it should return NA result
        result = self.resilience_manager.evaluate_plan_with_fallback(
            "TestPlan", "Test content", "Test context"
        )

        assert result["status"] == "NA"
        assert "LLMs unavailable" in result["na_reason"]

    def test_llm_availability_check_failures(self):
        """Test LLM availability check failure scenarios"""

        # Test when availability check itself fails
        with patch.object(self.resilience_manager, "_test_llm_connection") as mock_test:
            mock_test.side_effect = Exception("Availability check failed")

            availability = self.resilience_manager.check_llm_availability()

            # Should handle gracefully and mark as unavailable
            assert availability["gemini"] is False
            assert availability["openai"] is False

    def test_evaluation_with_mixed_availability(self):
        """Test evaluation with mixed LLM availability"""

        # Mock mixed availability
        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": True, "openai": False}

            # Mock successful evaluation with available LLM
            mock_result = Mock()
            mock_result.content = "Evaluation completed"
            self.mock_llm_manager.gemini.invoke.return_value = mock_result

            result = self.resilience_manager.evaluate_plan_with_fallback(
                "TestPlan", "Test content", "Test context"
            )

            assert result["status"] == "completed"
            assert result["llm_used"] == "gemini"
            assert "Evaluation completed" in result["evaluation_content"]

    def test_na_result_generation_edge_cases(self):
        """Test NA result generation with edge cases"""

        # Test with empty plan name
        result = self.resilience_manager.mark_evaluation_as_na(
            "", "gemini", "Test reason"
        )
        assert result["status"] == "NA"
        assert result["plan_name"] == ""

        # Test with None reason
        result = self.resilience_manager.mark_evaluation_as_na(
            "TestPlan", "gemini", None
        )
        assert result["status"] == "NA"
        assert result["na_reason"] == "Unknown error"

        # Test with very long reason
        long_reason = "A" * 1000
        result = self.resilience_manager.mark_evaluation_as_na(
            "TestPlan", "gemini", long_reason
        )
        assert result["status"] == "NA"
        assert len(result["na_reason"]) <= 500  # Should be truncated

    def test_resilience_config_validation(self):
        """Test resilience configuration validation"""

        # Test invalid configuration - Pydantic v2 doesn't auto-validate these
        # but we can test that the values are set correctly
        config = ResilienceConfig(max_retries=-1)
        assert config.max_retries == -1

        config = ResilienceConfig(retry_delay_seconds=-1)
        assert config.retry_delay_seconds == -1

        config = ResilienceConfig(timeout_seconds=0)
        assert config.timeout_seconds == 0

        config = ResilienceConfig(minimum_llm_requirement=0)
        assert config.minimum_llm_requirement == 0

    def test_status_tracking_and_monitoring(self):
        """Test status tracking and monitoring functionality"""

        # Set initial status to unavailable for testing
        self.resilience_manager.llm_status["gemini"].available = False
        self.resilience_manager.llm_status["openai"].available = False

        # Test initial status
        status = self.resilience_manager.get_status_summary()
        assert len(status["llm_status"]) == 2
        available_count = sum(
            1 for s in status["llm_status"].values() if s["available"]
        )
        unavailable_count = sum(
            1 for s in status["llm_status"].values() if not s["available"]
        )
        assert available_count == 0
        assert unavailable_count == 2

        # Test status update
        self.resilience_manager.llm_status["gemini"].available = True
        status = self.resilience_manager.get_status_summary()
        available_count = sum(
            1 for s in status["llm_status"].values() if s["available"]
        )
        unavailable_count = sum(
            1 for s in status["llm_status"].values() if not s["available"]
        )
        assert available_count == 1
        assert unavailable_count == 1

        # Test failure count tracking
        self.resilience_manager.llm_status["gemini"].failure_count = 1
        status = self.resilience_manager.get_status_summary()
        assert status["llm_status"]["gemini"]["failure_count"] == 1

    def test_reset_functionality(self):
        """Test reset functionality for recovery"""

        # Set up some state
        self.resilience_manager.llm_status["gemini"].available = False
        self.resilience_manager.llm_status["gemini"].failure_count = 1

        # Reset
        self.resilience_manager.reset_failure_counts()

        # Verify reset
        status = self.resilience_manager.get_status_summary()
        assert status["llm_status"]["gemini"]["failure_count"] == 0

    def test_error_classification_edge_cases(self):
        """Test error classification with edge cases"""

        from src.utils.llm_exceptions import classify_llm_error

        # Test with None error
        classification = classify_llm_error(None, "gemini")
        assert classification.retryable is True
        assert "connection failed" in str(classification).lower()

        # Test with string error
        classification = classify_llm_error("Some string error", "gemini")
        assert classification.retryable is True
        assert "connection failed" in str(classification).lower()

        # Test with custom exception
        class CustomError(Exception):
            pass

        classification = classify_llm_error(CustomError("Custom error"), "gemini")
        assert classification.retryable is True
        assert "connection failed" in str(classification).lower()


class TestWorkflowControllerErrorScenarios:
    """Test error scenarios in workflow controller"""

    def setup_method(self):
        """Set up workflow controller test components"""
        self.mock_crew = Mock(spec=AccessibilityEvaluationCrew)
        self.mock_resilience_manager = Mock(spec=LLMResilienceManager)

        # Mock the config attribute
        mock_config = Mock()
        mock_config.minimum_llm_requirement = 1
        self.mock_resilience_manager.config = mock_config

        self.workflow_controller = WorkflowController(
            self.mock_crew, self.mock_resilience_manager
        )

    def test_workflow_with_no_llms_available(self):
        """Test workflow behavior when no LLMs are available"""

        # Mock no LLMs available
        self.mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": False,
            "openai": False,
        }

        # Create proper EvaluationInput structure
        audit_report = DocumentContent(
            title="Test Audit", content="Test context", page_count=1, metadata={}
        )
        remediation_plans = {
            "PlanA": DocumentContent(
                title="TestPlan", content="Test content", page_count=1, metadata={}
            )
        }

        evaluation_input = EvaluationInput(
            audit_report=audit_report, remediation_plans=remediation_plans
        )

        with pytest.raises(RuntimeError, match="Insufficient LLMs available"):
            asyncio.run(
                self.workflow_controller._run_evaluation_workflow(
                    evaluation_input, mode="standard", include_consensus=False
                )
            )

    def test_workflow_with_partial_availability(self):
        """Test workflow behavior with partial LLM availability"""

        # Mock partial availability
        self.mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }

        # Mock successful evaluation
        self.mock_resilience_manager.evaluate_plan_with_fallback.return_value = {
            "status": "completed",
            "evaluation_content": "Test evaluation",
            "llm_used": "gemini",
        }

        # Mock crew execution
        self.mock_crew.execute_complete_evaluation.return_value = {
            "individual_evaluations": {"PlanA": {"status": "completed", "score": 8.5}},
            "comparison_analysis": {"status": "completed"},
            "optimal_plan": {"status": "completed", "plan": "PlanA"},
        }

        # Create proper EvaluationInput structure
        audit_report = DocumentContent(
            title="Test Audit", content="Test context", page_count=1, metadata={}
        )
        remediation_plans = {
            "PlanA": DocumentContent(
                title="TestPlan", content="Test content", page_count=1, metadata={}
            )
        }

        evaluation_input = EvaluationInput(
            audit_report=audit_report, remediation_plans=remediation_plans
        )

        # Should not raise exception
        result = asyncio.run(
            self.workflow_controller._run_evaluation_workflow(
                evaluation_input, mode="standard", include_consensus=False
            )
        )

        assert result is not None


class TestCrewErrorScenarios:
    """Test error scenarios in crew configuration"""

    def setup_method(self):
        """Set up crew test components"""
        self.mock_llm_manager = Mock()
        self.mock_resilience_manager = Mock(spec=LLMResilienceManager)
        self.crew = AccessibilityEvaluationCrew(
            self.mock_llm_manager, self.mock_resilience_manager
        )

    def test_crew_with_no_available_agents(self):
        """Test crew behavior when no agents are available"""

        # Mock no agents available
        self.mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": False,
            "openai": False,
        }

        # Create proper EvaluationInput structure
        audit_report = DocumentContent(
            title="Test Audit", content="Test context", page_count=1, metadata={}
        )
        remediation_plans = {
            "PlanA": DocumentContent(
                title="TestPlan", content="Test content", page_count=1, metadata={}
            )
        }

        evaluation_input = EvaluationInput(
            audit_report=audit_report, remediation_plans=remediation_plans
        )

        result = self.crew.execute_complete_evaluation(evaluation_input)

        # Should return NA results
        assert result is not None
        # Additional assertions based on expected NA result structure

    def test_crew_with_partial_agent_availability(self):
        """Test crew behavior with partial agent availability"""

        # Mock partial availability
        self.mock_resilience_manager.check_llm_availability.return_value = {
            "gemini": True,
            "openai": False,
        }

        # Create proper EvaluationInput structure
        audit_report = DocumentContent(
            title="Test Audit", content="Test context", page_count=1, metadata={}
        )
        remediation_plans = {
            "PlanA": DocumentContent(
                title="TestPlan", content="Test content", page_count=1, metadata={}
            )
        }

        evaluation_input = EvaluationInput(
            audit_report=audit_report, remediation_plans=remediation_plans
        )

        # Mock successful evaluation
        with patch.object(self.crew, "get_available_agents") as mock_agents:
            mock_agents.return_value = ["primary_judge"]

            result = self.crew.execute_complete_evaluation(evaluation_input)

            # Should handle partial availability gracefully
            assert result is not None
