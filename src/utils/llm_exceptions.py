"""
Custom exceptions for LLM error handling and resilience management.

This module defines specific exception types for different LLM failure scenarios,
enabling precise error handling and recovery strategies.

References:
    - LLM Error Handling Enhancement Plan - Phase 1.1
    - Master Plan: Error handling patterns
"""

from typing import Optional


class LLMError(Exception):
    """Base exception for all LLM-related errors"""

    def __init__(self, llm_type: str, error_details: str, retryable: bool = True):
        self.llm_type = llm_type
        self.error_details = error_details
        self.retryable = retryable
        super().__init__(f"{llm_type} error: {error_details}")


class LLMConnectionError(LLMError):
    """Raised when LLM API connection fails"""

    def __init__(self, llm_type: str, error_details: str, retryable: bool = True):
        super().__init__(llm_type, f"Connection failed: {error_details}", retryable)


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out"""

    def __init__(self, llm_type: str, timeout_seconds: int, retryable: bool = True):
        super().__init__(
            llm_type, f"Request timed out after {timeout_seconds} seconds", retryable
        )


class LLMRateLimitError(LLMError):
    """Raised when LLM API rate limit is exceeded"""

    def __init__(
        self,
        llm_type: str,
        retry_after_seconds: Optional[int] = None,
        retryable: bool = True,
    ):
        retry_info = (
            f" (retry after {retry_after_seconds}s)" if retry_after_seconds else ""
        )
        super().__init__(llm_type, f"Rate limit exceeded{retry_info}", retryable)


class LLMAuthenticationError(LLMError):
    """Raised when LLM API authentication fails"""

    def __init__(self, llm_type: str, error_details: str):
        super().__init__(
            llm_type, f"Authentication failed: {error_details}", retryable=False
        )


class LLMQuotaExceededError(LLMError):
    """Raised when LLM API quota is exceeded"""

    def __init__(self, llm_type: str, error_details: str):
        super().__init__(llm_type, f"Quota exceeded: {error_details}", retryable=False)


class PartialEvaluationError(Exception):
    """Raised when evaluation completes partially due to LLM failures"""

    def __init__(self, completed_count: int, total_count: int, failed_llms: list[str]):
        self.completed_count = completed_count
        self.total_count = total_count
        self.failed_llms = failed_llms
        completion_rate = (
            (completed_count / total_count) * 100 if total_count > 0 else 0
        )
        super().__init__(
            f"Partial evaluation completed: {completed_count}/{total_count} "
            f"({completion_rate:.1f}%) - Failed LLMs: {', '.join(failed_llms)}"
        )


class NoLLMAvailableError(Exception):
    """Raised when no LLMs are available for evaluation"""

    def __init__(self, attempted_llms: list[str]):
        self.attempted_llms = attempted_llms
        super().__init__(
            f"No LLMs available for evaluation. Attempted: {', '.join(attempted_llms)}"
        )


def classify_llm_error(error: Exception, llm_type: str) -> LLMError:
    """
    Classify a generic exception into a specific LLM error type.

    Args:
        error: The original exception
        llm_type: Type of LLM that generated the error

    Returns:
        Appropriate LLMError subclass instance
    """
    error_str = str(error).lower()

    # Check for timeout errors
    if any(keyword in error_str for keyword in ["timeout", "timed out", "time out"]):
        return LLMTimeoutError(llm_type, 30)  # Default timeout

    # Check for rate limiting
    if any(
        keyword in error_str
        for keyword in ["rate limit", "rate_limit", "too many requests"]
    ):
        return LLMRateLimitError(llm_type)

    # Check for authentication errors
    if any(
        keyword in error_str
        for keyword in ["authentication", "unauthorized", "invalid api key"]
    ):
        return LLMAuthenticationError(llm_type, str(error))

    # Check for quota exceeded
    if any(
        keyword in error_str for keyword in ["quota", "billing", "payment required"]
    ):
        return LLMQuotaExceededError(llm_type, str(error))

    # Default to connection error
    return LLMConnectionError(llm_type, str(error))
