"""
Unit tests for LLM exception handling and classification.

Tests the custom exception classes and error classification functionality
for the LLM resilience system.

References:
    - LLM Error Handling Enhancement Plan - Phase 1.1
    - Master Plan: Testing standards and patterns
"""

from unittest.mock import Mock

import pytest

from src.utils.llm_exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMError,
    LLMQuotaExceededError,
    LLMRateLimitError,
    LLMTimeoutError,
    NoLLMAvailableError,
    PartialEvaluationError,
    classify_llm_error,
)


class TestLLMExceptions:
    """Test suite for LLM exception classes"""

    def test_llm_error_base_class(self):
        """Test base LLMError class functionality"""
        error = LLMError("Gemini Pro", "Test error", retryable=True)

        assert error.llm_type == "Gemini Pro"
        assert error.error_details == "Test error"
        assert error.retryable is True
        assert str(error) == "Gemini Pro error: Test error"

    def test_llm_connection_error(self):
        """Test LLMConnectionError creation and properties"""
        error = LLMConnectionError("GPT-4", "Network timeout")

        assert error.llm_type == "GPT-4"
        assert "Connection failed: Network timeout" in error.error_details
        assert error.retryable is True
        assert "GPT-4 error: Connection failed: Network timeout" in str(error)

    def test_llm_timeout_error(self):
        """Test LLMTimeoutError creation and properties"""
        error = LLMTimeoutError("Gemini Pro", 30)

        assert error.llm_type == "Gemini Pro"
        assert "Request timed out after 30 seconds" in error.error_details
        assert error.retryable is True
        assert "Gemini Pro error: Request timed out after 30 seconds" in str(error)

    def test_llm_rate_limit_error(self):
        """Test LLMRateLimitError creation and properties"""
        error = LLMRateLimitError("GPT-4", retry_after_seconds=60)

        assert error.llm_type == "GPT-4"
        assert "Rate limit exceeded (retry after 60s)" in error.error_details
        assert error.retryable is True
        assert "GPT-4 error: Rate limit exceeded (retry after 60s)" in str(error)

    def test_llm_rate_limit_error_no_retry_after(self):
        """Test LLMRateLimitError without retry_after parameter"""
        error = LLMRateLimitError("Gemini Pro")

        assert error.llm_type == "Gemini Pro"
        assert "Rate limit exceeded" in error.error_details
        assert "(retry after" not in error.error_details

    def test_llm_authentication_error(self):
        """Test LLMAuthenticationError creation and properties"""
        error = LLMAuthenticationError("GPT-4", "Invalid API key")

        assert error.llm_type == "GPT-4"
        assert "Authentication failed: Invalid API key" in error.error_details
        assert error.retryable is False  # Authentication errors are not retryable
        assert "GPT-4 error: Authentication failed: Invalid API key" in str(error)

    def test_llm_quota_exceeded_error(self):
        """Test LLMQuotaExceededError creation and properties"""
        error = LLMQuotaExceededError("Gemini Pro", "Monthly quota exceeded")

        assert error.llm_type == "Gemini Pro"
        assert "Quota exceeded: Monthly quota exceeded" in error.error_details
        assert error.retryable is False  # Quota errors are not retryable
        assert "Gemini Pro error: Quota exceeded: Monthly quota exceeded" in str(error)

    def test_partial_evaluation_error(self):
        """Test PartialEvaluationError creation and properties"""
        error = PartialEvaluationError(3, 5, ["Gemini Pro"])

        assert error.completed_count == 3
        assert error.total_count == 5
        assert error.failed_llms == ["Gemini Pro"]
        assert "Partial evaluation completed: 3/5 (60.0%)" in str(error)
        assert "Failed LLMs: Gemini Pro" in str(error)

    def test_partial_evaluation_error_zero_total(self):
        """Test PartialEvaluationError with zero total count"""
        error = PartialEvaluationError(0, 0, [])

        assert error.completed_count == 0
        assert error.total_count == 0
        assert error.failed_llms == []
        assert "Partial evaluation completed: 0/0 (0.0%)" in str(error)

    def test_no_llm_available_error(self):
        """Test NoLLMAvailableError creation and properties"""
        error = NoLLMAvailableError(["Gemini Pro", "GPT-4"])

        assert error.attempted_llms == ["Gemini Pro", "GPT-4"]
        assert "No LLMs available for evaluation" in str(error)
        assert "Attempted: Gemini Pro, GPT-4" in str(error)


class TestErrorClassification:
    """Test suite for error classification functionality"""

    def test_classify_timeout_error(self):
        """Test classification of timeout errors"""
        timeout_exception = Exception("Request timed out after 30 seconds")
        classified = classify_llm_error(timeout_exception, "Gemini Pro")

        assert isinstance(classified, LLMTimeoutError)
        assert classified.llm_type == "Gemini Pro"
        assert "30 seconds" in classified.error_details

    def test_classify_rate_limit_error(self):
        """Test classification of rate limit errors"""
        rate_limit_exception = Exception(
            "Rate limit exceeded. Try again in 60 seconds."
        )
        classified = classify_llm_error(rate_limit_exception, "GPT-4")

        assert isinstance(classified, LLMRateLimitError)
        assert classified.llm_type == "GPT-4"
        assert "rate limit" in str(classified).lower()

    def test_classify_authentication_error(self):
        """Test classification of authentication errors"""
        auth_exception = Exception("Authentication failed: Invalid API key")
        classified = classify_llm_error(auth_exception, "Gemini Pro")

        assert isinstance(classified, LLMAuthenticationError)
        assert classified.llm_type == "Gemini Pro"
        assert classified.retryable is False

    def test_classify_quota_error(self):
        """Test classification of quota exceeded errors"""
        quota_exception = Exception("Quota exceeded for this billing period")
        classified = classify_llm_error(quota_exception, "GPT-4")

        assert isinstance(classified, LLMQuotaExceededError)
        assert classified.llm_type == "GPT-4"
        assert classified.retryable is False

    def test_classify_generic_error_as_connection(self):
        """Test that generic errors are classified as connection errors"""
        generic_exception = Exception("Some random error occurred")
        classified = classify_llm_error(generic_exception, "Gemini Pro")

        assert isinstance(classified, LLMConnectionError)
        assert classified.llm_type == "Gemini Pro"
        assert classified.retryable is True

    def test_classify_error_case_insensitive(self):
        """Test that error classification is case insensitive"""
        # Test timeout with different cases
        timeout_exception = Exception("TIMEOUT after 30 seconds")
        classified = classify_llm_error(timeout_exception, "GPT-4")

        assert isinstance(classified, LLMTimeoutError)
        assert classified.llm_type == "GPT-4"

        # Test rate limit with different cases
        rate_limit_exception = Exception("RATE_LIMIT exceeded")
        classified = classify_llm_error(rate_limit_exception, "Gemini Pro")

        assert isinstance(classified, LLMRateLimitError)
        assert classified.llm_type == "Gemini Pro"

    def test_classify_error_with_multiple_keywords(self):
        """Test classification when error message contains multiple keywords"""
        # Should match the first keyword found (timeout)
        mixed_exception = Exception("Request timed out due to rate limit issues")
        classified = classify_llm_error(mixed_exception, "GPT-4")

        assert isinstance(classified, LLMTimeoutError)
        assert classified.llm_type == "GPT-4"


class TestExceptionInheritance:
    """Test exception inheritance and type checking"""

    def test_exception_inheritance_hierarchy(self):
        """Test that all LLM exceptions inherit from LLMError"""
        exceptions = [
            LLMConnectionError("test", "test"),
            LLMTimeoutError("test", 30),
            LLMRateLimitError("test"),
            LLMAuthenticationError("test", "test"),
            LLMQuotaExceededError("test", "test"),
        ]

        for exception in exceptions:
            assert isinstance(exception, LLMError)
            assert isinstance(exception, Exception)

    def test_partial_evaluation_error_inheritance(self):
        """Test PartialEvaluationError inheritance"""
        error = PartialEvaluationError(1, 2, ["test"])

        assert isinstance(error, Exception)
        assert not isinstance(error, LLMError)  # Should not inherit from LLMError

    def test_no_llm_available_error_inheritance(self):
        """Test NoLLMAvailableError inheritance"""
        error = NoLLMAvailableError(["test"])

        assert isinstance(error, Exception)
        assert not isinstance(error, LLMError)  # Should not inherit from LLMError


class TestExceptionProperties:
    """Test exception properties and attributes"""

    def test_llm_error_retryable_property(self):
        """Test retryable property of LLM errors"""
        retryable_error = LLMConnectionError("test", "test", retryable=True)
        non_retryable_error = LLMAuthenticationError("test", "test")

        assert retryable_error.retryable is True
        assert non_retryable_error.retryable is False

    def test_timeout_error_timeout_seconds(self):
        """Test timeout_seconds property of LLMTimeoutError"""
        error = LLMTimeoutError("test", 45)

        assert "45 seconds" in error.error_details

    def test_rate_limit_error_retry_after(self):
        """Test retry_after_seconds property of LLMRateLimitError"""
        error = LLMRateLimitError("test", retry_after_seconds=120)

        assert "retry after 120s" in error.error_details

    def test_partial_evaluation_error_calculation(self):
        """Test completion rate calculation in PartialEvaluationError"""
        error = PartialEvaluationError(7, 10, ["test"])

        # 7/10 = 70%
        assert "70.0%" in str(error)

    def test_partial_evaluation_error_zero_division(self):
        """Test PartialEvaluationError handles zero division gracefully"""
        error = PartialEvaluationError(0, 0, [])

        # Should not raise exception, should show 0.0%
        assert "0.0%" in str(error)
