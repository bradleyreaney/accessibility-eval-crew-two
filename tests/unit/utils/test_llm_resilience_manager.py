"""
Unit tests for LLM Resilience Manager.

Tests the LLM resilience management functionality including availability checking,
fallback handling, and error recovery strategies.

References:
    - LLM Error Handling Enhancement Plan - Phase 1.1
    - Master Plan: Testing standards and patterns
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.config.llm_config import LLMManager
from src.models.evaluation_models import DocumentContent, EvaluationInput
from src.utils.llm_exceptions import (
    LLMConnectionError,
    LLMTimeoutError,
    NoLLMAvailableError,
)
from src.utils.llm_resilience_manager import (
    LLMResilienceManager,
    LLMStatus,
    ResilienceConfig,
)


class TestResilienceConfig:
    """Test suite for ResilienceConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = ResilienceConfig()

        assert config.max_retries == 3
        assert config.retry_delay_seconds == 2
        assert config.exponential_backoff is True
        assert config.timeout_seconds == 30
        assert config.enable_partial_evaluation is True
        assert config.minimum_llm_requirement == 1
        assert config.na_reporting_enabled is True
        assert config.availability_check_timeout == 10

    def test_custom_config(self):
        """Test custom configuration values"""
        config = ResilienceConfig(
            max_retries=5,
            retry_delay_seconds=3,
            exponential_backoff=False,
            minimum_llm_requirement=2,
        )

        assert config.max_retries == 5
        assert config.retry_delay_seconds == 3
        assert config.exponential_backoff is False
        assert config.minimum_llm_requirement == 2


class TestLLMStatus:
    """Test suite for LLMStatus"""

    def test_llm_status_creation(self):
        """Test LLMStatus creation with required fields"""
        status = LLMStatus(
            llm_type="Gemini Pro", available=True, last_check=datetime.now()
        )

        assert status.llm_type == "Gemini Pro"
        assert status.available is True
        assert isinstance(status.last_check, datetime)
        assert status.failure_count == 0
        assert status.consecutive_failures == 0
        assert status.last_failure is None
        assert status.last_failure_reason is None

    def test_llm_status_with_optional_fields(self):
        """Test LLMStatus creation with optional fields"""
        last_failure = datetime.now()
        status = LLMStatus(
            llm_type="GPT-4",
            available=False,
            last_check=datetime.now(),
            failure_count=3,
            last_failure=last_failure,
            last_failure_reason="Rate limit exceeded",
            consecutive_failures=2,
        )

        assert status.llm_type == "GPT-4"
        assert status.available is False
        assert status.failure_count == 3
        assert status.last_failure == last_failure
        assert status.last_failure_reason == "Rate limit exceeded"
        assert status.consecutive_failures == 2


class TestLLMResilienceManager:
    """Test suite for LLMResilienceManager"""

    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager"""
        mock_manager = Mock(spec=LLMManager)
        mock_manager.gemini = Mock()
        mock_manager.openai = Mock()
        return mock_manager

    @pytest.fixture
    def resilience_manager(self, mock_llm_manager):
        """Create a resilience manager instance"""
        return LLMResilienceManager(mock_llm_manager)

    def test_initialization(self, mock_llm_manager):
        """Test resilience manager initialization"""
        manager = LLMResilienceManager(mock_llm_manager)

        assert manager.llm_manager == mock_llm_manager
        assert isinstance(manager.config, ResilienceConfig)
        assert "gemini" in manager.llm_status
        assert "openai" in manager.llm_status
        assert manager.llm_status["gemini"].llm_type == "Gemini Pro"
        assert manager.llm_status["openai"].llm_type == "GPT-4"
        assert manager.evaluation_stats["total_evaluations"] == 0

    def test_initialization_with_custom_config(self, mock_llm_manager):
        """Test resilience manager initialization with custom config"""
        config = ResilienceConfig(max_retries=5, minimum_llm_requirement=2)
        manager = LLMResilienceManager(mock_llm_manager, config)

        assert manager.config.max_retries == 5
        assert manager.config.minimum_llm_requirement == 2

    @patch("src.utils.llm_resilience_manager.LLMResilienceManager._test_llm_connection")
    def test_check_llm_availability_success(
        self, mock_test_connection, resilience_manager
    ):
        """Test LLM availability check when both LLMs are available"""
        mock_test_connection.side_effect = [True, True]

        availability = resilience_manager.check_llm_availability()

        assert availability["gemini"] is True
        assert availability["openai"] is True
        assert resilience_manager.llm_status["gemini"].available is True
        assert resilience_manager.llm_status["openai"].available is True

    @patch("src.utils.llm_resilience_manager.LLMResilienceManager._test_llm_connection")
    def test_check_llm_availability_partial_failure(
        self, mock_test_connection, resilience_manager
    ):
        """Test LLM availability check when one LLM fails"""
        mock_test_connection.side_effect = [True, False]

        availability = resilience_manager.check_llm_availability()

        assert availability["gemini"] is True
        assert availability["openai"] is False
        assert resilience_manager.llm_status["gemini"].available is True
        assert resilience_manager.llm_status["openai"].available is False
        assert resilience_manager.llm_status["openai"].failure_count == 1

    @patch("src.utils.llm_resilience_manager.LLMResilienceManager._test_llm_connection")
    def test_check_llm_availability_both_fail(
        self, mock_test_connection, resilience_manager
    ):
        """Test LLM availability check when both LLMs fail"""
        mock_test_connection.side_effect = [False, False]

        availability = resilience_manager.check_llm_availability()

        assert availability["gemini"] is False
        assert availability["openai"] is False
        assert resilience_manager.llm_status["gemini"].available is False
        assert resilience_manager.llm_status["openai"].available is False

    def test_test_llm_connection_gemini_success(self, resilience_manager):
        """Test successful Gemini connection test"""
        mock_response = Mock()
        mock_response.content = "Connection successful."
        resilience_manager.llm_manager.gemini.invoke.return_value = mock_response

        result = resilience_manager._test_llm_connection("gemini")

        assert result is True
        resilience_manager.llm_manager.gemini.invoke.assert_called_once()

    def test_test_llm_connection_openai_success(self, resilience_manager):
        """Test successful OpenAI connection test"""
        mock_response = Mock()
        mock_response.content = "Connection successful."
        resilience_manager.llm_manager.openai.invoke.return_value = mock_response

        result = resilience_manager._test_llm_connection("openai")

        assert result is True
        resilience_manager.llm_manager.openai.invoke.assert_called_once()

    def test_test_llm_connection_failure(self, resilience_manager):
        """Test LLM connection test failure"""
        resilience_manager.llm_manager.gemini.invoke.side_effect = Exception(
            "Connection failed"
        )

        result = resilience_manager._test_llm_connection("gemini")

        assert result is False

    def test_test_llm_connection_unknown_type(self, resilience_manager):
        """Test LLM connection test with unknown LLM type"""
        with pytest.raises(ValueError, match="Unknown LLM type: unknown"):
            resilience_manager._test_llm_connection("unknown")

    def test_update_llm_status_success(self, resilience_manager):
        """Test updating LLM status for successful connection"""
        resilience_manager._update_llm_status("gemini", True)

        status = resilience_manager.llm_status["gemini"]
        assert status.available is True
        assert status.consecutive_failures == 0
        assert status.last_failure_reason is None

    def test_update_llm_status_failure(self, resilience_manager):
        """Test updating LLM status for failed connection"""
        resilience_manager._update_llm_status("openai", False, "Rate limit exceeded")

        status = resilience_manager.llm_status["openai"]
        assert status.available is False
        assert status.failure_count == 1
        assert status.consecutive_failures == 1
        assert status.last_failure_reason == "Rate limit exceeded"
        assert status.last_failure is not None

    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_safe_llm_invoke_success(self, mock_sleep, resilience_manager):
        """Test successful LLM invocation"""
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_llm = Mock()
        mock_llm.invoke.return_value = mock_response

        result = resilience_manager.safe_llm_invoke(mock_llm, "Test prompt", "gemini")

        assert result["success"] is True
        assert result["content"] == "Test response"
        assert result["llm_type"] == "gemini"
        assert result["attempt"] == 1
        assert "duration" in result

    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_safe_llm_invoke_retry_success(self, mock_sleep, resilience_manager):
        """Test LLM invocation with retry on failure"""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = [
            Exception("Temporary error"),
            Mock(content="Success"),
        ]

        result = resilience_manager.safe_llm_invoke(mock_llm, "Test prompt", "openai")

        assert result["success"] is True
        assert result["attempt"] == 2
        assert mock_sleep.called  # Should have slept between attempts

    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_safe_llm_invoke_max_retries_exceeded(self, mock_sleep, resilience_manager):
        """Test LLM invocation when max retries are exceeded"""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("Persistent error")

        result = resilience_manager.safe_llm_invoke(mock_llm, "Test prompt", "gemini")

        assert result["success"] is False
        assert result["error_type"] == "LLMConnectionError"
        assert result["retryable"] is True
        assert result["attempt"] == 3  # Should have tried 3 times

    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_safe_llm_invoke_non_retryable_error(self, mock_sleep, resilience_manager):
        """Test LLM invocation with non-retryable error"""
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception(
            "Authentication failed: Invalid API key"
        )

        result = resilience_manager.safe_llm_invoke(mock_llm, "Test prompt", "openai")

        assert result["success"] is False
        assert result["error_type"] == "LLMAuthenticationError"
        assert result["retryable"] is False
        assert result["attempt"] == 1  # Should not retry

    def test_mark_evaluation_as_na(self, resilience_manager):
        """Test marking evaluation as NA"""
        result = resilience_manager.mark_evaluation_as_na(
            "TestPlan", "gemini", "LLM unavailable"
        )

        assert result["plan_name"] == "TestPlan"
        assert result["evaluator"] == "Gemini Judge"
        assert result["status"] == "NA"
        assert result["na_reason"] == "LLM unavailable"
        assert result["llm_used"] == "gemini"
        assert result["success"] is False
        assert resilience_manager.evaluation_stats["na_evaluations"] == 1

    def test_execute_with_fallback_no_llms_available(self, resilience_manager):
        """Test execution with fallback when no LLMs are available"""
        with patch.object(resilience_manager, "check_llm_availability") as mock_check:
            mock_check.return_value = {"gemini": False, "openai": False}

            evaluation_input = EvaluationInput(
                audit_report=DocumentContent(
                    title="Test", content="Test audit", page_count=1, metadata={}
                ),
                remediation_plans={
                    "PlanA": DocumentContent(
                        title="Plan1", content="Test plan", page_count=1, metadata={}
                    )
                },
            )

            with pytest.raises(NoLLMAvailableError):
                resilience_manager.execute_with_fallback(evaluation_input)

    @patch(
        "src.utils.llm_resilience_manager.LLMResilienceManager._evaluate_plan_with_fallback"
    )
    def test_execute_with_fallback_success(
        self, mock_evaluate_plan, resilience_manager
    ):
        """Test successful execution with fallback"""
        with patch.object(resilience_manager, "check_llm_availability") as mock_check:
            mock_check.return_value = {"gemini": True, "openai": True}

            # Mock successful evaluation
            mock_evaluate_plan.return_value = {
                "plan_name": "Plan1",
                "success": True,
                "status": "completed",
            }

            evaluation_input = EvaluationInput(
                audit_report=DocumentContent(
                    title="Test", content="Test audit", page_count=1, metadata={}
                ),
                remediation_plans={
                    "PlanA": DocumentContent(
                        title="Plan1", content="Test plan", page_count=1, metadata={}
                    )
                },
            )

            result = resilience_manager.execute_with_fallback(evaluation_input)

            assert result["availability_status"]["gemini"] is True
            assert result["availability_status"]["openai"] is True
            assert result["partial_evaluation"] is False
            assert result["completion_stats"]["total_plans"] == 1
            assert result["completion_stats"]["completed"] == 1
            assert len(result["evaluations"]) == 1

    @patch(
        "src.utils.llm_resilience_manager.LLMResilienceManager._evaluate_plan_with_fallback"
    )
    def test_execute_with_fallback_partial_success(
        self, mock_evaluate_plan, resilience_manager
    ):
        """Test partial execution with fallback"""
        with patch.object(resilience_manager, "check_llm_availability") as mock_check:
            mock_check.return_value = {"gemini": True, "openai": False}

            # Mock mixed results
            mock_evaluate_plan.side_effect = [
                {"plan_name": "Plan1", "success": True, "status": "completed"},
                {"plan_name": "Plan2", "success": False, "status": "NA"},
            ]

            evaluation_input = EvaluationInput(
                audit_report=DocumentContent(
                    title="Test", content="Test audit", page_count=1, metadata={}
                ),
                remediation_plans={
                    "PlanA": DocumentContent(
                        title="Plan1", content="Test plan 1", page_count=1, metadata={}
                    ),
                    "PlanB": DocumentContent(
                        title="Plan2", content="Test plan 2", page_count=1, metadata={}
                    ),
                },
            )

            result = resilience_manager.execute_with_fallback(evaluation_input)

            assert result["partial_evaluation"] is True
            assert result["completion_stats"]["completed"] == 1
            assert result["completion_stats"]["na_count"] == 1
            assert resilience_manager.evaluation_stats["partial_evaluations"] == 1

    def test_evaluate_plan_with_fallback_primary_success(self, resilience_manager):
        """Test plan evaluation with primary LLM success"""
        resilience_manager.llm_status["gemini"].available = True
        resilience_manager.llm_status["openai"].available = True

        with patch.object(resilience_manager, "safe_llm_invoke") as mock_invoke:
            mock_invoke.return_value = {
                "success": True,
                "content": "Test evaluation content",
            }

            result = resilience_manager._evaluate_plan_with_fallback(
                "TestPlan", "Test content", "Test audit"
            )

            assert result["plan_name"] == "TestPlan"
            assert result["evaluator"] == "Primary Judge (Gemini Pro)"
            assert result["status"] == "completed"
            assert result["success"] is True

    def test_evaluate_plan_with_fallback_secondary_success(self, resilience_manager):
        """Test plan evaluation with secondary LLM success after primary failure"""
        resilience_manager.llm_status["gemini"].available = False
        resilience_manager.llm_status["openai"].available = True

        with patch.object(resilience_manager, "safe_llm_invoke") as mock_invoke:
            mock_invoke.return_value = {
                "success": True,
                "content": "Test evaluation content",
            }

            result = resilience_manager._evaluate_plan_with_fallback(
                "TestPlan", "Test content", "Test audit"
            )

            assert result["plan_name"] == "TestPlan"
            assert result["evaluator"] == "Secondary Judge (GPT-4)"
            assert result["status"] == "completed"
            assert result["success"] is True

    def test_evaluate_plan_with_fallback_both_fail(self, resilience_manager):
        """Test plan evaluation when both LLMs fail"""
        resilience_manager.llm_status["gemini"].available = False
        resilience_manager.llm_status["openai"].available = False

        result = resilience_manager._evaluate_plan_with_fallback(
            "TestPlan", "Test content", "Test audit"
        )

        assert result["plan_name"] == "TestPlan"
        assert result["status"] == "NA"
        assert result["na_reason"] == "Both primary and secondary LLMs unavailable"
        assert result["success"] is False

    def test_create_evaluation_prompt(self, resilience_manager):
        """Test evaluation prompt creation"""
        prompt = resilience_manager._create_evaluation_prompt(
            "TestPlan", "Test plan content", "Test audit content"
        )

        assert "TestPlan" in prompt
        assert "Test plan content" in prompt
        assert "Test audit content" in prompt
        assert "Strategic Prioritization (40%)" in prompt
        assert "Technical Specificity (30%)" in prompt

    def test_get_status_summary(self, resilience_manager):
        """Test status summary generation"""
        summary = resilience_manager.get_status_summary()

        assert "llm_status" in summary
        assert "evaluation_stats" in summary
        assert "config" in summary
        assert "timestamp" in summary
        assert "gemini" in summary["llm_status"]
        assert "openai" in summary["llm_status"]

    def test_reset_failure_counts(self, resilience_manager):
        """Test resetting failure counts"""
        # Set some failure counts
        resilience_manager.llm_status["gemini"].failure_count = 5
        resilience_manager.llm_status["openai"].consecutive_failures = 3

        resilience_manager.reset_failure_counts()

        assert resilience_manager.llm_status["gemini"].failure_count == 0
        assert resilience_manager.llm_status["openai"].failure_count == 0
        assert resilience_manager.llm_status["gemini"].consecutive_failures == 0
        assert resilience_manager.llm_status["openai"].consecutive_failures == 0
        assert resilience_manager.llm_status["gemini"].last_failure is None
        assert resilience_manager.llm_status["openai"].last_failure is None


class TestResilienceManagerIntegration:
    """Integration tests for resilience manager"""

    @pytest.fixture
    def evaluation_input(self):
        """Create a test evaluation input"""
        return EvaluationInput(
            audit_report=DocumentContent(
                title="Test Audit",
                content="This is a test audit report with accessibility findings.",
                page_count=1,
                metadata={},
            ),
            remediation_plans={
                "PlanA": DocumentContent(
                    title="Plan A",
                    content="This is plan A content.",
                    page_count=1,
                    metadata={},
                ),
                "PlanB": DocumentContent(
                    title="Plan B",
                    content="This is plan B content.",
                    page_count=1,
                    metadata={},
                ),
            },
        )

    @patch("src.utils.llm_resilience_manager.LLMResilienceManager._test_llm_connection")
    @patch("src.utils.llm_resilience_manager.LLMResilienceManager.safe_llm_invoke")
    def test_full_evaluation_workflow(
        self, mock_safe_invoke, mock_test_connection, evaluation_input
    ):
        """Test complete evaluation workflow with resilience"""
        # Setup mocks
        mock_test_connection.side_effect = [True, True]  # Both LLMs available
        mock_safe_invoke.return_value = {
            "success": True,
            "content": "Comprehensive evaluation of the plan",
        }

        mock_llm_manager = Mock(spec=LLMManager)
        mock_llm_manager.gemini = Mock()
        mock_llm_manager.openai = Mock()
        manager = LLMResilienceManager(mock_llm_manager)

        # Execute evaluation
        result = manager.execute_with_fallback(evaluation_input)

        # Verify results
        assert result["availability_status"]["gemini"] is True
        assert result["availability_status"]["openai"] is True
        assert result["partial_evaluation"] is False
        assert result["completion_stats"]["total_plans"] == 2
        assert result["completion_stats"]["completed"] == 2
        assert len(result["evaluations"]) == 2

        # Verify evaluation stats
        assert manager.evaluation_stats["total_evaluations"] == 2
        assert manager.evaluation_stats["successful_evaluations"] == 2
        assert manager.evaluation_stats["partial_evaluations"] == 0
