"""
Resilience Integration Tests - Phase 4
LLM Error Handling Enhancement Plan

Comprehensive integration tests for resilience scenarios, error handling,
and performance testing with degraded LLM availability.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.config.crew_config import AccessibilityEvaluationCrew
from src.models.evaluation_models import DocumentContent, EvaluationInput
from src.reports.generators.evaluation_report_generator import EvaluationReportGenerator
from src.utils.llm_exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMQuotaExceededError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from src.utils.llm_resilience_manager import LLMResilienceManager, ResilienceConfig
from src.utils.workflow_controller import WorkflowController


class TestResilienceIntegration:
    """Integration tests for LLM resilience and error handling scenarios"""

    def setup_method(self):
        """Set up test components with resilience capabilities"""
        self.resilience_config = ResilienceConfig(
            max_retries=3,
            retry_delay_seconds=1,
            exponential_backoff=True,
            timeout_seconds=10,
            enable_partial_evaluation=True,
            minimum_llm_requirement=1,
            na_reporting_enabled=True,
        )

        # Mock LLM manager
        self.mock_llm_manager = Mock()
        self.mock_llm_manager.gemini_llm = Mock()
        self.mock_llm_manager.openai_llm = Mock()

        # Create resilience manager
        self.resilience_manager = LLMResilienceManager(
            self.mock_llm_manager, config=self.resilience_config
        )

        # Create crew with resilience
        self.crew = AccessibilityEvaluationCrew(
            self.mock_llm_manager, self.resilience_manager
        )

        # Create workflow controller
        self.workflow_controller = WorkflowController(
            self.crew, self.resilience_manager
        )

        # Create report generator
        self.report_generator = EvaluationReportGenerator()

    def test_single_llm_failure_scenario(self):
        """Test evaluation continues when one LLM fails"""

        # Mock LLM availability - only Gemini available
        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": True, "openai": False}

            # Mock successful evaluation with Gemini
            mock_result = Mock()
            mock_result.content = "Evaluation completed successfully"
            self.mock_llm_manager.gemini_llm.invoke.return_value = mock_result

            # Create test evaluation input
            evaluation_input = EvaluationInput(
                audit_report=DocumentContent(
                    title="Test Audit Report",
                    content="Test audit content",
                    page_count=1,
                    metadata={"source": "test"},
                ),
                remediation_plans={
                    "PlanA": DocumentContent(
                        title="TestPlan",
                        content="Test content",
                        page_count=1,
                        metadata={"source": "test"},
                    )
                },
            )

            # Use evaluation_input to avoid unused variable warning
            assert evaluation_input.audit_report.title == "Test Audit Report"

            # Execute evaluation
            result = self.resilience_manager.evaluate_plan_with_fallback(
                "TestPlan", "Test content", "Test audit context"
            )

            # Verify evaluation completed with available LLM
            assert result["status"] == "completed"
            assert result["llm_used"] == "gemini"
            assert "Evaluation completed successfully" in result["evaluation_content"]

            # Verify availability was checked
            mock_availability.assert_called_once()

    def test_both_llm_failure_scenario(self):
        """Test system handles complete LLM unavailability"""

        # Mock both LLMs unavailable
        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": False, "openai": False}

            # Mock LLM failures
            self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMConnectionError(
                "gemini", "Connection failed"
            )
            self.mock_llm_manager.openai_llm.invoke.side_effect = LLMConnectionError(
                "openai", "Connection failed"
            )

            # Execute evaluation
            result = self.resilience_manager.evaluate_plan_with_fallback(
                "TestPlan", "Test content", "Test audit context"
            )

            # Verify NA result generated
            assert result["status"] == "NA"
            assert "LLM unavailable" in result["reason"]
            assert result["evaluation_content"] is None

    def test_intermittent_llm_failures(self):
        """Test recovery from temporary LLM failures"""

        # Mock intermittent failures
        call_count = 0

        def mock_invoke(prompt):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # First two calls fail
                raise LLMConnectionError("gemini", "Temporary failure")
            else:  # Third call succeeds
                mock_result = Mock()
                mock_result.content = "Recovery successful"
                return mock_result

        self.mock_llm_manager.gemini_llm.invoke.side_effect = mock_invoke

        # Mock availability check
        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": True, "openai": False}

            # Execute evaluation with retry logic
            result = self.resilience_manager.safe_llm_invoke(
                self.mock_llm_manager.gemini_llm, "Test prompt", max_retries=3
            )

            # Verify recovery after retries
            assert result["success"] is True
            assert "Recovery successful" in result["content"]
            assert call_count == 3  # Should have retried twice

    def test_timeout_and_rate_limit_scenarios(self):
        """Test handling of timeout and rate limit errors"""

        # Test timeout scenario
        self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMTimeoutError(
            "gemini", "Request timeout"
        )

        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": True, "openai": False}

            result = self.resilience_manager.safe_llm_invoke(
                self.mock_llm_manager.gemini_llm, "Test prompt", max_retries=2
            )

            # Should fail after retries
            assert result["success"] is False
            assert "timeout" in result["error"].lower()

        # Test rate limit scenario
        self.mock_llm_manager.gemini_llm.invoke.side_effect = LLMRateLimitError(
            "gemini", "Rate limit exceeded"
        )

        result = self.resilience_manager.safe_llm_invoke(
            self.mock_llm_manager.gemini_llm, "Test prompt", max_retries=1
        )

        # Should fail immediately (rate limit is not retryable)
        assert result["success"] is False
        assert "rate limit" in result["error"].lower()

    def test_workflow_controller_resilience_integration(self):
        """Test workflow controller integration with resilience features"""

        # Mock availability check
        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": True, "openai": False}

            # Mock successful evaluation
            mock_result = Mock()
            mock_result.content = "Workflow evaluation completed"
            self.mock_llm_manager.gemini_llm.invoke.return_value = mock_result

            # Create evaluation input
            evaluation_input = EvaluationInput(
                plan_name="WorkflowTest",
                plan_content="Workflow test content",
                audit_context="Workflow test context",
            )

            # Execute workflow
            result = asyncio.run(
                self.workflow_controller._run_evaluation_workflow(
                    evaluation_input, mode="standard", include_consensus=False
                )
            )

            # Verify workflow completed successfully
            assert result is not None
            # Additional assertions based on expected workflow output structure

    def test_crew_resilience_integration(self):
        """Test crew integration with resilience capabilities"""

        # Mock availability check
        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": True, "openai": False}

            # Create evaluation input
            evaluation_input = EvaluationInput(
                plan_name="CrewTest",
                plan_content="Crew test content",
                audit_context="Crew test context",
            )

            # Mock agent availability
            with patch.object(self.crew, "get_available_agents") as mock_agents:
                mock_agents.return_value = ["primary_judge"]

                # Execute crew evaluation
                result = self.crew.execute_evaluation(evaluation_input)

                # Verify crew handled partial availability
                assert result is not None
                # Additional assertions based on expected crew output

    def test_report_generation_with_na_sections(self):
        """Test report generation with NA evaluation sections"""

        # Create evaluation results with NA sections
        evaluation_results = {
            "evaluations": [
                {
                    "plan_name": "PlanA",
                    "status": "completed",
                    "evaluation_content": "Successful evaluation",
                    "llm_used": "gemini",
                },
                {
                    "plan_name": "PlanB",
                    "status": "NA",
                    "evaluation_content": None,
                    "reason": "LLM unavailable",
                    "llm_used": None,
                },
            ],
            "resilience_info": {
                "available_llms": ["gemini"],
                "unavailable_llms": ["openai"],
                "completion_percentage": 50.0,
                "na_evaluations_count": 1,
            },
        }

        # Generate report
        report_content = self.report_generator._create_evaluation_summary(
            evaluation_results
        )

        # Verify NA section was generated
        na_section_found = False
        for item in report_content:
            if hasattr(item, "text") and "PlanB" in item.text and "NA" in item.text:
                na_section_found = True
                break

        assert na_section_found, "NA section should be present in report"

    def test_performance_with_degraded_availability(self):
        """Test system performance with degraded LLM availability"""

        import time

        # Mock partial availability
        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": True, "openai": False}

            # Mock successful evaluation with delay
            def mock_invoke_with_delay(prompt):
                time.sleep(0.1)  # Simulate network delay
                mock_result = Mock()
                mock_result.content = "Delayed evaluation"
                return mock_result

            self.mock_llm_manager.gemini_llm.invoke.side_effect = mock_invoke_with_delay

            # Measure performance
            start_time = time.time()

            result = self.resilience_manager.evaluate_plan_with_fallback(
                "PerformanceTest", "Test content", "Test context"
            )

            end_time = time.time()
            execution_time = end_time - start_time

            # Verify evaluation completed successfully
            assert result["status"] == "completed"
            assert execution_time < 1.0  # Should complete within reasonable time

    def test_error_classification_and_handling(self):
        """Test comprehensive error classification and handling"""

        # Test different error types
        error_scenarios = [
            (LLMConnectionError("gemini", "Network error"), "connection"),
            (LLMTimeoutError("gemini", "Request timeout"), "timeout"),
            (LLMRateLimitError("gemini", "Rate limit exceeded"), "rate_limit"),
            (LLMAuthenticationError("gemini", "Invalid API key"), "authentication"),
            (LLMQuotaExceededError("gemini", "Quota exceeded"), "quota"),
        ]

        for error, expected_type in error_scenarios:
            # Mock LLM to raise specific error
            self.mock_llm_manager.gemini_llm.invoke.side_effect = error

            with patch.object(
                self.resilience_manager, "check_llm_availability"
            ) as mock_availability:
                mock_availability.return_value = {"gemini": True, "openai": False}

                result = self.resilience_manager.safe_llm_invoke(
                    self.mock_llm_manager.gemini_llm, "Test prompt", max_retries=1
                )

                # Verify error was handled appropriately
                assert result["success"] is False
                assert (
                    expected_type in result["error"].lower()
                    or expected_type in str(error).lower()
                )

    def test_recovery_from_temporary_failures(self):
        """Test system recovery from temporary LLM failures"""

        # Mock recovery scenario
        failure_count = 0

        def mock_invoke_with_recovery(prompt):
            nonlocal failure_count
            failure_count += 1
            if failure_count <= 2:  # First two calls fail
                raise LLMConnectionError("gemini", "Temporary network issue")
            else:  # Third call succeeds
                mock_result = Mock()
                mock_result.content = "Recovery successful"
                return mock_result

        self.mock_llm_manager.gemini_llm.invoke.side_effect = mock_invoke_with_recovery

        with patch.object(
            self.resilience_manager, "check_llm_availability"
        ) as mock_availability:
            mock_availability.return_value = {"gemini": True, "openai": False}

            # Execute with retry logic
            result = self.resilience_manager.safe_llm_invoke(
                self.mock_llm_manager.gemini_llm, "Test prompt", max_retries=3
            )

            # Verify successful recovery
            assert result["success"] is True
            assert "Recovery successful" in result["content"]
            assert failure_count == 3  # Should have retried twice

    def test_comprehensive_error_scenario_coverage(self):
        """Test comprehensive coverage of all error scenarios"""

        # Test all major error scenarios
        scenarios = [
            {
                "name": "Single LLM Failure",
                "availability": {"gemini": True, "openai": False},
                "expected_status": "completed",
            },
            {
                "name": "Both LLM Failure",
                "availability": {"gemini": False, "openai": False},
                "expected_status": "NA",
            },
            {
                "name": "Intermittent Failure",
                "availability": {"gemini": True, "openai": False},
                "side_effect": LLMConnectionError("gemini", "Intermittent"),
                "expected_status": "NA",
            },
        ]

        for scenario in scenarios:
            with patch.object(
                self.resilience_manager, "check_llm_availability"
            ) as mock_availability:
                mock_availability.return_value = scenario["availability"]

                if "side_effect" in scenario:
                    self.mock_llm_manager.gemini_llm.invoke.side_effect = scenario[
                        "side_effect"
                    ]
                else:
                    # Mock successful evaluation
                    mock_result = Mock()
                    mock_result.content = f"Evaluation for {scenario['name']}"
                    self.mock_llm_manager.gemini_llm.invoke.return_value = mock_result

                result = self.resilience_manager.evaluate_plan_with_fallback(
                    f"TestPlan_{scenario['name']}", "Test content", "Test context"
                )

                # Verify expected behavior
                assert (
                    result["status"] == scenario["expected_status"]
                ), f"Failed for scenario: {scenario['name']}"


class TestResiliencePerformance:
    """Performance tests for resilience features"""

    def setup_method(self):
        """Set up performance test components"""
        self.resilience_manager = LLMResilienceManager(Mock())
        self.report_generator = EvaluationReportGenerator()

    def test_resilience_manager_performance(self):
        """Test resilience manager performance under load"""

        import time

        # Test multiple concurrent evaluations
        start_time = time.time()

        for i in range(10):
            result = self.resilience_manager.mark_evaluation_as_na(
                f"Plan{i}", "gemini", "Performance test"
            )
            assert result["status"] == "NA"

        end_time = time.time()
        execution_time = end_time - start_time

        # Should handle 10 evaluations quickly
        assert execution_time < 1.0

    def test_report_generation_performance(self):
        """Test report generation performance with NA sections"""

        import time

        # Create large evaluation results
        evaluation_results = {
            "evaluations": [
                {
                    "plan_name": f"Plan{i}",
                    "status": "NA" if i % 2 == 0 else "completed",
                    "evaluation_content": (
                        f"Content for plan {i}" if i % 2 == 1 else None
                    ),
                    "reason": "LLM unavailable" if i % 2 == 0 else None,
                }
                for i in range(20)
            ],
            "resilience_info": {
                "available_llms": ["gemini"],
                "unavailable_llms": ["openai"],
                "completion_percentage": 50.0,
                "na_evaluations_count": 10,
            },
        }

        # Measure report generation time
        start_time = time.time()

        report_content = self.report_generator._create_evaluation_summary(
            evaluation_results
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Should generate report quickly
        assert execution_time < 2.0
        assert len(report_content) > 0


class TestResilienceDocumentation:
    """Tests for documentation and user guidance features"""

    def setup_method(self):
        """Set up documentation test components"""
        self.report_generator = EvaluationReportGenerator()

    def test_troubleshooting_guidance_generation(self):
        """Test generation of troubleshooting guidance for NA sections"""

        # Create evaluation results with NA sections
        evaluation_results = {
            "evaluations": [
                {"plan_name": "PlanA", "status": "NA", "reason": "LLM unavailable"}
            ],
            "resilience_info": {
                "available_llms": [],
                "unavailable_llms": ["gemini", "openai"],
                "completion_percentage": 0.0,
                "na_evaluations_count": 1,
            },
        }

        # Generate troubleshooting guidance
        guidance = self.report_generator._create_troubleshooting_guidance(
            evaluation_results
        )

        # Verify guidance was generated
        assert guidance is not None
        assert len(guidance) > 0

        # Check for helpful content
        guidance_text = " ".join([str(item) for item in guidance])
        assert (
            "troubleshoot" in guidance_text.lower()
            or "guidance" in guidance_text.lower()
        )

    def test_na_result_interpretation_documentation(self):
        """Test documentation for NA result interpretation"""

        # Test NA section creation
        na_section = self.report_generator._create_na_evaluation_section(
            "TestPlan", "gemini", "LLM unavailable"
        )

        # Verify NA section contains helpful information
        section_text = " ".join([str(item) for item in na_section])
        assert "Not Available" in section_text
        assert "LLM unavailable" in section_text
        assert "troubleshooting" in section_text.lower()
